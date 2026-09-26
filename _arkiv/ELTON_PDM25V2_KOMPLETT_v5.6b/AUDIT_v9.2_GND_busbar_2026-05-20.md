# Elton_v9.2.HWPDM — GND-busbar topology

**Datum:** 2026-05-20
**Bygger på:** v9.1 (Cut Off-tröskel sänkt + I2/I12 thr 1V)
**Syfte:** Förbereda PDM för komplett ombyggnad där signal-busbar bär GND istället för +12V. Alla manuella switchar grundar mot busbar → switch-to-GND topologi.

---

## Vad ändrades i v9.2 vs v9.1

### 11 inputs flyttade till GND-busbar-konfiguration

| Input | activeLevel | thresholdVoltage | pullResistor | Vad förändras |
|---|---|---|---|---|
| **I2 HIBEAM** | LOW (oförändrad) | 1V (oförändrad) | OFF → **PullUp 200K** | Definierar idle 5V istället för flytande 1.5V |
| **I3 HAZARD** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I4 BRAKE** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I5 TURN_L** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I6 TURN_R** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I7 REVERSE** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I8 WASHER** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I10 COOLANT_LOW** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I12 HORN** | LOW (oförändrad) | 1V (oförändrad) | OFF → **PullUp 200K** | Definierar idle |
| **I13 BRAKE_FAULT** | HIGH → **LOW** | 6V → **1V** | OFF → **PullUp 200K** | Komplett flip |
| **I14 OIL.PRESS** | LOW (oförändrad) | 2.5V (oförändrad) | OFF → **PullUp 200K** | Definierar idle |

### 2 key-barrel-inputs får PullDown (idle = 0V definierad)

| Input | activeLevel | threshold | pullResistor | Varför |
|---|---|---|---|---|
| **I15 START** | HIGH | 6V (oförändrad) | OFF → **PullDown 40K** | Tändlåsets kl.50 är +12V-källa. PullDown drar idle till 0V så switchen ger ren puls från 0V till +12V vid start. |
| **I16 IGNITION** | HIGH | 6V (oförändrad) | OFF → **PullDown 40K** | Tändlåsets kl.15 är +12V-källa. PullDown definierar idle 0V (istället för flytande 1.5V). |

### 3 analoga inputs oförändrade

I1 BLOWER, I9 WIPER_SPEED, I11 COOLANT — dessa har egna spänningsdelningskretsar och är inte switchar. Lämna som de är.

---

## Vad detta innebär för kablaget

```
Före (v9.0/v9.1) — +12V busbar:           Efter (v9.2) — GND busbar:

  +12V (säkrad)                            Chassijord punkt 5
       │                                        │
       ▼                                        ▼
  ┌──────────┐                            ┌──────────┐
  │  Signal- │                            │  Signal- │
  │  busbar  │                            │  busbar  │
  └──────────┘                            └──────────┘
       │                                        │
   ┌───┼─...                                ┌───┼─...
   ▼                                        ▼
  E2  blink V ───── till I5                E2  blink V ───── till I5
  E3  hazard  ───── till I3                E3  hazard  ───── till I3
  etc.                                     etc.

  Switch trycks: input = +12V              Switch trycks: input = 0V
  Switch öppen: input flyter ~1.5V         Switch öppen: PullUp drar till ~5V
```

### Konkreta kablage-effekter

1. **Tag bort matarkabeln** som idag matar in +12V till signalbusbaren (och dess säkring).
2. **Anslut signalbusbaren mot chassijord** med en kort 2.5–4 mm² kabel.
3. **Alla switch-kablar oförändrade** — de fortsätter gå från busbar → switch → PDM-input.
4. **Säkring kan tas bort** — GND-busbar behöver ingen säkring (kortslutning till GND är "no-op" eftersom det redan är GND).

### Ändringar du INTE behöver göra (kvarstår precis som idag)

- I15/I16 till tändlåset (kl.50, kl.15)
- I1/I9/I11 analoga sensorkretsar
- I14 oljetryck (F1 grundar redan mot chassi i originalet)
- ALLA outputs (de drivs av PDM, oberoende av input-topologi)
- ALLA timers, GFs, output-funktioner

---

## Bekräftelse efter uppladdning

Efter att du laddat v9.2 till PDM:n och anslutit GND-busbaren, gå till Inputs-fliken och verifiera:

- **Idle-spänning på alla LOW-inputs:** ska visa ~5V (PullUp till intern referens) istället för 1.5V som tidigare
- **Status:** alla 11 nya LOW-inputs ska visa **OFF** vid idle (5V > 1V threshold, Active LOW = ej aktiv)
- **Tryck en switch i taget** — t.ex. blinkerspak V → I5 ska tappa till 0V → status OFF→ON
- **Tändlåset OFF:** I15 och I16 ska visa ~0V (PullDown drar idle till GND) och OFF
- **Tändlåset RUN:** I16 ska visa ~12V → ON. I15 fortfarande ~0V → OFF.
- **Tändlåset START:** I15 ska visa ~12V → ON (momentärt).

---

## OBS — verifiera pullResistor-encoding

Hardwire-formatet dokumenterar inte explicit värdena för `pullResistor`-fältet. Jag antagit:
- `0` = OFF
- `1` = PullDown 40K
- `2` = PullUp 200K

Detta är min bästa tolkning baserat på manualens hardware-beskrivning ("40K pull Down / 200K pull up" per pin). **Verifiera i konfiguratorn** — om värdena är tilldelade fel kommer du se idle-spänningar långt över eller under förväntan. Skulle det vara fel, swappa 1 ↔ 2 i fältet `pullResistor` på alla 13 ändrade inputs.

---

*Genererad 2026-05-20 från Elton_v9.1.HWPDM.*
