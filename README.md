# BurpSuite Tool

A terminal-based HTTP interception and analysis tool, inspired by Burp Suite. It supports proxy mode, packet capture, and request manipulation, and works on both rooted and non-rooted devices.

## Main Menu

![BurpSuite main menu](Screenshot_20261109_191005.jpg)

## Features

| Mode | Description |
|------|-------------|
| [1] Automated Scanner | Direct URL scan with security analysis |
| [2] Packet Sniffer | Network traffic capture (requires root) |
| [3] View Captured | View intercepted requests |
| [4] Repeater | Manual request testing |
| [5] Intruder | Automated fuzzing attack |
| [6] Export Data | Save all captured requests |
| [7] Exit | Close BurpSuite |

## Additional Screenshot

![Screenshot](Screenshot_20261109_191918.jpg)

## Requirements

- Python 3
- Root access for the Packet Sniffer mode (other modes work without root)

## Usage

```bash
python3 burpsuite_tool.py
```

Then select a mode by entering its number at the `[SELECT] >>` prompt.

## Disclaimer

This tool is intended for educational purposes and for testing systems you own or have explicit written permission to test. Unauthorized interception or scanning of traffic or systems is illegal. The author is not responsible for misuse.
