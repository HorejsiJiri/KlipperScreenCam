# První nasazení archivu 0.2.0

Balíček neobsahuje osobní nastavení ani soubory z běžícího RPi. Na RPi je potřeba zachovat
současné HDMI rozložení a mapování dotyků. Pro první zkoušku není potřeba restartovat celé RPi.

Pokud ještě nemáš připravený druhý monitor a jeho dotyk, nejdříve dokonči
[SECOND_DISPLAY.cs.md](SECOND_DISPLAY.cs.md). Instalátor jejich konfiguraci nemění.

1. Přenes `KlipperScreenCam-0.2.0.tar.gz` například přes WinSCP do domovského adresáře
   uživatele tiskárny. Připoj se přes SSH jako stejný uživatel, který spouští KlipperScreen.

2. Ověř, že již nemáš adresář `~/KlipperScreenCam` s jiným projektem nebo nastavením.
   Pokud existuje, nejdříve porovnej obsah; archiv nerozbaluj naslepo přes něj.
   Jinak:

   ```bash
   cd ~
   tar -xzf KlipperScreenCam-0.2.0.tar.gz
   cd ~/KlipperScreenCam
   bash scripts/install.sh
   ```

3. Otevři `~/printer_data/config/KlipperScreenCam.conf` v Mainsailu nebo nano.
   Pro současnou konfiguraci z chatu jsou připravené souřadnice druhého displeje
   `x = 1024`, `y = 0`, velikost `1024 × 600`, jazyk a motiv `auto`.
   Vyber výchozí kameru:

   ```bash
   python3 launcher.py --list-cameras
   nano ~/printer_data/config/KlipperScreenCam.conf
   python3 launcher.py --check
   ```

   Do `[main]` napiš `default_camera = UID` z výpisu. Můžeš použít i přesný název.

4. Jestli používáš náhled vytvořený v předchozím chatu, proveď postup
   [MIGRATION.cs.md](MIGRATION.cs.md). Zachovej příkazy pro monitory a dotyky;
   odstraňuje se jen staré automatické spuštění kamerové aplikace.

5. Pro první zkoušku spusť novou službu:

   ```bash
   sudo systemctl start KlipperScreenCam
   systemctl status KlipperScreenCam --no-pager
   journalctl -u KlipperScreenCam -n 80 --no-pager
   ```

6. Vyzkoušej přepínání, obnovení stejné kamery, vypnutí obrazu, zapnutí výběrem kamery,
   změnu motivu, dotykový posun seznamu a souběh s Mainsailem i kamerou v KlipperScreenu.

7. Po úspěšném pilotu povol automatické spouštění:

   ```bash
   sudo systemctl enable KlipperScreenCam
   ```

   Úplný restart RPi proveď až ve vhodnou dobu bez probíhajícího tisku a ověř start obou aplikací.

Při neúspěchu můžeš novou službu zastavit přes `sudo systemctl stop KlipperScreenCam`
a obnovit původní spouštěcí skript podle dokumentu MIGRATION. Odinstalace:
`bash ~/KlipperScreenCam/scripts/uninstall.sh`.

## Již nasazená verze 0.1.x

Funkční instalaci nepřepisuj archivem naslepo. Zachovej KlipperScreenCam.conf a zazálohuj
zdrojový adresář. Pro řízenou aktualizaci a návrat použij [UPDATE.cs.md](UPDATE.cs.md).
