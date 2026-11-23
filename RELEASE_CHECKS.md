# Release checklist — 0.3.0

I keep this checklist for maintaining releases. Installation and configuration are
covered in README.md and the deployment guides; test counts do not belong in the
main user guide.

## Checks I use before release

- Validate configuration, all 32 locale files and Python syntax.
- Run core and real MJPEG transport tests.
- Run browser checks for touch controls, menu layout, languages and FPS selection.
- Verify the generated systemd unit on Linux.
- Build source archives and SHA-256 checksums without live printer configuration or logs.

```bash
python3 -m unittest discover -s tests -v
python3 launcher.py --check-locales
python3 launcher.py --config config/KlipperScreenCam.conf --check
python3 scripts/package.py
```

The [Checks run for the released commit](https://github.com/HorejsiJiri/KlipperScreenCam/actions/runs/45075895035)
and the [publish run](https://github.com/HorejsiJiri/KlipperScreenCam/actions/runs/45075950633)
completed successfully. I published [v0.3.0](https://github.com/HorejsiJiri/KlipperScreenCam/releases/tag/v0.3.0)
with ZIP, TAR.GZ and SHA-256 files.

## Practical checks

I test on my Raspberry Pi 5 printer with two HDMI touch displays. My practical
observations and remaining device-specific checks are in [the validation notes](docs/VERIFICATION.md).
Automated checks support this work; they do not establish compatibility with every
camera, display, theme or graphics driver.

New translations still need native-speaker review. I have not independently
measured hardware MJPEG decoding. The public release does not implement synchronized
display wake-up or automatic stream pause when a monitor powers down.

## RPi sleep/wake verification — 2026-11-23

I verified shared display wake, immediate local stream resume and operation after
reboot on my Raspberry Pi 5. DPMS sleep monitoring closes the local connection;
manual pause is preserved by the implementation. The FIFO path was checked through
application logs. Both services must restart after installing the integration.
Linux-specific library and FIFO behavior also require the actual target environment;
Windows checks alone do not establish these results.
