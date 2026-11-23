# Přehled změn

[English](CHANGELOG.md)

## 0.3.0 — 22. 11. 2026

### Kamerový displej a ovládání

- Samostatný dotykový náhled pro X11, Klipper a Moonraker s vlastní službou,
  instalací a konfigurací vedle konfigurace tiskárny.
- Existující HTTP(S) MJPEG streamy a názvy kamer z Moonrakeru. Pevná výchozí kamera
  podle přesného názvu nebo UID, nezávislá na Mainsailu.
- Obraz přes plochu displeje, průhledné překryvy, barvy a SVG ikony z místního
  KlipperScreenu. Automatické přebírání motivu a jazyka.
- Posuvný seznam kamer, vypnutí/zapnutí obrazu, měřené FPS zdroje/předávání a živé
  předvolby 10/20/30, vlastní hodnota a Neomezeně. Vlastní limit se seřadí bez duplicit.
  Číselná tlačítka mají stejnou šířku, Neomezeně doplní druhý řádek.
- Výchozí místní limit 15 FPS; rozsah 1–120 nebo `unlimited`. Vynechané komprimované
  snímky nejdou WebKitu, bez překódování. Zdrojový stream i vzdálení diváci jsou nezávislí.
  Čítače ukazují průměry zaokrouhlené na celá čísla. Změna v menu se neukládá.
- Vypnutí obrazu skutečně zavře místní spojení. Výběr kamery jej znovu zapne.
- Volitelná politika akcelerace WebKitu `off/auto/on`, výchozí off; nezaručuje
  hardwarové dekódování MJPEG.

### Uspání a společné probuzení

- Odpojení místního streamu po zjištění uspání X11 DPMS, výchozí kontrola po 20 sekundách.
  Čas zhasnutí dál řídí KlipperScreen.
- Volitelná integrace `--shared-wake` zavře černou plochu spořiče KlipperScreenu
  a pošle neblokující zprávu pro okamžité obnovení obrazu.
- Ruční vypnutí, zvolená kamera a aktuální limit FPS se při uspání zachovají.
- Volby uspávání patří do `[display]`; starší zápis v `[stream]` vyvolá upozornění.
  Stejná volba v obou sekcích je chyba.
- Úprava zdrojů KlipperScreenu ověřuje známou podobu a vytváří časované zálohy.
  Po instalaci je nutný restart obou služeb. Aktualizace KlipperScreenu může úpravu přepsat.

### Instalace a dokumentace

- Registrace služby v `moonraker.asvc` bez duplicit, se zachováním ostatních položek
  a zálohou. Moonraker se restartuje ručně.
- Primární anglická a sekundární česká dokumentace: oba HDMI displeje a dotyky krok
  za krokem, konfigurace, přechod, uspávání a návrat k záloze.
- 32 samostatných jazykových JSON včetně popisků FPS a RTL. Třicet překladů vzniklo
  s pomocí AI a čeká na kontrolu rodilými mluvčími.
- Automatické kontroly konfigurace, přenosu, rozhraní a platforem. Podrobnosti
  ověření zůstávají v RELEASE_CHECKS.md mimo instalační manuál.

### Ověření a omezení

Na svém Raspberry Pi 5 s Debianem 13, X11 a dvěma HDMI dotykovými displeji 1024 × 600
jsem ověřil start po restartu, společné probouzení a okamžité obnovení kamery.
Následné ověření uspávání z 23. 11. 2026 je součástí tohoto sloučeného záznamu 0.3.0.
Obraz při 15 i 10 FPS byl plynulý; skutečné odpojení jsem ověřil na tiskárně.
Pozorování CPU nepovažuji za benchmark.

Podporované je X11 a HTTP(S) MJPEG, nikoli WebRTC, HLS, RTSP ani Wayland.
Volitelná úprava probouzení odmítne neznámou podobu zdrojů KlipperScreenu.
Jiné sestavy, ovladače, motivy a kombinace jazyků a písem vyžadují vlastní ověření.
