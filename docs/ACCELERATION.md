# Optional WebKit hardware acceleration

[English](ACCELERATION.md) · [Česky](ACCELERATION.cs.md)

```ini
[display]
hardware_acceleration = off
```

Accepted policies are `off` (compatible default), `auto` (on demand) and `on`
(always request acceleration). Restart KlipperScreenCam after changing the setting:

```bash
python3 ~/KlipperScreenCam/launcher.py --check
sudo systemctl restart KlipperScreenCam
```

The policy requests accelerated WebKit rendering; the driver and WebKit build
determine what is actually available. It does not guarantee hardware MJPEG decoding.
Compare the same camera, resolution, FPS limit and scene before drawing conclusions
from CPU samples. In normal top output a process percentage refers to one CPU core,
while the summary describes the whole machine. Return to `off` if graphics become unstable.

A [local FPS limit](FPS.md) reduces frames sent to WebKit. [Sleep pause](RPI_SLEEP.md)
and video off close the local stream entirely. Neither stops remote viewers.
