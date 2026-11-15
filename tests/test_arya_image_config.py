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

    def test_gaming_mode_is_staged(self):
        app = (ROOT / "apps/arya-gaming/arya_gaming.py").read_text()
        self.assertIn("gamemoderun", app)
        self.assertIn("Arya Gaming", (ROOT / "apps/arya-gaming/arya-gaming.desktop").read_text())


if __name__ == "__main__":
    unittest.main()
