# Display sleep and shared wake

[English](RPI_SLEEP.md) · [Česky](RPI_SLEEP.cs.md)

I verified shared wake and immediate camera resume on my Raspberry Pi 5 with
Debian 13 and X11, including operation after reboot.

## Behavior

KlipperScreen keeps control of the blanking timeout. When DPMS sleep is detected,
KlipperScreenCam closes its actual local camera connection, not just the image.
The default check interval is 20 seconds, so the stream may continue for up to
that interval after the displays turn off. Remote viewers remain independent.

Touching either display wakes both. The optional KlipperScreen integration dismisses
its black screensaver overlay and sends a nonblocking local FIFO notification.
The viewer resumes immediately on that message, without waiting for the periodic
DPMS check. Camera connection startup still takes its normal time. Manual video-off
state remains off; the selected camera and live FPS limit are preserved.

## Configuration

Add these to the existing `[display]` section:

```ini
[display]
pause_on_dpms = true
dpms_poll_seconds = 20
```

These are also the defaults when omitted. The interval accepts 1–120 seconds.
`pause_on_dpms = false` disables automatic pause. Move old copies out of `[stream]`;
keep `max_fps` and `start_paused` there. Do not define sleep options in both sections.
A software-only screensaver without DPMS is not tracked. The app does not change
DPMS enablement or the blanking timeout. If DPMS is unavailable, it logs the condition.

## Install the optional integration

Back up an existing installation using [the update guide](UPDATE.md). Then run:

```bash
cd ~/KlipperScreenCam
bash scripts/install.sh --no-deps --shared-wake
python3 launcher.py --check
```

The helper checks both files before writing, refuses an unrecognized source layout,
and creates timestamped `*.before-ksc-shared-wake-*` backups. It targets the
KlipperScreen source layout used on my printer, not every upstream version.
It updates `screen.py` to dismiss the black overlay when DPMS is on, and
`ks_includes/widgets/screensaver.py` to send a wake message after the overlay closes.
Already installed changes are not duplicated.

Only if installation and validation succeed, restart **both** services outside a print:

```bash
sudo systemctl restart KlipperScreen
sudo systemctl restart KlipperScreenCam
systemctl is-active KlipperScreen KlipperScreenCam
```

Restarting only the viewer is insufficient: KlipperScreen must load its new code.
Otherwise video can wait up to the DPMS check interval after a touch.
A KlipperScreen update can overwrite the patch; check/reapply it after such updates.
The helper does not restart KlipperScreen automatically.

Standalone check and application:

```bash
python3 scripts/shared_wake.py --directory ~/KlipperScreen
python3 scripts/shared_wake.py --directory ~/KlipperScreen --apply
```

Both applications must use the same account and `XDG_RUNTIME_DIR`. The FIFO is
normally `/run/user/UID/KlipperScreenCam/wake.fifo`, with permissions 0600 and a
0700 parent directory. Sending a message does not block if the viewer is stopped.

## Verify

1. Enable video, let both displays sleep, then wait another 25 seconds.
2. Check the log for `DPMS display sleep` and a closed local camera connection.
3. Touch either screen. Both should wake and video should resume without a 20-second wait.
4. Check for `Wake notification received from local FIFO` followed by `DPMS display wake`.
5. Repeat using the other screen. Test manual video off across sleep/wake.
6. Check that Mainsail continues receiving video. Reboot and repeat.

```bash
journalctl -u KlipperScreenCam --since "5 minutes ago" --no-pager |
  grep -E 'DPMS|Wake notification|Local camera connection'
```

If video only resumes on the interval, first ensure both services were restarted.
With the viewer running, this tests notification reception but does not wake the monitors:

```bash
printf 'wake
' > /run/user/$(id -u)/KlipperScreenCam/wake.fifo
```

Use normal touch wake for the final check. A manual message while monitors remain
asleep can start video briefly; the next DPMS check stops it again.

## Roll back

Stop KlipperScreenCam and restore the project/configuration from their backups.
To undo the optional KlipperScreen patch, restore only the two corresponding
source files from the helper's timestamped backups, then restart KlipperScreen.
Setting `pause_on_dpms = false` disables automatic stream pause without restoring files.
