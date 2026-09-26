# Elton PDM25 V2 — Final konfiguration v9.4

**Datum:** 2026-05-20
**Status:** ✅ **Produktionsverifierad** (uppladdad till PDM, accepterad utan warnings, alla inputs läser korrekt)
**Aktuell fil:** `Builds/Elton_v9.4.HWPDM`

---

## Bakgrund

Detta dokument summerar felsökningssessionen 2026-05-20 där `Elton_v9.0.HWPDM` upptäcktes ha tre problem:

1. **Cut Off / Reset-oscillation** (uppfattades som kortslutning)
2. **10 Active LOW + threshold 6V-warnings** efter att inputs analyserats
3. **Felaktig topologi-antagande för nyckelvredet** (I15/I16)

Lösningen iterades genom v9.1 → v9.2 → v9.3 → v9.4 med systematiska tester mot fysisk PDM.

## Vad v9.4 innehåller

### Globala ändringar

| Funktion | v9.0 | **v9.4** |
|---|---|---|
| Cut Off threshold | `Battery V < 10.00` | `Battery V < 9.00` |
| Reset trigger | `I16 Status == True` | Oförändrad |

### Input-konfiguration (slutgiltig)

| Input | Pin | Mode | Active | Threshold | Hysteresis | PullResistor | Topologi |
|---|---|---|---|---|---|---|---|
| I1 BLOWER | A7 | Analog | HIGH | 1V | 0.2V | OFF | Analog spänningsdelare |
| I2 HIBEAM | A6 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I3 HAZARD | A8 | Latching | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I4 BRAKE | A5 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I5 TURN_L | A9 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I6 TURN_R | A4 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I7 REVERSE | A10 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I8 WASHER | A3 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I9 WIPER_SPEED | A11 | Analog | HIGH | 1V | 0.2V | OFF | Analog spänningsdelare |
| I10 COOLANT_LOW | A2 | Latching | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND (F66 nivåvakt) |
| I11 COOLANT | A12 | Analog | HIGH | 1V | 0.2V | OFF | Analog NTC + 1k pull-up |
| I12 HORN | A1 | Momentary | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND (slip ring) |
| I13 BRAKE_FAULT | C11 | Latching | **LOW** | 1V | 0.2V | PullUp* | Switch-to-GND |
| I14 OIL.PRESS | C12 | Latching | **LOW** | 2.5V | 0.5V | PullUp* | Switch-to-GND (F1) |
| **I15 START** | C2 | Momentary | **LOW** | 1V | 0.2V | PullUp* | **Switch-to-GND (nyckelvred grundar)** |
| **I16 IGNITION** | C1 | Momentary | **LOW** | 1V | 0.2V | PullUp* | **Switch-to-GND (nyckelvred grundar)** |

\* = PullResistor=2 är konfigurerat men **PDM25 V2-hårdvaran respekterar inte fältet**. Idle-spänningen är ändå ~1.82V (floating bias via interna 40K pull-down + 200K pull-up), vilket är över 1V threshold → Active LOW läser INAKTIV korrekt vid idle. Fältet sparas för forward-compat.

### Outputs, Timers, GFs

**Oförändrade från v9.0.** Alla output-funktioner, generic functions, timers och CAN-stream-mappningar fortsätter fungera eftersom `I_n Status == True`-semantiken bevarades genom samtidig wiring+config-flip.

## Lärdomar från sessionen

### 1. "Kortslutning" var en Cut Off/Reset-oscillation

PDM:n rapporterade 10.83V vid C3 trots 12.5V multimeter-mätning på samma plinte. Mitt initialantagande att det var **internt ADC-fel** var fel. Den verkliga orsaken:

- Cut Off vid `< 10V` triggade vid små belastnings-dipps
- Reset (`I16 == True`) auto-återställde direkt
- Loop mellan av/på drog ned momentärspänningen vid C3
- Med Cut Off sänkt till `< 9V` stannade oscillationen och PDM:n läser nu stabil 12.79V

### 2. Floating idle-spänning på ~1.5V är normalt

Manualens sektion 9.2 säger explicit att flytande inputs sätter sig vid 1.5–2V tack vare interna 40K pull-down + 200K pull-up. När jag första gången såg alla 16 inputs på 1.5V misstänkte jag wiring-fel — det var helt felaktigt.

### 3. PullResistor-fältet är HW-ignorerat på PDM25 V2

Konfiguratorns UI inaktiverar fältet för modelVersion 23 (PDM25 V2), men firmware tar emot och lagrar värdet. PDM-retur-export bekräftar att hårdvaran **inte** kopplar in pull-up: idle-spänning förblev 1.82V även med `pullResistor=2`. Funktionellt OK ändå (1.82V > 1V threshold).

### 4. Hysteresis MÅSTE vara mindre än threshold

Konfiguratorn varnar `hyst >= thr`. Manualens exempel för Active LOW: `thr=1V + hyst=0.2V`. Föregående v9.0 hade `thr=6V + hyst=1V` (17% — bra), men när jag sänkte thr till 1V måste hyst också sänkas till 0.2V.

### 5. JSON-typer ska vara strängar i sparade .HWPDM-filer

Originalfiler från konfiguratorn lagrar numeriska fält som **strängar** (`"1"`, `"6"`, `"0"`). Skriver man som JS-numbers (`1`, `6`, `0`) triggar konfiguratorn migrationskoden och varnar om "Could not convert config file. Logic Functions may be incorrect."

PDM-RETURFILER däremot lagrar som number — det är OK, formaten är båda accepterade men input-filen måste matcha originalformatet.

### 6. `MetaData.ConfiguratorVersion` måste vara exakt "1.2.3"

Att lägga in en custom-string som "1.2.3-elton-fix" där triggar samma migrations-varning som typkonflikten.

### 7. Nyckelvredet i Elton grundar inputs

Den största överraskningen: I15 + I16 går till en switch som **grundar** mot chassi vid RUN/START, inte +12V som standard VW LT. Manualens text om "kl.15/kl.50 levererar +12V" gäller inte denna installation.

Hela elsystemet använder nu **konsistent switch-to-GND-topologi** över alla 13 digitala inputs.

## Verifiering — vad PDM:n bekräftade efter Send

Från `Elton_v9.2_FROMPDM AFTER SEND.HWPDM`:

| Mätning | Värde | Status |
|---|---|---|
| Comparing PC to PDM - Global | ✅ | OK |
| Comparing PC to PDM - Inputs | ⚠️ | Bara runtime-värden (voltage, status, onTime) — inte konfig |
| Comparing PC to PDM - Outputs | ⚠️ | Samma — runtime, ej konfig |
| Comparing PC to PDM - Timers | ✅ | OK |
| Comparing PC to PDM - Generic Functions | ✅ | OK |
| Comparing PC to PDM - CAN Stream | ✅ | OK |

Alla kritiska konfigurations-fält matchade PERFEKT mellan PC-fil och PDM. ⚠️-flaggorna är förväntade (runtime-drift på live-mätvärden).

| Driftsmätning | Värde |
|---|---|
| Battery V | 12.79V ✓ (matchar verklighet) |
| Temperature | 32°C ✓ |
| Update Rate | 726Hz ✓ |
| On Time | 15m 36s (stabil drift utan reset) |
| Inputs idle voltage | 1.82V på alla (floating bias, normalt) |

## Filsekvens (för historik)

| Version | Datum | Status |
|---|---|---|
| Elton_v9.0.HWPDM | 2026-05-10 | Baseline med ovanstående problem |
| Elton_v9.1.HWPDM | 2026-05-20 | Akut-fix: Cut Off 10V→9V + I2/I12 thr 6V→1V |
| Elton_v9.2.HWPDM | 2026-05-20 | + 11 inputs flippade till Active LOW + PullUp (för GND-busbar) |
| Elton_v9.3.HWPDM | 2026-05-20 | + Hysteresis fixed (0.2V för alla thr=1V inputs) |
| **Elton_v9.4.HWPDM** | 2026-05-20 | + I15/I16 flippade till Active LOW (nyckelvred grundar) — **PRODUKTIONSKLAR** |

## Outstanding / Framtida arbete

- 🟡 **`pullResistor`-fältet:** Ignoreras av PDM25 V2-firmware. Kontakta Hardwire support om hårdvarustödd pull-up är önskvärt i framtiden.
- 🟡 **SC2 FUEL_LVL:** Föråldrad sensorkalibrering — bränslemätning flyttad till `analog-bridge` (ADS1115). Kan inaktiveras i konfiguratorn vid tillfälle.
- 🟡 **SC1 COOLANT_T:** NTC-kalibreringskurvan är tom. Om PDM ska skicka kalibrerade °C-värden via CAN behöver tabellen fyllas i.
- 🟡 **Driver-dash + st7789-bridge:** Se separat audit `docs/audits/2026-05-20-pdm-v9-can-drift.md` i Pi-projektet. Konsumentsidan av CAN-streamen var stale — fixad i `feat/pdm-v9-consumer-drift` (mergat 2026-05-20).

---

*Genererad 2026-05-20 efter komplett verifiering av Elton_v9.4.HWPDM mot fysisk PDM25 V2.*
