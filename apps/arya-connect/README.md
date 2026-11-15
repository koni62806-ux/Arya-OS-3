# Arya Connect

GTK3 front-end for explicitly starting and stopping the Tor client service.
Actions require a desktop authorization prompt via pkexec. The app does not
claim to provide a system-wide VPN. Tor/Snowflake can help under some forms
of censorship but cannot guarantee connectivity when international routes
are completely unavailable. Hardware and network behavior still require
testing on the target device.


The "Open browser through Tor" action launches Firefox ESR with a dedicated
profile configured for the local SOCKS5 listener at 127.0.0.1:9050, remote DNS
through SOCKS, DNS-over-HTTPS disabled, and WebRTC disabled in that profile.
It only launches after the Tor service reports active. This is browser-scoped,
not a system-wide VPN; service-active does not prove Tor has completed bootstrap
or that the external network is reachable.
