# Kabelinventering — fysiska färger per PDM-pin
## 2026-06-13 · från Joels röstmemo (okulär besiktning på bilen)

> **Detta är fysisk sanning** — vad som FAKTISKT sitter på varje pin idag, observerat
> på bilen. Slår all tidigare färgdokumentation (v7.1 och den inbäddade `pinManager`-
> exporten är båda inaktuella). Kolumnen "Stämmer doc?" jämför mot WireViz-schemana
> före denna uppdatering.
>
> Tvärgående streck = fysisk ringmärkning på kabeln (WireViz ritar bara längsgående rand).

## Kontakt A (1-DT-Grå) — inputs

| Pin | Input | Etikett | Observerad färg | Doc före | Status |
|-----|-------|---------|-----------------|----------|--------|
| 1 | I12 | HORN | brun + blå (längs) | br/bl | ✅ stämmer (omärkt kabel — märk!) |
| 2 | I10 | COOLANT_TEMP | blå + gul (**tvärs**) | gn | 🔧 doc fel → blå/gul |
| 3 | I8 | FUEL_LEVEL | grön + röd (längs) | li/sw | ⚠️ = gamla SPOLAR-kabeln (gn/ro). Riktig fuel-givarkabel ej dragen hit än |
| 4 | I6 | TURN_R | svart + grön | gr | 🔧 doc fel → sv/gn |
| 5 | I4 | BRAKE | röd + gul | sv/ro | 🔧 doc fel → rö/gul (omärkt) |
| 6 | I2 | HIBEAM | brun + vit | ge | 🔧 doc fel → br/vit (omärkt) |
| 7 | I1 | BLOWER | **tom** | — | ⬜ ej inkopplad (fläkt-mux planerad v9.60) |
| 8 | I3 | HAZARD | svart + grön | (saknades) | 🔧 → sv/gn |
| 9 | I5 | TURN_L | svart + vit | sv/vit | ✅ stämmer |
| 10 | I7 | REVERSE | **tom** | — | ⬜ ej inkopplad |
| 11 | I9 | WIPER_SLOW | grön + gul | sv/gr | 🔧 doc fel → gn/gul |
| 12 | I11 | WIPER_PARK | grön (hel) | gn | ✅ stämmer |

## Kontakt C (2-DT-Grön) — kraft / CAN / tändning / sensorer

| Pin | Roll | Etikett | Observerad färg | Doc före | Status |
|-----|------|---------|-----------------|----------|--------|
| 1 | I16 | (HANDBRAKE plan) | **tom** | — | ⬜ handbroms planerad hit (v9.60) |
| 2 | I15 | START | röd + svart, **grov 2.5** | sv/vit | 🔧 doc fel → rö/sv |
| 3 | — | PWR.CTRL | **svart** (hel) | rö | ⚠️ doc sa röd; verifiera (ovanligt för kraft) |
| 4 | O3 | IGN_COIL | svart | sv/li | ~ li-rand kanske ej synlig; → sv |
| 5 | O2 | ALT_EXCITE | (ej beskriven) | bl | ⬜ ej i bruk (väntar 82Ω) |
| 6 | O1 | BUSBAR | svart + gul | (saknades) | 🔧 → sv/gul |
| 7 | — | GND.CHASSIS | brun (hel) | br | ✅ stämmer |
| 8 | — | CAN.H | gul | ge | ✅ stämmer |
| 9 | — | CAN.L | blå | bl | ✅ stämmer |
| 10 | — | 5V REF | **tom** | — | ⬜ ej dragen (behövs för muxar v9.60) |
| 11 | I13 | BRAKE_FAULT | **tom** | — | ⬜ givare ej installerad |
| 12 | I14 | OIL.PRESS | (oljebrytare, färg ej angiven) | bl/gn | 🟡 ansluten, färg overifierad |

## Kontakt D (3-DT-Brun) — outputs

| Pin | Output | Etikett | Observerad färg | Doc före | Status |
|-----|--------|---------|-----------------|----------|--------|
| 1 | O17 | HORN_2 | **tom** | sv/ge | ⬜ kabel ej dragen till tuta 2 |
| 2 | O21 | RESERVE | **tom** | — | ⬜ |
| 3 | O24 | TURN_R fram | svart + grön | sv/gn | ✅ stämmer |
| 4 | O9 | RESERVE9 | grön + gul (lös) | rö | ⬜ kvarlämnad kabel, output oanvänd |
| 5 | O8 | WIPER_FST | (ej beskriven) | sv/gr | 🟡 overifierad |
| 6 | O7 | HIBEAM_R | (färg ej angiven) | vit | 🟡 overifierad |
| 7 | O4 | **PARK** | **blå (hel)** | rö | ✅ blå → parkljus. Build O4=PARK bekräftad korrekt (Joel 2026-06-13) |
| 8 | O5 | FUEL (pump) | svart **+** brun (2 kablar) | sv+br | ✅ stämmer |
| 9 | O6 | **BRAKE** | **röd (hel)** | bl | ✅ röd → bromsljus. Build O6=BRAKE bekräftad korrekt (Joel 2026-06-13) |
| 10 | O24 | TURN_R bak | grön | gn | ✅ stämmer |
| 11 | O20 | RESERVE20 | grå + röd (lös) | — | ⬜ gammal radio-acc-kabel, oanvänd |
| 12 | O16 | HIBEAM_L | vit + svart | vit/sv | ✅ stämmer |

## Kontakt B (4-DT-Svart) — outputs

| Pin | Output | Etikett | Observerad färg | Doc före | Status |
|-----|--------|---------|-----------------|----------|--------|
| 1 | O19 | REVERSE | **tom** | gr | ⬜ backljus-utgång ej dragen |
| 2 | O23 | STARTER | svart + röd | rö/sv | ✅ stämmer |
| 3 | O25 | TURN_L fram | gul | sv/vit | 🔧 → gul (märkt "turn left") |
| 4 | O15 | LOWBEAM_R | gul (hel) | ge | ✅ stämmer |
| 5 | O14 | LOWBEAM_L | gul + svart (**tvärs**) | ge/sv | ✅ stämmer |
| 6 | O13 | HORN_1 | röd + gul | sv/ge | 🔧 → rö/gul (omärkt; ev. sv/ge misstolkat) |
| 7 | O10 | WIPER_SLO | grön + svart | gn | 🔧 → gn/sv |
| 8 | O11 | BLOWER | grön + svart (**tvärs**) | sv/ge | 🔧 → gn/sv |
| 9 | O12 | WASHER | grön + röd | gn/ro | ✅ stämmer |
| 10 | O25 | TURN_L bak | gul | gul | ✅ stämmer |
| 11 | O22 | USB_12V | **tom** | vit | ⬜ |
| 12 | O18 | RESERVE18 | **tom** | — | ⬜ |

---

## Kritiska fynd

1. **PARK/BRAKE — LÖST 2026-06-13.** Färgerna (pin7 O4 blå, pin9 O6 röd) avviker från
   VW-original-konventionen, men Joel bekräftar att build-logiken (O4=PARK, O6=BRAKE)
   är **rätt som den är** — blå kabel går faktiskt till parkljus, röd till bromsljus.
   Ingen ändring behövs. Endast WireViz-färgerna uppdaterade.

2. **Fuel-input (A3/I8) har fortfarande gamla spolarkabeln (grön/röd).** Den riktiga
   bränslegivarkabeln är inte dragen dit än. I8 läser alltså fel källa tills dess.

## 🟢 Bekräftat korrekt (bygger förtroende)
GND brun, CAN gul/blå, TURN_R sv-gn/gn, LOWBEAM gul & gul/sv, WASHER gn/rö,
STARTER rö/sv, FUEL-pump sv+br, HIBEAM_L vit/sv, WIPER_PARK gn, TURN_L sv/vit, HORN br/bl.

## ⬜ Omärkta kablar att märka
A1 HORN, A4 TURN_R, A5 BRAKE, A6 HIBEAM, A11 WIPER_SLOW — alla saknar fysisk märkning.

## Pins utan kabel (planerat/ej klart)
A7 fläkt-in, A10 reverse-in, C1 handbroms, C5 alt-excite, C10 5V, C11 brake-fault,
D1 horn2, D2 rpi, B1 reverse-ut, B11 usb, B12 reserve.
