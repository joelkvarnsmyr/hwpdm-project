# ELTON — Komplett Kabelmärkning & PDM-konfiguration v5.9
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
| **v5.9** | **CRASH+HORN+IND+STARTER.** Timer2 CRASH TMR (10 min, GF2). GF2 CRASH DET (MC1>40). Alla outputs utom RPi/blinkers: AND T2=F. Blinkers: OR T2 AND T1 (hazard vid crash). O8=IND.TURN (K5). O9=WARN.MASTER (CAN). Horn I12: extern 10kΩ → PDM intern 200kΩ. P028 borttagen, P051 direkt. **Externt startrelä borttaget** — O23 driver solenoid direkt (Peak 50A/0.5s, High 12A). RPi GPIO bromssäkerhet. |

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
| `PDM.OUT.PARK` | O6 | D9 | 1.5mm² | **röd** 🔴 | Terminal-splitter → M1 M3 M2 M4 X |
| `PDM.OUT.TURN-R-F` | O24 | D3 | 1.5mm² | **sw/gn** ⚫️🟢 | M7 blink H fram |
| `PDM.OUT.TURN-R-R` | O24 | D10 | 1.5mm² | **grön** 🟢 | M8 blink H bak |

> 💡 **O24 är en dubbel-pin output (D3+D10).** Detta låter oss dra en kabel separat framåt (D3) och en bakåt (D10) för höger blinkers.
| `PDM.OUT.TURN-L-F` | O25 | B3 | 1.5mm² | **sw/ws** ⚫️⚪️ | M5 blink V fram |
| `PDM.OUT.TURN-L-R` | O25 | B10 | 1.5mm² | **gul** 🟡 | M6 blink V bak |
> 💡 **O25 är en dubbel-pin output (B3+B10).** Låter oss dra separat kabel framåt och bakåt för vänster blinkers.
| `PDM.OUT.BRAKE` | O4 | D7 | 1.5mm² | **blå** 🔵 | M9 + M10 bromsljus |
| `PDM.OUT.REVERSE` | O19 | B1 | 1.5mm² | **grå** 🔘 | M16 + M17 backljus (drivs av I7 efter omallokering från PARK) |

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
| `PDM.OUT.STARTER` | O23 | B2 | 2.5mm² | **ro/sw** 🔴⚫️ | Solenoid kl.50 (direkt, inget relä) |

### Moderna tillägg

| Etikett | Output | Pin | Kabel | Till |
|---------|--------|-----|-------|------|
| `PDM.OUT.RADIO.ACC` | O20 | D11 | 1.5mm² | Radio ACC |
| `PDM.OUT.RPI` | O21 | D2 | 2.0mm² | Raspberry Pi 5 + CAN HAT |
| `PDM.OUT.USB12V` | O22 | **B11** | 1.5mm² | 12V USB-uttag |

> ⚠️ **O22 sitter på B11** (inte D1 som i v5.5). Korrigerad enligt manual.
> **Radio permanent minne** — flyttat från O18 till **O1 signalbusbar** (terminalblock). O18 (B12) nu ledig.

### Instrumentering och varning

| Etikett | Output | Pin | Kabel | Originalfärg | Till |
|---------|--------|-----|-------|-------------|------|
| `PDM.OUT.IND.TURN` | O8 | D5 | 1.5mm² | **sw/bl** ⚫️🔵 | K5 blinkers kontrollampa |
| `PDM.OUT.WARN.MASTER` | O9 | D4 | 1.5mm² | **ro** 🔴 | Varningslampa (K3/F) — CAN-styrd |

> O8 IND.TURN: Drivs direkt av PDM → eliminerar behovet av externa dioder från O24/O25.
> O9 WARN.MASTER: Default False — styrs via CAN Receive från RPi vid kritiska fel.

### Lediga outputs

| Output | Pin | Typ | Status |
|--------|-----|-----|--------|
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
| `PDM.IN.REVERSE` | **I7** | A10 | **Momentary** | **sw/bl** ⚫️🔵 | Backväxelkontakt (kl.15 → switch → I7). Driver O19 BACKLJUS. |
| `PDM.IN.WASHER` | I8 | A3 | Momentary | **gn/ro** 🟢🔴 | Höger spak (dra) |
| `PDM.IN.WIPER.SPEED` | **I9** | A11 | **Analog** | **sw/gr** ⚫️🔘 | E22 stalk via resistor-stege (12V→4.7kΩ SLOW / 470Ω FAST → I9 → 1kΩ pulldown→GND). Driver GF5 + GF6. |
| `PDM.IN.COOLANT.LOW` | **I10** | A2 | **Latching High** | **li/sw** 🟣⚫️ | F66 nivåvakt (NC mot jord). 4.7kΩ pullup→12V vid I10. Latchar vid låg nivå. |

### Direkt matade inputs (ej busbar)

| Etikett | Input | Pin | Mode | Originalfärg | Från |
|---------|-------|-----|------|-------------|------|
| `PDM.IN.BRAKE` | **I4** | A5 | **Momentary** | **sw/ro** ⚫️🔴 | Bromslysbrytare (bat → switch → I4) |
| `PDM.IN.OIL.PRESS` | **I14** | C12 | **Latching Active Low** | 0.75mm² **bl/gn** 🔵🟢 | F1 oljetrycksbrytare (NC mot motorblock-jord), 200kΩ intern PU |
| ~~`PDM.IN.REVERSE`~~ | ~~I14~~ | ~~C12~~ | STUB | — | DISABLED — pin omallokerad till OIL.PRESS |
| `PDM.IN.BLOWER` | I1 | A7 | **Analog** | **sw/ge** ⚫️🟡 | E9 fläktomkopplare (4.7k+4.7k delare) |
| `PDM.IN.HIGHBEAM` | I2 | A6 | **Latching Active Low** | **ge** 🟡 | E4 helljusspak (kl.56b) — jordswitchad via slip ring |

> I4 broms: Direkt från batteri via bromsljusbrytare (funkar utan tändning).
> I14 backväxel: Direkt från tändning via växellådsbrytare.

### Helljus — Active Low (intern 200kΩ pull-up)

```
PDM intern 200kΩ pull-up (till VCC)
       │
       ├───── PDM I2 pin A6
       │
  VW helljuskabel (ge, via slip ring)
       │
       ▼
   E4 HELLJUSSPAK ──── GND (chassis)
```

> ⚠️ **Ingen extern resistor.** Samma princip som horn I12. PDM:ens inbyggda 200kΩ pull-up håller I2 HIGH vid öppen krets. Spakdrag kopplar till chassijord via slip ring → I2 går LOW → PDM togglar helljus PÅ/AV.

| State | I2 | O16/O7 |
|-------|-----|-----|
| Spak ej dragen | ~3.3V (intern PU) | Ingen toggle |
| Spak dragen | ~0V (GND) | Toggle helljus PÅ/AV |

### Horn — Active Low (intern 200kΩ pull-up)

| Etikett | Input | Pin | Mode | Kabel | Originalfärg | Från |
|---------|-------|-----|------|-------|-------------|------|
| `PDM.IN.HORN` | I12 | A1 | **Momentary Active Low** | 1.0mm² | **br/bl** 🟤🔵 | Hornknapp via slip ring |

```
PDM intern 200kΩ pull-up (till VCC)
       │
       ├───── PDM I12 pin A1
       │
  VW horn cable (br/bl, 1.0mm², via slip ring)
       │
       ▼
   HORN BUTTON ──── GND (chassis)
```

> ⚠️ **Ingen extern resistor.** PDM:ens inbyggda 200kΩ pull-up räcker för att hålla I12 HIGH vid öppen krets. Hornknappen drar till chassijord via slip ring → I12 går LOW → O13 aktiveras.

| State | I12 | O13 |
|-------|-----|-----|
| Not pressed | ~3.3V (intern PU) | OFF |
| Pressed | 0V (GND) | ON |
| Cable broken | ~3.3V (intern PU) | OFF (safe) |

### Analoga sensorinputs (5V referens via C10)

| Etikett | Input | Pin | Mode | Originalfärg | Från | Pull-up |
|---------|-------|-----|------|-------------|------|---------|
| `PDM.IN.COOLANT` | I11 | A12 | **Analog** | **gn** 🟢 | G2 NTC kyltemp | 1kΩ ext → C10 5V |
| `PDM.IN.BRAKE.FAULT` | **I13** | C11 | **Latching High** | **br/ws** 🟤⚪️ | F bromskrets-differensbrytare | 4.7kΩ ext → 12V (gamla 100Ω→5V borttagen) |
| ~~`PDM.IN.FUEL.LVL`~~ | ~~I13~~ | ~~C11~~ | FLYTTAD | — | Flyttad till Pi via ADS1115 (16-bit ADC) i v9.0 |

> ⚠️ C10 5V max **100mA** (ej 500mA som i v5.5). 1kΩ drar 5mA, 100Ω drar 50mA → totalt 55mA. OK.

### Lediga inputs

> ⚠️ Alla 16 inputs är nu tilldelade. Inga lediga inputs kvar. Reset sker via CAN-kommando eller strömcykel.

### CAN-bus

| Etikett | Pin | Kabel | Till |
|---------|-----|-------|------|
| `PDM.CAN.H` | C8 | 0.75mm² tvinnad **ge** | RPi CAN High |
| `PDM.CAN.L` | C9 | 0.75mm² tvinnad **bl** | RPi CAN Low |

> 250 kbps. PDM intern terminering **aktiveras i mjukvara**.
> ⚠️ **KRAV: CAN HAT MÅSTE ha inbyggd 120Ω terminering** (jumper eller lödbrygga). Ingen extern resistor. Waveshare, PiCAN2 och de flesta MCP2515-baserade HATs har detta — **verifiera innan köp**. Aktivera jumper → bussen får korrekt 60Ω (PDM 120Ω ∥ HAT 120Ω).

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
   │    │    │    │    │    │    │    └──→ Reserve (I12 horn intern PU)
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

**EJ via busbar:** I1 (blower analog), I2 (high beam), I4 (brake), I11 (coolant 5V), I12 (horn, intern PU), I13 (fuel 5V), I14 (reverse), I16 (ignition)

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
| `INST.SENS.OIL` | F1 | Oljetryck | **bl/gn** 🔵🟢 | → **PDM I14** (C12), Active Low, 200kΩ intern PU. Status speglas via CAN till RPi. |
| `INST.SENS.COOL.LVL` | F66 | Kylvätskenivå | **li/sw** 🟣⚫️ | → RPi GPIO |
| `INST.SENS.COOL.LVL.GND` | F66 | Kylnivå jord | **br** 🟤 | → Chassijord |
| `INST.LAMP.HIGHBEAM` | K1 | Helljus blå | **ws/bl** ⚪️🔵 | → Parallellkopplas med O7 eller O16 (kräver ej egen PDM-output) |
| `INST.LAMP.OIL` | K3 | Oljetryck röd | **bl/gn** 🔵🟢 | → Kan drivas av (Master Varning) eller digital dashboard |
| `INST.LAMP.TURN` | K5 | Blinkers grön | **sw/bl** ⚫️🔵 | → Drivs direkt av O8 IND.TURN (D5) — inga dioder behövs |
| `INST.LAMP.COOLANT` | K28 | Kylvätska röd | **bl/ro** 🔵🔴 | → Kan drivas av (Master Varning) eller digital dashboard |
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

### Timer 2 — CRASH TMR (crash-latch)

| Parameter | Värde |
|-----------|-------|
| Label | `CRASH TMR` |
| Mode | **Duration** |
| Duration | **600 000 ms** (10 min) |
| Start Condition | **GF2 Equals True** |
| Reset On End | ✅ |
| Enabled | ✅ |

> **Crash-detektion:** GF2 (MC1 > 40 m/s² ≈ 4g) triggar Timer2 → alla outputs utom RPi och blinkers stängs av i 10 min.
> Blinkers (O24/O25) har `OR Timer2` i sin funktion → blinkar som hazard under crash-perioden.
> RPi (O21) har `Always True` → förblir PÅ för CAN-kommunikation och loggning.
> Timer2 återställs automatiskt efter 10 min (Reset On End).

---

## ⚙️ GENERIC FUNCTIONS (Configurator → Generic Functions Tab)

### GF1 — Ignition detect

| Parameter | Värde |
|-----------|-------|
| Label | `IGN ON` |
| Function | `I16 Status = True` |

> Används i output-logik där "tändning PÅ" krävs.

### GF2 — Crash detection

| Parameter | Värde |
|-----------|-------|
| Label | `CRASH DET` |
| Function | `MC1 > 40` |

> **MC1** = G-force magnitude = √(AccX² + AccY² + AccZ²) från PDM:ens inbyggda IMU.
> Vid vila ≈ 9.81 m/s² (gravitation). Tröskelvärde 40 m/s² ≈ 4g.
> Triggar Timer2 (CRASH TMR) → outputs stängs av, hazard blinkar.

### GF3 — Oil pressure OK

| Parameter | Värde |
|-----------|-------|
| Label | `OIL OK` |
| Function | `I14 Status = False` |

> F1 är NC-brytare som *öppnar* när oljetrycket är OK (>~0.3-0.6 bar).
> I14 Active Low: brytare öppen = pin på +5V (intern PU) = I14 Status False = **GF3 True**.
> Brytare sluten (motor av eller lågt tryck) = pin på 0V = I14 Status True = **GF3 False**.
> Används för:
> - O5 FUEL: `GF1 AND (GF3 OR I15 Status)` — pump stannar vid stall, men kör under cranking
> - O23 STARTER: `GF1 AND I15 AND NOT GF3` — kan inte starta mot rullande motor

### GF4 — Oil OK or Cranking (existing, dokumenteras här)

| Parameter | Värde |
|-----------|-------|
| Label | `OIL OR CR` |
| Function | `GF3 OR I15 Status` |

### GF5 — Wiper FAST detected (NY i v9.0)

| Parameter | Värde |
|-----------|-------|
| Label | `WIPER FST` |
| Function | `I9 Voltage > 5` |

> I9 är analog avläsning av wiper-stalkens 3 lägen (OFF/SLOW/FAST) via resistor-stege.
> FAST-läget ger ~9.4V (vid 13.8V batteri) eller ~6.1V (vid 9V cranking).
> Tröskel 5V ger marginal mot lågt batteri men separation från SLOW (~2.4V).
> Driver O2 WIPER_FST.

### GF6 — Wiper SLOW detected (NY i v9.0)

| Parameter | Värde |
|-----------|-------|
| Label | `WIPER SLO` |
| Function | `I9 Voltage > 1.0 AND I9 Voltage < 4` |

> SLOW-läget ger ~2.4V vid 13.8V. Fönster 1.0-4.0V fångar normal drift med marginal.
> Dödzon 4-5V mellan SLOW och FAST buffrar mot chatter vid spakomställning.
> Driver O10 WIPER_SLO.

### GF7 — ANY FAULT aggregat (NY i v9.0)

| Parameter | Värde |
|-----------|-------|
| Label | `ANY FAULT` |
| Function | `GF3 Equals False AND Timer3 Equals False OR I13 Status OR I10 Status` |

> Master-fault aggregat. True om någon av tre säkerhetsindikatorer triggar:
> - **Oljetryck förlorat** (GF3 = False) — efter 5s cranking-grace via Timer3
> - **Bromskretsfel** (I13 latched True)
> - **Kylvätskenivå låg** (I10 latched True)
>
> Cranking-grace förhindrar oljelarm vid varje motorstart (oljetryck byggs upp först efter 1-2s rotation).
>
> Driver O9 WARN.MASTER (`GF1 AND GF7 AND Timer2 Equals False`).
>
> Mellansteg-GF nödvändig eftersom Configurator-parsern strippar parenteser och NOT inte stöds.

### Timer3 — START GRACE (NY i v9.0)

| Parameter | Värde |
|-----------|-------|
| Label | `START_GRACE` |
| Mode | Duration |
| Duration | 5000 ms |
| Start Condition | `I15 Status = True` |
| Reset On End | true |

> Triggas när startknappen (I15 kl.50) trycks. Under 5s efter att startknappen släppts ignoreras GF3=False (lågt oljetryck) i master-warning-logiken så att varningslampan inte tänds vid varje motorstart.

---

## ⚙️ PDM25 V2 — INPUT-KONFIGURATION (Configurator → Input Tab)

> **PDM-namn** = exakt det du skriver i Configurator. Max 10 tecken.

| Input | PDM-namn | Mode | Active | Threshold | Hysteresis | Delay | EMA | Källa |
|-------|----------|------|--------|-----------|------------|-------|-----|-------|
| I1 | `BLOWER` | **Analog** | — | — | — | 0s | 5 | E9 fläktvred (4.7k+4.7k) |
| I2 | `HIBEAM` | **Latching** | **Low** | 6.0V | 1.0V | 0s | 0 | E4 helljusspak (jordswitchad, intern 200kΩ PU) |
| I3 | `HAZARD` | **Latching** | High | 6.0V | 1.0V | 0s | 0 | Varningsblinkersknapp |
| I4 | `BRAKE` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Bromsljusbrytare |
| I5 | `TURN L` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Blinkerspak V |
| I6 | `TURN R` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Blinkerspak H |
| I7 | `REVERSE` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Backväxelkontakt (växellåda → I7). Driver O19. |
| I8 | `WASHER` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Spolarspak |
| I9 | `WIPER SPEED` | **Analog** | — | — | — | 0s | 10 | E22 stalk via resistor-stege (4.7k/470Ω) → driver GF5+GF6 |
| I10 | `COOLANT_LOW` | **Latching** | High | 6.0V | 1.0V | 0.5s | 5 | F66 nivåvakt (4.7kΩ→12V pullup) |
| I11 | `COOLANT` | **Analog** | — | — | — | 0s | 10 | G2 NTC (1kΩ→5V) |
| I12 | `HORN` | **Momentary** | **Low** | 6.0V | 1.0V | 0s | 0 | Hornknapp (PDM intern 200kΩ PU) |
| I13 | `BRAKE_FAULT` | **Latching** | High | 6.0V | 1.0V | 0.2s | 5 | F bromskrets (4.7kΩ→12V pullup). FUEL_LVL flyttad till Pi ADS1115. |
| I14 | `OIL.PRESS` | **Latching** | **Low** | 2.5V | 0.5V | 0.2s | 5 | F1 oljetrycksbrytare (NC, intern 200kΩ PU). Driver GF3. |
| I15 | `START` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Tändningslås terminal 50 |
| I16 | `IGNITION` | **Momentary** | High | 6.0V | 1.0V | 0s | 0 | Tändningslås t.15 |

> **Threshold 6.0V + Hysteresis 1.0V:** Slår PÅ vid >6V, slår AV vid <5V. Enl. manual-rekommendation.
> **EMA 5–10** på analoga givare: Jämnar ut brus. Högre = mer utjämning.
> **Active Low (I12):** Slår PÅ vid <6V, slår AV vid >7V. PDM intern 200kΩ pull-up (ingen extern resistor).

---

## ⚙️ PDM25 V2 — OUTPUT-KONFIGURATION (Configurator → Output Tab)

> **PDM-namn** = exakt det du skriver i Configurator. Max 10 tecken.

| Output | PDM-namn | Trip | Low Fuse | High Fuse | Peak Fuse | Peak Time | Stay On | Delay | Clear | Retries | Soft Start | Funktion |
|--------|----------|------|----------|-----------|-----------|-----------|---------|-------|-------|---------|------------|----------|
| O1 | `BUSBAR` | Normal | 0 | **3.0A** | — | — | 0s | 0s | 2s | 3 | Av | Always True |
| O2 | `WIPER FST` | Normal | 0 | 7.0A | 12A | 3s | 0s | 0s | 2s | 2 | 1s | **GF5** AND T2=F |
| O3 | `IGN COIL` | Normal | 0 | 5.0A | — | — | 0s | 0s | 2s | 3 | Av | GF1 AND T2=F |
| O4 | `BRAKE` | **Instant** | 0.05A | 3.0A | 5.0A | 0.1s | 0s | 0s | 1s | 3 | Av | I4 Status AND T2=F (HS!) |
| O5 | `FUEL` | Normal | 0 | 8.0A | 12A | 3s | **2s** | 0s | 3s | 2 | 1s | GF1 AND T2=F **AND (GF3 OR I15)** |
| O6 | `PARK` | Normal | 0.05A | 2.0A | 5.0A | 0.1s | 0s | 0s | 2s | 2 | Av | GF1 AND T2=F |
| O7 | `HIBEAM R` | Normal | 0 | 5.0A | 10A | 0.1s | 0s | 0s | 2s | 3 | Av | O15 AND I2 AND T2=F |
| O8 | `IND.TURN` | Normal | 0 | 2.0A | 5.0A | 0.1s | 0s | 0s | 2s | 1 | Av | Timer1 AND (I5 OR I6 OR I3) |
| O9 | `WARN.MASTER` | Normal | 0 | 2.0A | 5.0A | 0.1s | 0s | 0s | 2s | 1 | Av | **GF1 AND GF7 AND T2=F** |
| O10 | `WIPER SLO` | Normal | 0 | 7.0A | 12A | 3s | 0s | 0s | 2s | 2 | 1s | **GF6** AND T2=F |
| O11 | `BLOWER` | Normal | 0 | 9.0A | 16A | 4s | **30s** | 0s | 3s | 2 | 1s | GF1 AND I1>1V AND T2=F |
| O12 | `WASHER` | Normal | 0 | 5.0A | 8A | 2s | 0s | 0s | 2s | 2 | Av | I8 Status AND T2=F |
| O13 | `HORN` | Normal | 0 | 6.0A | **8A** | **0.5s** | 0s | 0s | 1s | 3 | Av | I12 Status AND T2=F |
| O14 | `LOWBEAM L` | Normal | 0.5A | 5.0A | 10A | 0.1s | 0s | **3s** | 2s | 3 | Av | GF1 AND T2=F |
| O15 | `LOWBEAM R` | Normal | 0.5A | 5.0A | 10A | 0.1s | 0s | **3s** | 2s | 3 | Av | GF1 AND T2=F |
| O16 | `HIBEAM L` | Normal | 0 | 5.0A | 10A | 0.1s | 0s | 0s | 2s | 3 | Av | O14 AND I2 AND T2=F |
| O17 | `RESERVE17` | — | — | — | — | — | — | — | — | — | — | — |
| O18 | `RESERVE18` | — | — | — | — | — | — | — | — | — | — | — (radio-minne flyttat till O1 busbar) |
| O19 | `REVERSE` | Normal | 0.05A | 3.0A | 5A | 0.1s | 0s | 0s | 2s | 2 | Av | I7 Status AND T2=F |
| O20 | `RADIO ACC` | Instant | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | GF1 AND T2=F |
| O21 | `RPI` | Instant | 0 | 5.0A | — | — | 0s | 0s | 5s | 3 | 2s | Always True |
| O22 | `USB 12V` | Instant | 0 | 3.0A | — | — | 0s | 0s | 2s | 2 | Av | GF1 AND T2=F |
| O23 | `STARTER` | Normal | 0 | **12A** | **50A** | **0.5s** | **0s** | 0s | 5s | 0 | Av | GF1 AND I15 AND T2=F **AND NOT GF3** |
| O24 | `TURN R` | Normal | 0.05A | 2.0A | 5A | 0.1s | 0s | 0s | 2s | 2 | Av | I6 OR I3 OR T2 AND T1 |
| O25 | `TURN L` | Normal | 0.05A | 2.0A | 5A | 0.1s | 0s | 0s | 2s | 2 | Av | I5 OR I3 OR T2 AND T1 |

### Output-logik förklaring

> **T2=F** = `Timer2 Equals False` (= crash-timer EJ aktiv). Vid crash (GF2 triggar Timer2) stängs alla outputs med T2=F av i 10 min.

**Blinkers (O25/O24) — Timer-baserad, EJ PWM, med crash-hazard:**
```
O25 funktion: I5 OR I3 OR Timer2 AND Timer1
O24 funktion: I6 OR I3 OR Timer2 AND Timer1
```
- Timer 1 = Pulse Train 400/400ms → blinkar
- I5/I6 = momentary (spaken hålls fysiskt i position av VW-mekanismen)
- I3 = latching hazard (tryck en gång → PÅ, igen → AV)
- Hazard: Båda sidor blinkar samtidigt
- **Crash-logik:** Timer2 (crash-latch) OR:as in → vid crash blinkar BÅDA sidor automatiskt (hazard) i 10 min

**Blinkersindikator (O8 IND.TURN):**
- O8 funktion: `Timer1 AND (I5 OR I6 OR I3)` — blinkar K5 i takt med Timer1 oavsett riktning
- Drivs direkt av PDM — eliminerar behovet av externa dioder från O24/O25

**Master Varning (O9 WARN.MASTER):**
- O9 funktion: `False` — default AV, styrs via CAN Receive från RPi
- RPi skickar CAN-kommando vid kritiska fel (bromskrets, oljetryck, kylnivå)

**Halvljus (O14/O15) — Turn On Delay 3s:**
- Fördröjer 3 sekunder efter tändning → ersätter J59 X-kontaktrelä
- Funktion: `GF1 AND Timer2 Equals False`

**Helljus (O16/O7) — Toggle:**
- O16: `O14 AND I2 AND Timer2 Equals False`
- O7: `O15 AND I2 AND Timer2 Equals False`
- I2 latchar vid spakdrag → helljus på/av

**Kupéfläkt (O11) — PWM mapping, 11-punktstabell (GF1 AND I1>1V AND T2=F):**

| I1 Voltage | 0V | 1V | 2V | 3V | 4V | 5V | 6V | 8V | 10V | 11V | 12V |
|------------|----|----|----|----|----|----|----|----|-----|-----|-----|
| Duty % | 0 | 0 | 0 | 0 | 0 | 0 | 40 | 40 | 100 | 100 | 100 |

> 0–5V = AV. ~6V = steg 1 (40% PWM). ~12V = steg 2 (100% full fart).
> Stay On 30s: kör vidare efter tändning av → blåser ut restvärme.

**E9 Fläktvred — Switch-position → spänning (D2):**

Switchen har **3 lägen** (AV / LÅG / HÖG). En extern **4.7kΩ resistor** i LÅG-kretsen skapar spänningsdelning mot PDM:ens interna 40kΩ pull-down.

```
Signalbusbar 12V ──┬── Switch läge HÖG ──── direkt ──→ I1 (~12V → 100%)
                   │
                   └── Switch läge LÅG ──── 4.7kΩ ──→ I1 (~6V → 40%)

                       Switch AV ──── öppen ──→ I1 (~2V → av)
```

| Position E9 | Approx. spänning I1 | Duty % | Kommentar |
|-------------|---------------------|--------|-----------|
| OFF | ~2V (intern pull-down) | 0% | Switch öppen — intern PDM 40kΩ PD dominerar |
| LÅG | ~6V | 40% | Via 4.7kΩ extern resistor. Verifieras med voltmeter |
| HÖG | ~12V | 100% | Direkt busspänning, full fart |

> ⚠️ **Mät med voltmeter i varje switchläge** och justera PWM-tabellen om avvikelse >0.5V. Resistorn (4.7kΩ, 0.25W) löds in i kabeln med krympslang.

**Torkare — 2 outputs + parkkrets:**
- O10 (B7, slow): `I10 Status AND Timer2 Equals False`
- O2 (C5, fast): `I9 Status AND Timer2 Equals False`
- VW-spaken har mekanisk interlock (bara en position åt gången)
- **Parkkrets:** Extern jumper 31b→53 vid motorns kontaktdon (1.5mm²)
- E22 i AV-läge kopplar busbar 12V direkt till 53a → kamswitch → 31b → jumper → 53 → motor parkerar
- O1 busbar fuse justerad till 3.0A för att hantera parkström (~1–2A)

**Tändspole (O3 IGN COIL — K4):**
- O3 funktion: `GF1 AND Timer2 Equals False` (tändning PÅ → spole får ström, AV vid crash)
- O3 (C4) → kabel `PDM.OUT.IGNITION` → N6 seriemotstånd (ballast) → tändspole kl.15
- Kabel internt i motorlocket: N6 → spole kl.15 (COIL.N6, ws/li)
- High Fuse 5.0A skyddar kretsen. O3 är HS/LS-kanal, konfigureras som HS.

**Parkljus (O6 PARK — K3):**
- O6 funktion: `I7 Status AND Timer2 Equals False` (parkljusswitch → output PÅ, oavsett tändning)
- Parkljus ska fungera med tändning AV — terminal 30-krets per trafikregler
- I7 matas från signalbusbaren (O1, always-on)

**Startmotor (O23 STARTER — direkt till solenoid, inget relä):**
- O23 funktion: `GF1 AND I15 Status AND Timer2 Equals False` (tändning PÅ OCH startknapp nedtryckt, EJ crash)
- **Direkt till solenoid kl.50** — PDM-kanalen driver solenoiden utan externt relä
- Pull-in: ~30–40A i ~0.1–0.3s (Peak Fuse **50A/0.5s** ger marginal)
- Hold-in: ~8–10A (High Fuse **12A** skyddar)
- I15 (C2) = tändningslåsets terminal 50 (startläge, momentärt) → Momentary Active High
- Stay On = **0s** — startmotorn stannar omedelbart när knappen släpps
- ⚠️ **B5 Starterinterlock:** RPi övervakar oljetryck (F1 → GPIO). Om oljetryck detekteras (motor igång) skickar RPi CAN-kommando som disablar O23 → skyddar kuggkrans mot ingrepp i roterande motor.

**Bränslepump (O5 FUEL — D8):**
- O5 funktion: `GF1 AND Timer2 Equals False` (tändning PÅ → pump PÅ, AV vid crash), Stay On 2s
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
| B2 | Output 23 | O23 Starter (direkt till solenoid) |
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
| D3 | Output 24 | O24 Turn R (Fram) |
| D4 | Output 9 | O9 WARN.MASTER (CAN-styrd varningslampa) |
| D5 | Output 8 | O8 IND.TURN (K5 blinkersindikator) |
| D6 | Output 7 | O7 High beam R |
| D7 | Output 4 (HS/LS) | O4 Brake (konfigurera HS!) |
| D8 | Output 5 | O5 Fuel pump |
| D9 | Output 6 | O6 Parkljus |
| **D10** | **Output 24** | O24 Turn R (Bak, parallell med D3) |
| D11 | Output 20 | O20 Radio ACC |
| D12 | Output 16 | O16 High beam L |

> D10 dubbel-pin O24 (extra strömkapacitet). O24 är speglad mot O25 (Vänster blinkers).

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
| Externt startrelä | PDM O23 driver solenoid direkt (Peak 50A/0.5s) |

---

## ETIKETTÖVERSIKT — FULLSTÄNDIG LISTA

### 🟡 Gul tejp (31 st)

| # | Etikett |
|---|---------|
| 1 | `PDM.PWR.BAT+` |
| 2 | `PDM.PWR.CTRL` |
| 3 | `PDM.OUT.BUSBAR` |
| 4 | `PDM.OUT.LOWBEAM-L` |
| 5 | `PDM.OUT.LOWBEAM-R` |
| 6 | `PDM.OUT.HIGHBEAM-L` |
| 7 | `PDM.OUT.HIGHBEAM-R` |
| 8 | `PDM.OUT.PARK` *(PDM-sidan, kabel D9 → grenuttag)* |
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
| 28 | `PDM.OUT.IND.TURN` |
| 29 | `PDM.OUT.WARN.MASTER` |
| 30 | `PDM.ENG.BAT→START` |
| 31 | `PDM.ENG.GEN.B+` |

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
| 🟡 Gul | PDM.OUT + PDM.ENG | 31 | 62 |
| 🔵 Blå | PDM.IN + CAN | 18 | 36 |
| ⚫️ Svart | GND | 11 | 22 |
| 🟢 Grön | INST + motorsignaler | 14 | 28 |
| | **TOTALT** | **74** | **148 etiketter** |

### Resursanvändning

| Resurs | Använda | Lediga |
|--------|---------|--------|
| Outputs (25 st) | 24 | 1 (O17) |
| Inputs (16 st) | 16 | 0 |
| Timers (30 st) | 2 | 28 |
| Generic Functions | 2 | — |
| CAN Inputs | 0 | 100 |

---

## STEGVIS INSTALLATION v9.0 — Brake Safety Integration 🛡

**Mål:** Aktivera oljetryck + bromskrets + kylvätskenivå som PDM-NATIVE säkerhetsindikatorer. Konsolidera wiper SLOW/FAST till en analog input. Flytta FUEL_LVL till Pi.

**Förutsättningar innan start:**
- ✅ v9.0 HWPDM flashad i PDM
- ⚠ Aktivera tillfälligt **GF7 ANY_FAULT som disabled** i Configurator innan hårdvaran är klar — annars triggas WARN.MASTER felaktigt vid varje tändningsstart
- 🔧 Verktyg: lödkolv, krymp-isolering, multimeter, motstånd (1kΩ ¼W, 470Ω ¼W, 4.7kΩ ¼W ×3)

---

### Steg 1 — Flytta FUEL_LVL till Pi (frigör I13)

**Tid:** ~30 min  
**Risk:** Låg (Pi-failure = tappad tankmätare, inte motor-kritiskt)

- [ ] **PDM-skåp:** Lokalisera 100Ω pullup-resistorn på C10→C11 — **ta bort den**
- [ ] **PDM-skåp:** Klipp av PDM.IN.FUEL.LVL (li/sw) från PDM C11
- [ ] **Tank → Pi-skåp:** Dra ny 0.75mm² li/sw från tanksändarens signalpinne till **ADS1115 A0**
- [ ] **Pi-side:** Implementera/aktivera FUEL-bridge i Python (läs ADS1115 A0 → mappa via SC2-kalibrering → publicera `vehicle/fuel_level` MQTT)
- [ ] **Test:** Tom tank ≈ 4.5V (på Pi-side ADC), full tank ≈ 0.45V — verifiera med multimeter
- [ ] **PDM-monitor:** I13 ska nu vara "frikopplad", visar floatande spänning ~1.8V — ignoreras tills steg 4

**Output efter steg 1:** Tankmätaren fungerar via Pi → CAN → Dashboard. PDM I13 (C11) redo för BRAKE_FAULT.

---

### Steg 2 — Bygg WIPER resistor-stege (frigör I10)

**Tid:** ~45 min  
**Risk:** Medium (felmonterad stege = torkare fungerar inte, körbart men irriterande)

- [ ] **E22 stalk:** Identifiera SLOW-kontakten (tidigare gick till I10 A2 via gn) och FAST-kontakten (tidigare I9 A11 via sw/gr)
- [ ] **E22 stalk → ny resistor-modul:** Löd **4.7kΩ ¼W i serie med SLOW-kabeln** + **470Ω ¼W i serie med FAST-kabeln**
- [ ] **Resistor-modul:** Sätt båda resistorerna i en liten potted Deutsch-shell eller 3D-printad låda — placeras nära E22 stalk
- [ ] **Resistor-modul → PDM:** Sammanfoga båda resistor-utgångarna till **EN kabel** (sw/gr 1.0mm²) → PDM A11 (I9)
- [ ] **PDM-skåp:** Löd **1kΩ ¼W pulldown** mellan I9 (A11) och GND
- [ ] **PDM-skåp:** Säkring 12V till stalkens matning (om inte redan sker via E22 internt)
- [ ] **Test (motor av, tändning på):** Mät I9 spänning i varje stalkläge:
  - OFF: ~0V
  - SLOW: ~2.4V
  - FAST: ~9.4V
- [ ] **Configurator monitor:** Verifiera GF5 WIPER_FST = True i FAST-läge, GF6 WIPER_SLO = True i SLOW-läge
- [ ] **Test torkare:** Kör motorn, testa båda hastigheter — torkaren ska köra normalt

**Output efter steg 2:** Wiper-spaken styr torkaren via en analog input. PDM I10 (A2) frikopplad och redo för COOLANT_LOW.

---

### Steg 3 — Koppla F66 kylvätskenivå (I10)

**Tid:** ~30 min  
**Risk:** Låg (latched fault, ingen direkt motor-påverkan — bara varning)

- [ ] **Motorrum:** Identifiera F66 kylvätskenivåvakt på expansionskärlet (NC-brytare mot motorblock-jord)
- [ ] **F66 → PDM:** Dra ny **0.75mm² li/sw** från F66 signalpinne till PDM A2 (I10)
- [ ] **PDM-skåp:** Löd **4.7kΩ ¼W pullup** mellan I10 (A2) och säkrad +12V (samma fuse-rail som BUSBAR matas av)
- [ ] **F66 hus:** Verifiera god jord mot motorblock (multimeter < 0.5Ω till chassi)
- [ ] **Test (kylvätska OK):** F66 sluten → I10 = ~0V → COOLANT_LOW Status = False ✅
- [ ] **Test (simulera lågt nivå):** Koppla bort F66 fysiskt → I10 = ~12V → COOLANT_LOW latchar True
- [ ] **Reset-test:** Slå av tändning + på igen → latched state ska försvinna

**Output efter steg 3:** Lågt kylvätskenivå detekteras direkt i PDM. Inga indikationer på dashboard ännu (väntar på steg 5).

---

### Steg 4 — Koppla F bromskrets (I13)

**Tid:** ~45 min  
**Risk:** Medium (säkerhetskritisk signal — kontrollera noga att F är funktionsduglig först)

- [ ] **Bromsledning:** Identifiera F differentialtryckbrytare (oftast vid huvudbromscylindern eller i T-stycke i bromsledningen)
- [ ] **Förkontroll:** Mät F brytarens kontinuitet med multimeter — ska vara sluten mot jord vid normalt bromstryck
- [ ] **F → PDM:** Dra ny **0.75mm² br/ws** från F signalpinne till PDM C11 (I13)
- [ ] **PDM-skåp:** Löd **4.7kΩ ¼W pullup** mellan I13 (C11) och säkrad +12V
- [ ] **Test (bromskrets OK):** F sluten → I13 = ~0V → BRAKE_FAULT Status = False ✅
- [ ] **Test (simulera fel):** Koppla bort F fysiskt → I13 = ~12V → BRAKE_FAULT latchar True
- [ ] **Vibrations-test:** Knacka lätt på F under några sekunder — får INTE trigga falsklarm (om så: höj `delay_s` till 0.5)
- [ ] **Reset-test:** Power-cycle PDM → latched state nollställs

**Output efter steg 4:** Bromskretsfel detekteras direkt i PDM. Inga indikationer på dashboard ännu.

---

### Steg 5 — Aktivera GF7 ANY_FAULT + O9 WARN.MASTER

**Tid:** ~15 min  
**Risk:** Låg (rent mjukvarusteg)

- [ ] **Configurator:** Öppna senaste HWPDM-fil, gå till **Generic Functions**-tabben
- [ ] Sätt **GF7 ANY_FAULT enabled = true**
- [ ] Verifiera funktion = `GF3 Equals False AND Timer3 Equals False OR I13 Status OR I10 Status`
- [ ] Gå till **Outputs**-tabben, hitta **O9 WARN.MASTER**
- [ ] Verifiera funktion = `GF1 AND GF7 AND Timer2 Equals False`
- [ ] Spara och flasha
- [ ] **Test 1 — kall start:** Starta motorn — varningslampan **får inte** lysa (Timer3 grace ger 5s mellanrum)
- [ ] **Test 2 — låt motorn gå:** Efter 5s varningslampan **släckt** (oljetryck OK + inga andra fel)
- [ ] **Test 3 — simulera oljetryckfel:** Koppla bort F1 (öppen krets) → I14 läses som motor-av → GF3=False → varningslampa **lyser**
- [ ] **Test 4 — bromskretsfel:** Koppla bort F → I13 latchar → varningslampa **lyser** även efter F återansluten
- [ ] **Test 5 — kylnivåfel:** Koppla bort F66 → I10 latchar → varningslampa **lyser**
- [ ] **Reset:** Power-cycle PDM → alla latched states nollställs, varningslampa släckt

**Output efter steg 5:** Komplett PDM-NATIVE säkerhetsövervakning aktiv. Pi-failure påverkar inte denna funktion.

---

### Pi-side komplettering (parallellt med steg 1-5)

**Tid:** ~30 min total  
**Status:** Information — implementeras separat på Pi-sidan när Pi-bridge utvecklas

- [ ] F34 bromsvätska-nivåvakt → Pi GPIO (slow event, Pi-failure-tolerant OK)
- [ ] F9 handbroms-brytare → Pi GPIO
- [ ] Pi → CAN frame **0x110** (bit-packat: byte 0 bit0=handbrake, bit1=brake_fluid, bit2-7=reserved)
- [ ] PDM CAN Input filter för 0x110 → variabel `RPI_HANDBRAKE` etc.
- [ ] (Future) GF14 RPI_HANDBRAKE → addera till GF7 ANY_FAULT om så önskas

---

### Felsökningstips

| Symptom | Trolig orsak | Lösning |
|---------|--------------|---------|
| Varningslampa lyser hela tiden | GF3 evalueras False vid icke-monterad F1 | Verifiera I14 (C12) — ska gå till GND när F1 sluten |
| Varningslampa lyser vid varje motorstart | Timer3 ej triggad korrekt | Verifiera I15 (C2) når PDM och triggar Timer3 |
| GF5/GF6 chattrar mellan SLOW/FAST | För låg EMA eller smal hysteres | Höj EMA till 15, justera GF6 fönster till 1.5-3.5V |
| BRAKE_FAULT trippar vid skakning | Transient pulser för korta för delay | Höj `delay_s` på I13 från 0.2 till 0.5 |
| COOLANT_LOW falsklarm vid kall start | Bubbla i kylsystem under uppvärmning | Höj `delay_s` på I10 från 0.5 till 1.0 |

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
- [ ] CAN HAT: **inbyggd 120Ω jumper aktiverad** (krav — ingen extern resistor)
- [ ] Mät **60Ω** (±5Ω) mellan CAN-H och CAN-L med bussen avstängd
- [ ] Tvinnad kabel, minst 1 twist per 3cm
- [ ] Stubbkablar max 30cm
- [ ] CAN-buss hastighet = 250 kbps

### Inputs

- [ ] I5/I6: Momentary, Active High, Threshold 6V, Hysteresis 1V
- [ ] I3: **Latching**, Active High — testa varningsblinkers PÅ/AV
- [ ] I4: Momentary, Active High — testa bromsljus
- [ ] I7: Momentary, Active High — testa parkljus **utan** tändning
- [ ] I12: Active **Low**, Threshold 6V — testa horn (intern 200kΩ PU, ingen extern resistor)
- [ ] I14: Momentary — testa backljus i backväxel
- [ ] I15: Momentary, Active High — testa att startmotorn aktiverar vid kl.50 PÅ
- [ ] I16: Momentary — verifiera att GF1 visar True med tändning PÅ
- [ ] Analoga givare (I1, I11, I13): EMA filter aktiverat
- [ ] E9 blower switch: mät spänning I1 i varje position och verifiera mot PWM-tabell

### Outputs

- [ ] O4 Broms: Konfigurerad som **HS** (ej LS!) i Configurator
- [ ] O3 IGN COIL: Funktion = GF1 AND T2=F, High Fuse = 5.0A, konfigurerad som HS
- [ ] O25/O24: Funktion = **I5/I6 OR I3 OR Timer2 AND Timer1** — ej PWM!
- [ ] O7 HIBEAM R: Funktion = **O15 AND I2 AND T2=F**, High Fuse 5.0A
- [ ] O6 PARK: Funktion = **GF1 AND T2=F** (parkljus följer tändning, fysisk PARK-brytare borttagen)
- [ ] O8 IND.TURN: Funktion = **Timer1 AND (I5 OR I6 OR I3)** — K5 kontrollampa
- [ ] O9 WARN.MASTER: Funktion = **False** (CAN-styrd från RPi)
- [ ] Timer 1: Pulse Train **400ms/400ms** aktiverad
- [ ] Timer 2: Duration **600 000ms** (10 min), Start = GF2, Reset On End = ✅
- [ ] O11 Fläkt: PWM Mapping → I1 Voltage, 11-punktstabell inlagd
- [ ] O11 Stay On: **30s**
- [ ] O14/O15: Turn On Delay = **3s**
- [ ] O13 Horn: Peak Fuse **8A**, Peak Time **0.5s**
- [ ] O2 Wiper fast + O10 Wiper slow: Soft Start **1s**
- [ ] O23 Starter: Direkt till solenoid (inget relä), Peak **50A/0.5s**, High **12A**, Stay On **0s**, Retries = **0**
- [ ] O5 Fuel pump: Soft Start 1s, Stay On **2s**, High Fuse 8A, Peak 12A/3s
- [ ] O25 Turn L: Funktion = **I5 OR I3 OR Timer2 AND Timer1**, High Fuse 2.0A
- [ ] GF1: I16 Status = True (tändningsdetektion)
- [ ] GF2: MC1 > 40 (crash-detektion, ≈4g)
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

**Version:** 9.0
**Datum:** 2026-05-09
**Verifierad mot:** PDM15/25/35 Instruction Manual v1.0 (23 juni 2025) + Hardwire DBC export 2026-05-07
**Tillägg v9.0:** Brake Safety Integration. WIPER konsoliderad till analog input (I9 WIPER_SPEED via resistor-stege 4.7kΩ/470Ω/1kΩ pulldown). I10 omallokerad till COOLANT_LOW (F66). I13 omallokerad till BRAKE_FAULT (F bromskrets), FUEL_LVL flyttad till Pi ADS1115. Nya GF5 (WIPER FST) / GF6 (WIPER SLO) / GF7 (ANY_FAULT). Ny Timer3 START_GRACE (5s cranking-grace). O9 WARN.MASTER nu PDM-NATIVE via GF7. Stegvis installations-checklista i 5 steg.
**Tillägg v5.9:** Crash-detektion (Timer2 + GF2). O8=IND.TURN, O9=WARN.MASTER. Horn intern PU (extern 10kΩ borttagen). Alla output-funktioner uppdaterade med Timer2 crash-logik. RPi GPIO bromssäkerhet dokumenterad.
**Status:** SYNKAD — redo för konfigurering i PDM Configurator och fysisk installation

---

## KABLAR TILL BAKSTAM (Dras bakåt i fordonet)

Dessa kablar samlas i en bakre kabelstam och dras under chassit till baklyktor och bränslepump.
Tvärsnittsarea (mm²) och kabelfärger har optimerats för maximal säkerhet, dimensionering och spårbarhet.

| Etikett | System | Kabel | Till | Notering |
|---------|--------|-------|------|----------|
| `PDM.OUT.BRAKE` | Bromsljus | 1.5mm² **blå** 🔵 | M9 + M10 | Skyddas av Instant trip (HS) för snabb urkoppling vid fel. |
| `PDM.OUT.REVERSE` | Backljus | 1.5mm² **grå** 🔘 | M16 + M17 | |
| `PDM.OUT.PARK-R` | Parkering bak | 1.5mm² **röd** 🔴 | M4 + M2 | Utgör den bakre kretsen (bakre pinnen) för positionsljuset. |
| `PDM.OUT.TURN-L-R` | Blinkers V bak | 1.5mm² **gul** 🟡 | M6 | Bakre pinnen för vänster blinkers. |
| `PDM.OUT.TURN-R` | Blinkers H bak | 1.5mm² **grön** 🟢 | M8 | Dras till höger bak (i v5.6 splittad från huvudkabel eller dual-pin). |
| `PDM.OUT.FUEL` | Bränslepump | 2×1.5mm² **svart+brun** ⚫️🟤 | G6 | Parallellkopplade ledare (båda för plusmatning +12V) för 5A strömuttag. Separerad jord. |
| `GND.REAR.BUS` | Gemensam Jord | 1.5mm² **brun** 🟤 | Chassi / M8 | Alla bakre förbrukare (M2, M4, M6, M8, M9, M10, M16, M17, G6) delar jordpunkt i chassit. |
