# Aktualizace funkční instalace a návrat

Tento postup je pro uživatele, kterému již běží samostatný KlipperScreenCam 0.1.x nebo 0.2.0/0.2.1.
Konfigurace tiskárny ani HDMI/dotykový wrapper se při aktualizaci nepřepisují.
Příkazy zadávej na RPi s KlipperScreenCam, nikoliv na jiném serveru.

## 1. Připrav balíček a ověř aktuální stav

Přenes KlipperScreenCam-0.3.0.tar.gz do domovského adresáře uživatele tiskárny.

```bash
hostname
systemctl is-active KlipperScreenCam
python3 ~/KlipperScreenCam/launcher.py --version
ls -lh ~/KlipperScreenCam-0.3.0.tar.gz
```

Pokud používáš nestandardní zdrojový nebo konfigurační adresář, uprav následující cesty
podle `systemctl cat KlipperScreenCam`. Nejdříve ověř, že zálohovací adresáře níže neexistují;
při opakování zvol nový název zálohy, aby se původní záloha nesloučila ani nepřepsala.

## 2. Zastav jen kamerové okno a vytvoř zálohy

```bash
sudo systemctl stop KlipperScreenCam
cp -a ~/KlipperScreenCam ~/KlipperScreenCam.before-0.3.0
cp -p ~/printer_data/config/KlipperScreenCam.conf \
  ~/printer_data/config/KlipperScreenCam.conf.before-0.3.0
```

KlipperScreen, tiskový proces a kamerová služba se tímto příkazem nerestartují.

## 3. Aktualizuj zdroje a instalaci

Archiv má kořenový adresář KlipperScreenCam. Rozbal jej z domovského adresáře:

```bash
cd ~
tar -xzf KlipperScreenCam-0.3.0.tar.gz
cd ~/KlipperScreenCam
bash scripts/install.sh
python3 launcher.py --check
python3 launcher.py --check-locales
python3 launcher.py --version
```

Instalátor zachová existující KlipperScreenCam.conf, ověří službu přes systemd-analyze
a doplní závislosti včetně fontů. Očekávaná verze je 0.3.0. Neprováděj znovu migraci
starého společného náhledu, pokud již byla dokončená.

## 4. Spusť a ověř

```bash
sudo systemctl start KlipperScreenCam
systemctl is-active KlipperScreenCam
systemctl is-enabled KlipperScreenCam
journalctl -u KlipperScreenCam -n 80 --no-pager
```

Ověř obraz, dotyk, pevnou výchozí kameru a vypnutí/zapnutí obrazu. Vyzkoušej vybrané jazyky
a přepnutí motivu. Běžný start po zapnutí se zachová, pokud byla služba již povolená.
Jinak jej po ověření povol přes `sudo systemctl enable KlipperScreenCam`.

## Návrat

Předem ověř, že záloha z kroku 2 existuje a cílový adresář `KlipperScreenCam.failed-0.3.0`
je volný. Potom:

```bash
sudo systemctl stop KlipperScreenCam
mv ~/KlipperScreenCam ~/KlipperScreenCam.failed-0.3.0
mv ~/KlipperScreenCam.before-0.3.0 ~/KlipperScreenCam
cp -p ~/printer_data/config/KlipperScreenCam.conf.before-0.3.0 \
  ~/printer_data/config/KlipperScreenCam.conf
sudo systemctl start KlipperScreenCam
```

Oba adresáře zůstávají uchované. Pokud se liší konfigurace služby, obnov ji instalátorem
z obnovené verze nebo ze zálohy jednotky; u původního 0.1.0 instalátoru nejprve zachovej
ověřenou opravu bez WorkingDirectory. Návrat nevyžaduje změnu kamer ani HDMI konfigurace.
