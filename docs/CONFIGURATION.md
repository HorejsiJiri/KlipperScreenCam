# Configuration

[English](CONFIGURATION.md) · [Česky](CONFIGURATION.cs.md)

The configuration is `~/printer_data/config/KlipperScreenCam.conf`. I keep it beside
my printer configuration so it is accessible in Mainsail. The [full example](../config/KlipperScreenCam.conf)
is the reference for defaults. Add settings to existing sections, not duplicate sections.
Restart KlipperScreenCam after editing these settings.

## Main

```ini
[main]
moonraker_url = http://127.0.0.1:7125
web_url = http://127.0.0.1
default_camera = Cam2
language = auto
theme = auto
klipperscreen_directory = ~/KlipperScreen
klipperscreen_config =
theme_poll_seconds = 2
```

`web_url` resolves relative camera URLs, normally through Mainsail's nginx server.
`default_camera` accepts an exact camera name or UID from:

```bash
python3 ~/KlipperScreenCam/launcher.py --list-cameras
```

The configured camera is selected on each service start. Switching cameras during
use does not save a new default. A missing, disabled or empty choice falls back to
the first enabled camera. The choice is independent of Mainsail. Do not use a
Crowsnest `device` path. `language` and `theme` follow KlipperScreen when set to `auto`;
otherwise use a locale filename without `.json` or a local theme directory name.
An empty `klipperscreen_config` discovers standard locations. Relative file paths
are resolved from the configuration directory. Existing theme/language changes
and edits to the selected translation are picked up automatically.

## Display

```ini
[display]
display = :0
xauthority = ~/.Xauthority
x = 1024
y = 0
width = 1024
height = 600
menu_min_width = 410
gear_size = 88
hide_cursor = true
hide_name_single_camera = true
hardware_acceleration = off
pause_on_dpms = true
dpms_poll_seconds = 20
```

Coordinates refer to the shared X11 desktop, not a monitor number. The app does not
change HDMI modes. With one enabled camera its name can be hidden; the menu remains
available for video off/on and FPS controls. Long camera lists scroll.

`hardware_acceleration` accepts `off`, `auto` or `on`; this controls WebKit rendering
policy and does not guarantee hardware MJPEG decoding. See [acceleration](ACCELERATION.md).
`pause_on_dpms` closes the local stream during X11 DPMS sleep. Checks run every
`dpms_poll_seconds` (1–120 seconds); the shared-wake integration sends an immediate
wake event. These options belong in `[display]`. Legacy entries in `[stream]` are
accepted with a warning, but the same option in both sections is an error.
See [sleep/wake](RPI_SLEEP.md).

## Stream

```ini
[stream]
max_fps = 15
start_paused = false
reconnect_initial_seconds = 2
reconnect_max_seconds = 30
request_timeout_seconds = 5
```

`max_fps` accepts an integer from 1 to 120 or `unlimited`. Menu changes last until
restart; configuration defines the startup limit. `start_paused = true` starts
without a local camera connection. Selecting a camera enables video.
Reconnect delays apply to reported failures; a silent connection stall may require
reselecting the camera. The local FPS limit drops compressed frames before WebKit,
while still reading the upstream stream. See [FPS controls](FPS.md).

```bash
python3 ~/KlipperScreenCam/launcher.py --check
sudo systemctl restart KlipperScreenCam
```
