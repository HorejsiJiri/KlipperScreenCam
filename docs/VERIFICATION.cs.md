# Moje sestava a ověření

[English](VERIFICATION.md) · [Česky](VERIFICATION.cs.md)

Projekt vyvíjím a zkouším na své tiskárně. Tuto stránku si nechávám jako technický
záznam; pro běžnou instalaci stačí hlavní návod a kontrola obrazu, dotyků a startu.

## Na čem aplikaci používám

- Raspberry Pi 5 Model B Rev 1.0, Debian 13.8 Trixie.
- KlipperScreen přes X11 a dva dotykové HDMI displeje 1024 × 600.
- Rozšířená plocha 2048 × 600, KlipperScreen vlevo, kamerový náhled vpravo.
- Kamery zpřístupněné přes Crowsnest a zapsané v Moonrakeru.

## Co jsem ověřil na tiskárně

Ověřil jsem obraz, dotykové ovládání a automatický start samostatné služby.
Při přechodu ze společného spouštěcího skriptu jsem zachoval rozložení monitorů
a mapování dotyků. Výchozí kameru jsem vyzkoušel podle přesného názvu i UID.

Skutečné vypnutí přenosu jsem kontroloval přes log uzavřeného spojení a otevřené
TCP sockety. Po vypnutí nezůstával hlavnímu procesu náhledu otevřený kamerový
přenos. Tím se liší vypnutí obrazu od pouhého skrytí videa.

Na své tiskárně jsem označil obraz za plynulý při 15 FPS a později také při 10 FPS.
Vyzkoušel jsem požadavek na akceleraci WebKitu v režimu on. Log potvrzuje nastavenou
politiku, ale nemám z něj důkaz o hardwarovém dekódování MJPEG.

## Jak chápu měření

Krátké výpisy top mi pomohly při ladění, nepovažuji je ale za řízený benchmark.
Proto konkrétní procenta CPU nepoužívám jako slib úspory pro jinou tiskárnu.

FPS v menu počítám z přijatých a předaných celých snímků. Údaj Předáváno není
měřením skutečného vykreslení WebKitu. Log přepnutí limitu dokládá přijetí volby,
sám o sobě nedokládá změnu toku snímků.

## Co ověřují automatické kontroly

Kontroly zahrnují konfiguraci a překlady, vytváření služby, skutečný MJPEG přenos,
zavření spojení, omezení FPS, změnu limitu bez nového spojení a nezávislého druhého
klienta. Browser testy kontrolují rozložení menu, vlastní limit, překlady, dlouhé
názvy a chování vypnutí/zapnutí. Linux CI ověřuje systemd jednotku.

Výsledek vydání zaznamenávám v [RELEASE_CHECKS.md](../RELEASE_CHECKS.md).

## Co nechávám k dalšímu ověření

Nemám vyzkoušené všechny motivy, kamery, grafické ovladače ani všechny kombinace
výpadků a souběžných klientů. Nové překlady potřebují jazykovou kontrolu a část
RTL/CJK vykreslení stále vyžaduje praktické ověření na displeji.

U nového rozložení menu a čítačů nepovažuji samotný browser test za zkoušku všech
situací na GTK/WebKitu v RPi. Podobně si ponechávám samostatnou kontrolu správy
služby přes Moonraker. Společné probouzení a okamžité obnovení obrazu jsem ověřil na svém RPi,
včetně restartu. Podrobnosti jsou v [návodu k uspávání](RPI_SLEEP.cs.md).

Vlastní kontrolní postup je v [TESTING.cs.md](TESTING.cs.md).
