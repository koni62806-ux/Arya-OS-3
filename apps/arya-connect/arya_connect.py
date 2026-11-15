#!/usr/bin/env python3
"""Arya Connect: consent-based Tor/Snowflake connection control for Arya OS."""
import subprocess
import threading
from pathlib import Path
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

SERVICE = "tor@default"


class AryaConnect(Gtk.Window):
    def __init__(self):
        super().__init__(title="Arya Connect")
        self.set_default_size(520, 420)
        self.set_border_width(22)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(root)
        title = Gtk.Label()
        title.set_markup('<span size="xx-large" weight="bold">◈ Arya Connect</span>')
        title.set_xalign(0)
        root.pack_start(title, False, False, 0)
        subtitle = Gtk.Label(label="اتصال امن‌تر به اینترنت با Tor و Snowflake")
        subtitle.set_xalign(0)
        root.pack_start(subtitle, False, False, 0)
        info = Gtk.Label()
        info.set_markup(
            "<b>حریم خصوصی و محدودیت شبکه</b>\n"
            "این ابزار سرویس Tor را با درخواست خودت روشن یا خاموش می‌کند. "
            "Snowflake می‌تواند در بعضی شرایط فیلترینگ کمک کند؛ "
            "اما قطع کامل مسیر اینترنت بین‌الملل را دور نمی‌زند و اتصال را تضمین نمی‌کند."
        )
        info.set_line_wrap(True)
        info.set_xalign(0)
        root.pack_start(info, False, False, 8)
        self.status = Gtk.Label(label="وضعیت در حال بررسی…")
        self.status.set_xalign(0)
        root.pack_start(self.status, False, False, 8)
        row = Gtk.Box(spacing=10)
        root.pack_start(row, False, False, 0)
        self.start_btn = Gtk.Button(label="روشن کردن اتصال")
        self.start_btn.connect("clicked", self.run_action, "start")
        row.pack_start(self.start_btn, True, True, 0)
        self.stop_btn = Gtk.Button(label="خاموش کردن")
        self.stop_btn.connect("clicked", self.run_action, "stop")
        row.pack_start(self.stop_btn, True, True, 0)
        refresh = Gtk.Button(label="بررسی وضعیت")
        refresh.connect("clicked", lambda *_: self.refresh())
        root.pack_start(refresh, False, False, 0)
        browser = Gtk.Button(label="باز کردن مرورگر از طریق Tor")
        browser.connect("clicked", self.open_tor_browser)
        root.pack_start(browser, False, False, 0)
        note = Gtk.Label(label="نکته: این نسخه پراکسی Tor را مدیریت می‌کند؛ تونل سراسری VPN برای تمام برنامه‌ها نیست.")
        note.set_line_wrap(True)
        note.set_xalign(0)
        root.pack_end(note, False, False, 0)
        self.refresh()

    def open_tor_browser(self, *_):
        try:
            active = subprocess.run(["systemctl", "is-active", "--quiet", SERVICE],
                timeout=8).returncode == 0
        except (OSError, subprocess.SubprocessError):
            active = False
        if not active:
            self.status.set_text("ابتدا اتصال Tor را روشن کن؛ سپس مرورگر امن را باز کن.")
            return
        profile = Path.home() / ".local" / "share" / "arya-connect" / "firefox-tor-profile"
        try:
            profile.mkdir(parents=True, exist_ok=True)
            preferences = """user_pref("network.proxy.type", 1);
user_pref("network.proxy.socks", "127.0.0.1");
user_pref("network.proxy.socks_port", 9050);
user_pref("network.proxy.socks_version", 5);
user_pref("network.proxy.socks_remote_dns", true);
user_pref("network.proxy.no_proxies_on", "");
user_pref("network.trr.mode", 5);
user_pref("media.peerconnection.enabled", false);
"""
            (profile / "user.js").write_text(preferences, encoding="utf-8")
            subprocess.Popen(["firefox-esr", "--no-remote", "--profile", str(profile), "about:blank"],
                close_fds=True, start_new_session=True)
            self.status.set_text("مرورگر با پراکسی SOCKS5 باز شد؛ اتصال واقعی را در مرورگر بررسی کن.")
        except (OSError, subprocess.SubprocessError) as exc:
            self.status.set_text("مرورگر Tor باز نشد: " + str(exc))

    def run_action(self, _button, action):
        if action == "start":
            message = "سرویس Tor روشن شود؟"
        else:
            message = "سرویس Tor خاموش شود؟"
        dialog = Gtk.MessageDialog(transient_for=self, flags=0,
            message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            text=message)
        answer = dialog.run()
        dialog.destroy()
        if answer != Gtk.ResponseType.YES:
            return
        self.start_btn.set_sensitive(False)
        self.stop_btn.set_sensitive(False)
        command = ["pkexec", "systemctl", action, SERVICE]
        threading.Thread(target=self._worker, args=(command,), daemon=True).start()

    def _worker(self, command):
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=45)
            detail = result.stderr.strip() or result.stdout.strip()
            if result.returncode == 0:
                message = "درخواست با موفقیت اجرا شد."
            else:
                message = "عملیات انجام نشد: " + (detail or "دسترسی لغو شد یا سرویس در دسترس نیست.")
        except Exception as exc:
            message = "خطا: " + str(exc)
        GLib.idle_add(self._finish, message)

    def _finish(self, message):
        self.status.set_text(message)
        self.start_btn.set_sensitive(True)
        self.stop_btn.set_sensitive(True)
        self.refresh()
        return False

    def refresh(self):
        def worker():
            try:
                p = subprocess.run(["systemctl", "is-active", SERVICE],
                    capture_output=True, text=True, timeout=8)
                state = p.stdout.strip() or "نامشخص"
            except Exception:
                state = "در دسترس نیست"
            GLib.idle_add(self.status.set_text, "وضعیت سرویس Tor: " + state)
        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = AryaConnect()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
