# ELTON — Komplett Kabelmärkning & PDM-konfiguration v5.7
## VW LT31 1976 | JSN 398 | Hardwire Electronics PDM25 V2
## Dymo Märkningslista · Configurator-inställningar · Fullständig pinout

---

### Om detta arbete

Vid inspektion av fordonets elsystem konstaterades att den originala säkringscentralen från 1976 hade allvarliga skador — flera säkringshållare var smälta och interna lödningar hade gått sönder efter nästan 50 års bruk. Utöver detta hade tidigare ägare utfört ett flertal felkopplade reparationer och provisoriska lösningar som skapade brandrisker och gjorde felsökning extremt svår.

Under 2026 har därför **hela elsystemet byggts om från grunden** på ett fackmannamässigt sätt. Arbetet är utfört enligt tillverkarens kopplingsscheman (Haynes Service & Repair Manual) och fullständigt dokumenterat i denna handling.

**Den originala säkringscentralen, alla mekaniska reläer och provisorier har ersatts med en Hardwire Electronics PDM25 V2** — en modern, solid-state strömfördelningsenhet med 25 outputs, 16 inputs, inbyggd IMU och CAN-bus.

#### PDM25 V2 — Nyckeldata ur manual

| Parameter | Värde |
|-----------|-------|
| Storlek | 200×160×54mm, 690g |
| Drifttemperatur | −55°C till +90°C |
| Driftspänning | 4–32V |
| Vilostrom (quiescent) | 4–5mA |
| Driftström (controller) | 210mA @ 12V |
| Outputs | 4× HS/LS (O1–O4) + 21× HS (O5–O25). 20A per kanal, 80A peak. Pinbegränsad 13A @125°C |
| Kombinerad max | 120A total output |
| Inputs | **16 st** analog/digital, 0–28V, **12-bit** (0.007V), 40kΩ PD + 200kΩ PU internt |
| 5V utgång (C10) | **100mA max** |
| PWM | Alla outputs, max 1000Hz |
| CAN | 1× CAN 2.0A/B, 50–1000 kbps, **mjukvarustyrd 120Ω terminering** |
| Kontakter | 4× Deutsch DT 12-pin |
| Loggning | 128Mb flash, 1–50Hz |

---

### Ändringslogg

| Version | Ändring |
|---------|---------|
| v5.2 | Grundkonfiguration PDM25 V2 |
| v5.3 | O1 signalbusbar, I5/I6 Momentary, I12 Active Low horn |
| v5.4 | Borttaget: dimljus, defroster, kupébelysning, instrumentbelysning, dörrkontakter |
| v5.5 | Engelska etiketter, PDM-namn ≤10 tecken |
| **v5.6** | **MANUAL-VERIFIERAD.** Korrigerad pinout (B7–B11, D1, D10). 16 inputs (I16=tändning). C3=batteri (always on). Blinkers via Timer+AND (ej PWM). 5V=100mA. 12-bit ADC. O2=torkare snabb. I3=varningsblinkers. I4=broms. I14=backväxel. Fullständiga input/output-parametrar. CAN-terminering mjukvarustyrd. |
| **v5.7** | **AUDIT-KORRIGERAD.** B1: huvud 32mm². K1: I15=START (terminal 50), O23 funktion uppdaterad. K2: O23 Stay On 0s (var 10s — farligt). K3: O24 = I7 Status (parkljus utan tändning, dual-pin D3+D10). K4: O3=IGN COIL, tändspole skyddad via PDM-output. D1: PARK-note. D2: Blower spänningstabell. D3: COIL.T1 grön tejp. B2/B5: RPi CAN-interlock dokumenterat. B4: CAN HAT terminering förtydligad. |
| **v5.8** | **SYNK-FIX.** Output-konfigurationstabell synkad mot kabelmärkning: O5=FUEL (D8), O7=HIBEAM R (D6), O24=PARK (D3+D10 dual-pin), O25=TURN L (B3+B10 dual-pin). Helljuslogik: O16/O7 (ej O16/O24). Verifieringschecklista uppdaterad. |

---

## ARKITEKTUR — STRÖM OCH TÄNDNING

### ⚠️ Viktig ändring i v5.6: C3 = Batteri+

PDM:en behöver ström på C3 för att vara igång. Eftersom vi har "Always On"-utgångar (RPi, radio-minne, signalbusbar) **måste C3 vara kopplad till batteri** — inte till tändningslås.

```
BATTERI+ ──► Batterifrånskiljare ──► Startmotor kl.30 ──┬──► M8-stud (output-ström, 32mm²)
                                                        │
                                                        └──► C3 (PDM controller-ström, 4mm²)

Tändningslås terminal 15 ──► I16 (C1) → PDM vet nu om tändning är PÅ/AV
Tändningslås terminal 50 ──► I15 (C2) → PDM vet om startknapp är nedtryckt
```

| Kabel | Från | Till | Dimension |
|-------|------|------|-----------|
| `PDM.PWR.BAT+` | Startmotor kl.30 | M8-stud | **32mm² ro** |
| `PDM.PWR.CTRL` | Startmotor kl.30 | C3 | 4mm² **ro** |
| `PDM.IN.IGNITION` | Tändningslås terminal 15 | I16 (C1) | 2.5mm² **sw/ge** |
| `PDM.IN.START` | Tändningslås terminal 50 | I15 (C2) | 2.5mm² **sw/ws** |

**Vilostrom:** 4–5mA när alla outputs av. Med RPi + radio-minne ≈ 2.5A.
**Global Cut-Off:** Batterispänning < 10.0V → alla outputs av → skyddar batteri.

---

## FÄRGKODNINGSSYSTEM

| Tejpfärg | System-prefix | Betydelse |
|----------|--------------|-----------|
| 🟡 **Gul tejp** | `PDM.OUT` | PDM Outputs — effektutgångar |
| 🔵 **Blå tejp** | `PDM.IN` | PDM Inputs — signaler in |
| ⚫️ **Svart tejp** | `GND` | Jordkablar |
| 🟢 **Grön tejp** | `INST` | Givare och kontrollampor |

> **Format:** `[SYSTEM].[TYPE].[FUNCTION]-[SIDE]` — L=Left, R=Right.
> **Märk BÅDA ändar** med samma etikett.
> 12mm tejp för ≥2.0mm², 9mm för tunnare. Krympslang som skydd.

---

## VW KABELFÄRGER — REFERENSTABELL

| Kod | Färg | Emoji | Typisk användning |
|-----|------|-------|-------------------|
| **ro** | Röd | 🔴 | Batteriström (terminal 30) |
| **sw** | Svart | ⚫️ | Diverse, ofta med delfärg |
| **ws** | Vit | ⚪️ | Helljus, halvljus |
| **ge** | Gul | 🟡 | Halvljus (kl.56a), helljus (kl.56b) |
| **gn** | Grön | 🟢 | Torkare (kl.53), kyltemp |
| **gr** | Grå | 🔘 | Parkljus, nummerplåt |
| **bl** | Blå | 🔵 | Generator D+ |
| **br** | Brun | 🟤 | Jord |
| **li** | Lila | 🟣 | Bränslegivare, tändsystem |

---

## 🟡 GULA ETIKETTER — PDM.OUT (Outputs)

### PDM Strömförsörjning

| Etikett | Kabel | Originalfärg | Från | Till |
|---------|-------|-------------|------|------|
| `PDM.PWR.BAT+` | **32mm²** | **ro** 🔴 | Startmotor kl.30 | PDM M8-stud (8Nm max!) |
| `PDM.PWR.CTRL` | 4mm² | **ro** 🔴 | Startmotor kl.30 | PDM Pin C3 |

### Strålkastare

| Etikett | Output | Pin | Kabel | Originalfärg | Till |
|---------|--------|-----|-------|-------------|------|
| `PDM.OUT.LOWBEAM-L` | O14 | B5 | 2.5mm² | **ge/sw** 🟡⚫️ | L1 vänster (kl.56a) |
| `PDM.OUT.LOWBEAM-R` | O15 | B4 | 2.5mm² | **ge** 🟡 | L2 höger (kl.56a) |
| `PDM.OUT.HIGHBEAM-L` | O16 | D12 | 2.5mm² | **ws/sw** ⚪️⚫️ | L1 vänster (kl.56b) |
| `PDM.OUT.HIGHBEAM-R` | O7 | D6 | 2.5mm² | **ws** ⚪️ | L2 höger (kl.56b) |

### Signal- och positionsljus

| Etikett | Output | Pin | Kabel | Originalfärg | Till |
|---------|--------|-----|-------|-------------|------|
| `PDM.OUT.PARK-F` | O24 | D3 | 1.5mm² | **gr** 🔘 | M1 sido V + M3 sido H (fram) |
| `PDM.OUT.PARK-R` | O24 | D10 | 1.5mm² | **gr/sw** 🔘⚫️ | M4 bak V + M2 bak H (bak) |

> 💡 **O24 är en dubbel-pin output (D3+D10).** Detta låter oss dra en kabel separat framåt (D3) och en bakåt (D10) för parkljuset utan att behöva splitta en grov kabel under instrumentbrädan.
| `PDM.OUT.TURN-L-F` | O25 | B3 | 1.5mm² | **sw/ws** ⚫️⚪️ | M5 blink V fram |
| `PDM.OUT.TURN-L-R` | O25 | B10 | 1.5mm² | **sw/ws** ⚫️⚪️ | M6 blink V bak |
> 💡 **O25 är en dubbel-pin output (B3+B10).** Låter oss dra separat kabel framåt och bakåt för Vänster blinkers.
| `PDM.OUT.TURN-R` | O6 | D9 | 1.5mm² | **sw/gn** ⚫️🟢 | M7 blink H + M8 bak H (splittas externt) |
| `PDM.OUT.BRAKE` | O4 | D7 | 2.0mm² | **sw/ro** ⚫️🔴 | M9 + M10 bromsljus |
| `PDM.OUT.REVERSE` | O19 | B1 | 2.0mm² | **sw/bl** ⚫️🔵 | M16 + M17 backljus |

### Busbar

| Etikett | Output | Pin | Kabel | Till |
|---------|--------|-----|-------|------|
| `PDM.OUT.BUSBAR` | O1 | C6 | 0.75mm² | Signalbusbar (terminalblock) |

> O1 = HS/LS kanal, konfigurerad som HS. Always On. **High Fuse 3.0A.**
> Matar switch-inputs (~10mA) + torkarmotor parkkrets (~1–2A vid parkering).

### Motorer och tillbehör

| Etikett | Output | Pin | Kabel | Originalfärg | Till |
|---------|--------|-----|-------|-------------|------|
| `PDM.OUT.WIPER.SLO` | O10 | **B7** | 2.5mm² | **gn** 🟢 | V torkarmotor kl.53 |
| `PDM.OUT.WIPER.FST` | O2 | **C5** | 2.5mm² | **sw/gr** ⚫️🔘 | V torkarmotor kl.53b |
| `PDM.OUT.BLOWER` | O11 | **B8** | 2.5mm² | **sw/ge** ⚫️🟡 | V2 kupéfläkt |
| `PDM.OUT.WASHER` | O12 | **B9** | 1.5mm² | **gn/ro** 🟢🔴 | V5 spolarpump |
| `PDM.OUT.HORN` | O13 | B6 | 2.0mm² | **sw/ge** ⚫️🟡 | H1 signalhorn |

> ⚠️ **B7=O10, B8=O11, B9=O12** — korrigerad pinout enligt manual (v5.5 hade fel).
> Fläkt run-on: Stay On 30s. Horn: Peak Fuse 8A/0.5s.

### Torkarmotor — Komplett kopplingsschema

Torkarmotorn har 5 terminaler. Inuti motorn sitter en **kamdriven kontakt** på
utgående axel som styr parkeringsfunktionen. Kontakten är sluten så länge
torkarbladen INTE är i parkläge.

| Terminal | Funktion |
|----------|----------|
| 53 | Slow winding (långsam hastighet) |
| 53b | Fast winding (snabb hastighet) |
| 53a | Parkkontakt utgång (kamdriven, inuti motor) |
| 31b | Parkkontakt andra sida (inuti motor) |
| 31 | Jord (motor-chassi) |

**Kopplingsschema:**

```
                    SIGNAL BUSBAR 12V (O1, 3A fuse)
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
  ┌──────┴──────┐    ┌─────┴─────┐    ┌──────┴──────┐
  │ E22 switch  │    │ E22 switch│    │ E22 switch  │
  │ pos: SLOW   │    │ pos: FAST │    │ pos: OFF    │
  └──────┬──────┘    └─────┬─────┘    └──────┬──────┘
         │                 │                  │
      PDM I10           PDM I9          Direkt till
      (pin A2)          (pin A11)       motor 53a
         │                 │            (ej via PDM)
         ▼                 ▼                  │
  ┌──── PDM ──────────────────┐               │
  │                           │               │
  │  O10 (B7) ─── 2.5mm² ────────────►┌──────┴───────────┐
  │  Fn: I10                  │        │   TORKARMOTOR     │
  │                           │        │                   │
  │  O2  (C5) ─── 2.5mm² ─────────►   │  53    53b        │
  │  Fn: I9                   │        │   │      │        │
  └───────────────────────────┘        │  SLOW   FAST      │
                                       │                   │
                                  ────►│  53a              │
                                       │   │  ┌─────────┐ │
                                       │   └──│KAMSWITCH │ │
                                       │      │sluten om │ │
                                       │      │ej i park │ │
                                       │   ┌──│         │ │
                                       │   │  └─────────┘ │
                                  ◄────│  31b              │
                                       │                   │
                                 GND──►│  31               │
                                       └───────────────────┘
                                              │
                       EXTERN JUMPER:  31b ──► 53
                       (vid motorns kontaktdon, 1.5mm²)
```

**Extra kabel vid motorn (parkkrets):**

| Etikett | Kabel | Från | Till | Not |
|---------|-------|------|------|-----|
| `PDM.OUT.WIPER.PARK` | 1.5mm² | Motor terminal 31b | Motor terminal 53 | Extern jumper vid kontaktdon |

**Hur parkeringen fungerar:**

| Steg | Vad händer |
|------|------------|
| 1 | Föraren slår spaken till AV → E22 kopplar busbar 12V direkt till terminal 53a |
| 2 | PDM: I9=OFF, I10=OFF → O2=OFF, O10=OFF (ingen PDM-matning) |
| 3 | Kamswitch inuti motorn är SLUTEN (bladen ej i park ännu) |
| 4 | Ström: Busbar → E22(AV) → 53a → kamswitch → 31b → **extern jumper** → 53 → slow winding → 31 (jord) |
| 5 | Motorn kör långsamt mot parkläge (~1–2A) |
| 6 | Bladen når park → kamswitch ÖPPNAR → ström bryts → motor stannar |

> ⚠️ Parkström ~1–2A flödar via busbaren under kort tid.
> **O1 High Fuse justerad till 3.0A** (från 1.0A) för att hantera parkström + switch-inputs.

### Motor via PDM

| Etikett | Output | Pin | Kabel | Originalfärg | Till |
|---------|--------|-----|-------|-------------|------|
| `PDM.OUT.FUEL` | O5 | D8 | 1.5mm² | **sw** ⚫️ | G6 bränslepump |
| `PDM.OUT.IGNITION` | **O3** | **C4** | 1.5mm² | **sw/li** ⚫️🟣 | N6 seriemotstånd (ingång) |
| `PDM.OUT.STARTER` | O23 | B2 | 2.5mm² | **ro/sw** 🔴⚫️ | Startrelä terminal 50 |

### Moderna tillägg

| Etikett | Output | Pin | Kabel | Till |
|---------|--------|-----|-------|------|
| `PDM.OUT.RADIO.MEM` | O18 | B12 | 1.0mm² | Radio permanent minne |
| `PDM.OUT.RADIO.ACC` | O20 | D11 | 1.5mm² | Radio ACC |
| `PDM.OUT.RPI` | O21 | D2 | 2.0mm² | Raspberry Pi 5 + CAN HAT |
| `PDM.OUT.USB12V` | O22 | **B11** | 1.5mm² | 12V USB-uttag |

> ⚠️ **O22 sitter på B11** (inte D1 som i v5.5). Korrigerad enligt manual.

### Lediga outputs

| Output | Pin | Typ | Status |
|--------|-----|-----|--------|
| O8 | D5 | HS | Ledig |
| O9 | D4 | HS | Ledig |
| O17 | D1 | HS | Ledig |

### Direktkablar motorrum (gul tejp — ej via PDM)

| Etikett | Kabel | Originalfärg | Från | Till |
|---------|-------|-------------|------|------|
| `PDM.ENG.BAT→START` | 35mm² | **ro** 🔴 | Batteri + via frånskiljare | Startmotor terminal 30 |
| `PDM.ENG.GEN.B+` | 6mm² | **ro** 🔴 | Generator B+ | Batteri + |
| `PDM.ENG.COIL.N6` | 1.0mm² | **ws/li** ⚪️🟣 | N6 seriemotstånd | Tändspole kl.15 |

> ⚠️ `PDM.ENG.COIL.T1` (tändspole kl.1 → fördelare) är en **motorsignalkabel**, märk med **grön tejp** (INST-kategori), ej gul. Den är inte en PDM-output.

---

## 🔵 BLÅ ETIKETTER — PDM.IN (Inputs)

### Tändning (v5.6 — ny!)

| Etikett | Input | Pin | Mode | Originalfärg | Från |
|---------|-------|-----|------|-------------|------|
| `PDM.IN.IGNITION` | **I16** | **C1** | **Momentary** | **sw/ge** ⚫️🟡 | Tändningslås terminal 15 |
| `PDM.IN.START` | **I15** | **C2** | **Momentary** | **sw/ws** ⚫️⚪️ | Tändningslås terminal 50 (startläge) |

> C3 = batteri always-on. I16 detekterar tändningsläge (kl.15). I15 detekterar startläge (kl.50, momentärt).

### Signalbusbar-matade inputs (12V från O1)

Switch kopplar busbarens 12V till PDM-input. Internt: 40kΩ PD + 200kΩ PU.

| Etikett | Input | Pin | Mode | Originalfärg | Från |
|---------|-------|-----|------|-------------|------|
| `PDM.IN.TURN-L` | I5 | A9 | **Momentary** | **sw/ws** ⚫️⚪️ | Blinkerspak vänster |
| `PDM.IN.TURN-R` | I6 | A4 | **Momentary** | **sw/gn** ⚫️🟢 | Blinkerspak höger |
| `PDM.IN.HAZARD` | **I3** | A8 | **Latching** | — | Varningsblinkersknapp |
| `PDM.IN.PARK` | I7 | A10 | Momentary | — | Parkljusswitch |
| `PDM.IN.WASHER` | I8 | A3 | Momentary | **gn/ro** 🟢🔴 | Höger spak (dra) |
| `PDM.IN.WIPER.FST` | I9 | A11 | Momentary | **sw/gr** ⚫️🔘 | Torkaromkopplare kl.53b |
| `PDM.IN.WIPER.SLO` | I10 | A2 | Momentary | **gn** 🟢 | Torkaromkopplare kl.53 |

### Direkt matade inputs (ej busbar)

| Etikett | Input | Pin | Mode | Originalfärg | Från |
|---------|-------|-----|------|-------------|------|
| `PDM.IN.BRAKE` | **I4** | A5 | **Momentary** | **sw/ro** ⚫️🔴 | Bromslysbrytare (bat → switch → I4) |
| `PDM.IN.REVERSE` | **I14** | C12 | **Momentary** | **sw/bl** ⚫️🔵 | Backväxelkontakt (bat → switch → I14) |
| `PDM.IN.BLOWER` | I1 | A7 | **Analog** | **sw/ge** ⚫️🟡 | E9 fläktomkopplare (4.7k+4.7k delare) |
| `PDM.IN.HIGHBEAM` | I2 | A6 | **Latching** | **ge** 🟡 | E4 helljusspak (kl.56b) |

> I4 broms: Direkt från batteri via bromsljusbrytare (funkar utan tändning).
> I14 backväxel: Direkt från tändning via växellådsbrytare.

### Horn — Active Low

| Etikett | Input | Pin | Mode | Originalfärg | Från |
|---------|-------|-----|------|-------------|------|
| `PDM.IN.HORN` | I12 | A1 | **Momentary Active Low** | **br/bl** 🟤🔵 | Hornknapp via slip ring |

```
SIGNAL BUSBAR 12V (from O1)
       │
    ┌──┴──┐
    │10kΩ │  External pull-up (monterad nära PDM A1)
    │1/4W │
    └──┬──┘
       │
       ├───── PDM I12 pin A1
       │
  VW horn cable (br/bl, via slip ring)
       │
       ▼
   HORN BUTTON ──── GND (chassis)
```

| State | I12 | O13 |
|-------|-----|-----|
| Not pressed | 12V (pull-up) | OFF |
| Pressed | 0V (GND) | ON |
| Cable broken | 12V (pull-up) | OFF (safe) |

### Analoga sensorinputs (5V referens via C10)

| Etikett | Input | Pin | Mode | Originalfärg | Från | Pull-up |
|---------|-------|-----|------|-------------|------|---------|
| `PDM.IN.COOLANT` | I11 | A12 | **Analog** | **gn** 🟢 | G2 NTC kyltemp | 1kΩ ext → C10 5V |
| `PDM.IN.FUEL.LVL` | I13 | C11 | **Analog** | **li/sw** 🟣⚫️ | G bränslegivare | 100Ω ext → C10 5V |

> ⚠️ C10 5V max **100mA** (ej 500mA som i v5.5). 1kΩ drar 5mA, 100Ω drar 50mA → totalt 55mA. OK.

### Lediga inputs

> ⚠️ Alla 16 inputs är nu tilldelade. Inga lediga inputs kvar. Reset sker via CAN-kommando eller strömcykel.

### CAN-bus

| Etikett | Pin | Kabel | Till |
|---------|-----|-------|------|
| `PDM.CAN.H` | C8 | 0.75mm² tvinnad **ws** | RPi CAN High |
| `PDM.CAN.L` | C9 | 0.75mm² tvinnad **sw** | RPi CAN Low |

> 250 kbps. PDM intern terminering **aktiveras i mjukvara**. Extern 120Ω krävs **endast på RPi-sidan**.
> ⚠️ **B4 — Viktigt:** Många RPi CAN HATs (Waveshare, PiCAN2, MCP2515-baserade) har **inbyggd 120Ω jumper aktiverad som standard**. Kontrollera ditt HAT-kretskort innan extern 120Ω monteras. Om HAT har inbyggd terminering: **montera INGEN extern motstånd** — bussen har redan 60Ω (PDM 120Ω + HAT 120Ω parallellt). Om extern 120Ω läggs till på ett HAT med inbyggd terminering = 3 parallella 120Ω = **40Ω** → CAN-fel.

### System

| Etikett | Pin | Kabel | Till |
|---------|-----|-------|------|
| `PDM.GND.CHASSIS` | C7 | 10mm² **br** 🟤 | Chassijord (punkt 12) |
| `PDM.5V.REF` | C10 | — | 5V **100mA** sensorutgång |

---

## 🔵 SIGNAL BUSBAR — Fysisk specifikation

```
PDM O1 pin C6 (Always On, 3A fuse)
  │
  │  0.75mm²
  ▼
┌──────────────────────────────────────────────────┐
│                SIGNAL BUSBAR 12V                  │
│  Pos: 1    2    3    4    5    6    7    8    9   │
└──┬────┬────┬────┬────┬────┬────┬────┬────┬───────┘
   │    │    │    │    │    │    │    │    │
   │    │    │    │    │    │    │    │    └─→ Reserve
   │    │    │    │    │    │    │    │
   │    │    │    │    │    │    │    └──→ 10kΩ → I12 (Horn Active Low)
   │    │    │    │    │    │    │
   │    │    │    │    │    │    └──→ I10 (Wiper slow, t.53)
   │    │    │    │    │    │
   │    │    │    │    │    └──→ I9 (Wiper fast, t.53b)
   │    │    │    │    │
   │    │    │    │    └──→ I8 (Washer)
   │    │    │    │
   │    │    │    └──→ I7 (Park lights)
   │    │    │
   │    │    └──→ I3 (Hazard — Latching)
   │    │
   │    └──→ I5/I6 (Turn L/R via stalk)
   │
   └──→ Reserve
```

**EJ via busbar:** I1 (blower analog), I2 (high beam), I4 (brake), I11 (coolant 5V), I13 (fuel 5V), I14 (reverse), I16 (ignition)

---

## ⚫️ SVARTA ETIKETTER — GND

### Systemjordar

| Etikett | Kabel | Från | Till |
|---------|-------|------|------|
| `GND.BAT` | 25mm² **br** | Batteri − | Chassi framdel (punkt 1) |
| `GND.ENGINE` | 16mm² **br** | Motorblock | Chassi (punkt 3) |

### Jordsamlingsplint BAK

| Etikett | Kabel | Från | Till |
|---------|-------|------|------|
| `GND.REAR.BUS` | 4mm² **br** | Jordplint | Chassi bak M8 (punkt 15) |
| `GND.REAR.BRAKE-L` | 1.5mm² **br** | M9 | Jordplint |
| `GND.REAR.BRAKE-R` | 1.5mm² **br** | M10 | Jordplint |
| `GND.REAR.REV-L` | 1.5mm² **br** | M16 | Jordplint |
| `GND.REAR.REV-R` | 1.5mm² **br** | M17 | Jordplint |
| `GND.REAR.PARK-L` | 1.0mm² **br** | M4 | Jordplint |
| `GND.REAR.PARK-R` | 1.0mm² **br** | M2 | Jordplint |
| `GND.REAR.TURN-L` | 1.0mm² **br** | M6 | Jordplint |
| `GND.REAR.TURN-R` | 1.0mm² **br** | M8 | Jordplint |

---

## 🟢 GRÖNA ETIKETTER — INST (Givare & Sensorer)

| Etikett | Komponent | Funktion | Originalfärg | Koppling |
|---------|-----------|----------|-------------|----------|
| `INST.SENS.FUEL` | G | Bränslegivare | **li/sw** 🟣⚫️ | → I13 via 100Ω PU |
| `INST.SENS.FUEL.GND` | G | Bränslegivare jord | **br** 🟤 | → Chassijord |
| `INST.SENS.COOLANT` | G2 | Kyltemp NTC | **gn** 🟢 | → I11 via 1kΩ PU |
| `INST.SENS.OIL` | F1 | Oljetryck | **bl/gn** 🔵🟢 | → RPi GPIO |
| `INST.SENS.COOL.LVL` | F66 | Kylvätskenivå | **li/sw** 🟣⚫️ | → RPi GPIO |
| `INST.SENS.COOL.LVL.GND` | F66 | Kylnivå jord | **br** 🟤 | → Chassijord |
| `INST.LAMP.HIGHBEAM` | K1 | Helljus blå | **ws/bl** ⚪️🔵 | — |
| `INST.LAMP.OIL` | K3 | Oljetryck röd | **bl/gn** 🔵🟢 | — |
| `INST.LAMP.TURN` | K5 | Blinkers grön | **sw/bl** ⚫️🔵 | — |
| `INST.LAMP.COOLANT` | K28 | Kylvätska röd | **bl/ro** 🔵🔴 | — |
| `INST.LIC.PLATE` | X | Nummerplåt | **gr** 🔘 | — |
| `INST.LIC.PLATE.GND` | X | Nummerplåt jord | **br** 🟤 | — |

---

## ⚙️ TIMER-KONFIGURATION (Configurator → Timer Tab)

### Timer 1 — BLINK TMR (blinkerfrekvens)

> ⚠️ **Blinkers styrs INTE med PWM på output!** Korrekt metod (ur manualen):
> Skapa en Timer (Pulse Train) och AND:a timerns status med input-status i output-funktionen.

| Parameter | Värde |
|-----------|-------|
| Label | `BLINK TMR` |
| Mode | **Pulse Train** |
| On Time | **400 ms** |
| Off Time | **400 ms** |
| Enabled | ✅ |

> Ger ca 1.25 Hz blinkfrekvens (400+400=800ms period). Justeras vid behov.

---

## ⚙️ GENERIC FUNCTIONS (Configurator → Generic Functions Tab)

### GF1 — Ignition detect

| Parameter | Värde |
|-----------|-------|
| Label | `IGN ON` |
| Function | `I16 Status = True` |

> Används i output-logik där "tändning PÅ" krävs.

---

## ⚙️ PDM25 V2 — INPUT-KONFIGURATION (Configurator → Input Tab)

> **PDM-namn** = exakt det du skriver i Configurator. Max 10 tecken.

| Input | PDM-namn | Mode | Active | Threshold | Hysteresis | Delay | EMA | Källa |
|-------|----------|------|--------|-----------|------------|-------|-----|-------|
| I1 | `BLOWER` | **Analog** | — | — | — | 0s | 5 | E9 fläktvred (4.7k+4.7k) |
| I2 | `HIBEAM` | **Latching** | High | 6.0V | 1.0V | 0s | 0 | E4 helljusspak |
| I3 | `HAZARD` | **Latching** | High | 6.0V | 1.0V | 0s | 0 | Varningsblinkersknapp |
| I4 | `BRAKE` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Bromsljusbrytare |
| I5 | `TURN L` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Blinkerspak V |
| I6 | `TURN R` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Blinkerspak H |
| I7 | `PARK` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Parkljusswitch |
| I8 | `WASHER` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Spolarspak |
| I9 | `WIPER FST` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | E22 kl.53b |
| I10 | `WIPER SLO` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | E22 kl.53 |
| I11 | `COOLANT` | **Analog** | — | — | — | 0s | 10 | G2 NTC (1kΩ→5V) |
| I12 | `HORN` | **Momentary** | **Low** | 6.0V | 1.0V | 0s | 0 | Hornknapp (10kΩ ext PU) |
| I13 | `FUEL LVL` | **Analog** | — | — | — | 0s | 10 | G tanksändare (100Ω→5V) |
| I14 | `REVERSE` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Backväxelkontakt |
| I15 | `START` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Tändningslås terminal 50 |
| I16 | `IGNITION` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Tändningslås t.15 |

> **Threshold 6.0V + Hysteresis 1.0V:** Slår PÅ vid >6V, slår AV vid <5V. Enl. manual-rekommendation.
> **EMA 5–10** på analoga givare: Jämnar ut brus. Högre = mer utjämning.
> **Active Low (I12):** Slår PÅ vid <6V, slår AV vid >7V.

---

## ⚙️ PDM25 V2 — OUTPUT-KONFIGURATION (Configurator → Output Tab)

> **PDM-namn** = exakt det du skriver i Configurator. Max 10 tecken.

| Output | PDM-namn | Trip | Low Fuse | High Fuse | Peak Fuse | Peak Time | Stay On | Delay | Clear | Retries | Soft Start | Funktion |
|--------|----------|------|----------|-----------|-----------|-----------|---------|-------|-------|---------|------------|----------|
| O1 | `BUSBAR` | Normal | 0 | **3.0A** | — | — | 0s | 0s | 2s | 3 | Av | Always True |
| O2 | `WIPER FST` | Normal | 0 | 7.0A | 12A | 3s | 0s | 0s | 2s | 2 | 1s | I9 Status |
| O3 | `IGN COIL` | Normal | 0 | 5.0A | — | — | 0s | 0s | 2s | 3 | Av | GF1 |
| O4 | `BRAKE` | **Instant** | 0 | 5.0A | — | — | 0s | 0s | 1s | 3 | Av | I4 Status (HS!) |
| O5 | `FUEL` | Normal | 0 | 8.0A | 12A | 3s | **2s** | 0s | 3s | 2 | 1s | GF1 |
| O6 | `TURN R` | Normal | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | Timer1 AND (I6 OR I3) |
| O7 | `HIBEAM R` | Normal | 0 | 6.0A | — | — | 0s | 0s | 2s | 3 | Av | O15 AND I2 |
| O8 | `RESERVE 8` | — | — | — | — | — | — | — | — | — | — | — |
| O9 | `RESERVE 9` | — | — | — | — | — | — | — | — | — | — | — |
| O10 | `WIPER SLO` | Normal | 0 | 7.0A | 12A | 3s | 0s | 0s | 2s | 2 | 1s | I10 Status |
| O11 | `BLOWER` | Normal | 0 | 9.0A | 16A | 4s | **30s** | 0s | 3s | 2 | 1s | GF1 AND I1>1V |
| O12 | `WASHER` | Normal | 0 | 5.0A | 8A | 2s | 0s | 0s | 2s | 2 | Av | I8 Status |
| O13 | `HORN` | Normal | 0 | 6.0A | **8A** | **0.5s** | 0s | 0s | 1s | 3 | Av | I12 Status |
| O14 | `LOWBEAM L` | Normal | 0 | 6.0A | — | — | 0s | **3s** | 2s | 3 | Av | GF1 |
| O15 | `LOWBEAM R` | Normal | 0 | 6.0A | — | — | 0s | **3s** | 2s | 3 | Av | GF1 |
| O16 | `HIBEAM L` | Normal | 0 | 6.0A | — | — | 0s | 0s | 2s | 3 | Av | O14 AND I2 |
| O17 | `RESERVE17` | — | — | — | — | — | — | — | — | — | — | — |
| O18 | `RADIO MEM` | Normal | 0 | 1.0A | — | — | 0s | 0s | 2s | 3 | Av | Always True |
| O19 | `REVERSE` | Normal | 0 | 5.0A | — | — | 0s | 0s | 2s | 2 | Av | I14 Status |
| O20 | `RADIO ACC` | Normal | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | GF1 |
| O21 | `RPI` | Normal | 0 | 5.0A | — | — | 0s | 0s | 5s | 3 | 2s | Always True |
| O22 | `USB 12V` | Normal | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | GF1 |
| O23 | `STARTER` | Normal | 0 | 2.0A | — | — | **0s** | 0s | 5s | 0 | Av | GF1 AND I15 Status |
| O24 | `PARK` | Normal | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | I7 Status |
| O25 | `TURN L` | Normal | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | Timer1 AND (I5 OR I3) |

### Output-logik förklaring

**Blinkers (O25/O6) — Timer-baserad, EJ PWM:**
```
O25 funktion: Timer 1 Status AND (I5 Status OR I3 Status)
O6 funktion: Timer 1 Status AND (I6 Status OR I3 Status)
```
- Timer 1 = Pulse Train 400/400ms → blinkar
- I5/I6 = momentary (spaken hålls fysiskt i position av VW-mekanismen)
- I3 = latching hazard (tryck en gång → PÅ, igen → AV)
- Hazard: Båda sidor blinkar samtidigt

**Halvljus (O14/O15) — Turn On Delay 3s:**
- Fördröjer 3 sekunder efter tändning → ersätter J59 X-kontaktrelä
- Funktion: GF1 (I16 Status = True)

**Helljus (O16/O7) — Toggle:**
- O16: O14 Status = On AND I2 Status = True
- O7: O15 Status = On AND I2 Status = True
- I2 latchar vid spakdrag → helljus på/av

**Kupéfläkt (O11) — PWM mapping, 11-punktstabell:**

| I1 Voltage | 0V | 1V | 2V | 3V | 4V | 5V | 6V | 8V | 10V | 11V | 12V |
|------------|----|----|----|----|----|----|----|----|-----|-----|-----|
| Duty % | 0 | 0 | 0 | 0 | 0 | 0 | 40 | 40 | 70 | 70 | 100 |

> 0–5V = AV. ~6V = steg 1 (40%). ~10V = steg 2 (70%). ~12V = steg 3 (100%).
> Stay On 30s: kör vidare efter tändning av → blåser ut restvärme.

**E9 Fläktvred — Switch-position → spänning (D2):**

| Position E9 | Approx. spänning I1 | Duty % | Kommentar |
|-------------|---------------------|--------|-----------|
| OFF | ~2V (intern pull-down) | 0% | Switch öppen — intern PDM 40kΩ PD dominerar |
| 1 | ~6V | 40% | Verifieras med voltmeter |
| 2 | ~10V | 70% | Verifieras med voltmeter |
| 3 | ~12V | 100% | Direkt busspänning |

> ⚠️ Exakta spänningsnivåer beror på E9:s interna resistornät. **Mät med voltmeter i varje switchläge** och justera PWM-tabellen om avvikelse >0.5V från ovanstående.

**Torkare — 2 outputs + parkkrets:**
- O10 (B7, slow): I10 Status = True
- O2 (C5, fast): I9 Status = True
- VW-spaken har mekanisk interlock (bara en position åt gången)
- **Parkkrets:** Extern jumper 31b→53 vid motorns kontaktdon (1.5mm²)
- E22 i AV-läge kopplar busbar 12V direkt till 53a → kamswitch → 31b → jumper → 53 → motor parkerar
- O1 busbar fuse justerad till 3.0A för att hantera parkström (~1–2A)

**Tändspole (O3 IGN COIL — K4):**
- O3 funktion: GF1 (tändning PÅ → spole får ström)
- O3 (C4) → kabel `PDM.OUT.IGNITION` → N6 seriemotstånd (ballast) → tändspole kl.15
- Kabel internt i motorlocket: N6 → spole kl.15 (COIL.N6, ws/li)
- High Fuse 5.0A skyddar kretsen. O3 är HS/LS-kanal, konfigureras som HS.

**Parkljus (O24 PARK — K3):**
- O24 funktion: `I7 Status` (parkljusswitch → output PÅ, oavsett tändning)
- Parkljus ska fungera med tändning AV — terminal 30-krets per trafikregler
- I7 matas från signalbusbaren (O1, always-on)

**Startmotor (O23 STARTER — K1, K2, B5):**
- O23 funktion: `GF1 AND I15 Status` (tändning PÅ OCH startknapp nedtryckt)
- I15 (C2) = tändningslåsets terminal 50 (startläge, momentärt) → Momentary Active High
- Stay On = **0s** — startmotorn stannar omedelbart när knappen släpps
- ⚠️ **B5 Starterinterlock:** RPi övervakar oljetryck (F1 → GPIO). Om oljetryck detekteras (motor igång) skickar RPi CAN-kommando som disablar O23 → skyddar kuggkrans mot ingrepp i roterande motor.

**Bränslepump (O5 FUEL — D8):**
- O5 funktion: `GF1` (tändning PÅ → pump PÅ), Stay On 2s
- ⚠️ **B2 Motorstall-skydd:** RPi övervakar oljetryck via GPIO (F1). Om motor stannar med tändning kvar (oljetryck faller → GPIO LOW) skickar RPi CAN-kommando som stänger O5 → förhindrar bränslesvämning och brandrisk.

---

## ⚙️ GENERAL SETTINGS (Configurator → General Tab)

| Parameter | Värde |
|-----------|-------|
| CAN Bus Speed | **250 kbps** |
| CAN Termination | **Aktiverad** (PDM i ena änden) |
| Reset Function | **CAN-kommando** (via RPi) eller strömcykel — I15 används nu för START |
| Cut Off Function | Battery Voltage < 10.0V |
| Password | Sätt efter slutlig verifiering |

---

## 📌 CONNECTOR PINOUT — PDM25 V2 (verifierad mot manual)

### Connector A (12 pins)

| Pin | Manual | Vår signal |
|-----|--------|-----------|
| A1 | Input 12 | I12 Horn (Active Low) |
| A2 | Input 10 | I10 Wiper slow |
| A3 | Input 8 | I8 Washer |
| A4 | Input 6 | I6 Turn R |
| A5 | Input 4 | I4 **Brake** (NY) |
| A6 | Input 2 | I2 High beam toggle |
| A7 | Input 1 | I1 Blower (Analog) |
| A8 | Input 3 | I3 **Hazard** (NY) |
| A9 | Input 5 | I5 Turn L |
| A10 | Input 7 | I7 Park lights |
| A11 | Input 9 | I9 Wiper fast |
| A12 | Input 11 | I11 Coolant temp (Analog) |

### Connector B (12 pins)

| Pin | Manual | Vår signal |
|-----|--------|-----------|
| B1 | Output 19 | O19 Reverse |
| B2 | Output 23 | O23 Starter relay |
| B3 | Output 25 | O25 Turn L (Fram) |
| B4 | Output 15 | O15 Low beam R |
| B5 | Output 14 | O14 Low beam L |
| B6 | Output 13 | O13 Horn |
| **B7** | **Output 10** | **O10 Wiper slow** ⚠️ |
| **B8** | **Output 11** | **O11 Blower** ⚠️ |
| **B9** | **Output 12** | **O12 Washer** ⚠️ |
| **B10** | **Output 25** | O25 Turn L (Bak, parallell med B3) |
| **B11** | **Output 22** | **O22 USB 12V** ⚠️ |
| B12 | Output 18 | O18 Radio memory |

> B10 dubbel-pin O25 (extra strömkapacitet). B7–B11 korrigerade.

### Connector C (12 pins)

| Pin | Manual | Vår signal |
|-----|--------|-----------|
| **C1** | **Input 16** | **I16 Ignition** ⚠️ |
| C2 | Input 15 | **I15 Start (terminal 50)** |
| C3 | **PDM Power** | **Batteri+** via frånskiljare ⚠️ |
| C4 | Output 3 (HS/LS) | **O3 IGN COIL (tändspole)** |
| C5 | Output 2 (HS/LS) | **O2 Wiper fast** (NY) |
| C6 | Output 1 (HS/LS) | O1 Busbar |
| C7 | Ground | PDM chassijord (10mm²) |
| C8 | CAN 1 High | CAN-H → RPi |
| C9 | CAN 1 Low | CAN-L → RPi |
| C10 | 5V Out | 5V **100mA** sensorutgång |
| C11 | Input 13 | I13 Fuel level (Analog) |
| C12 | Input 14 | **I14 Reverse** (NY) |

### Connector D (12 pins)

| Pin | Manual | Vår signal |
|-----|--------|-----------|
| **D1** | **Output 17** | O17 *Ledig* ⚠️ (v5.5 hade O22 — FEL) |
| D2 | Output 21 | O21 RPi 5 |
| D3 | Output 24 | O24 Parkljus (Fram) |
| D4 | Output 9 | O9 *Ledig* |
| D5 | Output 8 | O8 *Ledig* |
| D6 | Output 7 | O7 High beam R |
| D7 | Output 4 (HS/LS) | O4 Brake (konfigurera HS!) |
| D8 | Output 5 | O5 Fuel pump |
| D9 | Output 6 | O6 Turn R |
| **D10** | **Output 24** | O24 Parkljus (Bak, parallell med D3) |
| D11 | Output 20 | O20 Radio ACC |
| D12 | Output 16 | O16 High beam L |

> D10 dubbel-pin O24 (extra strömkapacitet).

---

## 📡 CAN OUTPUT STREAM (Configurator → CAN Stream Tab)

| Frame | Data | Frekvens |
|-------|------|----------|
| 0x100 | Output-strömmar (mA) | 10 Hz |
| 0x101 | Input-spänningar (mV) | 10 Hz |
| 0x102 | Batterispänning, PCB-temp | 2 Hz |
| 0x103 | Output-status (on/off/trip) | 10 Hz |
| 0x104 | IMU acceleration (X,Y,Z) | 10 Hz |

> Aktivera CAN Stream i Configurator. DBC-fil finns på hardwire-electronics.co.uk/downloads

---

## ❌ BORTTAGET (jämfört med original 1976)

| Borttaget | Ersatt av |
|-----------|-----------|
| Original säkringscentral | PDM25 V2 |
| J2 Varningsblinkersrelä | PDM Timer 1 (Pulse Train) + AND-logik |
| J31 Torkarintervallrelä | PDM firmware |
| J59 X-kontaktrelä | PDM Turn On Delay 3s |
| K2 Laddningslampa | Digital via CAN → RPi |
| N23 Fläkt seriemotstånd | PDM PWM 11-punktstabell |
| Dörrkontakter | Ej monterade |
| Instrumentbelysning | Ej monterad |
| Bakrutedefroster | Ej monterad |
| Kupébelysning | Ej monterad |
| Dimljus | Aldrig monterat |

---

## ETIKETTÖVERSIKT — FULLSTÄNDIG LISTA

### 🟡 Gul tejp (29 st)

| # | Etikett |
|---|---------|
| 1 | `PDM.PWR.BAT+` |
| 2 | `PDM.PWR.CTRL` |
| 3 | `PDM.OUT.BUSBAR` |
| 4 | `PDM.OUT.LOWBEAM-L` |
| 5 | `PDM.OUT.LOWBEAM-R` |
| 6 | `PDM.OUT.HIGHBEAM-L` |
| 7 | `PDM.OUT.HIGHBEAM-R` |
| 8 | `PDM.OUT.PARK` *(PDM-sidan, kabel D6 → grenuttag)* |
| 9 | `PDM.OUT.PARK-L` *(vid grenuttaget, V-gren)* |
| 10 | `PDM.OUT.PARK-R` *(vid grenuttaget, H-gren)* |
| 11 | `PDM.OUT.TURN-L` |
| 12 | `PDM.OUT.TURN-R` |
| 13 | `PDM.OUT.BRAKE` |
| 14 | `PDM.OUT.REVERSE` |
| 15 | `PDM.OUT.WIPER.SLO` |
| 16 | `PDM.OUT.WIPER.FST` |
| 17 | `PDM.OUT.WIPER.PARK` |
| 18 | `PDM.OUT.BLOWER` |
| 19 | `PDM.OUT.WASHER` |
| 20 | `PDM.OUT.HORN` |
| 21 | `PDM.OUT.FUEL` |
| 22 | `PDM.OUT.IGNITION` |
| 23 | `PDM.OUT.STARTER` |
| 24 | `PDM.OUT.RADIO.MEM` |
| 25 | `PDM.OUT.RADIO.ACC` |
| 26 | `PDM.OUT.RPI` |
| 27 | `PDM.OUT.USB12V` |
| 28 | `PDM.ENG.BAT→START` |
| 29 | `PDM.ENG.GEN.B+` |

### 🔵 Blå tejp (18 st)

| # | Etikett |
|---|---------|
| 1 | `PDM.IN.IGNITION` |
| 2 | `PDM.IN.START` |
| 3 | `PDM.IN.TURN-L` |
| 4 | `PDM.IN.TURN-R` |
| 5 | `PDM.IN.HAZARD` |
| 6 | `PDM.IN.PARK` |
| 7 | `PDM.IN.WASHER` |
| 8 | `PDM.IN.WIPER.FST` |
| 9 | `PDM.IN.WIPER.SLO` |
| 10 | `PDM.IN.BRAKE` |
| 11 | `PDM.IN.REVERSE` |
| 12 | `PDM.IN.HORN` |
| 13 | `PDM.IN.BLOWER` |
| 14 | `PDM.IN.HIGHBEAM` |
| 15 | `PDM.IN.COOLANT` |
| 16 | `PDM.IN.FUEL.LVL` |
| 17 | `PDM.CAN.H` |
| 18 | `PDM.CAN.L` |

### ⚫️ Svart tejp (11 st)

| # | Etikett |
|---|---------|
| 1 | `GND.BAT` |
| 2 | `GND.ENGINE` |
| 3 | `GND.REAR.BUS` |
| 4 | `GND.REAR.BRAKE-L` |
| 5 | `GND.REAR.BRAKE-R` |
| 6 | `GND.REAR.REV-L` |
| 7 | `GND.REAR.REV-R` |
| 8 | `GND.REAR.PARK-L` |
| 9 | `GND.REAR.PARK-R` |
| 10 | `GND.REAR.TURN-L` |
| 11 | `GND.REAR.TURN-R` |

### 🟢 Grön tejp (14 st)

| # | Etikett |
|---|---------|
| 1 | `INST.SENS.FUEL` |
| 2 | `INST.SENS.FUEL.GND` |
| 3 | `INST.SENS.COOLANT` |
| 4 | `INST.SENS.OIL` |
| 5 | `INST.SENS.COOL.LVL` |
| 6 | `INST.SENS.COOL.LVL.GND` |
| 7 | `INST.LAMP.HIGHBEAM` |
| 8 | `INST.LAMP.OIL` |
| 9 | `INST.LAMP.TURN` |
| 10 | `INST.LAMP.COOLANT` |
| 11 | `INST.LIC.PLATE` |
| 12 | `INST.LIC.PLATE.GND` |
| 13 | `PDM.ENG.COIL.T1` *(tändspole kl.1 → fördelare — motorsignalkabel)* |
| 14 | `PDM.ENG.COIL.N6` *(N6 → tändspole kl.15)* |

---

## SAMMANFATTNING

| Tejpfärg | System | Kablar | Etiketter (×2) |
|----------|--------|--------|----------------|
| 🟡 Gul | PDM.OUT + PDM.ENG | 29 | 58 |
| 🔵 Blå | PDM.IN + CAN | 18 | 36 |
| ⚫️ Svart | GND | 11 | 22 |
| 🟢 Grön | INST + motorsignaler | 14 | 28 |
| | **TOTALT** | **72** | **144 etiketter** |

### Resursanvändning

| Resurs | Använda | Lediga |
|--------|---------|--------|
| Outputs (25 st) | 22 | 3 (O8, O9, O17) |
| Inputs (16 st) | 16 | 0 |
| Timers (30 st) | 1 | 29 |
| Generic Functions | 1 | — |
| CAN Inputs | 0 | 100 |

---

## VERIFIERINGSCHECKLISTA ⚠️

### Grundläggande

- [ ] C3 kopplad till batteri+ via frånskiljare — **EJ tändningslås**
- [ ] I16 (C1) kopplad till tändningslås terminal 15
- [ ] I15 (C2) kopplad till tändningslås terminal 50 (startläge)
- [ ] M8-stud åtdragen till **8Nm max** (skadar kretskort om mer!)
- [ ] Jordkabel C7 minst 10mm²

### CAN-buss

- [ ] CAN-terminering **aktiverad i Configurator** (PDM i ena änden)
- [ ] **Kontrollera RPi CAN HAT** — har den inbyggd 120Ω? (se jumper/dokumentation)
  - HAT med inbyggd term: **montera INGEN extern 120Ω**
  - HAT utan inbyggd term: montera extern 120Ω vid HAT-kontaktet
- [ ] Mät **60Ω** (±5Ω) mellan CAN-H och CAN-L med bussen avstängd
- [ ] Tvinnad kabel, minst 1 twist per 3cm
- [ ] Stubbkablar max 30cm
- [ ] CAN-buss hastighet = 250 kbps

### Inputs

- [ ] I5/I6: Momentary, Active High, Threshold 6V, Hysteresis 1V
- [ ] I3: **Latching**, Active High — testa varningsblinkers PÅ/AV
- [ ] I4: Momentary, Active High — testa bromsljus
- [ ] I7: Momentary, Active High — testa parkljus **utan** tändning
- [ ] I12: Active **Low**, Threshold 6V — testa horn
- [ ] I14: Momentary — testa backljus i backväxel
- [ ] I15: Momentary, Active High — testa att startmotorn aktiverar vid kl.50 PÅ
- [ ] I16: Momentary — verifiera att GF1 visar True med tändning PÅ
- [ ] 10kΩ pull-up: Monterad nära PDM A1 (ej i motorrummet)
- [ ] Analoga givare (I1, I11, I13): EMA filter aktiverat
- [ ] E9 blower switch: mät spänning I1 i varje position och verifiera mot PWM-tabell

### Outputs

- [ ] O4 Broms: Konfigurerad som **HS** (ej LS!) i Configurator
- [ ] O3 IGN COIL: Funktion = GF1, High Fuse = 5.0A, konfigurerad som HS
- [ ] O25/O6: Funktion = **Timer 1 AND (I5/I6 OR I3)** — ej PWM!
- [ ] O7 HIBEAM R: Funktion = **O15 AND I2**, High Fuse 6.0A
- [ ] O24 PARK: Funktion = **I7 Status** (ej GF1! Ska fungera utan tändning)
- [ ] Timer 1: Pulse Train **400ms/400ms** aktiverad
- [ ] O11 Fläkt: PWM Mapping → I1 Voltage, 11-punktstabell inlagd
- [ ] O11 Stay On: **30s**
- [ ] O14/O15: Turn On Delay = **3s**
- [ ] O13 Horn: Peak Fuse **8A**, Peak Time **0.5s**
- [ ] O2 Wiper fast + O10 Wiper slow: Soft Start **1s**
- [ ] O23 Starter: Stay On **0s** (EJ 10s!), Retries = **0**, Funktion = GF1 AND I15 Status
- [ ] O5 Fuel pump: Soft Start 1s, Stay On **2s**, High Fuse 8A, Peak 12A/3s
- [ ] O25 Turn L: Funktion = **Timer1 AND (I5 OR I3)**, High Fuse 3.0A
- [ ] O21 RPi: Always True, Soft Start **2s**

### General Settings

- [ ] Global Cut-Off: Battery Voltage < **10.0V**
- [ ] Reset Function: Definierad
- [ ] CAN Stream: Aktiverad

### Fysiskt

- [ ] Torkarmotor: Extern jumper 31b→53 installerad vid motorns kontaktdon (1.5mm²)
- [ ] Torkarmotor: E22 i AV-läge kopplar busbar till 53a — verifiera med multimeter
- [ ] Torkarmotor: Testa parkering — slå av spaken, bladen ska köra till park och stanna
- [ ] O1 Busbar: High Fuse **3.0A** (klarar parkström ~1–2A + switch-inputs)
- [ ] G2 NTC: 1kΩ pull-up till C10 5V — mät R vid känd temp
- [ ] G tanksändare: 100Ω pull-up till C10 5V — mät R full/tom
- [ ] 5V totallast: 55mA av **100mA max** — marginal OK
- [ ] Alla kabelmärkningar: **BÅDA ändar** märkta

---

**Version:** 5.8
**Datum:** 2026-03-05
**Verifierad mot:** PDM15/25/35 Instruction Manual v1.0 (23 juni 2025)
**Tillägg v5.8:** Output-konfigurationstabell synkad mot kabelmärkning. O5=FUEL, O7=HIBEAM R, O24=PARK (dual-pin), O25=TURN L (dual-pin). Helljuslogik korrigerad.
**Status:** SYNKAD — redo för konfigurering i PDM Configurator och fysisk installation
