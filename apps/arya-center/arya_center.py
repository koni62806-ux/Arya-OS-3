#!/usr/bin/env python3
"""Arya Center: lightweight app launcher and offline game library for Arya OS."""
import os
import subprocess
from pathlib import Path
from urllib.parse import quote

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Gio

GAMES_DIR = Path("/usr/share/arya/games")
APP_LAUNCHERS = [
    ("Files", "thunar"),
    ("Web browser", "firefox-esr"),
    ("Terminal", "xfce4-terminal"),
    ("Settings", "xfce4-settings-manager"),
    ("Arya Tool", "arya-tool"),
]

CSS = b"""
window { background: #111321; color: #f3f2fa; }
.header { color: #ffffff; font-size: 25px; font-weight: 700; }
.subtitle { color: #aaa9bd; font-size: 12px; }
.section { color: #c7bfff; font-size: 14px; font-weight: 700; }
button.tile { background: #20243a; color: #f4f1ff; border: 1px solid #343852; border-radius: 14px; padding: 12px; }
button.tile:hover { background: #303653; border-color: #9c8cff; }
button.tile label.name { font-weight: 600; }
button.action { background: #7565d9; color: white; border-radius: 10px; padding: 8px 15px; }
entry { background: #20243a; color: #ffffff; border: 1px solid #454967; border-radius: 12px; padding: 11px; }
"""

class AryaCenter(Gtk.Window):
    def __init__(self):
        super().__init__(title="Arya Center")
        self.set_default_size(900, 650)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(22)
        self.set_icon_name("applications-system")
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(root)

        top = Gtk.Box(spacing=12)
        heading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title = Gtk.Label(label="Arya Center", xalign=0)
        title.get_style_context().add_class("header")
        subtitle = Gtk.Label(label="برنامه‌ها، تنظیمات و بازی‌ها در یک جا", xalign=0)
        subtitle.get_style_context().add_class("subtitle")
        heading.pack_start(title, False, False, 0)
        heading.pack_start(subtitle, False, False, 0)
        top.pack_start(heading, True, True, 0)
        close = Gtk.Button(label="بستن")
        close.connect("clicked", lambda *_: self.destroy())
        top.pack_end(close, False, False, 0)
        root.pack_start(top, False, False, 0)

        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("جست‌وجوی برنامه‌های نصب‌شده…")
        self.search.connect("search-changed", self.filter_apps)
        root.pack_start(self.search, False, False, 0)

        quick_label = Gtk.Label(label="دسترسی سریع", xalign=0)
        quick_label.get_style_context().add_class("section")
        root.pack_start(quick_label, False, False, 0)
        quick_grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        for index, (name, command) in enumerate(APP_LAUNCHERS):
            button = self.tile(name, "باز کردن " + name)
            button.connect("clicked", self.launch_command, command)
            quick_grid.attach(button, index % 5, index // 5, 1, 1)
        root.pack_start(quick_grid, False, False, 0)

        apps_label = Gtk.Label(label="همهٔ برنامه‌ها", xalign=0)
        apps_label.get_style_context().add_class("section")
        root.pack_start(apps_label, False, False, 0)
        self.apps_flow = Gtk.FlowBox()
        self.apps_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.apps_flow.set_homogeneous(True)
        self.apps_flow.set_min_children_per_line(3)
        self.apps_flow.set_max_children_per_line(5)
        self.apps_flow.set_column_spacing(10)
        self.apps_flow.set_row_spacing(10)
        self.apps_flow.set_filter_func(self.app_filter)
        self.populate_apps()
        apps_scroll = Gtk.ScrolledWindow()
        apps_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        apps_scroll.add(self.apps_flow)
        root.pack_start(apps_scroll, True, True, 0)

        games_label = Gtk.Label(label="بازی‌های آفلاین", xalign=0)
        games_label.get_style_context().add_class("section")
        root.pack_start(games_label, False, False, 0)
        self.games_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        self.populate_games()
        games_scroll = Gtk.ScrolledWindow()
        games_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        games_scroll.set_max_content_height(110)
        games_scroll.set_propagate_natural_height(True)
        games_scroll.add(self.games_box)
        root.pack_start(games_scroll, False, True, 0)

        footer = Gtk.Label(label="Arya OS • سبک و مناسب سخت‌افزارهای قدیمی", xalign=0)
        footer.get_style_context().add_class("subtitle")
        root.pack_end(footer, False, False, 0)
        self.search.grab_focus()

    def tile(self, name, detail):
        button = Gtk.Button()
        button.get_style_context().add_class("tile")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        label = Gtk.Label(label=name)
        label.get_style_context().add_class("name")
        desc = Gtk.Label(label=detail)
        desc.get_style_context().add_class("subtitle")
        box.pack_start(label, False, False, 0)
        box.pack_start(desc, False, False, 0)
        button.add(box)
        return button

    def populate_apps(self):
        """Use the desktop database so this list reflects apps actually installed."""
        apps = []
        seen = set()
        for info in Gio.AppInfo.get_all():
            try:
                if not info.should_show():
                    continue
                name = (info.get_display_name() or info.get_name() or "").strip()
                app_id = info.get_id() or name
                if not name or app_id in seen:
                    continue
                seen.add(app_id)
                apps.append((name.casefold(), name, info))
            except (AttributeError, GLib.Error):
                continue
        for _, name, info in sorted(apps):
            child = Gtk.FlowBoxChild()
            child.app_name = name.casefold()
            child.app_info = info
            button = Gtk.Button()
            button.get_style_context().add_class("tile")
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
            icon = info.get_icon()
            if icon:
                image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG)
                box.pack_start(image, False, False, 0)
            label = Gtk.Label(label=name)
            label.get_style_context().add_class("name")
            label.set_ellipsize(3)
            box.pack_start(label, False, False, 0)
            button.add(box)
            button.connect("clicked", self.launch_app_info, info)
            child.add(button)
            self.apps_flow.add(child)
        self.apps_flow.show_all()

    def app_filter(self, child, _data=None):
        query = self.search.get_text().strip().casefold()
        return not query or query in getattr(child, "app_name", "")

    def filter_apps(self, *_):
        self.apps_flow.invalidate_filter()

    def launch_app_info(self, _button, info):
        try:
            info.launch([], None)
        except GLib.Error as error:
            self.message("اجرای برنامه ناموفق بود: " + str(error))

    def launch_command(self, _button, command):
        executable = command.split()[0]
        if not (os.path.isabs(executable) and os.access(executable, os.X_OK)) and not Gio.AppInfo.get_default_for_type("x-scheme-handler/" + executable, False):
            # PATH lookup is delegated to Popen; no shell is involved.
            pass
        try:
            subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        except OSError as error:
            self.message("باز کردن برنامه ناموفق بود: " + str(error))

    def populate_games(self):
        games = []
        if GAMES_DIR.exists():
            for folder in sorted(GAMES_DIR.iterdir()):
                index = folder / "index.html"
                if folder.is_dir() and index.is_file():
                    games.append((folder.name.replace("-", " ").title(), index))
        if not games:
            note = Gtk.Label(label="هنوز بازی‌ای نصب نشده است. بازی‌های HTML آفلاین پس از اضافه‌شدن اینجا نمایش داده می‌شوند.", xalign=0)
            note.set_line_wrap(True)
            note.get_style_context().add_class("subtitle")
            self.games_box.pack_start(note, False, False, 5)
            return
        for name, index in games:
            row = Gtk.Box(spacing=10)
            label = Gtk.Label(label=name, xalign=0)
            label.set_hexpand(True)
            row.pack_start(label, True, True, 0)
            play = Gtk.Button(label="بازی")
            play.get_style_context().add_class("action")
            play.connect("clicked", self.open_game, index)
            row.pack_end(play, False, False, 0)
            self.games_box.pack_start(row, False, False, 3)

    def open_game(self, _button, index):
        uri = "file://" + quote(str(index))
        try:
            subprocess.Popen(["firefox-esr", "--new-window", uri], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        except OSError as error:
            self.message("باز کردن بازی ناموفق بود: " + str(error))

    def message(self, text):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text=text)
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    window = AryaCenter()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
