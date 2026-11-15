#!/usr/bin/env python3
"""Read-only hardware and system diagnostics for Arya OS."""
import shutil
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

CHECKS = [
    ("System", ["uname", "-a"]),
    ("Processor", ["lscpu"]),
    ("Memory", ["free", "-h"]),
    ("Storage", ["df", "-hT"]),
    ("PCI devices", ["lspci", "-nn"]),
    ("USB devices", ["lsusb"]),
    ("Network links", ["ip", "-brief", "link"]),
]

def collect():
    sections = []
    for title, command in CHECKS:
        if not shutil.which(command[0]):
            output = command[0] + " is not installed."
        else:
            try:
                result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=12)
                output = result.stdout.strip() or result.stderr.strip() or "(no output)"
            except (OSError, subprocess.TimeoutExpired) as exc:
                output = "Unable to collect: " + str(exc)
        sections.append("## " + title + "\n" + output)
    return "\n\n".join(sections)

class Diagnostics(Gtk.Window):
    def __init__(self):
        super().__init__(title="Arya Diagnostics")
        self.set_default_size(780, 600)
        self.set_border_width(14)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(root)
        title = Gtk.Label(label="Arya Diagnostics", xalign=0)
        title.set_markup("<span size='x-large' weight='bold'>Arya Diagnostics</span>")
        root.pack_start(title, False, False, 0)
        note = Gtk.Label(label="Read-only system report. No settings or disks are changed.", xalign=0)
        root.pack_start(note, False, False, 0)
        self.view = Gtk.TextView()
        self.view.set_editable(False)
        self.view.set_monospace(True)
        self.view.set_wrap_mode(Gtk.WrapMode.NONE)
        self.buffer = self.view.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        root.pack_start(scroll, True, True, 0)
        actions = Gtk.Box(spacing=8)
        refresh = Gtk.Button(label="Refresh")
        refresh.connect("clicked", self.refresh)
        copy = Gtk.Button(label="Copy report")
        copy.connect("clicked", self.copy_report)
        actions.pack_start(refresh, False, False, 0)
        actions.pack_start(copy, False, False, 0)
        root.pack_end(actions, False, False, 0)
        self.refresh()

    def refresh(self, *_):
        self.buffer.set_text(collect())

    def copy_report(self, *_):
        start, end = self.buffer.get_bounds()
        Gtk.Clipboard.get_default(self.get_display()).set_text(self.buffer.get_text(start, end, True), -1)

if __name__ == "__main__":
    window = Diagnostics()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
