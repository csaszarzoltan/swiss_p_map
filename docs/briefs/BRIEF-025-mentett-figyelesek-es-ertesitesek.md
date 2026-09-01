# BRIEF-025: Mentett Figyelési Zónák és Építési Értesítések

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-025  
**Forrás:** kutatás, competitor scan és felhasználói igény

## Probléma
A felhasználó jelenleg csak akkor észlel új építési kérelmet, ha ismételten megnyitja az alkalmazást és újrakeresi a környéket.

## Célcsoport és kontextus
Lakók, tulajdonosok és ingatlanvásárlók, akik egy cím vagy sugár körüli új Baugesuchokat a 20 napos jogi ablakon belül szeretnék észlelni.

## Kívánt eredmény
A felhasználó menthet egy figyelési zónát, értesítési csatornát és gyakoriságot; új releváns rekordnál deduplikált, forráshivatkozásos értesítést kap.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek
- **US-025-01:** Felhasználóként szeretném elmenteni az aktuális cím és sugár kombinációját figyelési zónaként.
- **US-025-02:** Felhasználóként szeretném kiválasztani, milyen gyakran és mely csatornán kapjak értesítést.
- **US-025-03:** Felhasználóként szeretném szüneteltetni vagy törölni a figyelést.
- **US-025-04:** Felhasználóként szeretném, hogy ugyanarról a projektről ne kapjak ismétlődő értesítést, és kieső adatforrás esetén lássam a késést.

## Scope
- Mentett zóna, csatorna, gyakoriság, consent, deduplikáció és kézbesítési napló.
- Az ADR-018 térbeli keresés és ADR-002/009 ingestion új rekordjainak összekapcsolása.

## Non-scope
- Jogi képviselet, automatikus kifogásbenyújtás és marketingüzenetek.

## Érintett rendszerek
- tervezett backend watcher/notification service
- planning_repo és radius engine
- tervezett frontend watch management UI
- e-mail vagy push szolgáltató

## Bizonytalanságok
- Felhasználói azonosítás, nFADP/GDPR hozzájárulás, kézbesítési szolgáltató és freemium korlátok külön research/ADR döntést igényelnek.
