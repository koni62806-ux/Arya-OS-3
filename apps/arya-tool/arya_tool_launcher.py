#!/usr/bin/env python3
"""Small always-on-top Arya Tool edge launcher for XFCE/X11."""
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class EdgeLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Arya Tool")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_resizable(False)
        self.set_default_size(48, 58)
        self.set_border_width(3)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("realize", self.place_at_edge)
        self.connect("delete-event", lambda *_: Gtk.main_quit())
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
        window { background: transparent; }
        button { background: #6554c0; color: white; border: 1px solid #b9aaff;
                 border-radius: 18px; padding: 8px; font-size: 22px; }
        button:hover { background: #806ee8; }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        button = Gtk.Button(label="✦")
        button.set_tooltip_text("باز کردن Arya Tool")
        button.connect("clicked", self.open_tool)
        self.add(button)
    def place_at_edge(self, *_):
        screen = self.get_screen()
        monitor = screen.get_monitor_at_window(self.get_window())
        rect = screen.get_monitor_geometry(monitor)
        self.move(rect.x + rect.width - 54, rect.y + rect.height // 2 - 29)
    def open_tool(self, *_):
        try:
            subprocess.Popen(["arya-tool"], close_fds=True, start_new_session=True)
        except OSError as exc:
            dialog = Gtk.MessageDialog(transient_for=self, flags=0,
                message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
                text="Arya Tool اجرا نشد")
            dialog.format_secondary_text(str(exc))
            dialog.run()
            dialog.destroy()

if __name__ == "__main__":
    win = EdgeLauncher()
    win.show_all()
    Gtk.main()
