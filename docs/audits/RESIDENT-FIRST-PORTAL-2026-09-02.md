# Resident-first portal audit

## Változás
A kezdőlap információs hierarchiája OpenBorough-szerű, témaközpontú irányba változott. A térkép külön „Räumliche Analyse und Karte” szakaszba került, míg előtte egy hat témából álló helyi briefing jelenik meg.

## Témák
Demokrácia, környezet, időjárás, lakhatás, mobilitás és tervezés. Minden elem forrást, fontosságot és opcionális térképréteget tartalmaz.

## Hír-integritás
A megoldás nem generál hamis aktuális híreket. Az élő provider nélküli időjárás/hír tartalom `source_pending` állapotú. Az éles híraggregátor kötelező metaadatait a `docs/product/RESIDENT-FIRST-INFORMATION-ARCHITECTURE.md` rögzíti.

## Tesztek
- Új célzott unit és API tesztek: 3 passed.
- SPEC validator: 44 SPEC, 100% strukturális coverage.
- Teljes pytest a sandboxban 81 passed / 19 failed, kizárólag a hiányzó `pytest-asyncio` plugin miatt. Az új tesztek zöldek.
- A bemeneti ZIP nem tartalmaz `.git` metaadatot, ezért commit/push nem hajtható végre.
