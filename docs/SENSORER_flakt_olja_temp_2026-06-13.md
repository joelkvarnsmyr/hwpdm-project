# Fläkt, oljetryck & vattentemp — kopplingsdesign
## 2026-06-13 · komplement till MUX-torkare-dokumentet

> Tre givare/brytare som var olösta i pinmappen. Här: hur du kopplar var och en,
> verifierat mot build v9.59 + VW LT-manualen. WireViz-scheman i `docs/wireviz_v8.0/`:
> `mux_flakt.*`, `oljetryck.*`, `vattentemp.*`.

> **⚠️ UPPDATERING 2026-06-13 (Joels beslut):** Alla **analoga** givare matas från **5V REF
> (C10)**, inte intern VBat — alltså coolant (I10) OCH fuel (I8) får extern pull-up mot 5V,
> precis som muxarna. Stabilare avläsning (driver inte med batterispänningen). KONSEKVENS:
> SC1 (coolant) och SC2 (fuel) måste **byggas om** för 5V-delaren → kräver att vi mäter
> givarnas resistans. Digitala brytare (olja, handbroms, dörr) använder fortf. intern VBat-pull-up.
> Texten nedan om "intern VBat = enklast" är därmed **överspelad** för coolant/fuel.

---

## 1. Fläktomkopplare (E9 → I1 / pin A7) — analog mux, låg/hög

**Samma princip som torkar-muxen.** Manualen bekräftar att E9 är en 2-stegs
fläktomkopplare (track 52/53 = låg/hög), roterande → lägena är ömsesidigt uteslutande.
Det räcker alltså med **två motstånd** (ett färre än torkarna).

### Input — fysisk koppling (se `mux_flakt.png`)
Switch-to-GND, motstånd på utgångssidan (din byggordning), gemensam 5.6 kΩ pull-up
från C10 (5V REF) vid PDM:en — **delas med torkar-muxen, samma 5V-stam**.

| Läge | Motstånd | Spänning på A7 | PDM-fönster |
|------|----------|----------------|-------------|
| OFF (idle) | — | 5.00 V | > 4.4 V |
| LÅG | **10 kΩ** | 3.21 V | 2.7 – 3.7 V |
| HÖG | **2.2 kΩ** | 1.41 V | 1.0 – 2.0 V |

Marginal mellan fönstren ≥ 0.7 V — ännu rymligare än torkarnas (bara 2 lägen).
Båda motstånden finns i ditt sortiment. I1 ställs till **analog (mode 2), pullResistor 0**.

### Output — två hastigheter från EN utgång (O11)
O11 BLOWER har **redan PWM konfigurerat** i builden (100 Hz). Du behöver alltså
**inget effektmotstånd på motorsidan** — duty-cyklen ger hastigheten:

```
O11 ON om (LÅG-fönster ELLER HÖG-fönster)         ← annars av (idle = av)
   PWM-duty styrs av I1-spänningen (PWMMappingVariable = I1 Voltage, var 560):
      HÖG-fönster (~1.4 V)  → 100 % duty  → full fläkt
      LÅG-fönster (~3.2 V)  → ~40 % duty  → låg fläkt
```

> ⚠️ Build-justering till v9.60: nuvarande `PWMMappingVariable` pekar på en konstant
> (var 1) och mappningen `[0,0,0,0,0,0,40,40,100,100,100]` antar *stigande* spänning→duty.
> Med switch-to-GND blir idle = 5 V (hög spänning), så mappningen ska **vändas** till
> fallande (låg spänning = hög duty) och O11-funktionen gatas av över ~4.4 V. Verifieras
> med GUI-roundtrip, exakt som CAN-villkoren.

**Alternativ om du vill ha fler steg senare:** byt fläktvredet mot ett med flera lägen
och lägg till motstånd — mux:en skalar precis som torkarna. PWM kan ge steglös fart.

---

## 2. Oljetrycksomkopplare (F1 → I14 / pin C12)

**Enklaste givaren — en kabel, inget externt motstånd.** Manualen: F1 är en enkel
switch (track 8) som sluter signalterminal → kropp när oljetrycket är **lågt**.
Kroppen jordar genom gängan i motorblocket.

### Fysisk koppling (se `oljetryck.png`)
| Från | Kabel | Till |
|------|-------|------|
| C12 (I14) | `PDM.IN.OIL.PRESS` bl/gn 1.0 mm² | F1 signalterminal |
| F1 kropp | (gänga, ej kabel) | Motorblock → jord |

**Pull-up:** använd PDM:ens **interna** 10 kΩ mot VBat (`pullResistor = 1`).
Inget externt motstånd.

### Logik
| Tillstånd | Switch | I14 läser | Betyder |
|-----------|--------|-----------|---------|
| Motor av / lågt tryck | sluten | ~0 V (LÅG) | varning |
| Motor igång, tryck OK | öppen | ~VBat (HÖG) | OK |

> ⚠️ Vid nyckel-på före start är trycket 0 → lampan/larmet "lyser" tills motorn går.
> Det är normalt, men för att slippa falsklarm bör oljevarningen **gatas mot en
> start-grace** (motorn igång en kort stund). Det är precis vad **Timer3 START_GRACE**
> var till för — den är `disabled` i fil sedan v9.5x och bör återaktiveras när I14
> tas i bruk (se KVAR-listan i pinmap-minnet). F1-brytaren ska dessutom **bytas** innan
> inkoppling (känd åtgärd).

---

## 3. Kylvätsketempgivare (G2 → I10 / pin A2)

**Bra nyhet: "det saknade motståndet" behövs förmodligen inte externt.**
Manualen: G2 är en NTC-sender (resistans sjunker när temp stiger), kropp jordad via
gängan. För att läsa den som spänning krävs en pull-up → spänningsdelare.

### Verifiering av befintlig kalibrering (SC1)
Build v9.59 har en färdig 20-punkts kalibreringskurva (SC1 COOLANT_T, var 605).
Råvärdena går från 200 mV (120 °C) till **5200 mV** (−40 °C). Eftersom 5200 mV
överstiger 5 V kan kurvan **inte** ha byggts mot 5V-referensen — den förutsätter en
**~10 kΩ pull-up mot VBat**. Den pull-up:en finns **inbyggd** i PDM:en.

### Rekommenderad koppling — enklaste (matchar SC1)
| Inställning | Värde |
|-------------|-------|
| I10 | analog (mode 2), **pullResistor = 1** (intern 10 kΩ → VBat) |
| Kabel | G2 signalterminal → A2, `INST.SENS.COOLANT` gn 1.0 mm² |
| Jord | G2-kropp via gänga → motorblock |
| Externt motstånd | **inget** |

Då stämmer den befintliga SC1-kurvan direkt — testa mot gamla mätaren/kokande vatten.

### Alternativ — extern pull-up mot 5V REF (högre noggrannhet)
Intern pull-up mot **VBat** gör att avläsningen driver lite med batterispänningen
(12–14.6 V). Vill du ha rock-stabil avläsning: extern pull-up från **C10 (5V REF)**
till A2 i stället (`pullResistor = 0`). **Men då måste SC1 byggas om** för den nya
delaren. Det kräver att vi vet NTC:ns resistans vid några temperaturer.

### Kalibreringsprocedur (om du väljer 5V-vägen, eller vill verifiera)
1. Mät NTC:ns resistans kall (rumstemp) och varm (≈90 °C, kör motorn varm).
2. Ge mig de värdena → jag räknar ut optimal pull-up och bygger en ny SC1-kurva.
3. Riktvärde för pull-up om NTC ≈ 150 Ω–6 kΩ-typ: **~1 kΩ** mot 5V (bekräftas av mätning).

> Detta följer projektets regel (minne `feedback_mcp_manual`): verifiera mot verkligheten
> innan vi litar på en kurva — den byggda databasen har luckor.

---

## 4. Handbromsvarning (F9 → I16 / pin C1) — tillägg 2026-06-13

Joel valde **Alternativ A**: handbromsbrytaren läggs på **I16/C1**, som frigörs av
torkar-muxen (spolaren flyttar därifrån till I9). Ingen blinkers-mux behövs.

Manualen: F9 är en mekanisk switch-to-ground (Fig 13.83, kabel bl/br) som grundar vid
dragen handbroms. Identisk topologi med bromsljusbrytaren (I4) → samma inställningar.

### Fysisk koppling (se `handbroms.png`)
| Från | Kabel | Till |
|------|-------|------|
| C1 (I16) | `PDM.IN.HANDBRAKE` bl/br 1.0 mm² | F9 signalterminal |
| F9 fäste | (mekaniskt, ej kabel) | Kaross → jord |

**PDM-inställning (kopia av I4 BRAKE):** mode 0 (digital), pullResistor=1 (intern
10k → VBat), activeLevel=0 (active-low), thr 6 V, hyst 1 V. Inget externt motstånd.

| Tillstånd | Switch | I16 läser | Betyder |
|-----------|--------|-----------|---------|
| Handbroms dragen | sluten | ~0 V (LÅG) | indikator PÅ |
| Handbroms släppt | öppen | ~VBat (HÖG) | av |

Indikatorn visas i dashboarden (CAN), som allt annat varningsljus.

---

## Sammanfattning — vad du faktiskt behöver göra

| Givare | Extern komponent | PDM-inställning | Kabeldragning |
|--------|------------------|-----------------|---------------|
| **Fläkt** | 5.6k (delad) + 10k + 2.2k | I1 analog, O11 PWM (vänd mappning) | 1 signalkabel A7 → vred, motstånd på utgångar → jord |
| **Oljetryck** | inget | I14 digital, pullResistor=1, Timer3 grace | 1 kabel C12 → F1 (byt brytaren) |
| **Vattentemp** | inget (intern pull-up) | I10 analog, pullResistor=1 | 1 kabel A2 → G2 (redan dragen) |
| **Handbroms** | inget (intern pull-up) | I16 digital, pullResistor=1, active-low | 1 kabel C1 → F9 |

Bygge **v9.60** samlar PDM-ändringarna (fläkt-mux + PWM-vändning, I14/I10 pull-up,
Timer3, I16→handbroms, torkar-mux på I9). Säg till så bygger jag den — och bekräfta om du vill köra fläktens HÖG=2.2k /
LÅG=10k eller om du vill att jag väljer andra värden.
