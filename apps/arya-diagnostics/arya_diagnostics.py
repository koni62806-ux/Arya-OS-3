#!/usr/bin/env python3
"""Read-only Arya OS hardware diagnostics."""
import shutil
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

COMMANDS = [
    ("System", ["uname", "-a"]),
    ("Processor", ["lscpu"]),
    ("Memory", ["free", "-h"]),
    ("Storage", ["df", "-hT"]),
    ("PCI devices", ["lspci", "-nn"]),
    ("USB devices", ["lsusb"]),
    ("Network links", ["ip", "-brief", "link"]),
]

def report():
    parts = []
    for title, cmd in COMMANDS:
        if not shutil.which(cmd[0]):
            output = cmd[0] + " is not installed."
        else:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
                output = result.stdout.strip() or result.stderr.strip() or "(no output)"
            except (OSError, subprocess.TimeoutExpired) as exc:
                output = "Could not collect: " + str(exc)
        parts.append(title + "\n" + output)
    return "\n\n".join(parts)

class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title="Arya Diagnostics")
        self.set_default_size(760, 560)
        self.set_border_width(14)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(root)
        heading = Gtk.Label()
        heading.set_markup("<span size='x-large' weight='bold'>Arya Diagnostics</span>")
        heading.set_xalign(0)
        root.pack_start(heading, False, False, 0)
        note = Gtk.Label(label="Read-only report. No disks or system settings are changed.")
        note.set_xalign(0)
        root.pack_start(note, False, False, 0)
        self.view = Gtk.TextView()
        self.view.set_editable(False)
        self.view.set_monospace(True)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        root.pack_start(scroll, True, True, 0)
        buttons = Gtk.Box(spacing=8)
        refresh = Gtk.Button(label="Refresh")
        refresh.connect("clicked", self.refresh)
        copy = Gtk.Button(label="Copy report")
        copy.connect("clicked", self.copy_report)
        buttons.pack_start(refresh, False, False, 0)
        buttons.pack_start(copy, False, False, 0)
        root.pack_end(buttons, False, False, 0)
        self.refresh()

    def refresh(self, *_):
        self.view.get_buffer().set_text(report())

    def copy_report(self, *_):
        buf = self.view.get_buffer()
        start, end = buf.get_bounds()
        Gtk.Clipboard.get_default(self.get_display()).set_text(buf.get_text(start, end, True), -1)

if __name__ == "__main__":
    app = Window()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
