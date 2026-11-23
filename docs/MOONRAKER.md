# Service control through Moonraker

[English](MOONRAKER.md) · [Česky](MOONRAKER.cs.md)

The installer adds `KlipperScreenCam` to the matching `moonraker.asvc` allowlist
without duplicates, preserves other entries and makes a first-change backup.
For a normal installation this file is `~/printer_data/moonraker.asvc`.
Use `--moonraker-data-dir PATH` for another instance, or
`--skip-moonraker-registration` to leave the allowlist unchanged.

## Load the allowlist

Check that the file contains this separate, case-sensitive line without `.service`:

```text
KlipperScreenCam
```

Keep all other services. Restart the matching Moonraker instance once, outside a print:

```bash
sudo systemctl restart moonraker
```

This briefly interrupts the web interface connection. The installer does not restart
Moonraker automatically. Moonraker must already have its normal service-management permissions.

## Restart the viewer

```bash
curl --fail-with-body -sS -X POST   -H 'Content-Type: application/json'   -d '{"service":"KlipperScreenCam"}'   http://127.0.0.1:7125/machine/services/restart
```

A successful response contains `"result":"ok"`. Confirm using
`systemctl is-active KlipperScreenCam`. If authentication is required, use the
normal authenticated client; do not disable authorization. Mainsail may also offer
the service in its system menu; check the installed client version.

After uninstalling, remove only this service line if no longer needed and reload
Moonraker. See the official [allowed services](https://moonraker.readthedocs.io/en/latest/configuration/#allowed-services)
and [service restart API](https://moonraker.readthedocs.io/en/latest/external_api/machine/#restart-a-system-service).
