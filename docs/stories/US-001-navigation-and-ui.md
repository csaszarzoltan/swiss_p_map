# US-001: 3D Navigáció, Keresés és Felületi Élmény

> **Státusz:** ELKÉSZÜLT / VERIFIKÁLVA  
> **Kapcsolódó ADR-ek:** ADR-003 (3D Svájc-térkép), ADR-004 (4-nyelvű i18n), ADR-010 (Topic pill-tabs & detail panel)  
> **Teszt lefedettség:** `frontend/e2e/app.spec.ts` (7 E2E teszt)

---

## 1. Felhasználói Történet (User Story)

**Mint** svájci lakos vagy érdeklődő állampolgár,  
**Akarom** a svájci körzetek (PLZ / gemeinde) adatait egy interaktív 3D térképen és témakörökre bontott pill-tabokon keresztül áttekinteni,  
**Azért, hogy** gyorsan megtaláljam az építési engedélyeket (Planung), a helyi politikai képviselőket (Politik), valamint a körzeti mutatókat (Zaj, Adókulcs, Solar, ÖREB) a saját anyanyelvemen (DE, EN, FR, IT).

---

## 2. Felületi Folyamat (`gui_flow`)

```
[1. Megnyitás] ───> Svájc 3D térkép megjelenik (26 kanton + városok + N iránytű)
      │
[2. Keresés] ────> Felhasználó beír egy PLZ-t (pl. 8004) VAGY rákattint egy Quick-Pick gombra (pl. 8001 Altstadt)
      │
[3. Eredmény] ───> A 3D térkép és a témaköri pill-tabok jelvényei frissülnek (Politik: 2, Ort: 6, Planung: aktívak)
      │
[4. Témaváltás] ─> Felhasználó kiválaszt egy fület (pl. [🏗 Planung]) ──> TopicList és DetailPanel azonnal frissül
      │
[5. Nyelvváltás]─> Felhasználó átvált nyelvet (pl. EN vagy FR) ──> Minden felirat és URL azonnal lokalizálódik
```

---

## 3. Elfogadási Kritériumok (Acceptance Criteria)

- **AC-1 (3D Térkép & Iránytű):** A Three.js 3D térkép hiba nélkül betöltődik, a kantonok kiemelhetők, az iránytű a nemzetközileg szabványos `N` (Nord/North) betűt mutatja.
- **AC-2 (Nyelvi Konzisztencia):** A 3D térképen és az információs paneleken nem jelenhet meg idegen (nem a kiválasztott locale-nak megfelelő) hardkódolt felirat.
- **AC-3 (Keresés & Quick-Pick):** A keresőmező elfogad 4-jegyű PLZ-t és szabad szöveges címet. A Quick-Pick gombokra (`8004`, `8001`, `8610`, `3011`, `4001`) kattintva a lekérés automatikusan lefut.
- **AC-4 (CORS & Adatkapcsolat):** A frontend portjáról (`http://localhost:3310` vagy `3000`) érkező API lekérések CORS hiba nélkül 200 OK státusszal lefutnak.
- **AC-5 (Reszponzív Header & Témák):** A fejléc tartalmazza a brandinget (Swiss P Map logó), a keresőt és a nyelvválasztót; mobil kijelzőn a vezérlők és kártyák nem takarják ki használhatatlanul a felületet.
