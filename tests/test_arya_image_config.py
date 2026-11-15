from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AryaImageConfigurationTests(unittest.TestCase):
    def test_tor_snowflake_client_is_configured(self):
        torrc = (ROOT / "config/includes.chroot/etc/tor/torrc").read_text()
        self.assertIn("SocksPort 127.0.0.1:9050", torrc)
        self.assertIn("UseBridges 1", torrc)
        self.assertIn("ClientTransportPlugin snowflake exec /usr/bin/snowflake-client", torrc)
        self.assertIn("Bridge snowflake ", torrc)

    def test_tor_packages_are_declared(self):
        packages = set((ROOT / "config/package-lists/arya.list.chroot").read_text().split())
        for package in ("tor", "snowflake-client", "pkexec", "lxpolkit"):
            self.assertIn(package, packages)

    def test_policykit_agent_autostarts_in_xfce(self):
        desktop = (ROOT / "config/includes.chroot/etc/xdg/autostart/lxpolkit.desktop").read_text()
        self.assertIn("Exec=lxpolkit", desktop)
        self.assertIn("OnlyShowIn=XFCE;", desktop)

    def test_dock_and_edge_assistant_are_enabled(self):
        packages = set((ROOT / "config/package-lists/arya.list.chroot").read_text().split())
        self.assertIn("plank", packages)
        self.assertIn("gamemode", packages)
        plank = (ROOT / "config/includes.chroot/etc/xdg/autostart/plank.desktop").read_text()
        assistant = (ROOT / "config/includes.chroot/etc/xdg/autostart/arya-tool-launcher.desktop").read_text()
        self.assertIn("Exec=plank", plank)
        self.assertIn("Exec=arya-tool-launcher", assistant)

    def test_gaming_mode_supports_arguments(self):
        app = (ROOT / "apps/arya-gaming/arya_gaming.py").read_text()
        self.assertIn("gamemoderun", app)
        self.assertIn("shlex.split", app)
        self.assertIn('"--"] + command', app)
        self.assertLess(app.index("command = shlex.split(value)"), app.index("executable = command[0]"))
        self.assertIn("os.access(executable, os.X_OK)", app)
        self.assertIn("Arya Gaming", (ROOT / "apps/arya-gaming/arya-gaming.desktop").read_text())

    def test_arya_tool_edge_launcher_opens_half_screen_panel(self):
        app = (ROOT / "apps/arya-tool/arya_tool.py").read_text()
        launcher = (ROOT / "apps/arya-tool/arya_tool_launcher.py").read_text()
        self.assertIn("ARYA_TOOL_PANEL", app)
        self.assertIn("self.panel_width", app)
        self.assertIn('env["ARYA_TOOL_PANEL"] = "1"', launcher)

    def test_arya_tool_can_capture_and_attach_desktop_screenshot(self):
        app = (ROOT / "apps/arya-tool/arya_tool.py").read_text()
        self.assertIn('label="📸 اسکرین‌شات"', app)
        self.assertIn("Gdk.get_default_root_window()", app)
        self.assertIn("Gdk.pixbuf_get_from_window", app)
        self.assertIn("self.attachment = Path(filename)", app)


    def test_arya_center_discovers_and_filters_installed_apps(self):
        app = (ROOT / "apps/arya-center/arya_center.py").read_text()
        self.assertIn("Gio.AppInfo.get_all()", app)
        self.assertIn("info.should_show()", app)
        self.assertIn("Gtk.SearchEntry()", app)
        self.assertIn("self.apps_flow.invalidate_filter()", app)
        self.assertIn("info.launch([], None)", app)

    def test_arya_center_searches_app_names_and_descriptions(self):
        app = (ROOT / "apps/arya-center/arya_center.py").read_text()
        self.assertIn("info.get_description()", app)
        self.assertIn("info.get_executable()", app)
        self.assertIn("child.search_text = searchable", app)
        self.assertIn('query in getattr(child, "search_text", "")', app)
        self.assertIn("Pango.EllipsizeMode.END", app)

    def test_arya_center_quick_launch_checks_executable(self):
        app = (ROOT / "apps/arya-center/arya_center.py").read_text()
        self.assertIn("shutil.which(command)", app)
        self.assertIn("subprocess.Popen([executable]", app)
        self.assertNotIn('subprocess.Popen([command]', app)

    def test_arya_tool_uses_safe_network_and_conversation_handling(self):
        app = (ROOT / "apps/arya-tool/arya_tool.py").read_text()
        self.assertIn("urlsplit(url)", app)
        self.assertIn('parsed.scheme != "https"', app)
        self.assertIn("self.request_in_progress", app)
        self.assertIn("self.messages[-20:]", app)
        self.assertIn("Pango.WrapMode.WORD_CHAR", app)
        self.assertIn("temporary.replace(CONFIG_FILE)", app)

    def test_diagnostics_include_network_and_driver_visibility(self):
        app = (ROOT / "apps/arya-diagnostics/arya_diagnostics.py").read_text()
        self.assertIn('["lspci", "-nnk"]', app)
        self.assertIn('["rfkill", "list"]', app)
        self.assertIn('["nmcli", "general", "status"]', app)
        self.assertIn('["lsmod"]', app)

    def test_arya_center_search_supports_multiple_terms_and_categories(self):
        app = (ROOT / "apps/arya-center/arya_center.py").read_text()
        self.assertIn("info.get_categories()", app)
        self.assertIn("terms = self.search.get_text().casefold().split()", app)
        self.assertIn("return all(term in searchable for term in terms)", app)

    def test_tor_browser_uses_isolated_firefox_profile(self):
        app = (ROOT / "apps/arya-connect/arya_connect.py").read_text()
        self.assertIn("firefox-tor-profile", app)
        self.assertIn("network.proxy.socks_remote_dns", app)
        self.assertIn("media.peerconnection.enabled", app)
        self.assertIn("firefox-esr", app)


if __name__ == "__main__":
    unittest.main()
