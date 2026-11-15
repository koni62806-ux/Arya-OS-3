#!/usr/bin/env python3
"""Arya Tool: lightweight GTK assistant shell for Arya OS.

Cloud mode uses an OpenAI-compatible chat endpoint. Local mode can target
an OpenAI-compatible local server (for example Ollama). API keys are read
from ARYA_AI_API_KEY and are never written to the config file.
"""
import base64
import json
import mimetypes
import os
import re
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib

APP_NAME = "Arya Tool"
CONFIG_DIR = Path.home() / ".config" / "arya-tool"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULTS = {
    "mode": "cloud",
    "cloud_url": "https://api.openai.com/v1",
    "cloud_model": "gpt-4o-mini",
    "local_url": "http://127.0.0.1:11434/v1",
    "local_model": "llama3.2:3b",
}
SYSTEM_PROMPT = (
    "You are Arya Tool, the helpful assistant built into Arya OS. "
    "Be concise, friendly, and explain Linux steps simply. "
    "Never claim you changed the computer unless an approved action actually ran. "
    "If a desktop action is needed, suggest exactly one safe command token on its own line "
    "using [[open_app:APP]]. Allowed apps: firefox, files, terminal, settings. "
    "The user must approve every action before execution."
)
ALLOWED_APPS = {
    "firefox": ["firefox-esr"],
    "files": ["thunar"],
    "terminal": ["xfce4-terminal"],
    "settings": ["xfce4-settings-manager"],
}


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULTS, **data}
    except (OSError, ValueError):
        return DEFAULTS.copy()


def save_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    CONFIG_FILE.chmod(0o600)


class AryaTool(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.aryaos.Tool")
        self.config = load_config()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.attachment = None

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self, title="Arya Tool")
        self.window.set_default_size(760, 680)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_border_width(0)
        self.build_ui()
        self.window.show_all()

    def build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.get_style_context().add_class("arya-root")
        self.window.add(root)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header.set_border_width(16)
        header.get_style_context().add_class("arya-header")
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title = Gtk.Label()
        title.set_markup('<span size="large" weight="bold">✦ Arya Tool</span>')
        title.set_xalign(0)
        subtitle = Gtk.Label(label="دستیار هوشمند سیستم‌عامل Arya")
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class("muted")
        title_box.pack_start(title, False, False, 0)
        title_box.pack_start(subtitle, False, False, 0)
        header.pack_start(title_box, True, True, 0)
        settings_btn = Gtk.Button(label="تنظیمات")
        settings_btn.connect("clicked", self.open_settings)
        header.pack_end(settings_btn, False, False, 0)
        root.pack_start(header, False, False, 0)

        self.mode_label = Gtk.Label()
        self.update_mode_label()
        self.mode_label.set_xalign(0)
        self.mode_label.set_margin_start(18)
        self.mode_label.set_margin_top(8)
        root.pack_start(self.mode_label, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.chat = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.chat.set_border_width(18)
        scroller.add(self.chat)
        root.pack_start(scroller, True, True, 0)
        self.add_message("assistant", "سلام! من Arya Tool هستم. می‌تونم در فهم خطاها، پیدا کردن فایل‌ها و کار با Arya OS کمکت کنم. برای اتصال مدل آنلاین، تنظیمات را باز کن.")

        self.attachment_label = Gtk.Label(label="")
        self.attachment_label.set_xalign(0)
        self.attachment_label.set_margin_start(16)
        root.pack_start(self.attachment_label, False, False, 4)

        composer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        composer.set_border_width(14)
        composer.get_style_context().add_class("arya-composer")
        attach = Gtk.Button(label="＋ فایل")
        attach.connect("clicked", self.choose_file)
        composer.pack_start(attach, False, False, 0)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("پیامت را برای Arya بنویس...")
        self.entry.connect("activate", self.send_message)
        composer.pack_start(self.entry, True, True, 0)
        self.send_btn = Gtk.Button(label="ارسال")
        self.send_btn.get_style_context().add_class("suggested-action")
        self.send_btn.connect("clicked", self.send_message)
        composer.pack_end(self.send_btn, False, False, 0)
        root.pack_end(composer, False, False, 0)

    def update_mode_label(self):
        mode = self.config.get("mode", "cloud")
        label = {"cloud": "آنلاین", "local": "محلی", "hybrid": "ترکیبی"}.get(mode, "آنلاین")
        self.mode_label.set_text("● حالت " + label + "  |  کنترل دستگاه فقط با تأیید شما")

    def add_message(self, role, text):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        card.set_border_width(12)
        card.get_style_context().add_class("arya-message")
        who = Gtk.Label()
        who.set_markup("<b>{}</b>".format("شما" if role == "user" else "Arya"))
        who.set_xalign(0)
        body = Gtk.Label(label=text)
        body.set_xalign(0)
        body.set_line_wrap(True)
        body.set_line_wrap_mode(2)
        body.set_selectable(True)
        body.set_max_width_chars(82)
        card.pack_start(who, False, False, 0)
        card.pack_start(body, False, False, 0)
        self.chat.pack_start(card, False, False, 0)
        self.chat.show_all()
        GLib.idle_add(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        adj = self.chat.get_parent().get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

    def choose_file(self, *_):
        dialog = Gtk.FileChooserDialog(title="انتخاب فایل برای Arya", parent=self.window,
            action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("لغو", Gtk.ResponseType.CANCEL, "انتخاب", Gtk.ResponseType.ACCEPT)
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            self.attachment = Path(dialog.get_filename())
            self.attachment_label.set_text("پیوست: " + self.attachment.name)
        dialog.destroy()

    def send_message(self, *_):
        text = self.entry.get_text().strip()
        if not text and not self.attachment:
            return
        self.entry.set_text("")
        self.add_message("user", text or "لطفاً این فایل را بررسی کن: " + self.attachment.name)
        content = text
        if self.attachment:
            path = self.attachment
            mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            if mime.startswith("image/"):
                raw = base64.b64encode(path.read_bytes()).decode("ascii")
                content = [{"type": "text", "text": text or "این تصویر را بررسی کن."},
                           {"type": "image_url", "image_url": {"url": "data:{};base64,{}".format(mime, raw)}}]
            elif mime.startswith("text/") or path.suffix.lower() in (".log", ".py", ".sh", ".md", ".txt", ".yml", ".yaml", ".json"):
                try:
                    excerpt = path.read_text(encoding="utf-8", errors="replace")[:16000]
                    content = (text + "\n\nمحتوای فایل " + path.name + ":\n" + excerpt).strip()
                except OSError as exc:
                    content = text + "\nخواندن فایل ناموفق بود: " + str(exc)
            else:
                content = (text + "\nفایل پیوست شده: " + path.name +
                           " (این نوع فایل در نسخهٔ اولیه قابل تحلیل مستقیم نیست.)").strip()
            self.attachment = None
            self.attachment_label.set_text("")
        self.messages.append({"role": "user", "content": content})
        self.send_btn.set_sensitive(False)
        self.add_message("assistant", "دارم بررسی می‌کنم…")
        threading.Thread(target=self.ask_model, daemon=True).start()

    def ask_model(self):
        try:
            mode = self.config.get("mode", "cloud")
            if mode == "local":
                answer = self.request_endpoint("local")
            elif mode == "hybrid":
                try:
                    answer = self.request_endpoint("local")
                except Exception:
                    answer = self.request_endpoint("cloud")
            else:
                answer = self.request_endpoint("cloud")
            self.messages.append({"role": "assistant", "content": answer})
            GLib.idle_add(self.finish_answer, answer)
        except Exception as exc:
            GLib.idle_add(self.finish_answer, "اتصال به مدل برقرار نشد: {}\n\nبرای حالت آنلاین، آدرس مدل و کلید API را بررسی کن. در حالت محلی نیز باید سرویس سازگار با OpenAI روی دستگاه اجرا باشد.".format(exc))

    def request_endpoint(self, which):
        url = self.config.get(which + "_url", DEFAULTS[which + "_url"]).rstrip("/")
        model = self.config.get(which + "_model", DEFAULTS[which + "_model"])
        key = os.environ.get("ARYA_AI_API_KEY", "") if which == "cloud" else ""
        payload = {"model": model, "messages": self.messages, "temperature": 0.4}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url + "/chat/completions", data=data,
            headers={"Content-Type": "application/json", **({"Authorization": "Bearer " + key} if key else {})})
        with urllib.request.urlopen(req, timeout=75) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

    def finish_answer(self, answer):
        self.send_btn.set_sensitive(True)
        self.add_message("assistant", answer)
        self.check_action(answer)
        return False

    def check_action(self, answer):
        match = re.search(r"\[\[open_app:(firefox|files|terminal|settings)\]\]", answer)
        if not match:
            return
        app = match.group(1)
        dialog = Gtk.MessageDialog(parent=self.window, flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
            text="اجازهٔ اجرای عملیات؟")
        dialog.format_secondary_text("Arya می‌خواهد برنامهٔ «{}» را باز کند. این کار فقط پس از تأیید تو انجام می‌شود.".format(app))
        dialog.add_buttons("لغو", Gtk.ResponseType.CANCEL, "اجازه می‌دهم", Gtk.ResponseType.ACCEPT)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.ACCEPT:
            try:
                subprocess.Popen(ALLOWED_APPS[app], close_fds=True)
                self.add_message("assistant", "درخواست تأیید شد و برنامهٔ {} اجرا شد.".format(app))
            except OSError as exc:
                self.add_message("assistant", "اجرای برنامه ناموفق بود: " + str(exc))

    def open_settings(self, *_):
        dialog = Gtk.Dialog(title="تنظیمات Arya Tool", transient_for=self.window, flags=0)
        dialog.add_buttons("انصراف", Gtk.ResponseType.CANCEL, "ذخیره", Gtk.ResponseType.OK)
        dialog.set_default_size(520, 360)
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_border_width(16)
        mode = Gtk.ComboBoxText()
        for value, label in (("cloud", "آنلاین"), ("local", "محلی"), ("hybrid", "ترکیبی")):
            mode.append(value, label)
        mode.set_active_id(self.config.get("mode", "cloud"))
        cloud_url = self.add_setting(box, "آدرس API آنلاین", "cloud_url")
        cloud_model = self.add_setting(box, "مدل آنلاین", "cloud_model")
        local_url = self.add_setting(box, "آدرس API محلی", "local_url")
        local_model = self.add_setting(box, "مدل محلی", "local_model")
        mode_label = Gtk.Label(label="روش اتصال هوش مصنوعی")
        mode_label.set_xalign(0)
        box.pack_start(mode_label, False, False, 0)
        box.pack_start(mode, False, False, 0)
        hint = Gtk.Label(label="کلید آنلاین از متغیر محیطی ARYA_AI_API_KEY خوانده می‌شود و در فایل تنظیمات ذخیره نمی‌شود.")
        hint.set_line_wrap(True)
        hint.set_xalign(0)
        hint.get_style_context().add_class("muted")
        box.pack_start(hint, False, False, 0)
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            self.config.update({"mode": mode.get_active_id(), "cloud_url": cloud_url.get_text().strip(),
                "cloud_model": cloud_model.get_text().strip(), "local_url": local_url.get_text().strip(),
                "local_model": local_model.get_text().strip()})
            save_config(self.config)
            self.update_mode_label()
        dialog.destroy()

    def add_setting(self, box, label, key):
        lbl = Gtk.Label(label=label)
        lbl.set_xalign(0)
        entry = Gtk.Entry()
        entry.set_text(self.config.get(key, DEFAULTS[key]))
        box.pack_start(lbl, False, False, 0)
        box.pack_start(entry, False, False, 0)
        return entry


def main():
    css = b"""
    .arya-root { background: #f1efff; color: #20233b; }
    .arya-header { background: #dcd8f5; border-bottom: 1px solid #c5c0e8; }
    .arya-composer { background: #e3e0f7; border-top: 1px solid #c5c0e8; }
    .arya-message { background: #ffffff; border: 1px solid #dedaf2; border-radius: 14px; }
    .muted { color: #77758f; }
    button { border-radius: 10px; padding: 7px 12px; }
    entry { border-radius: 12px; padding: 9px; }
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(GdkPixbuf, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION) if False else None
    from gi.repository import Gdk
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    AryaTool().run(None)


if __name__ == "__main__":
    main()
