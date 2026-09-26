# ELTON — Dokumentationsindex & källa till sanning
## 2026-06-16 · ingångspunkt: läs detta först

> **Regel: varje fakta bor på EXAKT ETT ställe.** Övriga dokument refererar dit, restaterar inte.
> Hittar du samma uppgift på två ställen som säger olika — det här indexet avgör vilken som gäller.

---

## Källor till sanning (kanoniska)

| Vad | KÄLLA (enda sanning) | Övriga refererar |
|-----|----------------------|------------------|
| **PDM pin → funktion** (vad varje I/O gör + Deutsch-pin) | `PINMAP_v8.0_2026-06-11.md` | wireviz, mermaid |
| **Fysiska kabelfärger** (vad som faktiskt sitter på bilen) | `KABELINVENTERING_2026-06-13.md` | wireviz |
| **Faktisk PDM-logik** (det som körs) | `Builds/Elton_v9.xx.HWPDM` (senaste) + `Builds/CHANGELOG.md` | PINMAP |
| **Fysiska kopplingsscheman** | `wireviz_v8.0/` (mappstruktur, se dess README) | — |
| **Logik-/funktionsscheman** | `diagrams_v8.0/` (Mermaid, 1 av ~15 klar) | — |
| **Att göra** | `ATT_GORA_2026-06-13.md` | — |
| **Pi GPIO / dash** | `DRIVER-DASH.md §7` (Pi-repo, ej här) | wireviz `4_dash/` |
| **CAN-protokoll Pi↔PDM** | `pi_can_control_v1.0.md` + DBC-fil | HANDOVER |

## Design-/beslutsdokument (motivering, ej löpande sanning)
- `MUX_torkare_spolare_design_2026-06-12.md` — analog mux-design
- `SENSORER_flakt_olja_temp_2026-06-13.md` — fläkt/olja/temp/handbroms
- `AUDIT_scheman_2026-06-16.md` — schema-audit + konventioner

## Referensdokument (hur saker funkar)
- `HWPDM_FORMAT_REVERSE_ENGINEERING.md` — .HWPDM-filformat
- `HARDWIRE_INTERNAL_LOGIC.md` — PDM:ens interna logik
- `PDM15_25_35_Instruction_Manual.md` — tillverkarens manual

## Handover till Pi-expert
- `HANDOVER_pi_can_control.md`, `dual_horn_changes_for_pi_bridge.md`, `pdm_wake_service_spec.md`

---

## Arkiverat (FÅR EJ användas som sanning)

| Plats | Vad | Ersatt av |
|-------|-----|-----------|
| `_arkiv/ELTON_PDM25V2_KOMPLETT_v5.6b/` | Hela v5.6b-bunten: 15 gamla mermaid, märklistor v6.0/v7.0/v7.1, gamla audits (v5.6b/v9.0/v9.2/v9.4), installation-JSON, config-xlsx | PINMAP v8.0, KABELINVENTERING, wireviz_v8.0, diagrams_v8.0 |
| `docs/_arkiv/AUDIT_v9.56_2026-06-09.md` | Gammal projektaudit | PINMAP v8.0 |

> De gamla märklistorna (v6.0–v7.1) och den inbäddade `pinManager`-tabellen i .HWPDM hade
> MOTSTRIDIGA pin-etiketter. Det var själva problemet PINMAP v8.0 + KABELINVENTERING löste.
> Öppna aldrig en arkiverad fil för att "kolla en pin" — den ljuger. Använd PINMAP.
