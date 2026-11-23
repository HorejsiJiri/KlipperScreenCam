# Migrate from the earlier camera viewer

[English](MIGRATION.md) · [Česky](MIGRATION.cs.md)

My original `~/.config/KlipperScreen/start-displays.sh` launched both KlipperScreen
and `camera-viewer.py`, while configuring HDMI modes and touch mappings.
Keep the display commands. Only remove the old camera autostart.

1. Install the new project without `--enable`, configure it and run `--check`.
2. Back up the old wrapper and service configuration:

```bash
cp -p ~/.config/KlipperScreen/start-displays.sh   ~/.config/KlipperScreen/start-displays.sh.before-KlipperScreenCam
systemctl cat KlipperScreen > ~/KlipperScreen.service.before-KlipperScreenCam.txt
nano ~/.config/KlipperScreen/start-displays.sh
```

3. Remove only the old `camera-viewer.py` launch, `CAMERA_VIEWER_PID` assignment and
its corresponding `trap`. Preserve `xrandr`, `xinput` and the real `screen.py` launch.
If your script differs, compare it before editing; do not replace it blindly.

```bash
bash -n ~/.config/KlipperScreen/start-displays.sh
sudo systemctl restart KlipperScreen
sudo systemctl start KlipperScreenCam
journalctl -u KlipperScreenCam -n 80 --no-pager
```

4. Check displays, touch and camera controls, then enable startup:

```bash
sudo systemctl enable KlipperScreenCam
```

Old `camera-display.json` and `camera-choice.json` files are not imported. Put the
fixed startup camera's exact name or UID in the new configuration. Keep the old
viewer files until migration is verified. Crowsnest and Mainsail need no changes.

## Rollback

```bash
sudo systemctl disable --now KlipperScreenCam
cp -p ~/.config/KlipperScreen/start-displays.sh.before-KlipperScreenCam   ~/.config/KlipperScreen/start-displays.sh
sudo systemctl restart KlipperScreen
```
