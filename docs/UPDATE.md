# Update and rollback

[English](UPDATE.md) · [Česky](UPDATE.cs.md)

I keep configuration separate from the source tree. Before replacing a working
installation, stop the viewer and make a unique backup. Run as the regular printer user.

```bash
sudo systemctl stop KlipperScreenCam
ksc_backup=$(mktemp -d "$HOME/KlipperScreenCam-backup.XXXXXX")
cp -a ~/KlipperScreenCam "$ksc_backup/project"
cp -p ~/printer_data/config/KlipperScreenCam.conf "$ksc_backup/config.conf"
printf 'Backup: %s\n' "$ksc_backup"
```

Copy the new archive to the home directory, then:

```bash
cd ~
tar -xzf KlipperScreenCam-0.3.0.tar.gz
cd ~/KlipperScreenCam
bash scripts/install.sh --no-deps
python3 launcher.py --check
```

The installer preserves existing configuration. Review new defaults in
`config/KlipperScreenCam.conf`; do not overwrite your configured camera or geometry.
For shared wake use `--shared-wake` as described in [the sleep guide](RPI_SLEEP.md).
Only after successful validation:

```bash
sudo systemctl restart KlipperScreenCam
systemctl is-active KlipperScreenCam
journalctl -u KlipperScreenCam -n 60 --no-pager
```

If the shared-wake patch changed KlipperScreen, restart KlipperScreen first and
then the viewer. Verify normal touch wake and operation after a reboot.

## Rollback

Use the exact backup path printed above. Stop the viewer, move the new project
aside under a unique name, copy the backed-up `project` directory back as
`~/KlipperScreenCam`, and restore `config.conf` to its original config path.
Re-run the restored install script with `--no-deps`, validate, then start the service.
Do not delete the backup or blindly copy paths from another machine.
Optional KlipperScreen source patches have separate timestamped backups; restore
those two files and restart KlipperScreen if reverting that integration too.
