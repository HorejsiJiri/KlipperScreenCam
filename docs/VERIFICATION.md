# Verification and scope

[English](VERIFICATION.md) · [Česky](VERIFICATION.cs.md)

I use a Raspberry Pi 5, Debian 13, X11, KlipperScreen and two 1024 × 600 HDMI touch
displays. On this setup I verified video, touch controls, automatic startup,
manual connection shutdown and smooth video at 15 and 10 FPS. Local connection
logs and socket checks established actual transport closure rather than image hiding.

I also verified shared display wake, immediate camera resume and operation after
reboot with the optional KlipperScreen integration. Both services must load the
patched code. The default 20-second check detects sleep; a FIFO message handles wake.

Short CPU samples are observations, not controlled benchmarks. Source/forwarded
counters measure complete MJPEG frames and are not rendered-frame counters.
Automated transport and browser checks cover additional behavior, but do not prove
every combination on every target. Native review of the 30 AI-assisted translations
and broader theme, RTL/CJK, driver and camera testing remain open.

See [the test checklist](TESTING.md), [sleep/wake](RPI_SLEEP.md) and
[release checks](../RELEASE_CHECKS.md) for the corresponding evidence and limits.
