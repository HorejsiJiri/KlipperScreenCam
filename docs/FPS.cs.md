# Limit snímků a údaje FPS

[English](FPS.md) · [Česky](FPS.cs.md)

Do existující sekce `[stream]` v `~/printer_data/config/KlipperScreenCam.conf` doplň:

```ini
[stream]
max_fps = 15
```

Nevytvářej druhou sekci `[stream]`, pokud už existuje. Výchozí limit při vynechání
volby je 15 FPS. Povolené jsou celé hodnoty 1 až 120 nebo unlimited. Limit nezvýší FPS nad možnosti zdroje.
Po změně ověř konfiguraci a restartuj pouze kamerový náhled:

```bash
python3 ~/KlipperScreenCam/launcher.py --check
sudo systemctl restart KlipperScreenCam
```

Aplikace načítá původní komprimovaný MJPEG z Crowsnestu, podle monotónního času
vybírá celé snímky a zbytek zahazuje. Vybrané JPEG snímky bez překódování předává
WebKitu. Nečeká mezi snímky pomocí sleep a nevytváří frontu starého obrazu.
Rozdělení multipart přenosu čeká na následující hranici snímku, což může přidat
přibližně jeden interval vstupního snímku, nikoli narůstající frontu.

To může snížit zatížení dekódování a vykreslování WebKitu, ale příjem původního
streamu a práce Crowsnestu zůstávají. Mainsail ani ostatní klienty toto nastavení
neomezuje. Úspora není automaticky 50 % při změně 30 na 15 FPS; záleží i na ostatní
práci a skutečné snímkové frekvenci kamery.

Pro srovnání použij tutéž kameru, rozlišení, scénu a nastavení akcelerace. Nejprve
změř 30 FPS a poté 15 FPS po přibližně 30 sekundách ustálení. Sleduj celkovou
zátěž, WebKit, Python i plynulost obrazu. Vyšší limit: `max_fps = 30` a restart služby.
Při vypnutí obrazu se jako dosud skutečně uzavírá místní kamerové spojení.

Testováno místně s nepřetržitým MJPEG HTTP serverem: omezení toku snímků, zachování
JPEG dat, fragmentované hranice, stream bez Content-Length a pokračování druhého
nezávislého klienta po vypnutí místního obrazu. Na svém RPi jsem vyzkoušel plynulý obraz při 15 FPS i při 10 FPS. Paměť parseru je omezená; část větší než 16 MiB je odmítnuta.

Při ladění jsem sledoval i CPU. Krátké vzorky beru jen orientačně;
výsledek nepřenáším jako záruku úspory na jinou sestavu.

## Přepínání za běhu

Menu jsem uspořádal v pořadí kamery, vypnout/zapnout obraz, nadpis Limity snímků,
naměřené FPS a tlačítka. Vybraný limit poznáš podle zvýrazněného tlačítka. Menu po změně zůstává
otevřené; zavřeš jej křížkem nebo klepnutím mimo ně. Změna nevytváří nové spojení,
nemění kameru a nezapíná vypnutý obraz. Platí společně pro všechny místní kamery.

Konfigurace podporuje celé číslo 1–120 nebo `unlimited` (bez ohledu na velikost písmen):

```ini
[stream]
max_fps = unlimited
```

`unlimited` znamená bez místního limitu, nikoli neomezené možnosti kamery. Nula ani
překlep `unlimitet` nejsou platné. Výchozí hodnota zůstává 15. Menu nemění soubor;
po restartu služby se obnoví hodnota z konfigurace. Od verze 0.3.0 se vlastní číselná hodnota z konfigurace vloží jako další
tlačítko; například 15 znamená 10, 15, 20 / 30, Neomezeně. Hodnota 20 se
nepřidává podruhé: 10, 20, 30 / Neomezeně.

Nové texty mají překlady ve všech 32 JSON souborech. Přepínání je ověřeno lokálními
transportními a browser testy; GTK/WebKit na cílovém RPi musí potvrdit testovací nasazení.

## Měření přijímaných a předaných snímků

Menu ukazuje Zdroj a Předáváno. Hodnoty se počítají podle celých přijatých a skutečně
odeslaných MJPEG částí, nezávisle na nastaveném limitu, v intervalu zhruba 2 sekund.
Po spuštění, přepnutí kamery nebo změně limitu vyčkej alespoň 5 sekund na ustálení.
Předáváno měří výstup Pythonu do WebKitu, nikoli skutečně vykreslené FPS.

Příklad při zdroji 30 FPS: limit 10 → Předáváno kolem 10, limit 20 → kolem 20,
30 nebo Neomezeně → kolem 30. Pokud zdroj běží jen 10 FPS, vyšší limity nezvýší
počet snímků. Vzorky mohou mírně překročit limit kvůli časovým hranicím měření.
Při vypnutém přenosu se oba čítače vrátí na nulu. Nové popisky jsou ve všech jazycích.

Pokud log uvádí Local FPS limit: 10, ale Předáváno zůstává po ustálení např. 30,
pošli obě hodnoty, verzi launcher.py --version a příslušný log. To je konkrétní
podklad pro hledání chyby, nikoli pouze dojem z plynulosti nebo krátký vzorek CPU.

Údaje v menu se zobrazují zaokrouhlené na nejbližší celé FPS: 14,4 → 14,
14,5 → 15. Výpočet rychlosti a vlastní časování limitu zůstávají nezaokrouhlené.

## Rozložení menu 0.3.0

Kamery → vypnout/zapnout obraz → Limity snímků → Zdroj/Předáváno → tlačítka.
Vypnutí má přeškrtnutou kameru, červený text a stejné zarovnání jako položky kamer.
Při vypnutém obrazu tlačítko nabízí zapnutí s běžnou kamerou bez přeškrtnutí.
Číselná tlačítka mají stejnou šířku, první řádek má tři; Neomezeně vyplňuje
zbytek druhého řádku. Seznam předvoleb vychází z konfigurace, nikoli z poslední
ruční volby. Měření a limitování se tímto přepracováním vzhledu nemění.
