# BRIEF-059: Heti Helyi Körzeti Értesítő és E-mailes Hírlevél Generátor

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-059  
**Forrás:** 3. Opció (Heti Helyi Értesítő & Értesítési Rendszer), OpenBorough Newsletter koncepció és a `SPEC-045` specifikáció alapján

## Probléma

A legtöbb lakos nem látogatja meg naponta a helyi hivatali vagy térinformatikai weboldalakat, emiatt lemarad a közvetlen környezetét érintő fontos határidőkről (pl. 20 napos építési észrevételi ablak, népszavazási vasárnap, kartonszállítási nap, helyi önkormányzati közgyűlés). Szükség van egy automatizált, kéretlen reklámoktól mentes, heti egyszeri e-mailes helyi összefoglalóra.

## Célcsoport és kontextus

Minden elfoglalt helyi polgár, család, bérlő és ingatlantulajdonos, aki heti 2 percben szeretne képben lenni a lakóhelye történéseivel.

## Kívánt eredmény

Egy heti rendszerességű **„Körzeti Értesítő” (*Wöchentliches Quartier-Briefing*)** e-mail szolgáltatás:
1. **Személyre Szabott Heti Hírlevél Generálás (Minden Péntek Reggel):**
   - **Építkezések:** A héten megjelent új építési kérelmek (*Baugesuche*) az adott PLZ-n vagy a mentett figyelési zónán belül.
   - **Közeledő Határidők:** Észrevételezési határidők lejárata a következő 7 napban.
   - **Demokrácia:** Közelgő szavazások összefoglalója vagy a legutóbbi szavazási eredmények.
   - **Hulladékrend:** A következő hét szállítási napjai (Karton, Papír, Zöldhulladék).
   - **Helyi Hírek:** A hét 3 legfontosabb kantonális/önkormányzati határozata.
2. **Kettős Opt-In és Egyszerű Feliratkozás (*Double Opt-In & 1-Klick Abmeldung*):**
   - Feliratkozás mindössze e-mail cím és PLZ megadásával (nem kötelező teljes regisztráció).
   - Megerősítő e-mail küldése és egykattintásos leiratkozási link a hírlevél alján (GDPR és svájci nDSG kompatibilis).
3. **Reszponzív, Letisztult HTML E-mail Sablon:**
   - Swiss Design tipográfia, dark/light mód kompatibilis elegáns layout.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-059-01:** Lakosként fel szeretnék iratkozni a Zürich 8004 heti pénteki összefoglalójára, hogy ne maradjak le a környékem változásairól.
- **US-059-02:** Feliratkozóként egy tiszta, áttekinthető e-mailben szeretném látni a jövő heti kartonszállítás napját és a környékemen induló építkezéseket.
- **US-059-03:** Felhasználóként egyetlen kattintással le szeretnék tudni iratkozni bármikor.

## Scope

- `src/services/newsletter_service.py` szolgáltatás és háttér-generátor.
- `POST /api/v1/newsletter/subscribe`, `GET /api/v1/newsletter/confirm`, `POST /api/v1/newsletter/unsubscribe` végpontok.
- Tranzakciós e-mail küldő adapter (SMTP / Resend / SendGrid / Postmark).

## Non-scope

- Marketing célú hirdetések vagy harmadik felek reklámjainak kiküldése.

## Érintett rendszerek

- `src/services/local_information_service.py`, `src/services/newsletter_service.py`, `frontend/src/components/LocalInformationHub.tsx`
