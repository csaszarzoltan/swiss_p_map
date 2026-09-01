# BRIEF-032: Országos Kantonális Adóverseny és Steuerfuss Hőtérkép

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-032  
**Forrás:** a Svájci Szövetségi Adóhivatal (ESTV - Eidgenössische Steuerverwaltung) hivatalos adóterhelési statisztikái, a kantonális adóhivatali mutatók és a 3D térképi hőtérkép motor alapján

## Probléma

Svájcban a kantonok és az önkormányzatok közötti adóterhelés (Steuerfuss / Steuerbelastung) drasztikusan eltér: egy család vagy cég adóterhe Zugban vagy Schwyzben akár fele vagy harmada lehet a berni, genfi vagy neuchâteli adóknak. A jelenlegi rendszerben a felhasználó csak egyedi kereséssel látja a zürichi adókulcsot, nem tudja egy pillantással átlátni a híres svájci "adóparadicsomok" és a magasabb adójú kantonok országos eloszlását.

## Célcsoport és kontextus

Költözést tervező magánszemélyek, expatok, svájci munkavállalók, cégalapítók és vagyontervezők.

## Kívánt eredmény

Egy dedikált **"Steuer / Impôts / Tax"** tematikus réteg és országos adó-hőtérkép a 3D térképen:
1. **Adó-hőtérkép:** A kantonok 3D színezése a kantonális adókulcsindex alapján (smaragdzöld/arany = rendkívül kedvező, pl. Zug 54%, Schwyz 60%, Nidwalden 65%; kék = középmezőny, pl. Zürich 119%, Luzern, St. Gallen; korall/vörös = magasabb adóterhelés, pl. Bern 154%, Genf, Jura).
2. **Kantonális Adóprofil Kártya:** Bármely kantonra vagy településre kattintva megjelenik a kombinált (Kanton + Gemeinde + Szövetségi közvetlen adó) effektív index és a szomszédos kantonokhoz viszonyított helyezés (pl. *"Kanton Zug · Rang: #1 Svájcban · Átlagos Steuerfuss: 54%"*).
3. **Interaktív Adókalkulátor Miniatűr:** Becsült éves adómegtakarítás kalkuláció a kiválasztott referencia-településhez képest.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-032-01:** Felhasználóként az "Adó" (Steuer) témára kattintva azonnal látni szeretném Svájc 26 kantonjának színkódolt adó-hőtérképét.
- **US-032-02:** Felhasználóként egy kanton (pl. Schwyz vagy Vaud) fölé mozgatva az egeret szeretném látni az átlagos kantonális adókulcsot és az országos rangsort.
- **US-032-03:** Felhasználóként egy konkrét települést (pl. 6300 Zug vs. 8004 Zürich vs. 3011 Bern) kiválasztva látni szeretném az adott település pontos adókulcsát és a kantonális átlagtól való eltérést.
- **US-032-04:** Rendszerként szeretném, hogy az ESTV hivatalos adóadatai strukturált JSON formátumban álljanak rendelkezésre a `GET /api/v1/tax/cantons` és `GET /api/v1/tax/compare` végpontokon.

## Scope

- ESTV szövetségi és kantonális adóindex adatbázis mind a 26 kantonra (`tax_service.py`).
- REST végpontok: `GET /api/v1/tax/cantons` és `GET /api/v1/tax/{canton_code}`.
- 3D térképi zöld-arany-korall hőtérkép színskála és jelmagyarázat.
- Részletező kártya és összehasonlító mutató a `DetailPanel.tsx` komponensben.

## Non-scope

- Egyéni svájci adóbevallás kitöltése és beküldése a kantonális adóhivatalhoz.

## Érintett rendszerek

- `src/models/tax.py` [ÚJ], `src/services/tax_service.py` [ÚJ], `src/main.py`, `frontend/src/app/Map3D.tsx`, `frontend/src/components/DetailPanel.tsx`

## Bizonytalanságok

- Felekezeti (egyházi) adókulcsok kantononkénti eltérő kötelezősége és kezelése (egyházi adó nélküli alapadókulcs használata egységesen).
