# Audit — kopplingsscheman & dokumentation
## 2026-06-16 · syfte: grundare scheman, hitta komplement/redundans, strukturera i mappar

---

## 1. Inventering — WireViz-scheman (13 st)

"Djup" = hur många kontakter en signal passerar i SERIE (grunt = lätt att läsa/skriva ut A4).

| Schema | Roll | Djup | Bedömning |
|--------|------|------|-----------|
| `kontakt_A_inputs` | Per-kontakt pin-referens (inputs) | 🟢 grunt (2) | **KÄRNA** — modellen alla bör likna |
| `kontakt_B_outputs` | Per-kontakt (outputs) | 🟢 grunt (2) | KÄRNA |
| `kontakt_C_kraft_can` | Per-kontakt (kraft/CAN/sensor) | 🟢 grunt (2) | KÄRNA |
| `kontakt_D_outputs` | Per-kontakt (outputs) | 🟢 grunt (2) | KÄRNA |
| `kraft_busbar` | 12V-distribution + wake | 🔴 djup (~5) | behåll, dela |
| `kraft_5v` | 5V-distribution + (nu) hela delaren | 🟠 medel (4) | behåll, **slimma till supply** |
| `mux_torkare_spolare` | Torkar/spolar-mux | 🔴 djup (~6) | behåll, gör grundare |
| `mux_flakt` | Fläkt-mux | 🔴 djup (~6) | behåll, gör grundare |
| `vattentemp` | NTC-delare | 🟠 medel | behåll, grunda |
| `oljetryck` | Oljebrytare | 🟢 grunt (2) | behåll |
| `handbroms` | Handbroms | 🟢 grunt (2) | behåll |
| `generator_dplus` | Excitering + D+ sense | 🔴 djup (~5) | behåll |
| `pi_spi_displays` | Dash-harness (daisy) | 🔴 djup (~5) | behåll (daisy är inneboende) |

Mermaid: `diagrams_v8.0/pdm_03_headlights` (1 av ~15 logikscheman — separat lager, "hur funkar kretsen").

---

## 2. Komplementaritet (vad hör ihop)

**Två lager som kompletterar varandra — inte dubbletter:**
- **Kontakt-scheman = ÖVERSIKT** ("vad sitter på pin X"). Grunda, en per fysisk kontakt.
- **Krets-scheman = DETALJ** ("hur är muxen/givaren byggd"). Djupare, en per funktion.

Regel: kontakt-schemat ska **peka** "→ se mux_torkare" i stället för att rita om muxen.
Då hålls de i synk och inget ritas två gånger.

**Möts vid gränser:**
- `kontakt_C` (C10-pin) → `kraft_5v` (5V-fördelning) → krets-scheman (sensor-benet). Tre segment, var och en grund.
- `kraft_busbar` (C3) ↔ tändning/hazard/wake.

---

## 3. Redundans & att lösa

1. **`kraft_5v` ritar nu HELA delaren** (supply + sensor-ben) → överlappar mux/sensor-kretsarna.
   **FIX:** kraft_5v = endast SUPPLY (splice → pull-up → ingångspin). Sensor-/brytar-benet
   (nod → switch/NTC → jord) ägs av respektive krets-schema. Då blir kraft_5v grunt OCH unikt.
2. **Djupa scheman** (mux, busbar, generator, dash): applicera samma princip som vi just gjorde
   med kraft_5v/kontakt_C — dela vid naturlig gräns, jord som pin.
3. **`AUDIT_v9.56_2026-06-09.md`** = föråldrad (ersatt av PINMAP v8.0). → `_arkiv/`.

---

## 4. Princip för grunda scheman (SAMMA för alla)

1. **Jord = pin på förbrukaren**, aldrig utritad jordkabel/chassi-nod. (Redan gjort på kraft_5v.)
2. **Dela vid PDM-kontaktgränsen:** matning/supply i ett schema, konsument i ett annat — möts vid pin/nod, med korsreferens i noten.
3. **Mål: max ~3 kontakter i djup** per schema. Då skrivs allt ut snyggt på A4.
4. Kontakt-scheman pekar på krets-scheman i stället för att rita om dem.

---

## 5. Föreslagen mappstruktur

```
docs/wireviz_v8.0/
├── README.md                  (uppdaterad index + konventioner)
├── 1_kontakter/               kontakt_A/B/C/D  (per-kontakt-referens)
├── 2_kraft/                   kraft_busbar, kraft_5v
├── 3_kretsar/                 mux_torkare_spolare, mux_flakt, (blinkers),
│                              vattentemp, oljetryck, handbroms, generator_dplus
├── 4_dash/                    pi_spi_displays
└── _arkiv/                    (utfasade scheman om/när de uppstår)
```

```
docs/  (markdown)
├── (sanning)     PINMAP_v8.0, KABELINVENTERING, ATT_GORA
├── (design)      MUX_torkare_spolare_design, SENSORER_flakt_olja_temp, AUDIT_scheman (denna)
├── (referens)    HANDOVER_pi_can_control, dual_horn_changes, pdm_wake_service_spec,
│                 HWPDM_FORMAT_REVERSE_ENGINEERING, HARDWIRE_INTERNAL_LOGIC,
│                 PDM15_25_35_Instruction_Manual, pi_can_control_v1.0
└── _arkiv/       AUDIT_v9.56_2026-06-09  (föråldrad)
```

---

## 6. Åtgärdsplan (om godkänd)

1. Skapa mappar, flytta .yml + genererade filer.
2. Slimma `kraft_5v` till supply-only (ta bort sensor-benen → de bor i kretsarna).
3. Applicera jord-som-pin + boundary-split på de djupa (mux, busbar, generator).
4. Uppdatera README (index + regenererings-sökvägar) + korsreferenser i docs.
5. Arkivera AUDIT_v9.56.
6. Regenerera alla.
