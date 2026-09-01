# BRIEF-022: Építési Kockázatjelzés és „Miért?” Indoklás

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** ADR-020  
**Forrás:** meglévő kód és ADR-020

## Probléma
A Planning találatok azonos súllyal jelennek meg, ezért a felhasználó nehezen azonosítja a sürgős vagy környezetileg érzékeny projekteket.

## Célcsoport és kontextus
Szomszédok, ingatlanvásárlók és szakmai elemzők, amikor rövid idő alatt sok építési találatot értékelnek.

## Kívánt eredmény
Minden értékelt projektnél determinisztikus low, medium vagy high jelzés és emberileg olvasható indoklás jelenik meg, félrevezető jogi minősítés nélkül.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-022-01:** Felhasználóként szeretném színnel és szöveggel látni egy projekt kockázati szintjét.
- **US-022-02:** Felhasználóként szeretném megnyitni a „Miért?” indoklást, hogy értsem a besorolás alapját.
- **US-022-03:** Felhasználóként szeretném, hogy hiányos adat esetén a rendszer ne adjon bizonytalan magas kockázati állítást.
- **US-022-04:** Képernyőolvasós felhasználóként szeretném a kockázati szintet színtől függetlenül is érzékelni.

## Scope
- RiskBadge megjelenítés és lokalizált indoklás.
- Determinisztikus, auditálható szabályok a rendelkezésre álló zóna- és határidőadatokból.

## Non-scope
- Jogi tanácsadás, automatikus fellebbezés vagy LLM-alapú kockázati döntés.

## Érintett rendszerek
- frontend/src/components/RiskBadge.tsx
- frontend/src/components/DetailPanel.tsx
- src/models/planning.py
- src/services/planning_service.py

## Bizonytalanságok
- A jelenlegi heurisztika jogi elnevezése és felelősségi nyilatkozata; kantonális szabályok egységesíthetősége.
