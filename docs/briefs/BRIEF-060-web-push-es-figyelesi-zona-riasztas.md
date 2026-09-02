# BRIEF-060: Böngészős Web Push és Figyelési Zóna Riasztási Rendszer

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-060  
**Forrás:** 3. Opció (Heti Helyi Értesítő & Értesítési Rendszer), W3C Push API / Web Push szabvány és a `SPEC-025` specifikáció alapján

## Probléma

A svájci építésügyi eljárásokban a nyilvános észrevételezési határidő (*Einsprachefrist*) mindössze **20 nap**. Ha a közvetlen szomszédban vagy 500 méteren belül új építkezést jelentenek be, a szomszédok gyakran csak akkor szembesülnek vele, amikor a munkagépek már megérkeztek. Azonnali, valós idejű riasztásra van szükség, amint egy új építési kérelem megjelenik a mentett figyelési zónán (Watch Zone) belül.

## Célcsoport és kontextus

Közvetlen szomszédok, lakástulajdonosok, bérlők és építésügyi szakértők, akik azonnal tudni akarnak a környezetükben induló építkezésekről.

## Kívánt eredmény

Egy modern, anonim Web Push riasztási rendszer:
1. **1-Kattintásos Böngészős Push Engedélyezés (*Web Push Notification*):**
   - VAPID kulcsos, titkosított böngészős Push Notification (Chrome, Safari iOS/macOS, Firefox, Edge).
   - Felhasználói fiók vagy e-mail cím nélküli, teljesen anonim működés (Device Token alapú).
2. **Figyelési Zóna (Watch Zone) Trigger:**
   - Amint a napi Amtsblatt szinkronizáció új *Baugesuch*-ot talál a felhasználó által beállított koordináta és sugár (300m, 500m, 1000m, 2000m) metszetében:
     - Push értesítés küldése: pl. *„Új építési kérelem 350m-re tőled: Hardstrasse 12 — 20 nap van észrevételre!”*.
3. **Mélylink az Építési Adatlapra & Észrevétel Munkatérbe:**
   - Az értesítésre kattintva a böngésző közvetlenül a projekt adatlapjára és a `SPEC-039` Einsprache Workspace-re ugrik.
4. **MeteoSwiss Extrém Viharriasztás Opcionális Push:**
   - 4-es vagy 5-ös szintű súlyos vihar- és árvízriasztások esetén push értesítés küldése a zónára.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-060-01:** Ingatlantulajdonosként szeretnék push értesítést kapni a telefonomra, ha 500 méteren belül új építkezést jelentenek be a hivatalos közlönyben.
- **US-060-02:** Felhasználóként regisztráció és jelszó nélkül, egyetlen gombnyomással szeretném bekapcsolni a push riasztást a mentett zónámra.
- **US-060-03:** Értesítést kapva a telefonomon egy kattintással meg akarom nézni az építési terveket és a lejárati határidőt.

## Scope

- `src/services/web_push_service.py` szolgáltatás (VAPID, `pywebpush` titkosítás).
- `POST /api/v1/push/subscribe`, `POST /api/v1/push/unsubscribe` végpontok.
- Service Worker `frontend/public/sw.js` push eseménykezelő (`push` és `notificationclick`).
- `WatchZone.tsx` UI vezérlő a push engedélyezéséhez.

## Non-scope

- SMS küldés (csak ingyenes Web Push értesítés).

## Érintett rendszerek

- `src/services/web_push_service.py`, `src/services/planning_service.py`, `frontend/public/sw.js`, `frontend/src/components/WatchZone.tsx`
