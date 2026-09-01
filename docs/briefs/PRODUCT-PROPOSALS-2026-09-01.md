# Termékfejlesztési javaslatok és új Feature Brief-ek

**Dátum:** 2026-09-01  
**Módszertan:** RVAD 1.1  
**Bővítés:** BRIEF-034–BRIEF-043

## Stratégiai irányok

1. **Döntéstámogatás és ingatlanpiac:** hivatalos ártrendekkel és összehasonlítható idősort mutató BRIEF-034.
2. **Klíma- és rezilienciaréteg:** természeti veszélyek, mikroklíma, levegőminőség és hosszú távú klímakitettség a BRIEF-035, 037 és 040 keretében.
3. **Helyi identitás és szabályozási kontextus:** ISOS örökségvédelmi réteg a BRIEF-036-ban.
4. **Mindennapi szolgáltatási hozzáférés:** oktatás, egészségügy és digitális infrastruktúra a BRIEF-038, 041 és 042-ben.
5. **Planningből cselekvéstámogatás:** forrásolt, de nem jogi tanácsadást végző ügy-munkatér a BRIEF-039-ben.
6. **Dekarbonizáció és felújítás:** épületenergetikai kontextus és hivatalos támogatási utak a BRIEF-043-ban.

## Prioritási javaslat

- **P0 kutatásra:** BRIEF-035 természeti veszélyek, BRIEF-034 ártrendek, BRIEF-036 ISOS. Ezek erősen illeszkednek a meglévő térképi és ingatlan-döntéstámogató maghoz.
- **P1:** BRIEF-037 mikroklíma, BRIEF-038 oktatás, BRIEF-043 épületenergetika.
- **P2:** BRIEF-040 levegő/pollen, BRIEF-041 egészségügyi elérhetőség, BRIEF-042 digitális elérhetőség.
- **Magas kockázatú külön discovery:** BRIEF-039, mert eljárási és adatvédelmi kérdéseket érint, ezért fejlesztés előtt kötelező research, jogi review és ADR.

## Architekturális illeszkedés

Az új képességek közös provider-adapter mintával illeszkedhetnek a FastAPI szolgáltatási réteghez, egységes provenance/frissesség metaadatokkal a BRIEF-029 szerint. A térképi rétegek a meglévő Map3D témamotorra, a MapLegend komponensre és a DetailPanelre épülhetnek. Nagy raszteres adatoknál tile-proxy/cache, kantonális eltéréseknél capability registry szükséges.

## RVAD kapuk

Minden új brief `READY_FOR_SPEC`, de egyik sem tekintendő fejlesztésre jóváhagyott specifikációnak. Következő lépésenként research és adatkontraktus-validáció, szükség szerint ADR, majd a 14 pontos SPEC, REQ/AC traceability, RED tesztbizonyíték és csak ezután BUILD szükséges.
