# Archivní postup pro verzi 0.2.5

> Archivní poznámky: aktuální postup je v [instalaci](DEPLOY.cs.md).

Tento postup si ponechávám jako záznam vývoje. Pro verzi 0.3.0 použij [aktuální nasazení a kontrolu](TEST_0.3.0.cs.md). Chování staršího menu se od aktuální verze liší.

Přenes KlipperScreenCam-0.2.5.tar.gz do /home/horejsi na RPi.
Příkazy jsou pro uživatele horejsi a existující funkční instalaci.
Zálohy before-0.2.5 nesmějí už existovat; při opakování zvol jiný název.

```bash
sudo systemctl stop KlipperScreenCam
cp -a ~/KlipperScreenCam ~/KlipperScreenCam.before-0.2.5
cp -p ~/printer_data/config/KlipperScreenCam.conf ~/printer_data/config/KlipperScreenCam.conf.before-0.2.5
cd ~
tar -xzf KlipperScreenCam-0.2.5.tar.gz
cd ~/KlipperScreenCam
bash scripts/install.sh --no-deps
python3 launcher.py --version
python3 launcher.py --check
```

Instalátor zachová konfiguraci a přidá službu do ~/printer_data/moonraker.asvc.
Sám nerestartuje Moonraker. Kontrola má vypsat 0.2.5 a Configuration OK.
Pak spusť náhled:

```bash
sudo systemctl start KlipperScreenCam
systemctl is-active KlipperScreenCam
```

V menu ověř 10, 20, 30 FPS a Neomezeně, zvýraznění aktuální volby, přepínání
kamer a změnu limitu s vypnutým obrazem. Ta nesmí obraz zapnout. Následný výběr
kamery obraz zapne a zachová zvolený limit. Po restartu služby se vrátí hodnota
max_fps z konfigurace. Při konfiguraci 15 se zobrazí 15 FPS bez vybrané předvolby.

Pro test konfiguračního režimu uprav v existující sekci [stream]:

```ini
max_fps = unlimited
```

Ověř --check a restartuj službu. Zvolená má být volba Neomezeně. Nakonec vrať
požadovanou výchozí hodnotu (např. 10 nebo 15) a restartuj. Ověř i změnu jazyka.

Pokud chceš nyní načíst nové povolení služby v Moonrakeru, ve vhodnou dobu
mimo tisk spusť `sudo systemctl restart moonraker`. Viz MOONRAKER.cs.md.

Návrat: zastav KlipperScreenCam, uchovej adresář s novou verzí pod novým názvem,
obnov adresář a konfiguraci ze záloh before-0.2.5 a spusť službu. Nastavení
monitorů ani dotyků se tímto nasazením nemění.

V menu po každé změně vyčkej alespoň 5 sekund. Zapiš Zdroj a Předáváno pro 10,
20, 30 a Neomezeně. Sleduj tutéž kameru a zdroj s alespoň 30 FPS, pokud je dostupný.
Měří se odeslání do WebKitu, nikoli počet skutečně vykreslených snímků.
