# BRIEF-039: Építési Észrevétel- és Fellebbezési Munkatér

**Státusz:** READY_FOR_SPEC  
**Kapcsolódó feature:** FEAT-039  
**Forrás:** Hivatalos kantonális építési eljárási tájékoztatók, Amtsblatt-hirdetmények és felhasználói igény

## Probléma

A rendszer megmutatja az építési kérelmet és a határidőt, de a lakos nem kap strukturált segítséget a tények, források, kérdések és saját észrevételei rendezéséhez.

## Célcsoport és kontextus

Érintett lakosok, tulajdonosi közösségek és civil szervezetek a nyilvános betekintési vagy észrevételezési időszak alatt.

## Kívánt eredmény

Forrásolt ügy-munkatér jön létre határidővel, dokumentum-checklisttel, személyes jegyzetekkel és szerkeszthető, általános levélvázzal, egyértelmű jogi felelősségkizárással.

## Jelenlegi / Tervezett funkciókat lefedő felhasználói történetek

- **US-039-01:** Érintett lakosként szeretném egy ügyben összegyűjteni a hivatalos hirdetményt, zónaadatot és határidőt, hogy ne veszítsek el fontos információt.
- **US-039-02:** Felhasználóként szeretnék semleges kérdés- és levélvázlatot generálni kizárólag az általam kiválasztott tényekből, hogy könnyebben egyeztessek a hatósággal.
- **US-039-03:** Felhasználóként szeretném, hogy hiányzó joghatóság vagy bizonytalan határidő esetén a rendszer ne adjon jogi következtetést, hanem a hivatalos szervhez irányítson.
- **US-039-04:** Képernyőolvasós és billentyűzetes felhasználóként szeretném a checklistet, szerkesztőt és exportot teljesen bejárni.

## Scope

- Ügy-munkatér, forráslista, határidő-checklist és privát jegyzet.
- Tényalapú, szerkeszthető kommunikációs vázlat és PDF/ODT export.
- Kanton- és községspecifikus hivatalos tájékoztató link, felelősségkizárás.

## Non-scope

- Jogi tanácsadás, automatikus benyújtás, joghatályos dokumentum garantálása, ügyvédi képviselet vagy hatósági portál automatizált kitöltése.

## Érintett rendszerek

- tervezett case_workspace service és privát adattár
- frontend case workspace és document editor
- Planning/ÖREB/ISOS forráskapcsolatok
- hivatalos kantonális eljárási oldalak

## Bizonytalanságok

- A határidők és formai követelmények kantononként eltérnek; adatvédelem, helyi tárolás, hitelesítés és a generált szöveg jogi korlátai külön magas kockázatú SPEC/ADR döntést igényelnek.
