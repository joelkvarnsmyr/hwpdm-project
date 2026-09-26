# ELTON PDM25 V2 — Avstämd Pinmap v8.0 (rev 3)
## VW LT31 1976 · JSN 398 · motorkod CH · 2026-06-11
### Källa: build `Elton_v9.59_radio_removed.HWPDM` (logik) + märklista v7.1 (Deutsch-pins)

> **Rev 3 (2026-06-13) — PLANERADE v9.60-ändringar (ej byggt/flashat än):**
> - **Torkare+spolare → analog mux på I9/A11** (`docs/MUX_torkare_spolare_design...`).
>   Spolaren lämnar I16/C1 → flyttas in i muxen.
> - **I16/C1 → HANDBRAKE** (F9 handbromsvarning, switch-to-GND, kopia av I4 BRAKE-inställningar).
> - **Fläkt → analog mux på I1/A7** (låg/hög) + O11 PWM-mappning vänd (`docs/SENSORER_flakt_olja_temp...`).
> - **I14 OIL.PRESS + I10 COOLANT_TEMP:** intern pull-up (pullResistor=1), inget externt motstånd.
>   Återaktivera Timer3 START_GRACE när I14 tas i bruk.
> Per-kontakt-schemana (kontakt_A/C) speglar fortfarande v9.59 tills v9.60 flashats.

> **Rev 2 (2026-06-11, senare samma dag):** Avvikelse A–D lösta av Joel — se respektive
> avsnitt. Spolare räddad till I16/C1 (v9.58), enabled-drift inbakad i fil (v9.58),
> PARK/BRAKE bekräftad enligt build, C3 bekräftad tändningskopplad.
> NY öppen punkt: Timer2 CRASH_TMR + Timer3 START_GRACE disabled i fil (var enabled i v9.4).

> **Syfte:** Detta är den första pinmappen som stämmer av **faktisk PDM-logik** (build-labels)
> mot **fysiska Deutsch-pins** (v7.1) efter CAN-/PWM-/dual-horn-/fuel-sessionen. Den ersätter
> märklista v7.1 som källa till sanning för *vad varje I/O gör*. Deutsch-pinbokstäverna
> (A/B/C/D + nr) är hårdvarufasta per I/O-nummer och kommer från v7.1.

---

## ⚠️ LÄSANVISNING — tre sanningsnivåer

| Kolumn | Källa | Tillförlitlighet |
|--------|-------|------------------|
| **Pin** (A5, D9, C6…) | Hårdvara — I/O-nummer → kontaktpin är fast | ✅ Säker |
| **Logik / label** | build v9.57 `.label` + funktion | ✅ Säker (det flashade kör detta) |
| **Konsument / wire** | v7.1 + härledning | ⚠️ Driftat — fältverifiera där märkt 🔶 |
| **Status** | denna avstämning | Se legend |

**Statuslegend:** ✅ Kopplat+testat live · 🟡 Kopplat, ej kalibrerat/testat · ⬜ Ej dragen/planerad · 🔴 Disabled i fil — bekräfta live · 🔶 Funktionskonflikt mot v7.1

---

## 🔑 4 BESLUT — LÅSTA 2026-06-11
Joel: *"Jag vill ha så mycket som möjligt på PDM för att göra det enkelt."* Build vinner överallt.

| # | Beslut | Resultat | Inbakat i v8.0 |
|---|--------|----------|----------------|
| 1 | Bränslenivå | **PDM I8** analog + 150Ω pull-up. ADS1115-plan skrotad. | ✅ |
| 2 | Vindrutetorkare | Behåll **digital** build-lösning (I9 + park-sensor I11). | ✅ |
| 3 | Kylvätska | Bara **temp** på I10. Ingen nivåvakt (har aldrig funnits). | ✅ |
| 4 | O2 | **ALT_EXCITE** (generator-magnetisering, 82Ω 5W). | ✅ |

---

## Strömförsörjning & buss

| Pin | Etikett | mm² | Från → Till | Status |
|-----|---------|-----|-------------|--------|
| M8-stud | PWR.BAT+ | 32 | Startmotor kl.30 → PDM M8 | ✅ |
| **C3** | PWR.CTRL | 4 (svart) | +12V busbar → tändningslås (RUN) → C3 | ✅ **Avvikelse A LÖST (2026-06-13):** matas från +12V-busbaren bakom PDM via tändningslåset. Se `kraft_busbar.*` |
| **C7** | GND.CHASSIS | 10 | C7 → Chassijord p.12 | ✅ |
| **C10** | 5V.REF | — | Sensor-matning (100 mA) | ✅ |
| **C8** | CAN.H | 0.75 tvinnad | C8 → RPi CAN High | ✅ testat (light show) |
| **C9** | CAN.L | 0.75 tvinnad | C9 → RPi CAN Low | ✅ testat |

> CAN: 11-bit standard, 0x500–0x502, 500 kbit/s. Pi måste sända kontinuerligt @20 Hz
> (CANInput-timeout 1000 ms = failsafe → ljus släcks 1 s efter Pi-tappad anslutning).

---

## INPUTS (Deutsch-kontakt A + C)

| Pin | I | Logik (build) | Mode | Konsument | Status |
|-----|----|--------------|------|-----------|--------|
| A7 | I1 | BLOWER | analog | E9 fläktomkopplare | 🔴 **disabled i fil** — bekräfta live |
| A6 | I2 | HIBEAM | momentary | E4 helljusspak | ✅ |
| A8 | I3 | HAZARD | latching | Varningsblinkersknapp | ✅ |
| A5 | I4 | BRAKE | momentary | Bromsljusbrytare (bat-matad) | ✅ |
| A9 | I5 | TURN_L | momentary | E2 blinkerspak V | ✅ |
| A4 | I6 | TURN_R | momentary | E2 blinkerspak H | ✅ |
| A10 | I7 | REVERSE | momentary | F4 backväxelkontakt | 🔴 **disabled i fil** — bekräfta live |
| **A3** | **I8** | **FUEL_LEVEL** | **analog** | Bränslegivare på tank + **150Ω PU** | 🟡 **Beslut 1** — kräver 150Ω + kalibrering. (v7.1:s WASHER på A3 flyttad till I16/C1 — Avvikelse B löst) |
| **A11** | **I9** | **WIPER_SLOW** | **digital** | Torkaromkopplare kl.53 | 🟡 **Beslut 2** (tillfällig, ~50% testad) |
| **A2** | **I10** | **COOLANT_TEMP** | **analog** | G2 NTC kyltemp | 🟡 **Beslut 3** — NTC inkopplad, **saknar pull-up** → läser ej rätt ännu |
| **A12** | **I11** | **WIPER_PARK** | **digital** | Torkarmotor park-sensor (kl.31b) | 🟡 testad i kombo med I9 |
| A1 | I12 | HORN | momentary | Hornknapp via slip ring | ✅ → GF8 HORN_MASTER |
| C11 | I13 | BRAKE_FAULT | latching | Ny bromsfel-givare | ⬜ **disabled** — givare ej installerad |
| C12 | I14 | OIL.PRESS | latching | F1 oljetryckskontakt | ⬜ **disabled** — brytare ska bytas |
| C2 | I15 | START | momentary, active-LOW thr 1V | Tändningslås kl.50 (grundar) | ✅ testat |
| **C1** | **I16** | **WASHER** (NY v9.58) | momentary, active-LOW | E22 spolarspak (switch-to-GND) | ⬜ **Avvikelse B LÖST:** spolarspaken flyttas hit (var I8/A3 i v7.1). Dra kabel spak → C1 |

> **Ingen input behövs för "tändning på".** GF1 PWR_ALIVE = `True` (konstant) — PDM:en är "alive"
> så fort den har ström på C3, som är **bekräftat tändningskopplad** (Avvikelse A löst).
> I16 är därmed fri för spolaren (v9.58).

---

## OUTPUTS (Deutsch-kontakt B + C + D)

| Pin | O | Logik (build) | Peak-säkr. | PWM | Konsument | Status |
|-----|----|--------------|-----------|-----|-----------|--------|
| C6 | O1 | BUSBAR | 10 A | — | Signalbusbar (always-on 3A) | ✅ |
| **C5** | **O2** | **ALT_EXCITE** | 3 A | — | Generator-magnetisering + **82Ω 5W** | ⬜ **Beslut 4** — disabled tills 82Ω monterad. 🔶 v7.1 hade C5=WIPER_FST |
| C4 | O3 | IGN_COIL | 12 A | — | N6 seriemotstånd → tändspole | ✅ |
| D7 | **O4** | **PARK** | 8 A | ✅ var945 | Parkljus-distribution M1/M3/M2/M4/X | ✅ **Avvikelse C LÖST:** build stämmer, kablarna sitter rätt |
| D8 | O5 | FUEL (pump) | 5.9 A | — | G6 bränslepump | ✅ enabled i fil sedan v9.58 |
| D9 | **O6** | **BRAKE** | 10 A | — | M9+M10 bromsljus | ✅ **Avvikelse C LÖST:** build stämmer |
| D6 | O7 | HIBEAM_R | 40 A | ✅ var940 | L2 höger helljus (56a) | ✅ testat (PWM-dimning verifierad) |
| D5 | O8 | WIPER_FST | 12 A | — | Torkarmotor kl.53b | ✅ enabled i fil sedan v9.58. (v7.1 hade D5=IND.TURN — lampan borttagen, logik flyttad O2→O8) |
| D4 | O9 | RESERVE9 | 5 A | — | (fri) | 🔶 v7.1 hade D4=WARN.MASTER varningslampa — **borttagen, allt i dashboard** |
| B7 | O10 | WIPER_SLO | 12 A | — | V torkarmotor kl.53 | ✅ enabled i fil |
| B8 | O11 | BLOWER | 16 A | — | V2 kupéfläkt | ✅ enabled i fil sedan v9.58 |
| B9 | O12 | WASHER | 8 A | — | V5 spolarpump | 🟡 **Avvikelse B LÖST:** enabled sedan v9.58, styrs av I16. Väntar fysisk spak-kabel → C1 |
| B6 | O13 | HORN_1 | 50 A | — | H1 signalhorn (primär) | ✅ → GF8 + CAN |
| B5 | O14 | LOWBEAM_L | 28.3 A | ✅ var925 | L1 vänster halvljus (56b) | ✅ **fix v9.57** (var disabled i fil) |
| B4 | O15 | LOWBEAM_R | 24.3 A | ✅ var930 | L2 höger halvljus (56b) | ✅ **fix v9.57** |
| D12 | O16 | HIBEAM_L | 20.8 A | ✅ var935 | L1 vänster helljus (56a) | ✅ |
| D1 | O17 | HORN_2 | 50 A | — | Sekundär tuta (ny kabel) | 🟡 logik klar (v9.56) — **dra fysisk kabel D1→tuta 2** |
| B12 | O18 | RESERVE18 | — | — | (fri) | ⬜ |
| B1 | O19 | REVERSE | 5 A | — | M16+M17 backljus | ✅ enabled i fil sedan v9.58 |
| D11 | O20 | RESERVE20 | — | — | (fri — radion matas från batteri-busbaren direkt, beslut 2026-06-12, build v9.59) | ⬜ |
| D2 | O21 | Reserve (RPi?) | — | — | (v7.1: Raspberry Pi-matning) | 🔴🔶 disabled — bekräfta hur Pi matas |
| B11 | O22 | USB_12V | — | — | 12V USB-uttag | 🔴 disabled i fil |
| B2 | O23 | STARTER | 22.1 A | — | B solenoid kl.50 | ✅ testat |
| D3 | O24 | TURN_R | 5 A | — | M7+M8 höger blink | ✅ |
| B10 | O25 | TURN_L | 5 A | — | M5+M6 vänster blink | ✅ |

> O4=PARK / O6=BRAKE bekräftat korrekt av Joel 2026-06-11 (Avvikelse C) — v7.1:s swap-varning
> är historisk.

---

## Sensor-kalibrering (build)

| SC | Label | Variabel | Status |
|----|-------|----------|--------|
| SC1 | COOLANT_T | 605 (I10 voltage) | 🟡 NTC saknar pull-up; kalibreringskurva ej slutförd |
| SC2 | FUEL_LVL | 595 (I8 voltage) | 🟡 Antagande: 150Ω PU, 80L tank (180Ω tom→0L, 10Ω full→80L). Verifiera givarens Ω-spann |

## Generic Functions (aktiva)

| GF | Label | Logik |
|----|-------|-------|
| GF1 | PWR_ALIVE | `True` (alltid sann när PDM strömsatt) |
| GF5 | PARK_LOCKED | Timer4 PARK_HOLD aktiv |
| GF6 | PARK_OR_HOLD | I-park ELLER GF5-hold |
| GF8 | HORN_MASTER | I12 HORN AND NOT Timer2 (crash-spärr bevarad) |

## Timers (aktiva)
- Timer1 BLINK_TMR (10 ms)
- Timer4 PARK_HOLD (60 000 ms)

> ⚠️ **NY ÖPPEN PUNKT (rev 2):** Timer2 CRASH_TMR och Timer3 START_GRACE är `enabled:false`
> i build-filerna v9.53–v9.58 men var `enabled:true` i v9.4. GF8 HORN_MASTER refererar
> fortfarande Timer2 — om crash-spärren ska fungera måste Timer2 vara enabled. Oklart om
> detta är medveten ändring eller samma klass av GUI-drift som LOWBEAM-buggen.
> **Bekräfta mot live-PDM:n innan nästa flash** — säkerhetsfunktion, ska inte gissas från script.

---

# ✅ AVVIKELSER A–D — LÖSTA 2026-06-11 (rev 2)

> Alla fyra bekräftades av Joel senare samma dag. Besluten i korthet; detaljer inbakade
> i tabellerna ovan.

### A. C3-strömkälla — LÖST: tändningskopplad
C3 (PWR.CTRL) är **tändningskopplad**, inte kl.30-alltid-hot som v7.1 påstod. Förklarar
live-beteendet (tändning på → halvljus + pump auto-på). Wake-relä-planen i
`pdm_wake_service_spec.md` kan utgå från detta. I16/C1 var fri — nu använd för spolaren (B).

### B. Spolaren — LÖST: räddad till I16 (C1)
Joel vill behålla spolaren. v9.58: I16 = WASHER-input (momentary, active-low, samma
inställningar som v9.4:s I8), O12 WASHER enabled, O12-logiken ompekad I8→I16 (var 597→637).
**Fysisk åtgärd:** spolarspakens kabel dras till pin C1 (inte A3, som nu är bränslegivare).

### C. PARK/BRAKE — LÖST: build stämmer
O4=PARK (D7, PWM), O6=BRAKE (D9) matchar den fysiska kabeldragningen. v7.1:s motsatta
mappning var fel/föråldrad. Ingen ändring behövs.

### D. Enabled-drift — LÖST: flaggorna inbakade i fil
Joel valde att baka in fil-flaggorna istället för live-export: v9.58 sätter O5 FUEL,
O8 WIPER_FST, O11 BLOWER, O19 REVERSE `enabled=true` (O10 var redan true). Fil ≈ live nu —
**men se ny öppen punkt om Timer2/Timer3 under Timers ovan.**

---

## Prioriterad åtgärdslista

**🔴 Före nästa flash:**
1. **Timer2 CRASH_TMR / Timer3 START_GRACE:** kolla i live-GUI:t om de är enabled på
   PDM:en. Om ja → de ska enables i nästa build (GUI-drift, samma klass som LOWBEAM-buggen).
2. Importera DBC v1.1 i v9.58 (Overwrite UNCHECKED) → CI28/CI29 horn-signaler, spara, flasha.

**🟡 Kabeldragning (nu möjlig — inga blockerande beslut kvar):**
3. Spolarspak → pin C1 (I16). OBS: inte A3.
4. I8 FUEL: montera 150Ω pull-up, kalibrera mot givarens verkliga Ω-spann.
5. I10 COOLANT: montera pull-up till NTC, slutför kalibreringskurva.
6. O2 ALT_EXCITE: montera 82Ω 5W, enable O2.

**🟢 När komponenter finns:**
7. O17 HORN_2: dra fysisk kabel D1 → tuta 2.
8. I14 OIL.PRESS: byt oljetryckskontakt, enable I14.

---
*v8.0 genererad 2026-06-11; rev 2 senare samma dag (avvikelse A–D lösta, källa uppdaterad
till Elton_v9.58_washer_enables.HWPDM). Deutsch-pins från märklista v7.1. Ersätter v7.1
som funktions-sanning; pin-positioner oförändrade.*
