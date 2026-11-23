# Přechod z původního náhledu

[English](MIGRATION.md) · [Česky](MIGRATION.cs.md)

Než jsem projekt oddělil, spouštěl jsem kamerový náhled společně s KlipperScreenem ze skriptu start-displays.sh. Pokud máš podobné řešení, tento postup ti pomůže přejít na samostatnou službu a zachovat funkční displeje i dotyky.

Nová aplikace je samostatná služba. Staré náhledové soubory nemaž, dokud není nový projekt
ověřený. Instalátor do starého spouštění sám nezasahuje.

## Moje původní instalace

Původní náhled spouští `~/.config/KlipperScreen/start-displays.sh` přes `KS_XCLIENT`
v doplňkové konfiguraci služby KlipperScreen. Tento skript současně nastavuje rozlišení,
polohu HDMI a mapování dotyků. **Tyto příkazy je potřeba zachovat.**

1. Nainstaluj nový projekt bez `--enable`.
2. Nastav `~/printer_data/config/KlipperScreenCam.conf` a ověř jej přes `--check`.
3. Zálohuj původní skript a doplňkovou konfiguraci služby:

   ```bash
   cp -p ~/.config/KlipperScreen/start-displays.sh \
     ~/.config/KlipperScreen/start-displays.sh.before-KlipperScreenCam
   systemctl cat KlipperScreen > ~/KlipperScreen.service.before-KlipperScreenCam.txt
   ```

4. V `start-displays.sh` odstraň pouze spuštění `camera-viewer.py`, proměnnou
   `CAMERA_VIEWER_PID` a navazující `trap` pro tento proces. Zachovej `xrandr`, `xinput`
   a spuštění skutečného `KlipperScreen/screen.py`. Před uložením si obsah ověř:

   ```bash
   nano ~/.config/KlipperScreen/start-displays.sh
   bash -n ~/.config/KlipperScreen/start-displays.sh
   ```

5. Restartuj KlipperScreen. Oba displeje se mají správně nastavit, ale staré kamerové okno
   se již nemá otevřít:

   ```bash
   sudo systemctl restart KlipperScreen
   ```

6. Spusť novou službu nejdříve pro pilot:

   ```bash
   sudo systemctl start KlipperScreenCam
   journalctl -u KlipperScreenCam -n 80 --no-pager
   ```

7. Po ověření zapni start po bootu:

   ```bash
   sudo systemctl enable KlipperScreenCam
   ```

Jestli se skutečný skript od popisu liší, nepřepisuj ho vzorem naslepo. Nejdříve porovnej
jeho obsah. Staré `camera-display.json` a `camera-choice.json` se automaticky neimportují;
UID výchozí kamery vlož do nové konfigurace.

## Návrat

```bash
sudo systemctl disable --now KlipperScreenCam
cp -p ~/.config/KlipperScreen/start-displays.sh.before-KlipperScreenCam \
  ~/.config/KlipperScreen/start-displays.sh
sudo systemctl restart KlipperScreen
```

Není potřeba měnit Crowsnest, Moonraker ani nastavení kamer v Mainsailu.
