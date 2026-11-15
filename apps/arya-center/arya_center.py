#!/usr/bin/env python3
"""Arya Center: lightweight app and offline game launcher for Arya OS."""
import os
import subprocess
from pathlib import Path
from urllib.parse import quote

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

GAMES_DIR = Path("/usr/share/arya/games")
APP_LAUNCHERS = [
    ("Files", "org.xfce.Thunar"),
    ("Web browser", "firefox-esr"),
    ("Terminal", "xfce4-terminal"),
    ("Settings", "xfce4-settings-manager"),
    ("Arya Tool", "arya-tool"),
]

CSS = b"""
window { background: #111321; color: #f3f2fa; }
.header { color: #ffffff; font-size: 23px; font-weight: 700; }
.subtitle { color: #aaa9bd; font-size: 12px; }
button.tile { background: #20243a; color: #f4f1ff; border: 1px solid #343852; border-radius: 14px; padding: 16px; }
button.tile:hover { background: #303653; border-color: #9c8cff; }
button.tile label.name { font-weight: 600; }
button.action { background: #7565d9; color: white; border-radius: 10px; padding: 9px 16px; }
.section { color: #c7bfff; font-size: 15px; font-weight: 700; }
"""

class AryaCenter(Gtk.Window):
    def __init__(self):
        super().__init__(title="Arya Center")
        self.set_default_size(760, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(22)
        self.set_icon_name("applications-system")
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.add(root)
        top = Gtk.Box(spacing=12)
        heading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title = Gtk.Label(label="Arya Center", xalign=0)
        title.get_style_context().add_class("header")
        subtitle = Gtk.Label(label="Your apps, settings and games in one place", xalign=0)
        subtitle.get_style_context().add_class("subtitle")
        heading.pack_start(title, False, False, 0)
        heading.pack_start(subtitle, False, False, 0)
        top.pack_start(heading, True, True, 0)
        close = Gtk.Button(label="Close")
        close.connect("clicked", lambda *_: Gtk.main_quit())
        top.pack_end(close, False, False, 0)
        root.pack_start(top, False, False, 0)

        apps_label = Gtk.Label(label="QUICK ACCESS", xalign=0)
        apps_label.get_style_context().add_class("section")
        root.pack_start(apps_label, False, False, 0)
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        for index, (name, command) in enumerate(APP_LAUNCHERS):
            button = self.tile(name, "Open " + name)
            button.connect("clicked", self.launch_command, command)
            grid.attach(button, index % 3, index // 3, 1, 1)
        root.pack_start(grid, False, False, 0)

        games_label = Gtk.Label(label="GAMES", xalign=0)
        games_label.get_style_context().add_class("section")
        root.pack_start(games_label, False, False, 0)
        self.games_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.populate_games()
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.games_box)
        root.pack_start(scroller, True, True, 0)

        footer = Gtk.Label(label="Arya OS • Lightweight mode", xalign=0)
        footer.get_style_context().add_class("subtitle")
        root.pack_end(footer, False, False, 0)

    def tile(self, name, detail):
        button = Gtk.Button()
        button.get_style_context().add_class("tile")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label(label=name)
        label.get_style_context().add_class("name")
        desc = Gtk.Label(label=detail)
        desc.get_style_context().add_class("subtitle")
        box.pack_start(label, False, False, 0)
        box.pack_start(desc, False, False, 0)
        button.add(box)
        return button

    def launch_command(self, _button, command):
        try:
            subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except (OSError, FileNotFoundError) as error:
            self.message("Could not open " + command + ": " + str(error))

    def populate_games(self):
        games = []
        if GAMES_DIR.exists():
            for folder in sorted(GAMES_DIR.iterdir()):
                index = folder / "index.html"
                if folder.is_dir() and index.is_file():
                    games.append((folder.name.replace("-", " ").title(), index))
        if not games:
            note = Gtk.Label(label="No games installed yet. HTML games added to Arya OS will appear here.", xalign=0)
            note.set_line_wrap(True)
            note.get_style_context().add_class("subtitle")
            self.games_box.pack_start(note, False, False, 8)
            return
        for name, index in games:
            row = Gtk.Box(spacing=10)
            label = Gtk.Label(label=name, xalign=0)
            label.set_hexpand(True)
            row.pack_start(label, True, True, 0)
            play = Gtk.Button(label="Play")
            play.get_style_context().add_class("action")
            play.connect("clicked", self.open_game, index)
            row.pack_end(play, False, False, 0)
            self.games_box.pack_start(row, False, False, 4)

    def open_game(self, _button, index):
        uri = "file://" + quote(str(index))
        try:
            subprocess.Popen(["firefox-esr", "--new-window", uri], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except OSError as error:
            self.message("Could not start the browser: " + str(error))

    def message(self, text):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=text)
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    window = AryaCenter()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
