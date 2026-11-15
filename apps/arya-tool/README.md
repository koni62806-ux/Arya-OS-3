# Arya Tool (foundation)

Arya Tool is the first native GTK3 assistant application for Arya OS.

## Current implementation
- Persian-first GTK desktop interface with a chat view and attachment picker.
- OpenAI-compatible cloud endpoint support.
- OpenAI-compatible local endpoint support (for example, a local Ollama server exposing its OpenAI-compatible API).
- Hybrid mode: tries the local endpoint first and falls back to the cloud endpoint.
- Image attachments are sent as data URLs to vision-capable endpoints; text and common source/log files are included as text.
- Cloud API key is read from `ARYA_AI_API_KEY`; it is never written to the JSON settings file.
- A deliberately small, explicit approval gate can launch only Firefox, Thunar, XFCE Terminal, or XFCE Settings when the assistant emits the documented action token.

## Configuration
Open Settings in Arya Tool to choose `cloud`, `local`, or `hybrid`, and configure endpoint URLs and model names.

For cloud mode, set `ARYA_AI_API_KEY` in the user's session environment before launching Arya Tool. Do not put secrets in the ISO, repository, or config file.

Local mode requires a compatible local inference service to be installed and running. The 4 GB RAM Pentium/GMA X3100 target is not suitable for large local models; local inference is optional and may be very slow or unavailable. Hybrid mode tries local first and then cloud.

## Safety and limitations
- Device actions are restricted to an explicit allowlist and always show a confirmation dialog.
- This initial version does not execute arbitrary shell commands, install packages, delete files, alter partitions, or control arbitrary windows.
- Non-text documents and arbitrary binary files are not parsed in this initial version.
- Voice input/output is intentionally not included.
- A successful ISO build proves packaging, not real model connectivity or hardware performance. Those require separate tests.
