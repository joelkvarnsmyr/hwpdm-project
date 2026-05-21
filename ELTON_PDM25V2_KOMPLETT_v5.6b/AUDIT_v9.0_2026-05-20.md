# Audit: Elton_v9.0.HWPDM (Joel, 2026-05-20)

**Källfil:** `Builds/Elton_v9.0.HWPDM` (2026-05-10 13:54Z)
**Trigger:** User rapporterar Battery V = 10.83V på PDM-display, 12.5V vid multimeter på plinten. Misstänker kortslutning.

---

## 🔴 KRITISK — Cut Off-tröskel för optimistisk

**Plats:** Global Settings → Cut Off → `Battery Voltage < 10.00`

PDM:s interna ADC visar 10.83V istället för 12.5V som finns på plinten. **Marginalen till Cut Off-tröskeln 10V är bara 0.83V.** Vid minsta belastning (startmotor, blower, etc.) dippar PDM-mätningen under 10V → **alla outputs stängs av samtidigt**. Reset-funktionen (`I16 == True`) försöker återställa direkt. Resultat: outputs flammar på/av — uppfattas som "kortslutning".

**Fix:** Sänk till `Battery Voltage < 9.00` (säkrar mot djupurladdning men ger marginal mot felmätning), ALT. inaktivera helt tills internt spänningsfel åtgärdat. Behåll Reset oförändrad — den är OK.

---

## 🟡 BETYDANDE — Active LOW + threshold 6V triggar permanent vid floating idle

**Plats:** I2 HIBEAM (A6), I12 HORN (A1)

Båda är konfigurerade Active LOW thr=6V. Manualen sektion 9.2 (ECU Triggered Input) rekommenderar threshold ~1V för Active LOW. Med idle-spänning 1.5V (intern bias-resistors) ligger input PERMANENT under 6V → permanent trigger om ingen extern pull-up finns.

**I2 visar "On" i din skärmdump trots inget tryck på helljus** — det matchar denna teori. För I12 HORN visar skärmdumpen "Off", vilket bara stämmer om E22-knappen har extern pull-up till +12V som håller idle över 6V.

**Fix:** Threshold 6V → 1V på båda. Eller flytta till Active HIGH om busbar-topologi används (12V från busbar → input).

---

## 🟡 Stort drop på PDM:s Battery V-mätning — INTE kablage

Du mätte 12.5V på själva PDM-plinten (kabelskor/kontakter nya). PDM rapporterar 10.83V. **1.7V "försvinner" inuti PDM:n.** Inte ett kablage-problem.

**Möjliga orsaker:**
1. Internt referensvärde drift (åldring/temperatur)
2. ADC-kalibreringsfel (firmware 1.2.3 — kolla om Hardwire har 1.2.4+)
3. Skadat skyddsmotstånd / TVS-diod i input-vägen från C3 till intern ADC

**Verifiering:** Mät +5V-railen på pin C10 (PDM 5V Out). Om den inte är ~5V → internt referensfel bekräftat.

**Åtgärd:** Kontakta Hardwire support med multimeter-mätningar. Inte säkerhetskritiskt — PDM funkar fortfarande, bara underrapporterar Battery V.

---

## 🟢 ÖVRIGT KORREKT KONFIGURERAT

| Område | Status |
|---|---|
| Reset = `I16 IGNITION == True` | OK — bra konvention |
| O5 FUEL `GF1 AND Timer2=False AND (GF3 OR I15)` (B2 fix) | OK — match v5.7-plan |
| O23 STARTER `GF1 AND I15 AND Timer2=False AND NOT GF3` (B5 fix) | OK |
| O14/O15 LOWBEAM turnOnDelay=3000ms (J59 X-kontakt ersättning) | OK — by design |
| O11 BLOWER stayOn=30000ms (restvärmeutblåsning) | OK |
| O5 FUEL stayOn=2000ms | OK |
| O23 STARTER stayOn=0ms | OK — K2 fix tillämpad |
| CAN baseID = 0x1000 extended | OK |
| O17/O18 disabled (sann reserve) | OK |
| Timers: BLINK 400/400, CRASH 600s, START_GRACE 5s | OK |
| GF1-GF7 logikkedja | OK |

---

## 🟡 MINDRE — Sensor calibrations tomma

**Plats:** SensorCalibration SC1 COOLANT_T och SC2 FUEL_LVL

Båda enabled med tomma `rawValue`/`calibratedValue`-arrayer. Det betyder PDM mappar inte spänning → °C eller voltage → liters. Inte ett bug om dashboard/can-bridge gör konverteringen, men:
- **SC1 COOLANT_T:** Om PDM ska skicka kalibrerat temperaturvärde via CAN behöver NTC-tabell läggas in (specifika punkter beroende på NTC-typ — G2 i LT31 är troligen 1k @ 25°C, 200Ω @ 100°C).
- **SC2 FUEL_LVL:** Föråldrad — FUEL_LVL flyttat till `analog-bridge` (ADS1115) i v9.0. SC2 kan inaktiveras.

---

## 🟡 MINDRE — Input turn-on-delay-värden

| Input | turnOnDelay | Tolkning |
|---|---|---|
| I10 COOLANT_LOW | 500 ms | OK (debounce) |
| I13 BRAKE_FAULT | 200 ms | OK |
| I14 OIL.PRESS | 200 ms | OK |

Per `HWPDM_FORMAT_REVERSE_ENGINEERING.md` är fältet i ms. Inga problem.

---

## Sammanfattning prioriterad

| ID | Allvar | Plats | Åtgärd |
|---|---|---|---|
| K1 | 🔴 | Cut Off `Battery V < 10` | Sänk till `< 9.0` |
| K2 | 🟡 | I2 HIBEAM thr=6V Active LOW | Sätt thr=1V |
| K3 | 🟡 | I12 HORN thr=6V Active LOW | Sätt thr=1V |
| B1 | 🟡 | PDM intern ADC-drift på Battery V | Mät +5V-rail C10, kontakta Hardwire |
| D1 | 🟢 | SC2 FUEL_LVL föråldrad | Inaktivera (FUEL flyttat till analog-bridge) |

---

*Genererad 2026-05-20 från Elton_v9.0.HWPDM.*
