# BRIEF-004: Négynyelvű Nemzeti Hozzáférés és Lokalizáció

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-004 (ADR-004)  
**Forrás:** a `next-intl` keretrendszer, a 4 svájci/nemzetközi nyelv (DE, EN, FR, IT) szótárai és a dinamikus útvonalkezelő alapján

## Probléma

Svájc többnyelvű konföderáció (német, francia, olasz, rétoromán), a nemzetközi befektetők pedig angolul használják a rendszereket. Egy egynyelvű felület kizárja a lakosság és a piaci szereplők jelentős részét.

## Célcsoport és kontextus

Minden svájci állampolgár és nemzetközi érdeklődő a saját anyanyelvén (Deutsch, Français, Italiano, English).

## Kívánt eredmény

Minden felhasználói felület, gomb, keresőmező, információs kártya, hibaüzenet és 3D térképi felirat (iránytű, népszavazási arányok, statisztikák) 100%-ban elérhető és azonnal váltható 4 nyelven (`/de`, `/en`, `/fr`, `/it`).

## Jelenlegi funkciókat lefedő felhasználói történetek

- **US-004-01:** Felhasználóként szeretném a fejlécben lévő nyelvválasztóval egyetlen kattintással átváltani a nyelvet DE, EN, FR és IT között.
- **US-004-02:** Francia vagy olasz felhasználóként szeretném a saját nyelvemen látni a kereső placeholder szövegeket, címkéket és témákat.
- **US-004-03:** Rendszerként szeretném, hogy az URL automatikusan tartalmazza a nyelvi előtagot (`/de/...`, `/fr/...`), és a gyökér URL (`/`) intelligensen átirányítson.

## Scope

- `next-intl` App Router integráció (`[locale]/page.tsx`).
- 4 komplett nyelvi JSON szótár (`messages/de.json`, `en.json`, `fr.json`, `it.json`).
- `LanguageSwitcher` komponens az aktív nyelv kiemelésével.
- Playwright E2E teszt a 4 nyelv integritásának ellenőrzésére.

## Non-scope

- Élő gépi fordító API hívás futásidőben (a szótárak előre ellenőrzöttek és pontosak).

## Érintett rendszerek

- `frontend/src/app/[locale]/`, `frontend/messages/`, `frontend/src/components/LanguageSwitcher.tsx`

## Bizonytalanságok

- Bizonyos kantonális szakkifejezések (pl. Steuerfuss / Coefficient d'impôt / Moltiplicatore d'imposta) pontos szakterületi terminológiája.
