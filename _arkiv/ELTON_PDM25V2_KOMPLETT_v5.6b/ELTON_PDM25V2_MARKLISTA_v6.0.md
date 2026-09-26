# ELTON PDM25 V2 — Komplett Märklista v6.0
## VW LT31 1976 · JSN 398 · 2026-04-06
### Genererad från `pdm25_outputs_complete.json` v7.2

> **Märk BÅDA ändar.** 6mm tejp for de flesta kablar. 12mm for grova (>=10mm²). Krympslang som skydd.

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
| 9 | `PDM.ENG.COIL.T1` | — | — | Tandspole kl.1 | Fordelare | gron tejp |

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

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 14 | `PDM.OUT.PARK` | O6 | D9 | 1.5 | rod (ny) | Splitter -> M1 M3 M2 M4 X |
| 15 | `PDM.OUT.TURN-R-F` | O24 | D3 | 1.5 | sw/gn | M7 blink H fram |
| 16 | `PDM.OUT.TURN-R-R` | O24 | D10 | 1.5 | gron (ny) | M8 blink H bak |
| 17 | `PDM.OUT.TURN-L-F` | O25 | B3 | 1.5 | sw/ws | M5 blink V fram |
| 18 | `PDM.OUT.TURN-L-R` | O25 | B10 | 1.5 | gul (ny) | M6 blink V bak |
| 19 | `PDM.OUT.BRAKE` | O4 | D7 | 1.5 | bla (ny) | M9 + M10 bromsljus |
| 20 | `PDM.OUT.REVERSE` | O19 | B1 | 1.5 | gra (ny) | M16 + M17 backljus |

### Busbar (1 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 21 | `PDM.OUT.BUSBAR` | O1 | C6 | 0.75 | — (ny) | Signalbusbar (terminalblock) |

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
| 27 | `PDM.OUT.IGNITION` | O3 | C4 | 1.5 | sw/li | N6 seriemotstand |
| 28 | `PDM.OUT.FUEL` | O5 | D8 | 2x1.5 par. | sw+br | G6 branslepump |
| 29 | `PDM.OUT.STARTER` | O23 | B2 | 2.5 | ro/sw | B solenoid kl.50 |

### Instrumentering och varning (2 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 30 | `PDM.OUT.IND.TURN` | O8 | D5 | 1.5 | sw/bl | K5 blinkerkontrollampa |
| 31 | `PDM.OUT.WARN.MASTER` | O9 | D4 | 1.5 | ro | Varningslampa (CAN-styrd) |

### Moderna tillagg (3 st)

| # | Etikett | Output | Pin | mm2 | Farg | Till |
|---|---------|--------|-----|-----|------|------|
| 32 | `PDM.OUT.RADIO.ACC` | O20 | D11 | 1.5 | — (ny) | Radio ACC |
| 33 | `PDM.OUT.RPI` | O21 | D2 | 2.0 | — (ny) | Raspberry Pi 5 + CAN HAT |
| 34 | `PDM.OUT.USB12V` | O22 | B11 | 1.5 | — (ny) | 12V USB-uttag |

### Parkkrets (1 st)

| # | Etikett | mm2 | Farg | Fran | Till | Not |
|---|---------|-----|------|------|------|-----|
| 35 | `PDM.OUT.WIPER.PARK` | 1.5 | — | Motor t.31b | Motor t.53 | Extern jumper vid kontaktdon |

### Lediga outputs (ej kabel, ej markning)

| Output | Pin | Status |
|--------|-----|--------|
| O17 | D1 | Ledig |
| O18 | B12 | Ledig (radio-minne flyttat till O1 busbar) |

---

## BLA TEJP — PDM Inputs (16 st)

### Tandning (2 st — redan listad ovan under strom, samma label)

| # | Etikett | Input | Pin | Mode | Farg | Fran |
|---|---------|-------|-----|------|------|------|
| — | `PDM.IN.IGNITION` | I16 | C1 | Momentary | sw/ge | Tandningslas t.15 |
| — | `PDM.IN.START` | I15 | C2 | Momentary | sw/ws | Tandningslas t.50 |

### Signalbusbar-matade (7 st)

| # | Etikett | Input | Pin | Mode | Farg | Fran |
|---|---------|-------|-----|------|------|------|
| 36 | `PDM.IN.TURN-L` | I5 | A9 | Momentary | sw/ws | E2 blinkerspak V |
| 37 | `PDM.IN.TURN-R` | I6 | A4 | Momentary | gr | E2 blinkerspak H |
| 38 | `PDM.IN.HAZARD` | I3 | A8 | Latching | — | Varningsblinkersknapp |
| 39 | `PDM.IN.PARK` | I7 | A10 | Momentary | — | Parkljusswitch |
| 40 | `PDM.IN.WASHER` | I8 | A3 | Momentary | gn/ro | E22 spolarspak |
| 41 | `PDM.IN.WIPER.FST` | I9 | A11 | Momentary | sw/gr | E22 kl.53b |
| 42 | `PDM.IN.WIPER.SLO` | I10 | A2 | Momentary | gn | E22 kl.53 |

### Direkt matade (4 st)

| # | Etikett | Input | Pin | Mode | Farg | Fran |
|---|---------|-------|-----|------|------|------|
| 43 | `PDM.IN.BRAKE` | I4 | A5 | Momentary | sw/ro | F bromsljusbrytare (bat-matad) |
| 44 | `PDM.IN.REVERSE` | I14 | C12 | Momentary | sw/bl | F4 backvaxelkontakt |
| 45 | `PDM.IN.BLOWER` | I1 | A7 | Analog | sw/ge | E9 flaktomkopplare |
| 46 | `PDM.IN.HIGHBEAM` | I2 | A6 | Latching Low | ge | E4 helljusspak (jordswitchad) |

### Active Low (1 st)

| # | Etikett | Input | Pin | Mode | Farg | mm2 | Fran |
|---|---------|-------|-----|------|------|-----|------|
| 47 | `PDM.IN.HORN` | I12 | A1 | Momentary Low | br/bl | 1.0 | Hornknapp via slip ring |

### Analoga sensorer (2 st)

| # | Etikett | Input | Pin | Mode | Farg | Fran |
|---|---------|-------|-----|------|------|------|
| 48 | `PDM.IN.COOLANT` | I11 | A12 | Analog | gn | G2 NTC kyltemp (1k -> 5V) |
| 49 | `PDM.IN.FUEL.LVL` | I13 | C11 | Analog | li/sw | G branslegivare (100R -> 5V) |

---

## BLA TEJP — CAN-bus (2 st)

| # | Etikett | Pin | mm2 | Farg | Till |
|---|---------|-----|-----|------|------|
| 50 | `PDM.CAN.H` | C8 | 0.75 tvinnad | ws | RPi CAN High |
| 51 | `PDM.CAN.L` | C9 | 0.75 tvinnad | sw | RPi CAN Low |

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

## GRON TEJP — Givare och kontrollampor (11 st)

| # | Etikett | Komponent | Farg | Koppling |
|---|---------|-----------|------|----------|
| 56 | `INST.SENS.FUEL` | G branslegivare | li/sw | -> I13 via 100R PU |
| 57 | `INST.SENS.FUEL.GND` | G branslegivare jord | br | -> Chassijord |
| 58 | `INST.SENS.COOLANT` | G2 kyltemp NTC | gn | -> I11 via 1k PU |
| 59 | `INST.SENS.OIL` | F1 oljetryck | bl/gn | -> RPi GPIO |
| 60 | `INST.SENS.COOL.LVL` | F66 kylvatskeniva | li/sw | -> RPi GPIO |
| 61 | `INST.SENS.COOL.LVL.GND` | F66 kylniva jord | br | -> Chassijord |
| 62 | `INST.LAMP.HIGHBEAM` | K1 helljus bla lampa | ws/bl | Parallell med O7/O16 |
| 63 | `INST.LAMP.OIL` | K3 oljetryck rod | bl/gn | Master Varning / RPi |
| 64 | `INST.LAMP.TURN` | K5 blinkers gron | sw/bl | Drivs av O8 (D5) |
| 65 | `INST.LAMP.COOLANT` | K28 kylvatska rod | bl/ro | Master Varning / RPi |

### Nummerplatsbelysning

| # | Etikett | Komponent | Farg | Koppling |
|---|---------|-----------|------|----------|
| 66 | `INST.LIC.PLATE` | X nummerplat | gr | Via O6 PARK, jord via GND.REAR.BUS |

---

## SAMMANFATTNING

| Kategori | Tejp | Antal |
|----------|------|-------|
| Strom + jord PDM | GUL + SVART | 5 |
| Motorkablar (ej PDM) | GUL/GRON | 4 |
| PDM Outputs | GUL | 29 |
| PDM Inputs | BLA | 14 unika (I15/I16 delade med strom) |
| CAN-bus | BLA | 2 |
| Jordar | SVART | 4 |
| Givare/lampor | GRON | 12 |
| **TOTALT etiketter att printa** | | **~67 st** |

> Varje kabel marks i BADA andar = **~134 etiketter totalt**.
> 6mm tejp for allt utom GND.BAT (25mm²), GND.ENGINE (16mm²), PDM.GND.CHASSIS (10mm²), PDM.PWR.BAT+ (32mm²), PDM.ENG.BAT->START (35mm²) — dar 12mm.

---

*Genererad 2026-04-06 fran pdm25_outputs_complete.json v7.2.*
*Korrigeringar: Gemensam jordplint bak (ej individuella jordkablar per lampa). Nummerplat jord via samma plint. I6 farg: gr (ej sw/gn). O5 dimension: 2x1.5 parallell. Tejpbredd: 6mm standard.*
