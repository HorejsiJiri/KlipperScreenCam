# Stav ověření — 0.3.0

Datum: 2026-11-22. Výsledky cílového nasazení jsou oddělené od místních testů.

## Potvrzeno na cílovém RPi

Raspberry Pi 5 Model B Rev 1.0, Debian 13.8 Trixie, X11,
dva HDMI dotykové displeje 1024 × 600, rozšířená plocha 2048 × 600.

- Uživatel potvrdil obraz, ovládání a automatický start samostatné služby.
- Zachováno rozložení displejů a mapování obou dotyků.
- Výchozí kamera funguje podle přesného názvu i UID z Moonrakeru.
- Vypnutí obrazu uzavírá přenos: doložen log uzavření a žádné TCP spojení hlavního
  procesu. V krátkém vzorku celková zátěž klesla přibližně z 15 % na 2 %.
- Nastavení akcelerace on bylo načteno a aplikace pokračovala v provozu.
  Log potvrzuje požadovanou politiku, nikoli skutečné GPU dekódování.
- Verze 0.2.3 s max_fps = 15 byla nasazena; uživatel výslovně potvrdil plynulý obraz.

## Orientační CPU měření

Cam1, zapnutá politika akcelerace, jednosekundové vzorky top před/po místním limitu:

| Metrika | Předchozí limit 30 FPS | Limit 15 FPS |
|---|---:|---:|
| WebKit, % jednoho jádra | 23,8 | 17,8 |
| Python náhledu, % jednoho jádra | 6,9 | 5,9 |
| Crowsnest Cam1, % jednoho jádra | 10,9 | 12,9 |
| Celý CPU, % všech jader | 12,5 | 11,5 |

Nejde o dlouhodobý řízený benchmark. Vzorky naznačují snížení práce WebKitu;
nelze z nich slibovat konkrétní úsporu na jiném zařízení. Crowsnest dodává původní
stream, proto se jeho zátěž místním limitem přímo nesnižuje.

## Místní kontroly

- Konfigurace, jazyky, výchozí kamera, GTK nastavení a generování služby.
- 32 jazykových variant, regionální aliasy, RTL metadata, JSON klíče a fallback.
- Reálný nepřetržitý MJPEG server: skutečné zavření spojení a zastavení bajtů,
  staré adresy, přepnutí kamery, limit snímků, zachování JPEG dat,
  fragmentované části bez Content-Length a nezávislý druhý klient.
- Browser testy: výběr, pauza, zapnutí výběrem, jedna kamera, dlouhé názvy,
  posun, motiv bez restartu streamu, kurzor, bezpečné názvy a jazyky/RTL.

Aktuální počet kontrol je v [RELEASE_CHECKS.md](../RELEASE_CHECKS.md).
Windows přeskakuje skutečné systemd ověření; to spouští Linux CI.

## Zbývá ověřit

- Všech 30 nových překladů rodilými mluvčími, veškeré CJK/RTL fonty na RPi.
- Všechny motivy, dlouhodobé výpadky, tiché zastavení kamery a souběhy klientů.
- Zhasnutí/probuzení obou výstupů. DPMS sám nepozastavuje přenos.
- Skutečnou GPU aktivitu a dlouhodobé CPU srovnání.
- Moonraker správu služby podle nového návodu na cílové instalaci.

Podrobnosti: [TESTING.cs.md](TESTING.cs.md), [FPS.cs.md](FPS.cs.md).

## Nové v 0.2.4

Přepínání limitu v menu a unlimited byly ověřeny místními testy skutečného přenosu
a rozhraní. Nové ovládání zatím není ověřeno na cílovém GTK/WebKit. Výše uvedené
výsledky RPi patří předchozí verzi 0.2.3.

## Diagnostika 0.2.5

Log RPi potvrdil přijetí unlimited, 10, 20 a 30 z menu. To samo neprokazuje změnu FPS.
Nové počítadlo zdroje a předaných snímků čeká na ověření na RPi. Reálný místní
server a test všech voleb potvrdily změnu počtu předaných snímků na stejném spojení.

## Vzhled menu 0.3.0

Nové pořadí, ikona a barva ovládání obrazu, vlastní řazené předvolby, rozměry a
zarovnání tlačítek byly zkontrolovány browser testem i náhledem. Nové rozložení
a ovládání vlastní hodnoty limitu na cílovém RPi ještě nejsou potvrzené.
