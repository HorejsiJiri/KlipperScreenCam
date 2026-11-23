# Konfigurace

[English](CONFIGURATION.md) · [Česky](CONFIGURATION.cs.md)

Konfiguraci ukládám do `~/printer_data/config/KlipperScreenCam.conf`, aby byla
přístupná i v Mainsailu. [Úplný vzor](../config/KlipperScreenCam.conf) obsahuje všechny
výchozí hodnoty. Volby přidávej do existujících sekcí, nevytvářej druhé stejné sekce.
Po změně konfigurace restartuj službu.

## Hlavní nastavení

```ini
[main]
moonraker_url = http://127.0.0.1:7125
web_url = http://127.0.0.1
default_camera = Cam2
language = auto
theme = auto
klipperscreen_directory = ~/KlipperScreen
klipperscreen_config =
theme_poll_seconds = 2
```

`web_url` doplňuje relativní adresy streamů, obvykle přes nginx Mainsailu.
`default_camera` přijímá přesný název nebo UID kamery z Moonrakeru:

```bash
python3 ~/KlipperScreenCam/launcher.py --list-cameras
```

UID přežije přejmenování. Výběr za běhu nepřepisuje výchozí kameru; po restartu se
znovu použije konfigurace. Prázdná, neexistující nebo vypnutá kamera vede k první
povolené kameře. Nastavení je nezávislé na Mainsailu. Cesta `device` z Crowsnestu sem nepatří.
`auto` přebírá jazyk a motiv KlipperScreenu. Pevný jazyk je název JSON bez přípony,
pevný motiv název jeho adresáře. Prázdná cesta ke konfiguraci hledá běžná umístění.
Relativní souborové cesty se počítají od adresáře konfigurace.
Motiv, jazyk a změny zvoleného překladu se načítají automaticky.

## Displej

```ini
[display]
display = :0
xauthority = ~/.Xauthority
x = 1024
y = 0
width = 1024
height = 600
menu_min_width = 410
gear_size = 88
hide_cursor = true
hide_name_single_camera = true
hardware_acceleration = off
pause_on_dpms = true
dpms_poll_seconds = 20
```

Souřadnice patří do společné plochy X11. Aplikace nepřepíná HDMI režimy.
U jediné kamery lze skrýt název, menu zůstává pro ovládání obrazu a FPS.
`hardware_acceleration` přijímá `off`, `auto`, `on`; nezaručuje hardwarové dekódování
MJPEG. Viz [akcelerace](ACCELERATION.cs.md).
`pause_on_dpms` skutečně odpojí místní stream při uspání DPMS. Interval kontrol je
1–120 sekund. Integrace společného probuzení předává okamžitou zprávu.
Tyto volby patří do `[display]`. Starší zápis v `[stream]` je podporovaný s upozorněním;
stejná volba v obou sekcích je chyba. Viz [uspávání](RPI_SLEEP.cs.md).

## Stream

```ini
[stream]
max_fps = 15
start_paused = false
reconnect_initial_seconds = 2
reconnect_max_seconds = 30
request_timeout_seconds = 5
```

Limit je celé číslo 1–120 nebo `unlimited`. Změna v menu platí do restartu.
`start_paused = true` spustí aplikaci bez odběru obrazu; výběr kamery jej zapne.
Obnovování řeší oznámené chyby; tiché zaseknutí může vyžadovat opětovný výběr kamery.
Limit vynechává komprimované snímky před WebKitem, ale zdrojový stream dál čte.
Viz [limity FPS](FPS.cs.md).

```bash
python3 ~/KlipperScreenCam/launcher.py --check
sudo systemctl restart KlipperScreenCam
```
