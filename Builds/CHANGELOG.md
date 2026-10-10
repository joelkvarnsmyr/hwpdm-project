# ELTON PDM25 V2 — Build-changelog

**Regel (från och med 2026-06-11):** Varje ny `.HWPDM`-version får EN rad här: vad ändrades, varför,
och om pinmap/märklista påverkas (`PINMAP-PÅVERKAN: ja/nej`). Ändringar gjorda live i GUI:t ska
antingen sparas som ny version direkt, eller noteras här som "GUI-drift" tills de byggs in.

**Aktuell baslinje:** `Elton_v9.59_radio_removed.HWPDM` (+ DBC v1.1-import krävs i GUI före flash, se workflow i `build_v9.58.py`)
**Sist helverifierade på bil:** `Elton_v9.4.HWPDM` (audit 2026-05-20, alla 16 inputs lästa korrekt)
**Källa till sanning för pins:** `docs/PINMAP_v8.0_2026-06-11.md`

> Filer äldre än v9.56 ligger i `archive/`. Icke-buildfiler (PDF:er, bilder, installers) i `archive/misc/`.

---

## Versionshistorik

Poster före 2026-06-11 är rekonstruerade i efterhand från filnamn och audit-rapporter
(`docs/AUDIT_*.md`) — detaljnivån varierar.

### Juni 2026

| Version | Datum | Ändring | Pinmap-påverkan |
|---|---|---|---|
| **v9.59_radio_removed** | 2026-06-12 | O20 RADIO_ACC → RESERVE20 disabled — radion matas från batteri-busbaren direkt (alltid på), inte via PDM. Byggd av `build_v9.59.py`. Timer2/3-frågan fortfarande öppen. | **ja** — D11 fri |
| **v9.58_washer_enables** | 2026-06-11 | (1) Enabled-drift inbakad: O5 FUEL, O8 WIPER_FST, O11 BLOWER, O19 REVERSE `enabled=true` (var handenablade i GUI). (2) Spolare räddad: I16/C1 = WASHER-input (v9.4-inställningar), O12 enabled, logik ompekad I8→I16 (var 597→637). Byggd av `build_v9.58.py`. ÖPPET: Timer2 CRASH_TMR/Timer3 START_GRACE disabled i fil sedan v9.5x men var enabled i v9.4 — bekräfta mot live före flash. | **ja** — I16/C1 ny spolarkabel |
| **v9.57_lowbeam_fix** | 2026-06-11 | BUGFIX: O14/O15 LOWBEAM `enabled=true` (var false i fil sedan v9.53 trots live-enable i GUI). Byggd av `build_v9.57.py`. OBS: rawSendData i filen är stale — ofarligt, GUI:t ignorerar den vid laddning (verifierat i app-källkod, se format-doc). | nej |
| **v9.56_dual_horn** | 2026-06-09 | Dual horn: O13=HORN_1 + O17=HORN_2 (ny), GF8 HORN_MASTER-säkerhet bevarad. Kräver DBC v1.1-import i GUI. | **ja** — O17/D1 ny kabel |
| **v9.55_fuel_temp_fixes** | 2026-06-09 | FUEL_LEVEL analog på I8 + 150Ω pull-up; COOLANT_TEMP på I10. (Beslut bekräftade av Joel 2026-06-11: allt på PDM, ADS1115-planen skrotad.) | **ja** — I8, I10 |
| **v9.54_pwm_enable** | 2026-06-08 | PWM-dimning aktiverad för ljus-outputs. | nej |
| **v9.53_all_outputs** | 2026-06-06 | CAN-styrning av alla outputs (0x500–0x502), live-testad (show-mode). HÄRIFRÅN: O14/O15-buggen introducerad. | nej |
| v9.52 (3 st: naming_fixes / postcan / o7_test) | 2026-06-05/06 | Namnstädning (RADIO→RADIO_ACC m.m.), CAN-förberedelser, O7-test. | nej |
| v9.45–v9.51 | 2026-06-05 | Torkar-iterationer: park-sensor på I11, debounce, latch-timer → landade i GF-park-latch (v9.50) + simple stayon (v9.51). Park-funktion ~50 % testad. | **ja** — I9/I11 |
| v9.34–v9.44 | 2026-06-02–05 | ALT_EXCITE på O2 (C5), WIPER_FST flyttad till O8, torkare active-low-iterationer. | **ja** — O2, O8 |
| v9.21–v9.33 | 2026-06-01–02 | PWR flyttad till tändningslås (I16→RESERVE16), lamp-softstart, olje-interlock (introducerad+rollback), säkrings- och logikjusteringar, HIBEAM latching+filter. | **ja** — I16 |

### Maj 2026

| Version | Datum | Ändring | Pinmap-påverkan |
|---|---|---|---|
| **v9.4** | 2026-05-20 | ✅ PRODUKTIONSVERIFIERAD (AUDIT_v9.4_FINAL): alla 16 inputs läser korrekt live. Grund för märklista v7.1. | baslinje |
| v9.5–v9.20 | 2026-05-20–31 | Iterationer: EMA-filter, horn, busbar-12V, coolant, blink-fix, headlight-säkringar, hazard momentary, autotune-pass. | delvis |
| v9.0–v9.3 | 2026-05-19/20 | Cut Off/Reset-oscillation löst (AUDIT_v9.0), GND-busbar-topologi bekräftad (AUDIT_v9.2: 13 inputs switch-to-GND). `v9.2_FROMPDM AFTER SEND` = readback från PDM. | — |
| v8.5–v8.12 | 2026-05 | Iterationer (odokumenterade i detalj). | — |

### Mars 2026

| Version | Datum | Ändring | Pinmap-påverkan |
|---|---|---|---|
| v8.0–v8.4 | 2026-03 | Generator-era: byggda med `generate_hwpdm.js` från `pdm25_outputs_complete.json`. | — |
| v7.0–v7.14 | 2026-03 | Format-reverse-engineering-eran. `v7.0.OR` + `joel fix_2` = manuella testconfigs som låste funktions-encodingen (AND/OR-träd, variabel-ID-karta). | — |
| v5.8–v6.2 | 2026-03 | Tidiga byggen. AUDIT_RAPPORT_v5.6b flaggade fel (undefined "start", osäker reset) — historiska, ersatta av v9-logiken. | — |

---

## Kända avvikelser fil ↔ verklighet (per 2026-06-11, efter v9.58)

- ~~GUI-drift för outputs~~ — LÖST i v9.58 (O5/O8/O11/O19 enabled i fil).
- **ÖPPET: Timer2 CRASH_TMR + Timer3 START_GRACE** är `enabled=false` i fil sedan v9.5x men
  var `true` i v9.4, och GF8 HORN_MASTER refererar Timer2. Bekräfta mot live-GUI före flash —
  säkerhetsfunktion, ska inte ändras blint från script.
- rawSendData i v9.53–v9.58 är stale (JSON-bara patchar). Självläker vid nästa GUI-spara.
