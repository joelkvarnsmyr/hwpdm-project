# ELTON PDM25 V2 — Projekt-audit v9.56

**Datum:** 2026-06-09
**Granskat mot:** `Elton_v9.56_dual_horn.HWPDM` (current build)
**Jämfört med:** Märklista v7.1 (v9.4-baserad, 2026-05-20), Installation-JSON (v5.8, 2026-03-05), 15 wiring-diagram, wiring-guide.html

---

## Sammanfattande omdöme

**PDM-logiken är i utmärkt skick. Dokumentationen är det inte.**

- ✅ **Output-logik + CAN-styrning + säkringar:** Solitt byggt, validerat live på bilen (ljus, horn, show-mode suppress).
- 🔴 **Det finns ingen enda aktuell källa till sanning för pin-mappningen.** Tre dokument beskriver tre olika bilar.
- 🟠 **Allt vi byggt denna session (CAN-control, PWM, dual horn, fuel, wake) saknas helt i den formella kabeldokumentationen.**
- 🔴 **Flera sensor-inputs är OLÖSTA BESLUT, inte bara "föråldrad dokumentation"** — och du står i begrepp att köpa komponenter + dra kablar till dem. Detta måste lösas FÖRE lödkolven.

**#1-leverabel ur denna audit:** EN avstämd pinmap med status-kolumn + en explicit OPEN-DECISIONS-lista. Allt annat är sekundärt.

---

## Det grundläggande problemet: tre baslinjer som inte stämmer överens

| Dokument | Version | Datum | Beskriver |
|----------|---------|-------|-----------|
| Installation-JSON | v5.8 | 5 mars | En gammal bil (pre-v9) |
| Märklista v7.1 | v9.4 | 20 maj | En mellanbil (pre-v9.21 ignition-ändring, pre-allt-denna-session) |
| **Build v9.56** | v9.56 | 9 juni | **Faktiska firmware-intentionen** |

Märklistan v7.1 säger själv "Bekräftad mot Elton_v9.4" — men sedan dess har minst **15 build-versioner** passerat, inklusive v9.21 (PWR flyttad till tändningslås, I16→RESERVE16) och hela denna sessions arbete. Installation-JSON är ännu äldre.

**Konsekvens:** Den som spårar en kabel via dokumentationen hamnar på fel pin.

---

## KRITISKT: skilj på "testat" och "intention"

Detta är auditens viktigaste distinktion. **Builden vinner INTE automatiskt** — det beror på om kabeln finns fysiskt:

- **Kopplat + testat på bilen** → builden är sanning, dokumentationen ska uppdateras.
- **Inte kopplat än** → build-etiketten är ett *förslag*. Där den krockar med ett medvetet dokumenterat beslut är det ett **ÖPPET BESLUT för dig**, inte en "föråldrad doc".

---

## INPUT-audit (16 st)

| I# | Pin | Build v9.56 | Doc v7.1-plan | Fysisk status | Verdikt |
|----|-----|-------------|---------------|---------------|---------|
| I1 | A7 | BLOWER (analog, off) | BLOWER analog | Ej aktiv | 🟡 Planerad — matchar |
| I2 | A6 | HIBEAM | HIBEAM momentary High | ✅ Kopplat+funkar | 🟢 Build = sanning, uppdatera doc-detaljer |
| I3 | A8 | HAZARD | HAZARD latching | ✅ Kopplat | 🟢 OK |
| I4 | A5 | BRAKE | BRAKE momentary | ✅ Kopplat+funkar | 🟢 OK |
| I5 | A9 | TURN_L | TURN_L | ✅ Kopplat | 🟢 OK |
| I6 | A4 | TURN_R | TURN_R | ✅ Kopplat | 🟢 OK |
| I7 | A10 | REVERSE (off) | REVERSE (flyttad till I7) | Ej kopplat | 🟡 Matchar plan, ej dragen |
| **I8** | **A3** | **FUEL_LEVEL** (analog, NY v9.55) | WASHER — och fuel→**ADS1115 på Pi** (wire #56) | **Ej kopplat** | 🔴 **ÖPPET BESLUT** (se nedan) |
| **I9** | **A11** | **WIPER_SLOW** (digital) | **WIPER_SPEED analog** (spänningsdelare) | ✅ Kopplat+funkar (v9.50) | 🟠 **ÖPPET BESLUT** (se nedan) |
| **I10** | **A2** | **COOLANT_TEMP** (analog) | **COOLANT_LOW** (F66 nivå, latching) | Osäkert | 🔴 **KONFLIKT** |
| **I11** | **A12** | **WIPER_PARK** (testat v9.50) | **COOLANT** (NTC temp, analog) | ✅ Kopplat+testat | 🔴 **KONFLIKT** (build vann pin, temp hemlös) |
| I12 | A1 | HORN | HORN momentary High | ✅ Kopplat+funkar | 🟢 OK |
| I13 | C11 | BRAKE_FAULT (off, latch) | BRAKE_FAULT (ny givare) | Ej kopplat | 🟡 Matchar plan, givare saknas |
| I14 | C12 | OIL.PRESS (off, latch) | OIL.PRESS (F1) | Ej kopplat | 🟡 Matchar plan, väntar F1-byte |
| I15 | C2 | START | START active Low | ✅ Kopplat+funkar | 🟢 OK |
| **I16** | **C1** | **RESERVE16** | **IGNITION** | n/a (PWR flyttad v9.21) | 🟢 Build rätt, **doc föråldrad** |

---

## OUTPUT-audit — utvalda konflikter (25 st totalt)

De flesta outputs stämmer, men dessa **krockar** mellan build och doc-plan:

| O# | Pin | Build v9.56 | Doc v7.1-plan | Status | Verdikt |
|----|-----|-------------|---------------|--------|---------|
| **O2** | C5 | **ALT_EXCITE** (off) | **WIPER FST** | Ej kopplat | 🔴 **KONFLIKT** — du köper just 82Ω för ALT_EXCITE |
| **O8** | D5 | WIPER_FST (off) | IND.TURN | Ej kopplat | 🟠 Funktion flyttad |
| **O9** | D4 | RESERVE9 (off) | WARN.MASTER | Ej kopplat | 🟠 Master-varning borttagen? |
| **O13** | B6 | **HORN_1** (NY denna session) | HORN | ✅ Kopplat | 🟢 Build = sanning |
| **O17** | D1 | **HORN_2** (NY denna session) | RESERVE17 | Ej kopplat (ny kabel) | 🟢 Build = sanning, doc saknar |
| **O14/O15** | B5/B4 | LOWBEAM L/R (**off i build!**) | LOWBEAM L/R | ✅ Du enablade i GUI live | 🔴 **Build-FIL ur synk med flashad PDM** |
| O20 | D11 | RADIO_ACC | RADIO ACC | — | 🟡 v9.52 skulle döpa → RADIO; build visar RADIO_ACC |
| O21 | D2 | Reserve (off) | RPI | — | 🟢 Build rätt (Pi på batteri direkt) |

> ⚠️ **O14/O15 LOWBEAM:** Du enablade dessa i PDM-GUI:t live under vårt test, men **build-filerna v9.53–v9.56 har dem fortfarande `enabled:false`**. Nästa gång du flashar en av mina byggda filer **släcks halvljuset igen**. Måste fixas i build-kedjan.

---

## ÖPPNA BESLUT — måste lösas före kabeldragning

### 1. 🔴 Bränslenivå: PDM-I8 vs Pi ADS1115
- **Build (v9.55, denna session):** FUEL_LEVEL analog på PDM I8 + 150Ω pull-up.
- **Doc v7.1 (medvetet beslut, wire #56):** Bränslegivaren bortkopplad från PDM, läses via **ADS1115 ADC på Pi:ns I²C** → MQTT `vehicle/fuel_level`.
- **Vad hände:** Vi valde PDM-vägen i konversationen, troligen utan att minnas ADS1115-planen.
- **Konsekvens om olöst:** Du köper 150Ω pull-up + drar sender till A3 — men om Pi-experten byggt analog-bridge för ADS1115 blir det dubbelarbete/konflikt.
- **Beslut behövs:** PDM-I8 ELLER Pi-ADS1115. (PDM = enklare, allt på ett ställe. ADS1115 = bättre upplösning 16-bit, avlastar PDM-input.)

### 2. 🟠 Vindrutetorkare: digital+park-sensor vs analog spänningsdelare
- **Build (v9.50, testat ~50%):** I9 WIPER_SLOW digital + I11 WIPER_PARK sensor.
- **Doc v7.1 (plan):** I9 WIPER_SPEED **analog spänningsdelare** (2 digitala → 1 analog).
- **Viktig insikt:** Resistor-ladder-designen vi "tog fram på nytt" tidigare i denna session (100k/10k för wiper) var **redan v7.1:s dokumenterade plan**. Jag insåg inte det då.
- **Beslut behövs:** Behåll nuvarande digital+park (funkar men park ~50%), ELLER gå till analog ladder (frigör I11, men förlorar nuvarande park-sensor-logik). Du köper resistorerna för analog-vägen nu.

### 3. 🔴 Kylvätsketemp-pin + kylvätskenivå (F66)
- **Build:** COOLANT_TEMP analog på **I10**. Ingen kylvätskenivå-input alls.
- **Doc v7.1:** COOLANT temp på **I11**, och F66 kylvätskeNIVÅ (latching) på I10.
- **Konflikt:** Build satte temp på den pin doc reserverat för nivå, och **droppade F66 helt**.
- **Beslut behövs:** (a) Bekräfta vilken pin NTC-temp-givaren fysiskt går till. (b) Vill du ha F66 kylvätskenivå-varning alls? Om ja — den behöver en egen input (I11 är upptagen av WIPER_PARK nu).

### 4. 🟠 O2: ALT_EXCITE vs WIPER_FST
- Build planerar O2 = ALT_EXCITE (generator-magnetisering, 82Ω). Doc v7.1 har O2 = WIPER FST.
- Du köper just 82Ω 5W för ALT_EXCITE. **Bekräfta att O2 är rätt pin** (C5) och att torkar-fast flyttats till O8 enligt build.

---

## PDM-inställningar — hälsobedömning (de goda nyheterna ✅)

| Område | Status | Kommentar |
|--------|--------|-----------|
| Output-funktioner (ljus/horn) | ✅ Validerat live | OR-logik + show-mode suppress testat på bilen |
| CAN-styrning (0x500-0x502) | ✅ Solitt | Bi-directional, fail-safe via 1s timeout |
| Säkringsinställningar | ✅ Rimliga | HIBEAM peak 40A (inrush-OK), horn 50A/4s |
| Crash-säkerhet | ✅ Bevarad | GF8 HORN_MASTER behåller Timer2-villkor |
| Dual horn | ✅ Byggt | Väntar DBC v1.1-import + fysisk kabel O17 |
| Generic Functions | ✅ Rena | PWR_ALIVE, PARK_LOCKED, PARK_OR_HOLD, HORN_MASTER |
| Sensor-kalibrering | ⚠️ Pin-osäker | SC1/SC2 pekar rätt variabel, MEN fysisk pin oklar (se öppna beslut) |

---

## Dokumentations-täckningsmatris

| Funktion | I build | I formell doc (märklista/JSON/diagram) | I /docs/*.md |
|----------|:-------:|:-------:|:-------:|
| Grundläggande I/O (ljus, start, horn) | ✅ | ⚠️ (v9.4-nivå) | — |
| v9.21 ignition→PWR-ändring | ✅ | ❌ | — |
| Wiper park-sensor (v9.50) | ✅ | ❌ | — |
| CAN-styrning alla outputs (v9.53) | ✅ | ❌ | ✅ HANDOVER + pi_can_control |
| PWM-dimning (v9.54) | ✅ | ❌ | ⚠️ delvis |
| Fuel/temp-fixar (v9.55) | ✅ | ❌ (motsäger v7.1) | — |
| Dual horn (v9.56) | ✅ | ❌ | ✅ dual_horn_changes |
| Wake-service (planerad) | n/a | ❌ | ✅ pdm_wake_service_spec |
| DBC-kontrakt | n/a | ❌ | ✅ v1.0 + v1.1 |

**Slutsats:** Den nya funktionaliteten är välbeskriven i `/docs/*.md` — men **helt frånkopplad** från den formella kabeldokumentationen (märklista/diagram). Två parallella dokumentationsvärldar som inte refererar varandra.

---

## "DT pins/kontakter"

PDM25 V2 använder 4× 12-pol **Deutsch-style-kontakter** (A/B/C/D). Pin-tilldelningen (A1–D12) är dokumenterad i märklista v7.1 — men med **v9.4-era-funktioner**, alltså samma föråldring som ovan. Om du även har **inline DT-harness-kontakter** mellan PDM och fordonsstammen är de **inte separat dokumenterade** — bekräfta om sådana finns.

---

## Prioriterad åtgärdslista

### 🔴 FÖRE nästa kabeldragning (blockerande)
1. **Lös de 4 öppna besluten** ovan (fuel, wiper, coolant, O2) — annars riskerar du löda till fel pin.
2. **Skapa EN avstämd pinmap** (märklista v8.0) med status-kolumn: Kopplat+testat / Kopplat / Ej-dragen / Planerad.

### 🟠 Snart (korrekthet)
3. **Fixa O14/O15 LOWBEAM enabled=true i build-kedjan** — annars släcks halvljuset vid nästa flash av mina filer.
4. **Bekräfta O20** namn (RADIO_ACC vs RADIO — v9.52-intentionen).
5. **Importera DBC v1.1** till v9.56 + verifiera dual horn-pins.

### 🟢 När tid finns (komplett dokumentation)
6. **Regenerera de 15 wiring-diagrammen** mot v9.56-tillståndet.
7. **Uppdatera wiring-guide.html** + installation-JSON till v9.56.
8. **Länka /docs/*.md ↔ formell doc** så de blir EN dokumentationsvärld.
9. **Lägg in wake-service + resistor-BOM** i installation-dokumentationen.

---

## Vad jag INTE kunde verifiera (kräver dig/bilen)

- Fysisk pin för NTC-temp-givaren (I10 vs I11?)
- Om Pi:ns analog-bridge (ADS1115) redan är byggd för fuel
- Om inline DT-harness-kontakter existerar mellan PDM och stam
- Faktisk kabeldragning vs build (jag litar på build där vi testat live)
