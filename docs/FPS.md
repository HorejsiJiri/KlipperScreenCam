# Local FPS limit and counters

[English](FPS.md) · [Česky](FPS.cs.md)

I found both 15 FPS and 10 FPS smooth on my printer. The default is 15:

```ini
[stream]
max_fps = 15
```

Use an integer from 1 to 120, or `unlimited`. Restart the service after editing
configuration. The menu offers 10, 20, 30 and Unlimited, plus the configured numeric
limit if different. For example, 15 produces 10 / 15 / 20 on the first row and
30 / Unlimited on the second; 20 produces no duplicate preset. Numeric buttons have
equal widths and Unlimited fills the remaining space.

Menu changes apply to the current connection without reconnecting or resuming
manually paused video. They are temporary; service restart restores `max_fps`.
The menu order is cameras, video off/on, frame-limit heading, measured FPS and presets.

## What is limited

The local relay reads complete compressed JPEG frames and forwards only those due
at the selected rate. Skipped frames never reach WebKit, reducing its decode/render
work. There is no JPEG decode or re-encode in the relay and no intentional frame queue.
The original upstream stream is still read at its source rate. This does not reduce
Crowsnest capture FPS or change Mainsail and other viewers.

## What the counters mean

Source FPS counts complete frames read by the relay; forwarded FPS counts frames
sent toward WebKit. These are measured averages, displayed as whole numbers rounded
to the nearest integer. They are not measurements of successfully rendered frames.
Counters are collected while streaming, including when the menu is closed.
An unlimited setting cannot exceed the source's available rate. Short samples can
vary; compare sustained behavior using the same camera and scene.

Actual video off and DPMS sleep pause close the local connection, rather than just
setting its FPS to zero. See [sleep/wake](RPI_SLEEP.md).
