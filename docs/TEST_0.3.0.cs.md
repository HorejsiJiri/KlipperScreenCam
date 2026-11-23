# Nasazení a kontrola verze 0.3.0

> Archivní poznámky: aktuální postup je v [instalaci](DEPLOY.cs.md).

Toto je můj kontrolní postup pro nasazení verze 0.3.0 na již fungující instalaci. Příklady vycházejí z účtu horejsi na mém RPi; při jiném účtu použij odpovídající cesty.

Přenes KlipperScreenCam-0.3.0.tar.gz do /home/horejsi na RPi.
Příkazy jsou pro uživatele horejsi a existující funkční instalaci.
Zálohy before-0.3.0 nesmějí už existovat; při opakování zvol jiný název.

```bash
sudo systemctl stop KlipperScreenCam
cp -a ~/KlipperScreenCam ~/KlipperScreenCam.before-0.3.0
cp -p ~/printer_data/config/KlipperScreenCam.conf ~/printer_data/config/KlipperScreenCam.conf.before-0.3.0
cd ~
tar -xzf KlipperScreenCam-0.3.0.tar.gz
cd ~/KlipperScreenCam
bash scripts/install.sh --no-deps
python3 launcher.py --version
python3 launcher.py --check
```

Instalátor zachová konfiguraci a přidá službu do ~/printer_data/moonraker.asvc.
Sám nerestartuje Moonraker. Kontrola má vypsat 0.3.0 a Configuration OK.
Pak spusť náhled:

```bash
sudo systemctl start KlipperScreenCam
systemctl is-active KlipperScreenCam
```

V menu ověř 10, 20, 30 FPS a Neomezeně, zvýraznění aktuální volby, přepínání
kamer a změnu limitu s vypnutým obrazem. Ta nesmí obraz zapnout. Následný výběr
kamery obraz zapne a zachová zvolený limit. Po restartu služby se vrátí hodnota
max_fps z konfigurace. Při konfiguraci 15 se přidá a vybere tlačítko 15 FPS.

Pro test konfiguračního režimu uprav v existující sekci [stream]:

```ini
max_fps = unlimited
```

Ověř --check a restartuj službu. Zvolená má být volba Neomezeně. Nakonec vrať
požadovanou výchozí hodnotu (např. 10 nebo 15) a restartuj. Ověř i změnu jazyka.

Pokud chceš nyní načíst nové povolení služby v Moonrakeru, ve vhodnou dobu
mimo tisk spusť `sudo systemctl restart moonraker`. Viz MOONRAKER.cs.md.

Návrat: zastav KlipperScreenCam, uchovej adresář s novou verzí pod novým názvem,
obnov adresář a konfiguraci ze záloh before-0.3.0 a spusť službu. Nastavení
monitorů ani dotyků se tímto nasazením nemění.

V menu po každé změně vyčkej alespoň 5 sekund. Zapiš Zdroj a Předáváno pro 10,
20, 30 a Neomezeně. Sleduj tutéž kameru a zdroj s alespoň 30 FPS, pokud je dostupný.
Měří se odeslání do WebKitu, nikoli počet skutečně vykreslených snímků.

Ověř pořadí kamery → červené vypnutí/zapnutí obrazu → Limity snímků → naměřené
FPS → tlačítka. Pro konfiguraci 15 očekávám první řádek 10/15/20 a druhý
30/Neomezeně. Pro konfiguraci 20 očekávám první 10/20/30 a druhý široké Neomezeně,
bez duplikátu 20. Číselná tlačítka musí mít stejnou šířku. Vyzkoušej i dlouhé
názvy kamer, posun menu, jiný jazyk a motiv. Při vypnutém obrazu má tlačítko Zapnout obraz kameru bez přeškrtnutí;
při běžícím obrazu má Vypnout obraz přeškrtnutou kameru.
