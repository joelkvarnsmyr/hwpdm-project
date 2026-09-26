# HWPDM File Format — Reverse Engineering Documentation

**Project:** Elton LT — VW LT31 1976 PDM25 V2 Wiring
**Date:** 2026-03-06
**Status:** Working — generates files that load correctly in Hardwire PDM Configurator
**Tool:** `generate_hwpdm.js`

---

## Overview

The `.HWPDM` file is the configuration format used by the **Hardwire Electronics PDM Configurator** software for their PDM15/25/35 power distribution modules. The file is JSON with a specific structure that includes both human-readable configuration objects and a `rawSendData` array containing the serial protocol commands sent to the PDM hardware.

This document describes the file format as reverse-engineered from existing configurator files, the official instruction manual, and iterative testing.

---

## File Structure (Top-Level JSON)

```
{
  "MetaData":          {},       // File metadata, version, timestamps
  "Global":            {},       // CAN bus settings, keypad keys, password
  "Input":             [16],     // 16 input channels
  "OutputHS":          [35],     // 35 high-side output slots (PDM25 uses 0-24)
  "OutputLS":          [35],     // 35 low-side output slots (PDM25: O1-O4 can be LS)
  "Timer":             [30],     // 30 timers (pulse train, one-shot, etc.)
  "LoggingGroup":      [10],     // Data logging groups
  "Counter":           [30],     // 30 counters
  "MathsChannel":      [30],     // 30 maths channels (arithmetic on variables)
  "GenericFunction":   [30],     // 30 generic logic functions
  "SensorCalibration": [20],     // 20-point calibration tables
  "TwoDTable":         [10],     // 2D lookup tables
  "CANKeypad":         [4],      // CAN keypad configs (Blink Marine, etc.)
  "CANInputFilter":    [100],    // CAN input message filters
  "CANInput":          [100],    // CAN input variable parsing
  "CANOutput":         [100],    // CAN output frame construction
  "CANStream":         [25],     // CAN output stream frames
  "MPDMDevice":        [],       // Multi-PDM device linking
  "LINBus":            {},       // LIN bus config
  "pinManager":        {},       // Physical pin assignments
  "rawSendData":       [...]     // Serial protocol command stream (see below)
}
```

---

## rawSendData Protocol

The `rawSendData` array contains strings, each representing a line of serial commands in the same format the configurator sends to the PDM.

> **VERIFIED 2026-06-11 (configurator source, unpacked-app):** `rawSendData` is **write-only** — a snapshot generated at save time, never read back.
> - `loadConfigFile()` (mainDOM.js:822) populates the UI from the JSON sections only; `rawSendData` is ignored on load.
> - Sending to the device (`startDeviceConfigurationSend()`, connection.js:758) rebuilds the command stream fresh from the in-memory config via `buildSendConfigArray()` — it does NOT replay the file's `rawSendData`.
> - `saveConfigFile()` (mainDOM.js:971) regenerates `rawSendData` from the in-memory config on every save.
>
> **Consequence:** script-built files only need correct JSON sections to load and flash correctly. A stale `rawSendData` (as in `Elton_v9.53`–`v9.57`, which were patched JSON-only) is harmless to the configurator — but do NOT use `rawSendData` as a data source in analysis scripts; read the JSON sections instead. Opening and re-saving a file in the configurator heals the snapshot.

(Earlier revisions of this document claimed both representations must be kept consistent; that was a misreading — kept here as a warning since the stale stream WILL mislead any tooling that parses it.)

### Line Format

```
$,6,CMD1,CMD2,CMD3,CMD4,#\n
```

- `$,6,` — frame header (constant)
- `CMD1,CMD2,...` — 1-4 commands per line, comma-separated
- `,#\n` — frame terminator

### Command Format

```
PREFIX,field,index,"value"           // Standard: section, field number, item index, value
PREFIX,field,index,subindex,"value"  // Subindexed: for arrays (functions, mappings)
PREFIX,field,"value"                 // Global: no index (GL section)
PREFIX,field,subindex,"value"        // Global subindexed (GL with sub-field)
```

### Section Prefixes (emission order)

| Prefix | Section              | Count  | Notes |
|--------|----------------------|--------|-------|
| `GL`   | Global               | ~10    | CAN speed, termination, keypad keys |
| `PH`   | Phase/Header?        | 1      | Always `PH,1,"0"` |
| `OP`   | Outputs (HS then LS) | ~1900  | Fields 1-19 = HS, fields 20-38 = LS |
| `IP`   | Inputs               | ~160   | 16 inputs x 10 fields |
| `LG`   | Logging Groups       | varies | Copy from template |
| `TI`   | Timers               | ~540   | 30 timers x 18 fields |
| `CT`   | Counters             | varies | Copy from template |
| `MC`   | Maths Channels       | varies | Copy from template |
| `GF`   | Generic Functions    | ~3120  | 30 GFs, field 3 has 100 subindexes |
| `SC`   | Sensor Calibrations  | varies | 20 calibration tables |
| `TD`   | 2D Tables            | varies | Copy from template |
| `CK`   | CAN Keypads          | varies | Copy from template |
| `CF`   | CAN Input Filters    | varies | Copy from template |
| `CI`   | CAN Inputs           | varies | Copy from template |
| `CO`   | CAN Outputs          | varies | Copy from template |
| `CS`   | CAN Streams          | ~17700 | Largest section by far |
| `EC`   | End marker           | 1      | Signals end of data |

**IMPORTANT:** The OP section emits ALL high-side outputs first (fields 1-19 for i=0..24), THEN all low-side outputs (fields 20-38 for i=0..24). They are NOT interleaved per output.

---

## Output Fields (OP Section)

### High-Side (HS) Fields: OP,1-19

| Field | Name               | Type     | Notes |
|-------|--------------------|----------|-------|
| 1     | lowFuse            | number   | Low fuse threshold in amps |
| 2     | highFuse           | number   | High fuse threshold in amps |
| 3     | peakFuse           | number   | Peak/inrush fuse in amps |
| 4     | peakFuseTime       | number   | Peak fuse time in milliseconds |
| 5     | enabled            | "0"/"1"  | Output enabled flag |
| 6     | stayOnTime         | number   | Stay-on after input removed (ms) |
| 7     | turnOnDelay        | number   | Delay before output activates (ms) |
| 8     | clearTime          | number   | Overcurrent clear time (value x10 = ms) |
| 9     | retries            | number   | Retry count after trip. **0 = continual retries (dangerous!)** |
| 10    | tripMode           | 0/1/2    | 0=Normal, 1=Instant, 2=Latching |
| 11    | (reserved)         | "0"      | Always 0 |
| 12    | function[]         | subidx   | Logic function array (see Function Format below) |
| 13    | label              | string   | Output name/label |
| 14    | scaler             | number   | Typically 100 |
| 15    | offset             | number   | Typically 0 |
| 16    | PWMFrequency       | number   | PWM frequency (Hz), max 1000 |
| 17    | PWMSoftStartEnable | "0"/"1"  | Soft start enabled |
| 18    | PWMSoftStartTime   | number   | Soft start ramp time (ms) |
| 19    | functionInfix[]    | subidx   | 11 subindexes (0-10), all "0" in rawSendData |

### Low-Side (LS) Fields: OP,20-38

Identical structure to HS but offset by +19. Field 20=lowFuse, 31=function[], 38=functionInfix[], etc.

### Subindex Counts

| Field    | Subindexes | Notes |
|----------|-----------|-------|
| OP,12/31 | Variable  | Length depends on function complexity (1 for Always True, 7 for simple, 15 for simple AND/OR, 25 for nested AND+OR) |
| OP,19/38 | 11        | Always indexes 0-10, always "0" in rawSendData |

---

## Input Fields (IP Section)

| Field | Name           | Type     | Notes |
|-------|----------------|----------|-------|
| 1     | mode           | 0/1/2    | 0=Momentary, 1=Latching, 2=Analog |
| 2     | (reserved)     | "0"      | |
| 3     | (mode related) | "0"/"1"  | "1" when mode is Latching or Analog |
| 4     | activeLevel    | "0"/"1"  | 0=Active High, 1=Active Low |
| 5     | (reserved)     | "0"      | |
| 6     | EMA filter     | "100"    | EMA filter percentage |
| 7     | pullResistor   | "0"      | Internal pull resistor config |
| 8     | (reserved)     | "0"      | |
| 9     | (unknown)      | "1"      | Always 1 |
| 10    | label          | string   | Input name/label |

---

## Timer Fields (TI Section)

| Field | Name                    | Notes |
|-------|-------------------------|-------|
| 1     | onTime                  | On period in milliseconds |
| 2     | offTime                 | Off period in milliseconds |
| 3     | enabled                 | "0"/"1" |
| 4     | label                   | Timer name |
| 5     | visibleInDOM            | "0"/"1" — show in configurator UI |
| 6     | type                    | "0"=Pulse Train, "1"=One Shot, etc. |
| 7-11  | startCondition*         | Start condition (Var1, VarOrConst, Var2, Const, Condition) |
| 12-16 | resetCondition*         | Reset condition (same structure) |
| 17    | resetOnEnd              | "0"/"1" |
| 18    | duration                | Duration count |

---

## Generic Function Fields (GF Section)

| Field | Subindexes | Notes |
|-------|-----------|-------|
| 1     | —         | enabled "0"/"1" |
| 2     | —         | label |
| 3     | 100       | function[] — subindexes 0-99, same format as OP,12 |
| 4     | —         | Single value "1" (NOT subindexed!) |

---

## Function Encoding Format

This is the most complex part of the format. Functions define the logic conditions for when outputs activate.

### Always True

```json
function: [7, "1", "1", "2", "10", "1", "1"]
functionInfix: [
  ["1", "1", "2", "10", "1", "1"],
  ["2", "1"],
  [0],
  ["2", "2"],
  [0]
]
```

This encodes the explicit expression **True Status Equals True**, which avoids the configurator warning for empty logic functions.
rawSendData: `OP,12,<idx>,0,"7"`, ..., `OP,12,<idx>,6,"1"`

### Simple Comparison ("Variable Status Equals True")

```json
function: [7, "1", "<varId>", "2", "10", "1", "1"]
functionInfix: [
  ["1", "<varId>", "2", "10", "1", "1"],   // root: comparison node
  ["2", "1"],                                // left: Variable1 ref
  [0],                                       // null leaf
  ["2", "2"],                                // right: Variable2 ref
  [0]                                        // null leaf
]
```

Token breakdown:
| Token | Meaning |
|-------|---------|
| `7`   | Total array length |
| `"1"` | Node type: comparison |
| `"<varId>"` | Configurator variable ID (see Variable ID Map) |
| `"2"` | Property selector: Status |
| `"10"` | Operator: Equals |
| `"1"` | Comparison value: True |
| `"1"` | Value type: Constant |

rawSendData: `OP,12,<idx>,0,"7"`, `OP,12,<idx>,1,"1"`, ..., `OP,12,<idx>,6,"1"`

### Binary Operator (AND / OR)

The function array uses **PREFIX** (pre-order) tree traversal. The operator comes first, then left operand, then right operand.

**Simple AND — "A AND B":**
```json
function: [15,
  "3", "1",                            // AND operator
  "1", "<varA>", "2", "10", "1", "1",  // left operand (leaf)
  "1", "<varB>", "2", "10", "1", "1"   // right operand (leaf) — NO marker at top level
]
```

**Nested — "A AND (B OR C)":**
```json
function: [23,
  "3", "1",                            // AND operator
  "1", "<varA>", "2", "10", "1", "1",  // AND's left operand (leaf)
  "4", "1",                            // OR operator (AND's right = subtree)
  "1", "<varB>", "2", "10", "1", "1",  // OR's left operand (leaf)
  "1", "<varC>", "2", "10", "1", "1"   // OR's right operand (leaf)
]
```

**Operator codes:**
| Code | Operator |
|------|----------|
| `"3"` | AND |
| `"4"` | OR |

`"2","2"` appears in `functionInfix` leaf-reference entries, but based on manual OR test configs it is **not used as a standalone marker inside the prefix `function[]` payload**.

### functionInfix (JSON property only)

The `functionInfix` property stores the same expression as a binary tree in array form. Index `i` has children at `2i+1` and `2i+2`.

For simple comparisons: 5-element array (root + 4 leaves).
For compound expressions: larger tree with operator nodes at branch points.

**Note:** In rawSendData, `OP,19` / `OP,38` (the infix fields) are always 11 zeros regardless of the function. The configurator reconstructs the display from the `function` array in the JSON.

---

## Variable ID Map

The configurator assigns numeric IDs to all variables. These IDs are used in function arrays to reference inputs, outputs, timers, etc.

### Formula

| Variable Type | Base ID | Stride | Range |
|---------------|---------|--------|-------|
| Literal `True` (pseudo-variable) | 1 | — | Used for explicit always-true comparisons |
| HS Outputs    | 34      | 10     | O1=34, O2=44, ..., O25=274 |
| LS Outputs    | 284     | 10     | O1_LS=284, O2_LS=294, ..., O25_LS=524 |
| Inputs        | 562     | 5      | I1=562, I2=567, ..., I16=637 |
| Timers        | 640     | 3      | Timer1=640, Timer2=643, ..., Timer30=727 |
| Generic Funcs | 730     | 3      | GF1=730, GF2=733, ..., GF30=817 |

### General formula

```
varId = base + (index - 1) * stride
```

### How we determined these

| Variable | ID  | Source |
|----------|-----|--------|
| I4       | 577 | Joel manual config: O4 BRAKE = I4 Status |
| I9       | 602 | Joel manual config: O2 WIPER = I9 Status |
| I12      | 617 | Joel manual config: O13 HORN = I12 Status |
| O14 HS   | 164 | Joel manual config: O7 HIBEAM = O14 Status |
| GF1      | 730 | Joel manual config: O3 IGN_COIL = GF1 |
| Timer1   | 640 | Joel manual config: O8 RESERVE = Timer1 |

From these 6 confirmed data points, the base+stride formulas were derived and verified for all 16 inputs, 25 HS outputs, 25 LS outputs, 30 timers, and 30 GFs.

### Verification status

- Inputs (I1-I16): **All 16 verified** by formula, 3 confirmed by manual config
- HS Outputs (O1-O25): Formula verified, O14=164 confirmed manually
- LS Outputs: Formula derived from HS pattern (not independently confirmed)
- Timers: Timer1=640 confirmed, Timer2-30 by formula
- Generic Functions: GF1=730 confirmed, GF2-30 by formula
- Maths Channels, Counters, Sensor Cals: **Not yet mapped** (no test data)

---

## Comparison Operators

Observed in function encoding:

| Code | Operator |
|------|----------|
| `"10"` | Equals |

The manual lists these as available but we haven't encoded them:
AND, OR, NOR, XOR, NAND, >, >=, <, <=, Equal, Not Equal

---

## Property Selectors

| Code | Property |
|------|----------|
| `"2"` | Status (boolean: on/off) |

Other properties likely exist (Voltage, Current, Value) but haven't been mapped.

---

## Known Limitations & Open Questions

1. **Analog comparisons** — "I1 > 1V" threshold comparisons in functions are not yet encoded. Currently stripped and treated as simple status checks. The threshold voltage comparison likely uses a different property selector and operator code.

2. **Maths Channel / Counter / Sensor Cal variable IDs** — Not yet mapped. Would need manual test configs to determine base and stride.

3. **functionInfix for compound expressions** — Pattern is partially verified against manual OR test configs (`A AND (B OR C)`), but more samples are still needed for deeper/mixed nesting cases.

4. **CAN Stream section** — Largest section (~17,700 commands). Currently copied verbatim from template. Not reverse-engineered.

5. **Section boundary bleeding** — In the original template's rawSendData, commands from different sections can appear on the same line (e.g., last MC command and first GF command on one line). Our generator avoids this by repacking all commands cleanly.

---

## Generator Usage

```bash
node generate_hwpdm.js [config.json] [template.hwpdm] [output.hwpdm]
```

Defaults:
- Config: `_arkiv/ELTON_PDM25V2_KOMPLETT_v5.6b/pdm25_outputs_complete.json` (arkiverad 2026-06-16)
- Template: `Elton.HWPDM` (blank/factory config used as skeleton)
- Output: `Elton_generated.HWPDM`

The generator:
1. Reads the human-readable JSON config (outputs, inputs, timers, GFs)
2. Reads the template HWPDM for sections we don't modify (CAN, logging, counters, etc.)
3. Builds all JSON sections with correct data
4. Generates rawSendData with commands in correct section order
5. Packs 4 commands per rawSendData line

Current safety defaults in `generate_hwpdm.js` (only when source fields are missing):
- Output `peak_time_s` → defaults to `5.0s` (5000ms)
- Analog input `threshold_V` → defaults to `1.0V`
- Analog input `hysteresis_V` → defaults to `0.2V` (and is clamped to stay `< threshold`)

---

## File Inventory

| File | Purpose |
|------|---------|
| `generate_hwpdm.js` | Main generator script |
| `pdm25_outputs_complete.json` | Human-readable vehicle config (source of truth) |
| `Elton.HWPDM` | Template file (factory/blank config) |
| `Elton_v7.0.HWPDM` | Latest generated output |
| `Elton joel fix_2.HWPDM` | Joel's manual test config (simple functions verified) |
| `Elton_v7.0.OR.HWPDM` | Joel's manual OR test (compound AND+OR verified) |
| `PDM15_25_35_Instruction_Manual.md` | Official manual (reference) |
| `HWPDM_FORMAT_REVERSE_ENGINEERING.md` | This document |
