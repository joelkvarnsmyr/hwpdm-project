# ELTON PDM25 V2 — Komplett Märklista v7.0
## VW LT31 1976 · JSN 398 · 2026-05-20
### Genererad från Elton_v9.0.HWPDM (2026-05-10 13:54Z)

> **Märk BÅDA ändar.** 6mm tejp for de flesta kablar. 12mm for grova (>=10mm²). Krympslang som skydd.

> ⚠️ **v9.0-omstrukturering:** 5 inputs och 7 outputs har bytt funktion sedan v6.0. Markeringar listade nedan; en sammanfattning finns längst ned under "Ändringar v6.0 → v7.0".

---

## Tejpfärger

| Tejp | Prefix | Betydelse |
|------|--------|-----------|
| GUL | `PDM.OUT` / `PDM.PWR` / `PDM.ENG` | Outputs + strömmatning + motorkablar |
| BLA | `PDM.IN` | Inputs — signaler till PDM |
| SVART | `GND` | Jordkablar |
| GRON | `INST` | Givare, kontrollampor, sensorer |

---

## GUL TEJP — Stromforsorjning (4 st)

| # | Etikett | mm2 | Farg | Fran | Till |
|---|---------|-----|------|------|------|
| 1 | `PDM.PWR.BAT+` | 32 | ro | Startmotor kl.30 | PDM M8-stud |
| 2 | `PDM.PWR.CTRL` | 4 | ro | Startmotor kl.30 | PDM pin C3 |
| 3 | `PDM.IN.IGNITION` | 2.5 | sw/ge | Tandningslas t.15 | I16 pin C1 |
| 4 | `PDM.IN.START` | 2.5 | sw/ws | Tandningslas t.50 | I15 pin C2 |

## SVART TEJP — Chassijord (1 st)

| # | Etikett | mm2 | Farg | Fran | Till |
|---|---------|-----|------|------|------|
| 5 | `PDM.GND.CHASSIS` | 10 | br | PDM pin C7 | Chassijord punkt 12 |

## GRON TEJP — Motorkablar ej via PDM (3 st)

| # | Etikett | mm2 | Farg | Fran | Till | Not |
|---|---------|-----|------|------|------|-----|
| 6 | `PDM.ENG.BAT->START` | 35 | ro | Batteri+ via franskiljare | Startmotor t.30 | gul tejp |
| 7 | `PDM.ENG.GEN.B+` | 6 | ro | Generator B+ | Batteri+ | gul tejp |
| 8 | `PDM.ENG.COIL.N6` | 1 | ws/li | N6 seriemotstand | Tandspole kl.15 | gron tejp |
| 9 | `PDM.ENG.COIL.T1` | — | gn | Tandspole kl.1 | Fordelare | gron tejp |

---

## GUL TEJP — PDM Outputs (29 kablar, 23 outputs)

### Stralkastrare (4 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 10 | `PDM.OUT.LOWBEAM-L` | O14 | B5 | 2.5 | ge/sw | L1 vanster halvljus (56b) |
| 11 | `PDM.OUT.LOWBEAM-R` | O15 | B4 | 2.5 | ge | L2 hoger halvljus (56b) |
| 12 | `PDM.OUT.HIGHBEAM-L` | O16 | D12 | 2.5 | ws/sw | L1 vanster helljus (56a) |
| 13 | `PDM.OUT.HIGHBEAM-R` | O7 | D6 | 2.5 | ws | L2 hoger helljus (56a) |

### Signal- och positionsljus (7 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till | Ändring v6→v7 |
|---|---------|--------|-----|-----|------|------|---------------|
| 14 | `PDM.OUT.PARK` | **O6** | D9 | 1.5 | rod | Splitter -> M1 M3 M2 M4 X | 🔄 **Flyttad O24→O6** |
| 15 | `PDM.OUT.TURN-R-F` | **O24** | D3 | 1.5 | sw/gn | M7 blink H fram | 🔄 **Flyttad O6→O24** |
| 16 | `PDM.OUT.TURN-R-R` | **O24** | D10 | 1.5 | gron | M8 blink H bak | 🔄 Samma som rad 15 (splitter) |
| 17 | `PDM.OUT.TURN-L-F` | O25 | B3 | 1.5 | sw/ws | M5 blink V fram | — |
| 18 | `PDM.OUT.TURN-L-R` | O25 | B10 | 1.5 | gul | M6 blink V bak | — |
| 19 | `PDM.OUT.BRAKE` | O4 | D7 | 1.5 | bla | M9 + M10 bromsljus | — |
| 20 | `PDM.OUT.REVERSE` | O19 | B1 | 1.5 | gra | M16 + M17 backljus | — |

### Busbar (1 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 21 | `PDM.OUT.BUSBAR` | O1 | C6 | 0.75 | — | Signalbusbar (terminalblock) |

### Torkare, flakt, spolare, horn (5 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 22 | `PDM.OUT.WIPER.SLO` | O10 | B7 | 2.5 | gn | V torkarmotor kl.53 |
| 23 | `PDM.OUT.WIPER.FST` | O2 | C5 | 2.5 | sw/gr | V torkarmotor kl.53b |
| 24 | `PDM.OUT.BLOWER` | O11 | B8 | 2.5 | sw/ge | V2 kupeflakt |
| 25 | `PDM.OUT.WASHER` | O12 | B9 | 1.5 | gn/ro | V5 spolarpump |
| 26 | `PDM.OUT.HORN` | O13 | B6 | 2.0 | sw/ge | H1 signalhorn |

### Motor via PDM (3 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 27 | `PDM.OUT.IGN_COIL` | O3 | C4 | 1.5 | sw/li | N6 seriemotstand |
| 28 | `PDM.OUT.FUEL` | O5 | D8 | 2x1.5 par. | sw+br | G6 branslepump |
| 29 | `PDM.OUT.STARTER` | O23 | B2 | 2.5 | ro/sw | B solenoid kl.50 |

### Instrumentering och varning (2 st) — 🆕 **AKTIVERAD i v9.0**

| # | Etikett | Output | Pin | mm2 | Farg | Till | Ändring v6→v7 |
|---|---------|--------|-----|-----|------|------|---------------|
| 30 | `PDM.OUT.IND.TURN` | **O8** | D5 | 1.5 | sw/bl | K5 blinkerkontrollampa | 🆕 Var RESERVE i v6 |
| 31 | `PDM.OUT.WARN.MASTER` | **O9** | D4 | 1.5 | ro | Varningslampa (CAN-styrd) | 🆕 Var RESERVE i v6 |

### Moderna tillagg (3 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 32 | `PDM.OUT.RADIO_ACC` | O20 | D11 | 1.5 | — | Radio ACC |
| 33 | `PDM.OUT.RPI` | O21 | D2 | 2.0 | — | Raspberry Pi 4 + CAN HAT |
| 34 | `PDM.OUT.USB_12V` | O22 | B11 | 1.5 | — | 12V USB-uttag |

### Parkkrets (1 st)

| # | Etikett | mm2 | Farg | Fran | Till | Not |
|---|---------|-----|------|------|------|-----|
| 35 | `PDM.OUT.WIPER.PARK` | 1.5 | — | Motor t.31b | Motor t.53 | Extern jumper vid kontaktdon |

### Lediga outputs (ej kabel, ej markning)

| Output | Pin | Status |
|--------|-----|--------|
| O17 | D1 | Ledig (sann reserve) |
| O18 | B12 | Ledig — radio-minne borttaget i v9.0 (radio har egen battery backup eller flyttat till O20 ACC) |

---

## BLA TEJP — PDM Inputs (16 st)

### Tandning (2 st — redan listad ovan under strom, samma label)

| # | Etikett | Input | Pin | Mode | Farg | Fran |
|---|---------|-------|-----|------|------|------|
| — | `PDM.IN.IGNITION` | I16 | C1 | Momentary | sw/ge | Tandningslas t.15 |
| — | `PDM.IN.START` | I15 | C2 | Momentary | sw/ws | Tandningslas t.50 |

### Signalbusbar-matade (6 st)

| # | Etikett | Input | Pin | Mode | Farg | Fran | Ändring v6→v7 |
|---|---------|-------|-----|------|------|------|---------------|
| 36 | `PDM.IN.TURN-L` | I5 | A9 | Momentary | sw/ws | E2 blinkerspak V | — |
| 37 | `PDM.IN.TURN-R` | I6 | A4 | Momentary | gr | E2 blinkerspak H | — |
| 38 | `PDM.IN.HAZARD` | I3 | A8 | Latching | — | Varningsblinkersknapp | — |
| 39 | `PDM.IN.REVERSE` | **I7** | A10 | Momentary | sw/bl | F4 backvaxelkontakt | 🔄 **Flyttad från I14 till I7** |
| 40 | `PDM.IN.WASHER` | I8 | A3 | Momentary | gn/ro | E22 spolarspak | — |
| 41 | `PDM.IN.WIPER_SPEED` | **I9** | A11 | **Analog** (1V thr) | sw/gr+gn | E22 spakdelare (kl.53/53b → spänningsdelare) | 🔄 **Konsoliderad: 2 digitala → 1 analog** |

### Direkt matade (3 st)

| # | Etikett | Input | Pin | Mode | Farg | Fran | Ändring v6→v7 |
|---|---------|-------|-----|------|------|------|---------------|
| 42 | `PDM.IN.BRAKE` | I4 | A5 | Momentary | sw/ro | F bromsljusbrytare (bat-matad) | — |
| 43 | `PDM.IN.BLOWER` | I1 | A7 | Analog (1V thr) | sw/ge | E9 flaktomkopplare | — (thr 0→1V) |
| 44 | `PDM.IN.HIBEAM` | I2 | A6 | **Momentary active High** | ge | E4 helljusspak | 🔄 **Mode latching→momentary, polaritet bytt** |

### Active Low (1 st)

| # | Etikett | Input | Pin | Mode | Farg | mm2 | Fran |
|---|---------|-------|-----|------|------|-----|------|
| 45 | `PDM.IN.HORN` | I12 | A1 | Momentary High | br/bl | 1.0 | Hornknapp via slip ring |

### Analoga + digitala sensorer (4 st) — 🔄 **Stor ändring i v9.0**

| # | Etikett | Input | Pin | Mode | Farg | Fran | Ändring v6→v7 |
|---|---------|-------|-----|------|------|------|---------------|
| 46 | `PDM.IN.COOLANT` | I11 | A12 | Analog (1V thr) | gn | G2 NTC kyltemp (1k -> 5V) | — |
| 47 | `PDM.IN.COOLANT_LOW` | **I10** | A2 | Latching | sw/gn | F66 kylvätskenivåvakt | 🆕 **Flyttad från RPi GPIO → PDM** |
| 48 | `PDM.IN.BRAKE_FAULT` | **I13** | C11 | Latching | bl/ws | Bromsfel-sensor (ny givare) | 🆕 **Ersatt FUEL_LVL — kräver fysisk koppling** |
| 49 | `PDM.IN.OIL.PRESS` | **I14** | C12 | Latching High (2.5V thr) | bl/gn | F1 oljetryckskontakt | 🔄 **Flyttad från RPi GPIO → PDM** (v5.7-plan klar) |

> ⚠️ **PDM.IN.FUEL.LVL borttagen** — bränslenivå går nu via `analog-bridge` (ADS1115 på RPi I²C) → MQTT `vehicle/fuel_level`. Den gamla `li/sw`-kabeln från bränslegivaren till C11 ska kopplas om till ADS1115 ingången.

---

## BLA TEJP — CAN-bus (2 st)

| # | Etikett | Pin | mm2 | Farg | Till |
|---|---------|-----|-----|------|------|
| 50 | `PDM.CAN.H` | C8 | 0.75 tvinnad | ws | RPi CAN High |
| 51 | `PDM.CAN.L` | C9 | 0.75 tvinnad | sw | RPi CAN Low |

CAN base-ID: **0x1000** (extended, 29-bit). 28 stream-frames aktiva, 250 kbps, programvarutermineringen aktiv på PDM-sidan.

---

## SVART TEJP — Jordar (4 st)

### Systemjordar

| # | Etikett | mm2 | Fran | Till |
|---|---------|-----|------|------|
| 52 | `GND.BAT` | 25 | Batteri - | Chassi framdel (punkt 1) |
| 53 | `GND.ENGINE` | 16 | Motorblock | Chassi (punkt 3) |

### Jordsamlingsplint bak

| # | Etikett | mm2 | Fran | Till | Not |
|---|---------|-----|------|------|-----|
| 54 | `GND.REAR.BUS` | 4 | Jordplint | Chassi bak M8 (punkt 15) | Gemensam jord for alla baklampor + nummerplat |

### Torkarmotor

| # | Etikett | mm2 | Fran | Till |
|---|---------|-----|------|------|
| 55 | `GND.WIPER` | 1.0 | V torkarmotor t.31 | Chassijord punkt 10 |

---

## GRON TEJP — Givare och kontrollampor (10 st)

| # | Etikett | Komponent | Farg | Koppling | Ändring v6→v7 |
|---|---------|-----------|------|----------|----------------|
| 56 | `INST.SENS.FUEL` | G branslegivare | li/sw | **→ ADS1115 (analog-bridge)** | 🔄 **Var I13 PDM, nu RPi** |
| 57 | `INST.SENS.FUEL.GND` | G branslegivare jord | br | -> Chassijord | — |
| 58 | `INST.SENS.COOLANT` | G2 kyltemp NTC | gn | -> I11 via 1k PU | — |
| 59 | `INST.SENS.OIL` | F1 oljetryck | bl/gn | **→ I14 (PDM) via 2.5V thr** | 🔄 **Flyttad från RPi GPIO** |
| 60 | `INST.SENS.COOL.LVL` | F66 kylvätskenivå | sw/gn | **→ I10 (PDM)** | 🔄 **Flyttad från RPi GPIO** |
| 61 | `INST.SENS.COOL.LVL.GND` | F66 kylniva jord | br | -> Chassijord | — |
| 62 | `INST.SENS.BRAKE_FAULT` | Bromsfel-givare | bl/ws | **→ I13 (PDM)** | 🆕 **Ny givare — behöver installeras** |
| 63 | `INST.LAMP.HIGHBEAM` | K1 helljus bla lampa | ws/bl | Parallell med O7/O16 | — |
| 64 | `INST.LAMP.OIL` | K3 oljetryck rod | bl/gn | Master Varning (O9) | 🔄 **Drivs av O9 WARN.MASTER nu** |
| 65 | `INST.LAMP.TURN` | K5 blinkers gron | sw/bl | Drivs av O8 (D5) IND.TURN | 🆕 **O8 aktiverad i v9.0** |
| 66 | `INST.LAMP.COOLANT` | K28 kylvatska rod | bl/ro | Master Varning (O9) | — |

### Nummerplatsbelysning

| # | Etikett | Komponent | Farg | Koppling |
|---|---------|-----------|------|----------|
| 67 | `INST.LIC.PLATE` | X nummerplat | gr | Via O6 PARK, jord via GND.REAR.BUS |

---

## Ändringar v6.0 → v7.0

### 🔴 Kritiska — kräver fysisk omkoppling

| # | Vad | Före (v6.0) | Efter (v9.0/v7.0) | Åtgärd |
|---|-----|-------------|-------------------|--------|
| 1 | **PARK output** | O24 (D3) | **O6 (D9)** | Flytta parkljus-distributionskabeln från D3 → D9 |
| 2 | **TURN_R output** | O6 (D9) | **O24 (D3)** | Flytta blinkers-fram/bak-kabeln från D9 → D3 |
| 3 | **REVERSE input** | I14 (C12) | **I7 (A10)** | Flytta F4 backväxelkontakt-kabeln från C12 → A10 |
| 4 | **OIL.PRESS input** | RPi GPIO | **I14 (C12)** | Dra F1 oljetryck till PDM C12 (v5.7-plan ska redan vara klar) |
| 5 | **COOLANT_LOW input** | RPi GPIO | **I10 (A2)** | Dra F66 kylvätskenivå till PDM A2 |
| 6 | **FUEL_LVL** | I13 (C11) → PDM | **ADS1115 (RPi)** | Koppla om bränslegivaren från PDM C11 till ADS1115 analog-input |
| 7 | **BRAKE_FAULT input** | — | **I13 (C11)** | Installera ny bromsfel-givare till PDM C11 |
| 8 | **WIPER_SPEED input** | I9/I10 digital | **I9 (A11) analog** | Bygg spänningsdelare vid E22 (likt blåsare), 1 kabel istället för 2 |

### 🟢 Aktiverat — kabel finns men output var disabled

| # | Vad | Status v6.0 | Status v9.0 | Åtgärd |
|---|-----|-------------|-------------|--------|
| 9 | O8 IND.TURN | RESERVE_8 | ENABLED | Verifiera att kabeln till K5 blinkerkontrollampa är dragen från D5 |
| 10 | O9 WARN.MASTER | RESERVE_9 | ENABLED | Verifiera att kabeln till varningslampa-distributionen är dragen från D4 |

### 🟡 Borttaget / vilande

| # | Vad | Status |
|---|-----|--------|
| 11 | O18 RADIO MEM | Disabled. Om radio kräver minne — vissa moderna har egen knappcells-backup, annars använd O20 RADIO_ACC permanent |
| 12 | I14 REVERSE | Flyttad till I7. Den gamla `sw/bl`-kabeln från F4 → C12 dras om till A10 |

---

## SAMMANFATTNING

| Kategori | Tejp | Antal | Ändring vs v6.0 |
|----------|------|-------|------------------|
| Strom + jord PDM | GUL + SVART | 5 | 0 |
| Motorkablar (ej PDM) | GUL/GRON | 4 | 0 |
| PDM Outputs | GUL | 29 | -1 (O18 RADIO MEM bort) |
| PDM Inputs | BLA | 14 unika | 0 (men 5 har bytt funktion) |
| CAN-bus | BLA | 2 | 0 |
| Jordar | SVART | 4 | 0 |
| Givare/lampor | GRON | 12 | +1 (BRAKE_FAULT givare) |
| **TOTALT etiketter att printa** | | **~67 st** | 0 |

> Varje kabel marks i BADA andar = **~134 etiketter totalt**.
> 6mm tejp for allt utom GND.BAT (25mm²), GND.ENGINE (16mm²), PDM.GND.CHASSIS (10mm²), PDM.PWR.BAT+ (32mm²), PDM.ENG.BAT->START (35mm²) — dar 12mm.

---

## Verifierings-checklista (för installation)

Inför första uppstart med v9.0-konfigen:

- [ ] **#1 PARK-kabel:** Distribution till parkljus M1/M3/M2/M4/X ska gå från **D9 (O6)**, inte D3
- [ ] **#2 TURN-R-kabel:** Höger blinkers ska gå från **D3 (O24)**, inte D9
- [ ] **#3 REVERSE-kabel:** F4 backväxelkontakt på **A10 (I7)**, inte C12
- [ ] **#4 OIL.PRESS-kabel:** F1 till **C12 (I14)**, inte RPi GPIO
- [ ] **#5 COOLANT_LOW-kabel:** F66 till **A2 (I10)**, inte RPi GPIO
- [ ] **#6 FUEL-givare:** Till ADS1115 (analog-bridge), inte PDM C11
- [ ] **#7 BRAKE_FAULT-givare:** Ny givare installerad och kopplad till C11
- [ ] **#8 WIPER-spakdelare:** E22 omkopplad till spänningsdelare (1 kabel till A11), inte 2 separata digitalkablar
- [ ] **#9 IND.TURN:** Kabel från D5 till K5 finns (kan ha funnits tidigare som testpunkt)
- [ ] **#10 WARN.MASTER:** Kabel från D4 till varningslamps-distribution finns
- [ ] **DBC + bridge:** Se separat audit `docs/audits/2026-05-20-pdm-v9-can-drift.md` i Pi-projektet — konsumenterna i driver-dash och st7789-bridge har stale input-mappningar som måste uppdateras innan dashboard visar rätt indikatorer

---

*Genererad 2026-05-20 från Elton_v9.0.HWPDM. Skiljer sig från v6.0 i 12 fysiska wire-routings (8 ändringar + 2 nya outputs aktiverade + 2 borttagna).*
