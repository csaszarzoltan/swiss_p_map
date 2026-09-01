# BRIEF-035: Természeti Veszélyek: Árvíz, Felszíni Lefolyás, Lavina és Földcsuszamlás

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-035  
**Forrás:** BAFU/FOEN országos és kantonális veszélytérképek, SLF lavinaadatok és Swisstopo domborzat

## Probléma

Egy ingatlan környezeti kockázata nem ítélhető meg pusztán zaj-, közlekedési és zónaadatokból; az árvíz, felszíni lefolyás, csuszamlás, kőhullás és lavina eltérő forrásokban található.

## Célcsoport és kontextus

Lakástulajdonosok, vásárlók, tervezők, önkormányzatok és biztosítási szakemberek, amikor helyszíni kitettséget vagy építési korlátozást vizsgálnak.

## Kívánt eredmény

Egységes, rétegenként kapcsolható 2D/3D kockázati nézet jelenik meg veszélytípussal, veszélyfokkal, intenzitással, valószínűséggel, forrással és jogi státusszal.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-035-01:** Ingatlanvásárlóként szeretném egy címnél látni az elérhető természeti veszélyrétegeket, hogy felismerjem a további szakértői vizsgálat szükségességét.
- **US-035-02:** Tervezőként szeretném veszélytípusonként be- és kikapcsolni a rétegeket, hogy ne fedjék el egymást.
- **US-035-03:** Felhasználóként szeretném, hogy hiányzó vagy nem harmonizált kantonális adat esetén a rendszer ezt egyértelműen jelezze, és ne értelmezze a hiányt veszélytelenségként.
- **US-035-04:** Színlátási nehézséggel élő felhasználóként szeretném a veszélyfokot mintázattal, felirattal és hozzáférhető jelmagyarázattal is érzékelni.

## Scope

- BAFU felszíni lefolyás és országos tájékoztató rétegek.
- Kantonális árvíz-, csuszamlás-, kőhullás- és lavinaveszély provider-adapterek.
- SLF aktuális lavinabulletin külön, időbélyegzett operatív információként.
- Forrás, adatdátum, harmonizáltság és jogi kötelező erő megjelenítése.

## Non-scope

- Biztosítási díjszámítás, hivatalos építési engedélyezési döntés vagy személyre szabott vészhelyzeti utasítás.

## Érintett rendszerek

- tervezett hazard provider réteg és cache
- frontend Map3D hazard overlay és legend
- kantonális geoportál adapterek
- BAFU, SLF és Swisstopo szolgáltatások

## Bizonytalanságok

- A kantonális veszélytérképek felbontása és licence eltér; az országos felszíni lefolyási térkép nem jogilag kötelező, és helyszíni plausibility check nélkül nem használható végleges döntésre.
