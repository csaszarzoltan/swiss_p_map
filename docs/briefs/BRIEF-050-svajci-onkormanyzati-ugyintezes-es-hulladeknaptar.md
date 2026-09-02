# BRIEF-050: Svájci Önkormányzati Ügyintézés és Hulladéknaptár

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-050  
**Forrás:** OpenBorough City Services modul, a svájci önkormányzati (Gemeinde) gyakorlat, az OGD hulladéknaptárak és a 2026-09-02-i egyeztetés alapján

## Probléma

A svájci hétköznapi életben a helyi polgárok számára az egyik leggyakoribb, elengedhetetlen információ a hulladékszállítási rend (a szigorú szelektív szabályok miatt kantononként és településenként eltérő napokon van karton-, papír-, zöldhulladék- és szemétszállítás). Emellett a költözéskor, átjelentkezéskor vagy ügyintézéskor a lakosok nehezen találják meg a helyi hivatalok pontos határidőit és elérhetőségeit.

## Célcsoport és kontextus

Minden svájci lakos, frissen beköltöző bérlő és ingatlantulajdonos.

## Kívánt eredmény

Egy **Helyi Szolgáltatások és Ügyintézési Központ (*Gemeindedienste & Abfallkalender*)**:
1. **Svájci Hulladéknaptár (Abfallkalender):**
   - Pontos szállítási naptár PLZ szerint: Karton (*Karton*), Papír (*Papier*), Bio/Komposzt (*Grüngut*), Háztartási szemét (*Kehricht*), Veszélyes hulladék / E-hulladék (*Sonderabfall*).
   - Figyelmeztetés a következő szállítási napokra és letölthető iCal/naptár fájl.
2. **Helyi Ivóvíz-minőség & Keménység:**
   - Francia keménységi fok (°fH) és német keménység (°dH) kijelzése.
   - Forrás eredete (forrásvíz, tavi víz, talajvíz) az SVGW adatai alapján.
3. **Önkormányzati Ügyintézés és Határidők:**
   - Lakcímbejelentési határidők (14 napos *Anmeldung* szabály).
   - Parkolási engedélyek (*Blaue Zone Parkkarte*) igénylési linkjei.
   - Helyi önkormányzati közgyűlések (*Gemeindeversammlung*) dátumai és napirendi pontjai.
   - Orvosi és fogorvosi ügyeletek, segélyhívó számok (144, 117, 118, 1414 Rega).

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-050-01:** Helyi lakosként a kezdőlapon azonnal látni szeretném, mikor viszik el a kartont és a papírt a körzetemben.
- **US-050-02:** Új lakóként azonnal látni szeretném a vezetékes ivóvíz keménységét a háztartási gépek és kávéfőzők beállításához.
- **US-050-03:** Polgárként látni szeretném a helyi közgyűlés (Gemeindeversammlung) következő időpontját és napirendjét.

## Scope

- `src/services/municipal_services.py` szolgáltatás.
- `GET /api/v1/municipal/waste-calendar?postcode={postcode}`, `GET /api/v1/municipal/water-quality?postcode={postcode}` végpontok.
- UI widget a `LocalInformationHub.tsx` alatt.

## Non-scope

- Fizetési tranzakciók lebonyolítása a szemétdíjakra (szemeteszsák-matrica értékesítés).

## Érintett rendszerek

- `src/services/municipal_services.py`, `frontend/src/components/LocalInformationHub.tsx`
