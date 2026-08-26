# ADR-004: 4 nyelvű i18n — next-intl App Router (de/en/fr/it)

- **Dátum:** 2026-08-26
- **Státusz:** accepted (2026-08-26 — „folytasd a legjobb véleményed szerint” + programozott folytatás)
- **Szerző:** analyst (research: `docs/research/2026-08-26-i18n-4lang.md`)
- **Kanban:** i18n-pillér (Planning után)

## Kontextus

FE: Next.js 14.2.35 App Router, nincs i18n (`layout lang="en"` hardcode, page német). Követelmény: **de/en/fr/it** (CH 3 + EN), URL-prefix (`/de`, `/fr` …), `Accept-Language` detektálás, SEO `hreflang`+`canonical`+`x-default`+`sitemap`, `<html lang>` dinamikus. Next App Routerben nincs beépített i18n routing — middleware + `[locale]` kell.

## Döntés

**A: `next-intl` 3.26.x (stabil Next14) / 4.13.x (aktuális) → 4.75/5 nyert.**

- `routing: { locales:['de','en','fr','it'], defaultLocale:'de', localePrefix:'always', localeDetection:true }`
- `app/[locale]/layout.tsx` (`setRequestLocale`, `<html lang>`), `messages/{de,en,fr,it}.json` (de teljes, többi fallback), `i18n/request.ts` + `i18n/routing.ts`, `middleware.ts` matcher `['/', '/(de|en|fr|it)/:path*', '/((?!api|_next|_vercel|.*\\..*).*)']`, `next.config.mjs` `createNextIntlPlugin('./i18n/request.ts')`, `generateMetadata` → `alternates.languages` + `canonical`, `app/sitemap.ts` per-locale alternates.
- Migráció: `3.26.5` konzervatív (bőven tesztelt 14-en) vagy `4.13.7` — mindkettő `peer ^14`; 4.x esetén új `routing` API.

## Elvetve

| Opció | Miért nem |
|---|---|
| B: next-i18n-router + i18next | routing OK de 2 lib + glue, SEO/format kézi, kisebb közösség |
| C: custom [locale] dictionary | 0 dep de 80–150 sor middleware + ICU/hreflang kézzel, törékeny |

## Következmény

- Kártyák: `feat: i18n scaffold (next-intl, de/fr/it/en)` → middleware + [locale] áthelyezés → messages + nyelvkapcsoló → E2E locale/hreflang
- Developer: max 400 sor/file, minden belső `Link` → i18n API-ra, `localePrefix always` → CDN cache kulcs = URL
- Validálás: `npm run build` zöld, `npx playwright test` 3/3 + locale prefix + `x-default` + sitemap hreflang

## Kapcsolódó

- Research: `docs/research/2026-08-26-i18n-4lang.md`
- Kód: `frontend/middleware.ts`, `frontend/i18n/*`, `frontend/app/[locale]/*`, `frontend/messages/*`
- Következő ADR: ADR-005 (élő Politics+Place)
