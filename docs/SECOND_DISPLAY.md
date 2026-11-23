# Two HDMI touch displays: step by step

[English](SECOND_DISPLAY.md) · [Česky](SECOND_DISPLAY.cs.md)

This guide follows my Raspberry Pi 5, Debian 13 (Trixie), X11 and two 1024 × 600
HDMI touch displays. KlipperScreen controls the first; KlipperScreenCam fills the
second. Adapt output names, device names and paths to your own machine.
The viewer does not configure HDMI modes or touch mappings itself.

## 1. Connect and identify

Connect each display to a separate HDMI output and each USB touch cable to the RPi.
HDMI carries video, not USB touch. Keep SSH available. Run as the regular user in
KlipperScreen's `User=` service setting. First check the actual system:

```bash
tr -d '\0' < /proc/device-tree/model
echo
cat /etc/os-release
systemctl cat KlipperScreen
ps -eo user,pid,args | grep -E 'Xorg|Xwayland|wayfire|labwc|screen.py' | grep -v grep
```

My setup uses Xorg `:0` and `BACKEND=X`. This is not a Wayland or DSI/GPIO guide.
Do not change the graphics overlay or boot configuration blindly.

## 2. Inspect output names and modes

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --query
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --listmonitors
```

Install missing utilities if needed:

```bash
sudo apt install --no-install-recommends x11-xserver-utils xinput
```

My outputs are `HDMI-1` and `HDMI-2`. DRM names such as `HDMI-A-1` need not match
xrandr names. Both outputs at `+0+0` means overlapping views, not necessarily two
KlipperScreen processes. For `Can't open display`, check user, DISPLAY and XAUTHORITY;
do not use `xhost +` as a workaround.

## 3. Extend the desktop temporarily

My first display advertised 1024x600; the other originally advertised 1024x576.
I assigned the already existing 1024x600 mode to the second output:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --addmode HDMI-2 1024x600
```

Skip this if both outputs already offer that mode. If the mode does not exist or
assignment fails, check display specifications, EDID and cabling rather than forcing
arbitrary timings. Then place the first screen on the left and the second on the right:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr \
  --output HDMI-1 --primary --mode 1024x600 --pos 0x0 \
  --output HDMI-2 --mode 1024x600 --pos 1024x0
```

Expected geometry:

```text
Screen 0: ... current 2048 x 600 ...
HDMI-1 connected primary 1024x600+0+0
HDMI-2 connected 1024x600+1024+0
```

KlipperScreen stays on the first screen; the second may be blank for now.
For another resolution, the second screen's x position is the first screen's width.
If you swap HDMI cables, identify the outputs again. If my second screen loses
video, its previously working temporary fallback is:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr \
  --output HDMI-2 --mode 1024x576 --pos 1024x0
```

## 4. Identify and map each touchscreen

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput list
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput test 6
```

Replace 6 with a current device ID. Touch each screen and note which produces events;
Ctrl+C stops the test. Repeat for the other device. IDs can change after reboot,
so persist names rather than numeric IDs. My verified mapping is:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput map-to-output \
  "WaveShare WS170120" HDMI-1
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput map-to-output \
  "深圳市全动电子技术有限公司 ByQDtech 触控USB鼠标" HDMI-2
```

These names are hardware examples. Use your own identified names. Identical names
require another way to distinguish the devices before mapping. Check all screen
edges; touching the second screen must not operate KlipperScreen. Complete the second
touch test in the camera menu once the viewer is running.

## 5. Persist layout inside the X11 session

If an existing `start-displays.sh` already works, preserve it and follow
[migration](MIGRATION.md). Do not install a competing startup wrapper.
For a new setup:

```bash
mkdir -p ~/.config/KlipperScreenCam
nano ~/.config/KlipperScreenCam/start-klipperscreen.sh
```

Insert the following, adapting the touch names and verifying the original Python
and screen.py paths from `systemctl cat KlipperScreen`. Preserve any original extra
arguments such as a custom configuration path.

```bash
#!/bin/bash
xrandr --addmode HDMI-2 1024x600 2>/dev/null || true
if xrandr \
    --output HDMI-1 --primary --mode 1024x600 --pos 0x0 \
    --output HDMI-2 --mode 1024x600 --pos 1024x0
then
    xinput map-to-output "WaveShare WS170120" HDMI-1
    xinput map-to-output \
        "深圳市全动电子技术有限公司 ByQDtech 触控USB鼠标" HDMI-2
else
    echo "HDMI layout failed; starting KlipperScreen with the current layout." >&2
fi
exec "$HOME/.KlipperScreen-env/bin/python" \
    "$HOME/KlipperScreen/screen.py" --monitor 0
```

```bash
chmod +x ~/.config/KlipperScreenCam/start-klipperscreen.sh
bash -n ~/.config/KlipperScreenCam/start-klipperscreen.sh
cat ~/KlipperScreen/scripts/KlipperScreen-start.sh
```

The wrapper must run inside the existing X session. My KlipperScreen startup uses
`xinit $KS_XCLIENT`. Inspect any custom `scripts/launch_KlipperScreen.sh` too;
it may override the normal path. If startup differs, adapt the method first.
Create a dedicated drop-in, leaving the original service unchanged:

```bash
sudo mkdir -p /etc/systemd/system/KlipperScreen.service.d
sudo systemctl cat KlipperScreen
sudo nano /etc/systemd/system/KlipperScreen.service.d/90-klipperscreencam-displays.conf
```

Use an absolute path with your actual username; this example is mine:

```ini
[Service]
Environment="KS_XCLIENT=/home/horejsi/.config/KlipperScreenCam/start-klipperscreen.sh"
```

Do not use `~` or `$HOME` in that service setting. Back up and reconcile any existing
KS_XCLIENT override instead of combining competing launchers. Outside a print:

```bash
sudo systemctl daemon-reload
sudo systemctl restart KlipperScreen
systemctl is-active KlipperScreen
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --query
```

To undo only this new drop-in:

```bash
sudo mv /etc/systemd/system/KlipperScreen.service.d/90-klipperscreencam-displays.conf \
  /etc/systemd/system/KlipperScreen.service.d/90-klipperscreencam-displays.conf.disabled
sudo systemctl daemon-reload
sudo systemctl restart KlipperScreen
```

## 6. Install the camera display

Follow [deployment](DEPLOY.md). My geometry in the existing configuration section is:

```ini
[display]
display = :0
xauthority = ~/.Xauthority
x = 1024
y = 0
width = 1024
height = 600
```

The camera service waits for X11 after KlipperScreen starts. The wrapper configures
HDMI before the camera window opens. Check both services after restarting KlipperScreen.

## 7. Reboot and check sleep/wake

Reboot outside a print, then check both displays and touch inputs:

```bash
systemctl is-active KlipperScreen KlipperScreenCam
systemctl is-enabled KlipperScreenCam
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --query
```

For shared touch wake and automatic local stream shutdown during sleep, follow
[the sleep/wake guide](RPI_SLEEP.md). I verified this integration after reboot on
my RPi. A KlipperScreen update may overwrite its optional source patch.
