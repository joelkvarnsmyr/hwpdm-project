# Analog multiplex: Torkare + Spolare på EN input (I9)
## Designdokument · 2026-06-12 · ersätter v9.58:s spolare-på-I16-beslut

> **Joels idé:** lägg spolarknappen och torkarlägena på samma kabel via motståndskodning,
> så slipper vi en egen input för spolaren. **Svar: ja, det fungerar — och med komponenter
> du redan köpt.** Detta dokument är den validerade, genomräknade planen.

---

## 1. Faktakoll av AI-konversationen (viktigt!)

Du resonerade med en annan AI-modell. Principen den beskrev (analog multiplexing /
motståndsstege, parallellkopplings-matte, spänningsfönster) är **helt korrekt**.
Men dess hårdvarupåståenden om PDM25 var **fel på tre punkter** — verifierat mot
konfigurator-appens källkod (`unpacked-app/src/configInputs.js`):

| Påstående (annan AI) | Verkligt (källkod, HW-version 23 = vår) | Konsekvens |
|---|---|---|
| "Permanent 200 kΩ pull-up + 40 kΩ pull-down på ingångarna" | ❌ Pull-motstånd är **valbara** per input: Ingen / 10 kΩ↑ / 10 kΩ↓ | Dess kalkyl med 2.2k-ankare mot inbyggda motstånd är fel |
| "Inbyggd pull-up till **5V** (10 kΩ branschstandard)" | ❌ Vår HW har pull-up till **VBat** (11.5–14.6 V, svajar!) — 5V-pull-up finns bara på HW-version 72–79, inte vår | Intern pull-up ger spänningsfönster som driver med batterispänningen — exakt det problem den själv varnade för |
| "5V-utgång 500 mA" | ⚠️ Obekräftat; vår dokumentation säger 100 mA | Irrelevant — nätet drar < 1 mA |

> Dess **sista** kopplingsförslag (5V-matning + externt 2.2k pull-down-ankare) byggde på de
> felaktiga interna motstånden och gav dessutom trångt packade nivåer (0.43–1.83 V, min-gap
> 240 mV **nominellt**, dvs. mindre med toleranser). Designen nedan ger **450 mV nominell
> min-gap, 183 mV worst-case** — nästan dubbelt så robust.

---

## 2. Vald topologi: **switch-to-GND med extern 5V-pull-up vid PDM:en**

Du frågade om det vore bättre att "gå mot jord istället" — **ja, av fyra skäl:**

1. **Matchar bilens befintliga topologi.** v9.4-verifieringen slog fast att Eltons
   spakar/brytare grundar mot chassi när aktiva. Samma princip här = konsekvent.
2. **Ingen 5V-kabel genom hytten.** Pull-up-motståndet monteras **vid PDM:en**
   (C10 → 5.6kΩ → I9-stiftet). Bara EN signalkabel går till spakarna. Chassijord
   finns redan vid rattstången.
3. **Stabila absoluta spänningar.** 5V REF (C10) är stabiliserad — fönstren driver
   inte med batteri/generator (vilket intern VBat-pull-up hade gjort).
4. **Snälla felmoder:**
   - Kabelbrott → 5.0 V = "ingen knapp" (torkare stannar — säkert)
   - Kortslutning mot chassi → 0 V = under alla fönster → ingen funktion + kan flaggas som fel
   - Lägsta giltiga nivå (1.71 V worst-case) har 1.7 V marginal till kortslutning

### Kretsen

Brytarna har **gemensam matning** — signalkabeln går till det gemensamma stiftet,
och motstånden sitter på **utgångssidan** (efter brytaren, mot jord). Elektriskt är
detta identiskt med motstånd-före-brytare (seriekrets — ordningen spelar ingen roll
för spänningsdelaren), men enklare att bygga med befintliga brytare:

```
PDM C10 (5V REF) ──[ Rp 5.6kΩ ]──┬── PDM I9 (pin A11, analog mode, pull=0)
       (monteras vid PDM:en)      │
                                  └── EN signalkabel → brytarnas GEMENSAMMA matningsstift
                                         Spolarknapp (momentary) ─[ 10kΩ ]──┐
                                         Vred LÅG (latching) ────[ 4.7kΩ ]──┤── chassijord
                                         Vred HÖG (latching) ────[ 22kΩ ]───┘
```

Torkare LÅG/HÖG kan aldrig vara aktiva samtidigt (mekaniskt vred). Spolaren kan
kombineras med båda. Latching vs momentary spelar ingen roll elektriskt — spänningen
hoppar mellan nivåerna i realtid och PDM:en läser av kontinuerligt.

---

## 3. Motstånd och spänningsnivåer

**Alla fyra motstånd finns i ditt inköpta sortiment** (metallfilm 1%):

| Motstånd | Värde | Placering |
|----------|-------|-----------|
| Rp (pull-up) | **5.6 kΩ** | Vid PDM: C10 → I9-stift |
| R-spolare | **10 kΩ** | Spolarknappens **utgång** → jord |
| R-låg | **4.7 kΩ** | Vredets LÅG-**utgång** → jord |
| R-hög | **22 kΩ** | Vredets HÖG-**utgång** → jord |

Brute-force-optimering över hela E12-serien gav 0.460 V min-gap som teoretiskt max —
**din uppsättning ger 0.450 V**, dvs. praktiskt taget optimalt.

### Nivåtabell med worst-case-toleranser
(1% motstånd, ±2% på 5V-referensen, ±50 mV mätfel — allt samtidigt åt värsta hållet)

| Läge | Nominellt | WC min | WC max | **PDM-fönster** |
|------|-----------|--------|--------|-----------------|
| Ingen knapp (idle) | 5.000 V | 4.85 | 5.15 | **> 4.45 V** |
| Torkare HÖG | 3.986 V | 3.84 | 4.13 | **3.59 – 4.45 V** |
| Spolare (ensam) | 3.205 V | 3.07 | 3.34 | **2.98 – 3.59 V** |
| Spolare + HÖG | 2.756 V | 2.63 | 2.89 | **2.51 – 2.98 V** |
| Torkare LÅG | 2.282 V | 2.16 | 2.40 | **2.04 – 2.51 V** |
| Spolare + LÅG | 1.817 V | 1.71 | 1.93 | **1.20 – 2.04 V** |
| Kortslutning/fel | 0 V | — | — | **< 1.0 V** → ingen funktion |

Minsta worst-case-marginal mellan två grannfönster: **183 mV** (Spolare ↔ Spolare+HÖG).
Övriga ≥ 224 mV. Idle-marginal 718 mV, kortslutningsmarginal 1708 mV. Mycket tryggt.

---

## 4. PDM-konfiguration (byggs som v9.60 — v9.59 är upptagen av radio-borttagningen)

### Input
| Inställning | Värde |
|---|---|
| I9 (A11) | label `WIPER_WASH_MUX`, **mode = 2 (analog)**, pullResistor = 0 |
| I16 (C1) | **frigörs** → RESERVE16, disabled (v9.58:s WASHER-flytt utgår) |
| I11 (A12) | WIPER_PARK — **oförändrad** (park-sensorn behövs fortfarande) |

### Output-logik (fönster på I9 Voltage, variabel 600)
```
O10 WIPER_SLO  ON om: (V > 1.20 AND V < 2.51)            ← LÅG eller SPOL+LÅG
                  OR (park-run-on via I11, oförändrad)
O8  WIPER_FST  ON om: (V > 3.59 AND V < 4.45)            ← HÖG
                  OR (V > 2.51 AND V < 2.98)             ← SPOL+HÖG
O12 WASHER     ON om: (V > 2.98 AND V < 3.59)            ← SPOL ensam
                  OR (V > 2.51 AND V < 2.98)             ← SPOL+HÖG
                  OR (V > 1.20 AND V < 2.04)             ← SPOL+LÅG
```

**Valbart (klassisk komfortfunktion):** spolar-fönster triggar en Timer →
spolarpump kör medan knappen hålls, och torkare LÅG fortsätter **5 s efter släpp**
(eftertorkning). Byggs enkelt med en timer + OR-villkor på O10. Säg till om du vill ha det.

> ⚠️ Build-detalj: exakt operand-kodning för spänningsvillkor (cond 6/7 = `>`/`<`,
> värdeskala) verifieras med GUI-roundtrip innan flash — samma metod som CAN-villkoren
> i v9.53 (skapa ett villkor i GUI, diffa filen, replikera i script).

---

## 5. Konsekvenser för befintliga beslut

| Vad | Före (v9.58) | Efter (v9.60, detta dokument) |
|---|---|---|
| Spolar-input | I16 (C1), digital | **I9-mux** — ingen egen input |
| I16 | WASHER | **FRI reserv** igen |
| Torkare LÅG-input | I9 digital | I9 **analog mux** |
| Torkare HÖG-input | (saknade input! bara O8-output fanns) | I9 analog mux ✅ |
| Fysisk kabel spak→C1 | skulle dras | **utgår** — dras aldrig |
| I11 WIPER_PARK | digital park-sensor | oförändrad |

Notera: mux-designen löser även ett hål i v9.58 — torkare HÖG hade en output (O8)
men **ingen input** som styrde den. Nu får den det.

---

## 6. Fysisk installation (steg för steg)

1. **Vid PDM:en:** löd 5.6 kΩ mellan C10 (5V REF) och I9-kabeln (A11). Krymp.
2. **Dra EN signalkabel** (1.0 mm², förslagsvis märkning `PDM.IN.WIPER_MUX`)
   från A11 till spak-området. (Befintlig I9-kabel kan återanvändas.)
3. **Vid spakarna:** anslut signalkabeln till brytarnas **gemensamma matningsstift**
   (förgrena till spolarknappens och vredets matning).
4. **På utgångssidan:** löd ett motstånd på varje brytarutgång, alla mot jord:
   - Spolarknappens utgång → 10 kΩ → jord
   - Vredets LÅG-utgång → 4.7 kΩ → jord
   - Vredets HÖG-utgång → 22 kΩ → jord
   Motståndens jordändar kan samlas till EN gemensam jordkabel → chassijord
   (rattstångens jordpunkt).
5. Den gamla spolar-planen (kabel till C1) och ev. separat HÖG-kabel utgår.
6. Flasha v9.60, verifiera nivåerna i PDM-GUI:ts live-vy (I9 Voltage ska visa
   tabellvärdena ±0.15 V) **innan** fönstren litas på.

**Mätverifiering vid installation:** med multimeter på A11 mot jord ska du se
≈5.0 / 4.0 / 3.2 / 2.8 / 2.3 / 1.8 V för respektive läge. Avvikelse > 0.2 V ⇒ kolla
lödning/jordpunkt.

---

## 7. WireViz

Schema: `docs/wireviz_v8.0/3_kretsar/mux_torkare_spolare.{yml,svg,png,html}` — visar hela
kretsen inkl. motståndsplaceringar. Kontakt-A- och kontakt-C-schemana uppdateras
när v9.60 är byggd och flashad (pinmappen hålls i synk med verkligheten, inte planer).

---
*Design validerad 2026-06-12 mot configInputs.js (HW-version 23), brute-force-optimerad
över E12, worst-case-analyserad (1% R, 2% VREF, 50 mV ADC). Ersätter spolar-delen av
v9.58; torkar-park-logiken (I11) orörd.*
