# Druhý HDMI displej a dva dotyky — krok za krokem

[English](SECOND_DISPLAY.md) · [Česky](SECOND_DISPLAY.cs.md)

Tento postup vychází z mé tiskárny: Raspberry Pi 5, Debian 13 (Trixie), KlipperScreen přes X11 a dva HDMI dotykové displeje 1024 × 600. Popisuji zde i nastavení rozšířené plochy a obou dotyků, abys je nemusel hledat v dalších návodech.

Postup můžeš použít i pro novou instalaci, kde zatím běží pouze KlipperScreen.
Příklady odpovídají mému zapojení; názvy zařízení a cesty přizpůsob svému systému.

**KlipperScreenCam sám HDMI ani dotyky nenastavuje.** Nejdříve připrav společnou
rozšířenou plochu; teprve potom spusť kamerový displej. Nepoužívej tento návod
naslepo pro Wayland, DSI/GPIO displeje nebo jiné rozlišení.

Příkazy zadávej přes SSH jako běžný uživatel tiskárny, tedy stejný uživatel jako
v `User=` služby KlipperScreen. V příkladech znamená `~` právě jeho domovský adresář.
KlipperScreen a kamery by měly před začátkem samostatně fungovat.

## 1. Zapojení

1. Připoj oba monitory do samostatných HDMI výstupů RPi.
2. Připoj oba dotykové USB kabely. HDMI přenáší obraz, nikoliv USB dotyk.
3. Monitory zapni a ponech přístup přes SSH i při dočasně špatném obrazu.

Ověř model, OS a grafickou relaci:

```bash
tr -d '\0' < /proc/device-tree/model
echo
cat /etc/os-release
systemctl cat KlipperScreen
ps -eo user,pid,args | grep -E 'Xorg|Xwayland|wayfire|labwc|screen.py' | grep -v grep
```

Na mém RPi běžel Xorg na `:0` a služba používala `BACKEND=X`.
Pokud je zde Wayland, jiný uživatel nebo jiná X relace, nejdříve přizpůsob následující
příkazy skutečnému systému. Neměň kvůli tomuto návodu naslepo `config.txt` ani grafický ovladač.

## 2. Zjisti výstupy a nabízená rozlišení

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --query
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --listmonitors
```

Pokud chybí diagnostické příkazy:

```bash
sudo apt install --no-install-recommends x11-xserver-utils xinput
```

Na mé instalaci jsou výstupy `HDMI-1` a `HDMI-2`. Jinde se mohou jmenovat jinak.
Názvy `HDMI-A-1` v `/sys/class/drm` nejsou automaticky stejné jako názvy pro xrandr.
Hvězdička u režimu znamená aktuální režim. `+0+0` u obou výstupů znamená překrytí
ploch: stejný obraz na obou displejích není důkazem dvou instancí KlipperScreenu.

Pokud dostaneš chybu `Can't open display`, zkontroluj uživatele, hodnotu DISPLAY a
cestu XAUTHORITY; nepoužívej jako zkratku `xhost +`.

## 3. Nastav dočasně rozšířenou plochu

Můj první monitor již nabízel `1024x600`, druhý původně jen `1024x576` a další režimy.
Přiřadil jsem mu **již existující** režim z prvního monitoru:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --addmode HDMI-2 1024x600
```

Pokud už oba výstupy `1024x600` nabízejí, tento krok není potřeba.
Pokud přiřazení selže nebo režim neexistuje ani na jednom výstupu, nepokračuj
vynucením náhodného časování. Ověř specifikace monitoru, EDID a HDMI kabeláž.

Potom nastav první displej vlevo a druhý vpravo:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr \
  --output HDMI-1 --primary --mode 1024x600 --pos 0x0 \
  --output HDMI-2 --mode 1024x600 --pos 1024x0
```

Očekávaný stav:

```text
Screen 0: ... current 2048 x 600 ...
HDMI-1 connected primary 1024x600+0+0
HDMI-2 connected 1024x600+1024+0
```

KlipperScreen patří na první displej. Druhý může být zatím prázdný.
Při jiném rozlišení je vodorovná pozice druhého displeje šířka prvního monitoru.
Pokud je to potřeba, fyzicky prohoď HDMI kabely a znovu proveď detekci; tím se může
změnit přiřazení názvů výstupů ke konkrétním panelům.

Pokud druhý monitor po změně ztratí obraz a původně měl funkční režim `1024x576`,
dočasný návrat na mém zařízení byl:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr \
  --output HDMI-2 --mode 1024x576 --pos 1024x0
```

## 4. Urči, který dotyk patří ke kterému displeji

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput list
```

Každé dotykové zařízení má název a číselné ID. Pro zkoušku použij aktuální ID:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput test 6
```

`6` nahraď ID ze svého výpisu. Dotkni se postupně obou displejů. Terminál bude
vypisovat události pouze pro právě sledovaný dotyk. Ukonči pomocí Ctrl+C.
Totéž můžeš zopakovat pro druhé ID. Zapiš si vztah **název zařízení → HDMI výstup**.

Po přepojení nebo restartu se číselná ID mohou změnit. Pro trvalé nastavení proto
použij názvy. Na svém zařízení jsem ověřil toto přiřazení:

```bash
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput map-to-output \
  "WaveShare WS170120" HDMI-1

DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xinput map-to-output \
  "深圳市全动电子技术有限公司 ByQDtech 触控USB鼠标" HDMI-2
```

**Tyto dva názvy jsou příklad konkrétního hardware.** Dosadit je na jiný počítač
bez ověření by nebylo správně. Pokud mají oba dotyky stejný název, samotné jméno
není jednoznačné; je nutné nejdříve rozlišit jejich zařízení nebo USB cesty.

Na KlipperScreenu ověř dotyk u všech okrajů. Dotyk druhého displeje nesmí ovládat
KlipperScreen. Druhý dotyk definitivně ověř v menu kamer, až bude náhled spuštěný.

## 5. Ulož rozložení pro start grafické relace

Pokud už máš funkční `start-displays.sh`, nedělej druhé paralelní nastavení a nic
z tohoto oddílu nepřepisuj. Zachovej jej a postupuj podle MIGRATION.cs.md.

Pro novou instalaci vytvoř vlastní spouštěcí skript. Používám adresář, který
nepatří do aktualizovaných zdrojů KlipperScreenu:

```bash
mkdir -p ~/.config/KlipperScreenCam
nano ~/.config/KlipperScreenCam/start-klipperscreen.sh
```

Vlož následující obsah a **uprav názvy dotyků podle kroku 4**. Cesty k Pythonu a
`screen.py` ověř proti původnímu `KS_XCLIENT` z `systemctl cat KlipperScreen`.
Pokud původní spuštění mělo další argumenty (například vlastní konfiguraci), zachovej je.

```bash
#!/bin/bash

xrandr --addmode HDMI-2 1024x600 2>/dev/null || true

if xrandr \
    --output HDMI-1 --primary --mode 1024x600 --pos 0x0 \
    --output HDMI-2 --mode 1024x600 --pos 1024x0
then
    xinput map-to-output "WaveShare WS170120" HDMI-1
    xinput map-to-output \
        "深圳市全动电子技术有限公司 ByQDtech 触控USB鼠标" HDMI-2
else
    echo "HDMI layout failed; starting KlipperScreen with the current layout." >&2
fi

exec "$HOME/.KlipperScreen-env/bin/python" \
    "$HOME/KlipperScreen/screen.py" --monitor 0
```

```bash
chmod +x ~/.config/KlipperScreenCam/start-klipperscreen.sh
bash -n ~/.config/KlipperScreenCam/start-klipperscreen.sh
```

Skript se musí spouštět **uvnitř již vytvořené X relace**, ne před Xorgem. V mé instalaci
KlipperScreenu to řeší `KS_XCLIENT`, který předává jeho startovací skript programu xinit:

```bash
cat ~/KlipperScreen/scripts/KlipperScreen-start.sh
```

Ověř, že větev pro X používá `xinit $KS_XCLIENT`. Pokud existuje vlastní
`scripts/launch_KlipperScreen.sh`, musíš zkontrolovat také jeho obsah; může běžné
spouštění přebíjet. Pokud se startovací mechanismus liší, následující drop-in nepoužívej naslepo.

Připrav samostatný drop-in pro službu. Výchozí jednotku KlipperScreenu neměň:

```bash
sudo mkdir -p /etc/systemd/system/KlipperScreen.service.d
sudo systemctl cat KlipperScreen
sudo nano /etc/systemd/system/KlipperScreen.service.d/90-klipperscreencam-displays.conf
```

Vlož **absolutní cestu s vlastním uživatelským jménem**, například pro uživatele `horejsi`:

```ini
[Service]
Environment="KS_XCLIENT=/home/horejsi/.config/KlipperScreenCam/start-klipperscreen.sh"
```

V systemd zde nepoužívej `~` ani `$HOME`. Pokud už jiný drop-in nastavuje KS_XCLIENT,
nejdříve jej zazálohuj a vyřeš, který má být aktivní; nekombinuj dva rozdílné spouštěče.

```bash
sudo systemctl daemon-reload
sudo systemctl restart KlipperScreen
```

Ověř stav a rozložení:

```bash
systemctl is-active KlipperScreen
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --query
```

Při neúspěchu vrať nově přidaný drop-in mimo aktivní jednotky (ostatní drop-iny ponech):

```bash
sudo mv /etc/systemd/system/KlipperScreen.service.d/90-klipperscreencam-displays.conf \
  /etc/systemd/system/KlipperScreen.service.d/90-klipperscreencam-displays.conf.disabled
sudo systemctl daemon-reload
sudo systemctl restart KlipperScreen
```

## 6. Nainstaluj a spusť kamerový displej

Teď pokračuj podle DEPLOY.cs.md. V `~/printer_data/config/KlipperScreenCam.conf` odpovídá
mému rozložení tato část:

```ini
[display]
display = :0
xauthority = ~/.Xauthority
x = 1024
y = 0
width = 1024
height = 600
```

Kamerové okno pak vyplní druhý monitor. Vlastní služba KlipperScreenCam se spouští
po KlipperScreenu a čeká na dostupnost X11; HDMI nastavení ve spouštěcím skriptu se tedy
provede před otevřením aplikace. Po restartu KlipperScreenu vždy ověř stav obou služeb.

## 7. Ověření po úplném zapnutí

Ve vhodnou dobu bez probíhajícího tisku restartuj RPi. Ověř oba obrazy, oba dotyky a služby:

```bash
systemctl is-active KlipperScreen
systemctl is-active KlipperScreenCam
systemctl is-enabled KlipperScreenCam
DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" xrandr --query
```

Nakonec ověř zhasnutí a probuzení podle skutečného nastavení KlipperScreenu.
Pro společné probuzení a automatické zastavení místního streamu při uspání
používám volitelnou integraci `--shared-wake`. Instalaci, konfiguraci a restart obou
služeb popisuji v [návodu k uspávání](RPI_SLEEP.cs.md). Na svém RPi jsem ověřil
společné probuzení i provoz po restartu. Bez této integrace samotné probuzení DPMS
nemusí zavřít černou plochu spořiče KlipperScreenu.
