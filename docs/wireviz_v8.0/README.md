# ELTON PDM25 V2 — Kopplingsscheman (WireViz) · v8.0

Fysiska kopplingsscheman för den som ska serva bilen. Källa: PINMAP v8.0 + kabelinventering
2026-06-13 (verkliga färger) + DRIVER-DASH.md §7 (Pi). Strukturerat i mappar 2026-06-16.

## Mappstruktur

```
wireviz_v8.0/
├── README.md            (denna)
├── 1_kontakter/         per Deutsch-kontakt (A/B/C/D) — grund översikt, "vad sitter på pin X"
├── 2_kraft/             kraftdistribution: busbar (12V), 5V-ref, hazard-wake
├── 3_kretsar/           detaljkretsar: muxar, givare, generator
├── 4_dash/              Raspberry Pi dash-harness
└── _arkiv/              utfasade scheman
```

**Två lager som kompletterar varandra:** `1_kontakter/` = ÖVERSIKT (grunda, en per kontakt).
`3_kretsar/` = DETALJ (hur en mux/givare är byggd). Kontakt-schemana pekar på krets-schemana
i stället för att rita om dem.

## Innehåll

### 1_kontakter/ — per Deutsch-kontakt
| Fil | Hus | Innehåll |
|-----|-----|----------|
| `kontakt_A_inputs.*` | GRÅ | Alla inputs: spakar, knappar, givare |
| `kontakt_B_outputs.*` | SVART | Outputs: halvljus, blink V, horn 1, torkare låg, fläkt, spolarpump, starter, backljus, USB |
| `kontakt_C_kraft_can.*` | GRÖN | Kraft (PWR/GND), CAN, tändning/start, tändspole, generator, busbar, 5V-fördelning, sensorer |
| `kontakt_D_outputs.*` | BRUN | Outputs: helljus, park, broms, blink H, bränslepump, torkare hög, horn 2 |

### 2_kraft/ — kraftdistribution
| Fil | Innehåll |
|-----|----------|
| `kraft_busbar.*` | Batteri → 10A keramiksäkring → +12V busbar → {radio ACC, Raspberry Pi, **TVÅ vägar till C3:** tändningslås (RUN) + hazard→diod (wake)}. Löser C3-källan (Avvikelse A). Hazard-wake kräver ignition-sense + suppress-logik (ATT_GORA spår 4) |
| `kraft_5v.*` | **PLANERAD v9.60.** 5V REF (matas från C10/kontakt C) → 5 separata pull-ups → nod → (ingång) + (sensor/brytare). Strömbudget ~37/100 mA. TURN_MUX = TURN_L+TURN_R ihop |

### 3_kretsar/ — detaljkretsar
| Fil | Innehåll |
|-----|----------|
| `mux_torkare_brytare.*` | **PLANERAD v9.60.** Torkar+spolar-muxens brytar-/motståndssida (I9). Matning/avläsning (pull-up→5V) i kraft_5v. Se `MUX_torkare_spolare_design`-doc |
| `mux_flakt_brytare.*` | **PLANERAD v9.60.** Fläkt-muxens vred-/motståndssida (I1). Matning i kraft_5v |
| `vattentemp.*` | G2 NTC → I10/A2, **extern pull-up mot 5V REF** (bygg om SC1). Se sensor-doc |
| `oljetryck.*` | F1 oljetrycksbrytare → I14/C12, intern pull-up VBat (digital) |
| `handbroms.*` | **PLANERAD v9.60.** F9 handbromsvarning → I16/C1, intern pull-up (kopia I4 BRAKE) |
| `generator_1_excitering.*` | DEL 1: O2 ALT_EXCITE → 82Ω → spärrdiod (katod→D+) → generator D+ |
| `generator_2_laddstatus.*` | DEL 2: generator D+ (mätpunkt) → laddstatus-sense → PDM → CAN laddlampa |
| `motor_tandspole_1_matning.*` | DEL 1: O3 → N6 ballast → spole kl.15 (+). Original-VW, återskapad ur manualen |
| `motor_tandspole_2_fordelare.*` | DEL 2: spole kl.1 (−) → fördelare/brytarspetsar → jord (motorblock) |

### 4_dash/ — Raspberry Pi
| Fil | Innehåll |
|-----|----------|
| `pi_1_ribbon.*` | DEL 1: Pi 5 (10 GPIO) → GX16 rainbow-ribbon (BK,WH,GY,VT,BU,GN,YE,OG,RD,BN). **GPIO-sanning: `DRIVER-DASH.md §7`** |
| `pi_2_displays.*` | DEL 2: GX16 → 3× ST7789 (SPI0, delad buss 1-7 daisy, unik CS/skärm: OG→S1, RD→S2, BN→S3) |

Per schema: `.png`/`.svg` (bild), `.html` (bild + BOM), `.bom.tsv` (kabellista), `.yml` (KÄLLAN — redigera denna).

## Konventioner (samma för alla scheman)

1. **Jord = GND-pin på förbrukaren**, aldrig utritad jordkabel/chassi-nod.
2. **Dela vid PDM-kontaktgränsen:** matning/supply i ett schema, konsument i ett annat — möts vid pin/nod.
3. **Mål: max ~5 kontakter i djup** → skrivs ut snyggt på A4.
4. **DT-husfärg** på titelraden (A=GY grå, B=BK svart, C=GN grön, D=BN brun) + i klartext (svart-på-svart oläsligt annars). Husfärg ≠ kabelfärg.
5. Kontakt-scheman pekar på krets-scheman, ritar inte om dem.

## Layout-riktning (vertikal/horisontell)

Kedjor/träd renderas **vertikalt (TB)** → blir kompakta i st.f. breda remsor (ryms på en sida).
Kontakter/fläktar (A-D, kraft_5v) + Pi-harnessen (pi_1/pi_2) renderas **horisontellt (LR)**.
Styrs av ELTON-patchen (`WIREVIZ_RANKDIR`). Använd **`render_all.py`** som sätter rätt riktning
per diagram (TB-listan finns i scriptet) — kör inte `wireviz` per fil manuellt.

**Långa kretsar delas i rena delgrafer** (inte pixel-delning av en bild): motor-tändspolen,
generatorn och Pi-dashen är var och en uppdelad i `_1`/`_2` vid en naturlig nod (spole, D+,
GX16) så varje delkrets får stora läsbara boxar och ryms helt på en A4-sida.

## Regenerera efter ändring

```powershell
$env:PATH += ";C:\Program Files\Graphviz\bin"
python render_all.py        # renderar ALLA med rätt riktning (TB/LR)
```

**Regel:** ändras pin-tilldelning i en ny build → uppdatera PINMAP FÖRST, sedan YAML, sedan regenerera.

> Verktyg: [WireViz](https://github.com/wireviz/WireViz) 0.4.1 + Graphviz. Färgkoder: sw=BK, ws=WH,
> ge=YE, gn=GN, gr=GY, bl=BU, ro=RD, br=BN, li=VT, orange=OG.
> Fallgropar: använd `→` (inte `->`) i texter; mellanslag efter kolon i inline-`{}`; kontakt-till-
> kontakt utan kabel kraschar (lägg stub).

**Tvärgående ringmärken — löst med text, inte grafik.** En lokal WireViz-patch testades
(`_patches/patch_transverse.py`, `[[tvar]]` i `notes` → tvärgående ringar). Den fungerade bara
delvis: Graphviz ritar kopplingar som böjda kanter och ringarna hamnade bara mitt på kabeln,
inte hela. **Beslut:** kablar med fysiska tvärringar ritas med **basfärg + beskrivande note**
(t.ex. coolant = BLÅ kabel + GULA tvärringar, blower = GRÖN + SVARTA, lowbeam-L = GUL + SVARTA).
Patch-filen finns kvar för referens men är inte aktivt använd i scheman.

**Manual-PDF stil:** `build_manual.py` använder dashboard-DNA — mörk titelsida med LT-logon
(`_assets/elton-logo.png`), guld accent (#a98a57 från logon), röd (#ff3333) för varningar.

## Komponentbilder (`_assets/`)

Motstånd och dioder visas med riktig färgkod (5-band 1%) via WireViz `image:`.
Bilderna genereras deterministiskt — kör `_assets/gen_components.py` (Pillow) för att
bygga om dem. Inbäddning: `image: {src: ../_assets/r_5k6.png, width: 150}` (sökväg
relativt undermappen). Värden: 5.6k/10k/4.7k/22k/2.2k/82Ω/150Ω + diod.

**Kontakt-ikoner:** kontakt A–D har en DT-kontakt-ikon i husfärg (`_assets/connectors/dt_*.png`,
genereras av `gen_connectors.py`). Det är platshållare — byt mot riktiga foton genom att
spara över filerna (samma namn: dt_gra/dt_gron/dt_svart/dt_brun.png) och regenerera.

## Komplement
- Logik-/funktionsscheman (Mermaid): `docs/diagrams_v8.0/` (1 av ~15)
- Sanning för pins: `docs/PINMAP_v8.0_2026-06-11.md` · Fysiska färger: `docs/KABELINVENTERING_2026-06-13.md`
- Att-göra: `docs/ATT_GORA_2026-06-13.md` · Audit: `docs/AUDIT_scheman_2026-06-16.md`
