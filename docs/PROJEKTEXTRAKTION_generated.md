# ELTON PDM25 V2 — Komplett projektextraktion

> **Genererad** ur samtliga `.HWPDM`-builds + kabelinventeringen 2026-06-13.
> Skapad som underlag inför Loom3D-piloten: allt som matas in i ett nytt verktyg
> måste vara NUVARANDE sanning. Varje kanalflytt nedan är en punkt där bilens
> kablage kan ha blivit kvar på den gamla pinnen — det var exakt så park/broms-felet uppstod.

- **Builds lästa:** 106 st, 2026-03-04 → 2026-09-25
- **Baslinje (logik):** `LISO.HWPDM`
- **Nyast på disk:** `LISO.HWPDM` (2026-09-25)
- **Pinkarta:** manualens pinout, korsverifierad mot konfiguratorns egen pinlayout-export
- **Kabelfärger:** okulärt besiktigade på bilen 2026-06-13 — slår all schemadokumentation

---

## ⚠ Kanalflyttar genom historiken

Funktioner som suttit på mer än en kanal. Varje rad kräver att den fysiska kabeln
flyttades med — gjordes inte det sitter den kvar på fel utgång.

### Utgångar

| Funktion | Kanaler (pin) | Period |
|---|---|---|
| **ALT_EXCITE** | O17 (D1) → O2 (C5) | 2026-06-04→2026-06-04 · 2026-06-04→2026-09-25 |
| **BRAKE** | O4 (D7) → O6 (D9) | 2026-03-04→2026-05-20 · 2026-05-20→2026-09-25 |
| **PARK** | O6 (D9) → O24 (D3+D10) → O4 (D7) | 2026-03-04→2026-05-20 · 2026-03-04→2026-03-05 · 2026-05-20→2026-09-25 |
| **REVERSE** | O19 (B1) → O21 (D2) | 2026-03-04→2026-09-25 · 2026-09-25→2026-09-25 |
| **TURN R** | O24 (D3+D10) → O6 (D9) | 2026-03-04→2026-03-04 · 2026-03-04→2026-03-04 |
| **TURN_R** | O6 (D9) → O24 (D3+D10) | 2026-03-05→2026-03-05 · 2026-03-06→2026-09-25 |
| **WIPER_FST** | O2 (C5) → O8 (D5) | 2026-03-05→2026-06-04 · 2026-06-04→2026-09-25 |

### Ingångar

| Funktion | Kanaler (pin) | Period |
|---|---|---|
| **COOLANT** | I11 (A12) → I10 (A2) | 2026-03-04→2026-06-04 · 2026-05-21→2026-06-04 |
| **COOLANT_TEMP** | I11 (A12) → I10 (A2) | 2026-06-04→2026-06-04 · 2026-06-04→2026-09-25 |
| **REVERSE** | I14 (C12) → I7 (A10) | 2026-03-04→2026-03-06 · 2026-03-04→2026-09-25 |
| **WASHER** | I8 (A3) → I16 (C1) | 2026-03-04→2026-09-25 · 2026-06-05→2026-06-05 |
| **WIPER_PARK** | I14 (C12) → I11 (A12) | 2026-06-04→2026-06-04 · 2026-06-04→2026-09-25 |

---

## Masterkarta per Deutsch-kontakt

Logik ur `LISO.HWPDM`. Status: ✅ kabel på plats · ⬜ pin tom · ⚠ avvikelse.

### Kontakt A (1-DT-GRÅ — ingångar)

| Pin | I/O | Funktion | Aktiv | Kabel på bilen | |
|---|---|---|---|---|---|
| **A1** | I12 | HORN | ja | brun + blå | ✅ |
| **A2** | I10 | COOLANT_TEMP | ja | blå + gul (tvärs) | ✅ |
| **A3** | I8 | WASHER | nej | grön + röd  ⚠ gammal spolarkabel | ⚠ |
| **A4** | I6 | TURN_R | ja | svart + grön | ✅ |
| **A5** | I4 | BRAKE | ja | röd + gul | ✅ |
| **A6** | I2 | HIBEAM | ja | brun + vit | ✅ |
| **A7** | I1 | BLOWER | nej | — tom | ⬜ |
| **A8** | I3 | HAZARD | ja | svart + grön | ✅ |
| **A9** | I5 | TURN_L | ja | svart + vit | ✅ |
| **A10** | I7 | REVERSE | nej | — tom | ⬜ |
| **A11** | I9 | WIPER_SLOW | ja | grön + gul | ✅ |
| **A12** | I11 | WIPER_PARK | ja | grön | ✅ |

### Kontakt C (2-DT-GRÖN — kraft / CAN / sensorer)

| Pin | I/O | Funktion | Aktiv | Kabel på bilen | |
|---|---|---|---|---|---|
| **C1** | I16 | RESERVE16 | nej | — tom | ⬜ |
| **C2** | I15 | START | ja | röd + svart, grov 2.5 | ✅ |
| **C3** | — | PWR.CTRL (tändningsmatad) | ja | svart (hel)  ⚠ doc sa röd | ⚠ |
| **C4** | O3 | IGN_COIL | ja | svart | ✅ |
| **C5** | O2 | ALT_EXCITE | ja | (ej beskriven) | ✅ |
| **C6** | O1 | BUSBAR | ja | svart + gul | ✅ |
| **C7** | — | GND.CHASSIS | ja | brun (hel) | ✅ |
| **C8** | — | CAN 1 High | ja | gul | ✅ |
| **C9** | — | CAN 1 Low | ja | blå | ✅ |
| **C10** | — | 5V REF (100 mA) | ja | — tom  ⚠ blockerar bränsle + muxar | ⚠ |
| **C11** | I13 | BRAKE_FAULT | nej | — tom | ⬜ |
| **C12** | I14 | OIL.PRESS | nej | (oljebrytare, overifierad) | ✅ |

### Kontakt D (3-DT-BRUN — utgångar)

| Pin | I/O | Funktion | Aktiv | Kabel på bilen | |
|---|---|---|---|---|---|
| **D1** | O17 | RESERVE17 | nej | — tom | ⬜ |
| **D2** | O21 | REVERSE | nej | — tom | ⬜ |
| **D3** | O24 | TURN_R | ja | svart + grön | ✅ |
| **D4** | O9 | RESERVE9 | nej | grön + gul (lös) | ✅ |
| **D5** | O8 | WIPER_FST | nej | (overifierad) | ✅ |
| **D6** | O7 | HIBEAM_R | ja | (overifierad) | ✅ |
| **D7** | O4 | PARK | ja | blå (hel) | ✅ |
| **D8** | O5 | FUEL | ja | svart + brun (2 kablar) | ✅ |
| **D9** | O6 | BRAKE | ja | röd (hel) | ✅ |
| **D10** | O24 | TURN_R | ja | grön | ✅ |
| **D11** | O20 | RADIO_ACC | ja | grå + röd (lös) | ✅ |
| **D12** | O16 | HIBEAM_L | ja | vit + svart | ✅ |

### Kontakt B (4-DT-SVART — utgångar)

| Pin | I/O | Funktion | Aktiv | Kabel på bilen | |
|---|---|---|---|---|---|
| **B1** | O19 | REVERSE | nej | — tom | ⬜ |
| **B2** | O23 | STARTER | ja | svart + röd | ✅ |
| **B3** | O25 | TURN_L | ja | gul | ✅ |
| **B4** | O15 | LOWBEAM_R | ja | gul (hel) | ✅ |
| **B5** | O14 | LOWBEAM_L | ja | gul + svart (tvärs) | ✅ |
| **B6** | O13 | HORN | ja | röd + gul | ✅ |
| **B7** | O10 | WIPER_SLO | ja | grön + svart | ✅ |
| **B8** | O11 | BLOWER | ja | grön + svart (tvärs) | ✅ |
| **B9** | O12 | WASHER | nej | grön + röd | ✅ |
| **B10** | O25 | TURN_L | ja | gul | ✅ |
| **B11** | O22 | USB_12V | nej | — tom | ⬜ |
| **B12** | O18 | RESERVE18 | nej | — tom | ⬜ |

---

## Kända avvikelser att bära med sig

1. **Främre parkljuset sitter i bromskretsen.** O4 PARK (D7) och O6 BRAKE (D9)
   bytte kanal i `Elton_v9.8_basic.HWPDM` 2026-05-20 17:39. Bakre park följde med, främre inte.
   PARK/BRAKE ligger kvar oförändrat i `LISO.HWPDM`, så analysen gäller fortfarande.
2. **Bränslemätaren är INTE konfigurerad i LISO.** A3/I8 står som `WASHER`, disabled,
   digital (mode 0) med intern pull-up mot VBat. Kabeln är dragen fram till PDM:en men
   ingången är inte förberedd. Ska vara: analog (mode 2), `pullResistor = 0`, enabled.
3. **Båda sensorkurvorna pekar på fel ingång i LISO.**
   `SC2 FUEL_LVL` läser var 641 = I13 (pin C11, tom) — ska vara 616 = I8.
   `SC1 COOLANT_T` läser var 631 = I11 (WIPER_PARK, digital) — ska vara 626 = I10.
   Stale pekare ärvda från den era då I13 var FUEL_LVL.
4. **Firmware 1.3.1 flyttade alla variabel-ID med +21.** Verifierat mot ett dussin
   referenser (577→598, 640→661, 850→871, 612→633, 734→755).
   ⚠ **Kör INTE de gamla `build_v9.*.py`-skripten mot en 1.3.1-fil** — de skriver
   det gamla numret och pekar då om logiken till fel variabel, tyst.
5. **C10 (5V REF) är odragen** — blockerar bränslemätare och samtliga muxar.
6. **O24/O25 är enda kanalerna med dubbla pins** (D3+D10, B3+B10). Alla andra har en.

## Buildlinje

`GOTLAND` → `LISO` är en egen gren, inte en fortsättning på `v9.59`.
LISO:s sensorpekare är exakt GOTLAND:s (610/620) plus firmwarens +21 → 631/641.
Det som finns i v9.59 men saknas i LISO: dual-horn (O17), WIPER_FST, WASHER, REVERSE
enabled, och den korrekt riktade bränslekurvan. **Bekräfta vilken som faktiskt är flashad.**

