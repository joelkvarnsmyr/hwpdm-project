# Säkringsplan — utkast 2026-09-29

Mål: varje utgångs elektroniska säkring ska skydda **kabeln och kontakten**, släppa igenom lastens **verkliga** ström (även startström och laddspänning 14,4 V) och bete sig rätt vid fel. Värdena ska vara motiverade och kontrollerade av byggskripten.

Det här är ett **utkast**. Kolumnen *Förslag* är preliminär tills mätningen i steg 2 är gjord. Utgångspunkt: det som ligger i PDM:en (v10.25).

## Regler

| Regel | Värde | Varför |
|---|---|---|
| **Tak** | hög säkring ≤ **13 A** per stift (Deutsch, 125 °C) och ≤ kabelns tålighet | Säkringen skyddar kabeln, inte lasten |
| **Hög säkring** | ≈ 1,5 × högsta uppmätta driftström, avrundat | Marginal för 14,4 V (+10 %), värme och slitage |
| **Topp, glödlampa** | 6–8 × driftström, **0,3 s** | Kall glödtråd drar 8–10× i några ms. PDM:en ser inte hela spiken |
| **Topp, LED** | 2 × hög, **0,2 s** | Liten startström |
| **Topp, motor** | ≈ 5 × driftström, **1 s** | Stillastående rotor vid start |
| **Topp, spole/resistiv** | = hög | Ingen startström |
| **Topptid** | **≤ 5 s** (GUI:ts max), i **sekunder** | Värden på 100–5000 är kvar från ms-eran och betyder minuter |
| **Låg säkring** | **0**, utom en-lamps-utgångar där lampfel ska synas (strålkastare) | En underströmsutlösning STÄNGER AV utgången |
| **Trip mode** | Normal | Instant löser ut på glödlampors startström |
| **Omförsök, kritiska** (tändning, pump, broms, blinkers, strålkastare) | 10 = oändligt, paus 0,1–0,5 s | En störning får inte släcka dem för gott |
| **Omförsök, övriga** | 3, paus 2–3 s | |
| **Mjukstart** | bara där den behövs (strålkastare 500 ms enligt Joel) | Ingen nytta på spole, pump eller relä |

## Utgångar

Nu = låg / hög / topp / topptid · försök. **Fet** = problem som finns i dag.

| Utg | Last | Nu | Uppmätt | Förslag | Anmärkning |
|---|---|---|---|---|---|
| O1 BUSBAR | +12V-busbaren? | 0 / 3 / 10 / **1000 s** · 3 | 0,00 A | efter inventering | Matar O1 verkligen busbaren? |
| O2 ALT_EXCITE | 82 Ω till D+ | 0 / 2 / 3 / 0,5 · 2 | **0,22 A** | 0 / 1 / 2 / 0,5 | Över vad 82 Ω släpper igenom (0,16 A). Kolla kopplingen |
| O3 IGN_COIL | tändspole + choke | 0 / 5 / 12 / **1000 s** · 10 | 3,7–4,2 A spetsar slutna, ~2 A i gång | 0 / 7 / 7 / 0,5 · 10 (0,1 s) | Mjukstart på. Onödig, stäng av |
| O4 PARK | parkeringsljus | 0 / 3 / 8 / 0,5 · 2 | 0,5–0,6 A | 0 / 2 / 6 / 0,3 | |
| **O5 FUEL** | bensinpump | **0,8** / 4 / 15 / 2 · 10 | **0,8–1,5 A pulserande**, ~3 A start | **0** / 4 / 10 / 1 · 10 (0,1 s) | **Låg säkring 0,8 A kan stänga av pumpen, och då dör motorn.** Stäng av den |
| **O6 BRAKE** | 2 × 21 W + ev. främre gren | 0 / 5 / 10 / **100 s** · 3, **Instant** | ej mätt | Normal, 0 / 6 / 25 / 0,3 · 10 | **Instant + glödlampor kan lösa ut bromsljuset** |
| O7, O16 HIBEAM | H4 60 W | 1 / 5,8 / 35 / 0,3 · 2 | ~4,6 A (autotune) | 1 / 7 / 35 / 0,3 · 10 | Mjukstart 500 ms behålls |
| O14, O15 LOWBEAM | H4 55 W | 1 / 5,9 / 35 / 2 · 2 | ~4,7 A (autotune) | 1 / 7 / 35 / 0,3 · 10 | Mjukstart 500 ms behålls |
| O10 WIPER_SLO | torkarmotor | 0 / 7 / 12 / 1 · 2 | ej mätt | mät | Finns torkaren? |
| O11 BLOWER | fläktmotor | 0 / 8 / 20 / 5 · 2 | 4,1–4,3 A vid 100 % | 0 / 8 / 20 / **1** · 3 | Fungerar. Kortare topptid räcker |
| O12 WASHER | spolarpump | 0 / 5 / 8 / **2000 s** · 2 | 0,01 A | mät | Är pumpen inkopplad? |
| O13 HORN | eltuta | 0 / **13** / 50 / 1 · 2 | ej mätt | troligen 0 / 8 / 20 / 0,5 | Hög säkring på stiftets gräns |
| O17 HORN_2 | kompressortuta | 0 / 5 / 10 / 1 · 2 | ej mätt | mät | Kompressor 10–20 A → troligen relä |
| O20 RADIO_ACC | radio? | 0 / 7 / 7 / **5000 s** · 2, **Instant** | 0,00 A | efter inventering | Radion kan sitta på busbaren |
| O23 STARTER | startrelä kl.50 | 3 / 7,4 / 22,1 / 0,1 · 2 | ej mätt | mät under start | Indragningslindning drar mycket en kort stund |
| O24, O25 TURN | blinkers LED | 0 / 2 / 5 / **100 s** · 2 | ej mätt | 0 / 2 / 5 / 0,2 · 10 | Dubbla stift. Säkerhetskritisk → oändliga försök |

## Steg

1. **Utkast** (detta dokument).
2. **Mätning, ca 15 min.** `python3 /tmp/fuse_survey.py 900` på Pi:n. Motorn på ~2000 rpm så att generatorn laddar. Slå på varje funktion i tur och ordning, minst 10 s var:
   parkeringsljus → halvljus → helljus → blinkers vänster/höger → varningsblinkers → broms (någon trampar) → torkare → spolare → tuta → kompressortuta → fläkt 1/2/3 → radio. Avsluta med en motorstart (startreläet).
   Skriptet ger medel, p95 och max per utgång och loggar varje utlösning.
3. **Förslag → bygge.** Jag fyller i tabellen med uppmätta värden, Joel granskar, jag bygger.
4. **Regler i build_lib.** Samma kontroll som CAN-filtret: varje bygge stoppas om en regel bryts, till exempel hög > 13 A, topptid > 5 s eller låg säkring på O3/O5.
