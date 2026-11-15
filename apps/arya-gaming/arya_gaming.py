#!/usr/bin/env python3
"""Arya Gaming: launch a selected game through GameMode when available."""
import shutil
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class GamingWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Arya Gaming")
        self.set_default_size(520, 300)
        self.set_border_width(20)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(root)
        title = Gtk.Label()
        title.set_markup('<span size="xx-large" weight="bold">🎮 Arya Gaming</span>')
        title.set_xalign(0)
        root.pack_start(title, False, False, 0)
        note = Gtk.Label(label="بازی را از اینجا اجرا کن تا GameMode در صورت نصب، تنظیمات عملکردی مجاز را هنگام اجرای آن اعمال کند.")
        note.set_line_wrap(True)
        note.set_xalign(0)
        root.pack_start(note, False, False, 0)
        self.path = Gtk.Entry()
        self.path.set_placeholder_text("نام فرمان یا مسیر اجرای بازی؛ مثال: /usr/games/...")
        root.pack_start(self.path, False, False, 0)
        self.status = Gtk.Label(label=self.mode_status(), xalign=0)
        root.pack_start(self.status, False, False, 0)
        run = Gtk.Button(label="اجرای بازی در حالت Gaming")
        run.connect("clicked", self.launch)
        root.pack_start(run, False, False, 0)
        disclaimer = Gtk.Label(label="این حالت محدودیت CPU/GPU و کارت گرافیک قدیمی را حذف نمی‌کند و بازی‌های ویندوزی را تضمین نمی‌کند.")
        disclaimer.set_line_wrap(True)
        disclaimer.set_xalign(0)
        root.pack_end(disclaimer, False, False, 0)
    def mode_status(self):
        return "GameMode نصب است." if shutil.which("gamemoderun") else "GameMode در دسترس نیست؛ پس از نصب بسته فعال می‌شود."
    def launch(self, *_):
        value = self.path.get_text().strip()
        if not value:
            self.status.set_text("ابتدا فرمان اجرای بازی را وارد کن.")
            return
        if not shutil.which(value) and not value.startswith("/"):
            self.status.set_text("فرمان پیدا نشد؛ نام برنامه یا مسیر کامل را بررسی کن.")
            return
        command = [value]
        if shutil.which("gamemoderun"):
            command = ["gamemoderun", "--", value]
        try:
            subprocess.Popen(command, close_fds=True, start_new_session=True)
            self.status.set_text("بازی اجرا شد؛ GameMode: " + ("فعال" if command[0] == "gamemoderun" else "در دسترس نیست"))
        except OSError as exc:
            self.status.set_text("اجرای بازی ناموفق بود: " + str(exc))

if __name__ == "__main__":
    win = GamingWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
