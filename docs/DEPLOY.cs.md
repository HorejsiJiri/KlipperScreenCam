# První nasazení archivu 0.3.0

Balíček neobsahuje osobní nastavení ani soubory z běžícího RPi. Na RPi je potřeba zachovat
současné HDMI rozložení a mapování dotyků. Pro první zkoušku není potřeba restartovat celé RPi.

Pokud ještě nemáš připravený druhý monitor a jeho dotyk, nejdříve dokonči
[SECOND_DISPLAY.cs.md](SECOND_DISPLAY.cs.md). Instalátor jejich konfiguraci nemění.

1. Přenes `KlipperScreenCam-0.3.0.tar.gz` například přes WinSCP do domovského adresáře
   uživatele tiskárny. Připoj se přes SSH jako stejný uživatel, který spouští KlipperScreen.

2. Ověř, že již nemáš adresář `~/KlipperScreenCam` s jiným projektem nebo nastavením.
   Pokud existuje, nejdříve porovnej obsah; archiv nerozbaluj naslepo přes něj.
   Jinak:

   ```bash
   cd ~
   tar -xzf KlipperScreenCam-0.3.0.tar.gz
   cd ~/KlipperScreenCam
   bash scripts/install.sh
   ```

3. Otevři `~/printer_data/config/KlipperScreenCam.conf` v Mainsailu nebo nano.
   Výchozí konfigurace používá souřadnice druhého displeje
   `x = 1024`, `y = 0`, velikost `1024 × 600`, jazyk a motiv `auto`.
   Vyber výchozí kameru:

   ```bash
   python3 launcher.py --list-cameras
   nano ~/printer_data/config/KlipperScreenCam.conf
   python3 launcher.py --check
   ```

   Do `[main]` napiš `default_camera = UID` z výpisu. Můžeš použít i přesný název.
   V sekci `[stream]` je výchozí `max_fps = 15`; pro vyšší limit lze nastavit 30.

4. Jestli přecházíš z původního společného náhledu, proveď postup
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

## Ovládání služby přes Moonraker

Instalátor automaticky doplní KlipperScreenCam do seznamu bez duplicit a zachová ostatní položky.
Před první změnou existujícího souboru uloží moonraker.asvc.ksc-backup. Moonraker automaticky
nerestartuje. Pro běžný datový
adresář `~/printer_data` otevři:

```bash
nano ~/printer_data/moonraker.asvc
```

Ponech ostatní řádky a přidej samostatný řádek, pokud už v seznamu není:

```text
KlipperScreenCam
```

Název musí odpovídat velikostí písmen, bez `.service`. Ulož soubor a načti nový seznam:

```bash
sudo systemctl restart moonraker
```

Webové rozhraní může při restartu Moonrakeru krátce ztratit spojení. Tento krok
proveď při prvním nastavení mimo probíhající tisk. U vlastní datové cesty nebo
více instancí použij příslušný datový adresář a název služby Moonrakeru.

Restart náhledu přes místní API Moonrakeru:

```bash
curl --fail-with-body -sS -X POST \
  -H 'Content-Type: application/json' \
  -d '{"service":"KlipperScreenCam"}' \
  http://127.0.0.1:7125/machine/services/restart
```

Úspěšná odpověď obsahuje `"result":"ok"`. Ověř běh přes
`systemctl is-active KlipperScreenCam`. Podle klienta může být služba dostupná také
v nabídce systémových služeb Mainsailu; ověř to v konkrétní verzi rozhraní.
Pokud API vyžaduje autentizaci, použij přihlášeného klienta nebo jeho běžné
přihlašovací údaje; nevypínej autorizaci Moonrakeru. Oprávnění ke správě systémových
služeb musí mít již nastavené samotný Moonraker.

Automatické povolení lze vynechat přes `--skip-moonraker-registration`. Vlastní datový
adresář zadej přes `--moonraker-data-dir /cesta/printer_data`; jinak se použije nadřazený
adresář `--config-dir`. Výše uvedená ruční úprava slouží ke kontrole nebo doplnění.
Při odinstalaci lze odstranit pouze řádek `KlipperScreenCam` a znovu načíst Moonraker.

Oficiální dokumentace: [povolené služby](https://moonraker.readthedocs.io/en/latest/configuration/#allowed-services)
a [restart přes API](https://moonraker.readthedocs.io/en/latest/external_api/machine/#restart-a-system-service).

