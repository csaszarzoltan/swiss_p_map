# BRIEF-028: Körzetek Összehasonlítása és Statisztikai Elemzés

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-028  
**Forrás:** meglévő Place, Politics és Planning adatokból levezetett termékigény

## Probléma
A felhasználó jelenleg egy körzetet vizsgál egyszerre, ezért több lakóhely- vagy befektetési alternatíva összevetése kézi jegyzetelést igényel.

## Célcsoport és kontextus
Lakáskeresők, családok, befektetők és önkormányzati elemzők, akik két vagy több svájci körzet között döntenek.

## Kívánt eredmény
A felhasználó 2-5 körzetet egy egységes, forrásolt és azonos mértékegységű összehasonlító nézetben lát, hiányzó adatok korrekt jelzésével.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-028-01:** Felhasználóként szeretnék 2-5 körzetet egy összehasonlító listához adni.
- **US-028-02:** Felhasználóként szeretném egymás mellett látni az adót, zajt, ÖV-t, napenergiát és Planning aktivitást.
- **US-028-03:** Felhasználóként szeretném rendezni vagy szűrni az összevetést egy kiválasztott mérőszám szerint.
- **US-028-04:** Felhasználóként szeretném, hogy eltérő évből vagy hiányos forrásból származó értékeket a rendszer ne rangsoroljon félrevezetően.

## Scope
- 2-5 körzet kiválasztása, normalizált mérőszámok, forrás és frissesség.
- Megosztható vagy exportálható összehasonlító állapot kapcsolódása BRIEF-020/024-hez.

## Non-scope
- Automatikus ingatlanvásárlási ajánlás vagy személyre szabott pénzügyi tanácsadás.

## Érintett rendszerek
- frontend összehasonlító nézet
- src/services/place_service.py
- planning és politics API-k
- export szolgáltatás

## Bizonytalanságok
- A normalizálás módszere, eltérő kantonális definíciók és súlyozott összpontszám használata research/ADR döntést igényel.
