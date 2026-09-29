# PDM ↔ Pi CAN contract — PDM build v10.18–v10.20

Supersedes `PDM_CAN_KONTRAKT_v10.8.md`. Written 2026-09-29 after a live session on the van: every frame below was captured on `can0` unless marked otherwise.

- DBC for 0x510, 0x511, 0x51F, 0x520: `elton_pdm_telemetry_v10.19.dbc` (this folder; v10.18 DBC kept for history).
- DBC for 0x512–0x51E: the dashboard's own `can-bridge/dbc/elton_pdm_perchannel_v10.11.dbc` (PR #148), verified against the van. It is unchanged.

## 0. Builds since v10.8

| Build | Flashed | Change that matters to the Pi |
|---|---|---|
| v10.9 | yes | `0x503` CAN input timeout 1 s → **10 s** |
| v10.10 | yes | Fuel curve x-axis in volts, **64 L** tank. `Fuel_Level` became plausible. |
| v10.11 | yes | **Per-channel data moved to CAN outputs 0x512–0x51E.** Configurator 1.3.1 zeroes the stream's per-channel frames. |
| v10.13 | yes | Headlight fuses (peak 35 A, soft start 500 ms). New **`0x51F PDM_InVolt`**. |
| v10.14 | yes | Ignition coil and fuel pump retry after 0.1 s, unlimited retries. New **`0x520 PDM_EngineDiag`**. |
| v10.15 | yes | **Blower from the app works.** The PDM's CAN acceptance filter excluded `0x503`, so `BLW_CMD` was 0 since v10.4. |
| v10.16 | yes | Air horn threshold fixed: 500 ms. It was 50 ms, because logic constants are stored ×10. |
| v10.17 | yes | Handbrake and doors share C1. **`0x511` is now 8 bytes** (`Door_Open`, `HbDoor_Fault`). |
| v10.18 | yes | Handbrake/door thresholds tuned to measured voltages. Signals and meaning are unchanged. |
| v10.19 | built — contained in v10.20 | Tachometer on I7 (A10). **`0x520` bytes 4–7 become `Engine_RPM` and `Engine_Running`** (were an unsupported, always-0 voltage). O19 reverse lights no longer follow I7. |
| v10.20 | **built, not yet flashed** | **O2 ALT_EXCITE on**: its current (`0x518` bytes 2–3) is the charge lamp, about 150 mA = not charging. **I13 BRAKE_FAULT on** (C11, `0x517` byte 4, 2 s delay). O19 REVERSE → RESERVE19, off (no reverse lights fitted). O14 now follows `LowBeam_L_Cmd`, not `LowBeam_R_Cmd`. |

---

## 1. PDM → Pi

| ID | Name | Rate | Layout (all big-endian) |
|---|---|---|---|
| `0x510` | PDM_Sensors | 5 Hz | int32 `Coolant_Temp` ×0.001 °C · int32 `Fuel_Level` ×0.001 L |
| `0x511` | PDM_Status | 5 Hz | u16 battery mV · u8 impact · u8 rollover · u8 oil low · u8 **handbrake** · u8 **door open** · u8 **hb/door fault** |
| `0x512–0x515` | PDM_OutStatus_1..4 | 10 Hz | u8 status per output, O1–O8, O9–O16, O17–O24, O25 |
| `0x516–0x517` | PDM_InStatus_1..2 | 10 Hz | u8 status per input, I1–I8, I9–I16 |
| `0x518–0x51E` | PDM_OutCurrent_1..7 | 5 Hz | u16 mA per output, 4 per frame (O1–O4 … O25) |
| `0x51F` | PDM_InVolt | 10 Hz | u16 mV: I1 washer · I8 fuel · I10 coolant · I16 handbrake/door |
| `0x520` | PDM_EngineDiag | 20 Hz | u16 O3 trip count · u16 O5 trip count · u16 **Engine_RPM** · u16 **Engine_Running** (v10.19; before that always 0) |
| `0x1000–0x1032` | stream | — | Only `0x1000–0x1002` carry data. **Ignore the per-channel frames**, they are all zeros. |

Useful offsets: blower O11 status is `0x513` byte 2, blower current is `0x51A` bytes 4–5, ignition coil O3 current is `0x518` bytes 4–5, **charge lamp O2 current is `0x518` bytes 2–3 (v10.20)**, **brake warning I13 is `0x517` byte 4 (v10.20)**.

### 1.1 Output status is an enum

From the configurator (`configOutputs.js` → `setOutputStatusIndicator`):

| Value | Meaning |
|---|---|
| 0 | Off |
| 1 | On |
| 2 | Tripped: over-current |
| 3 | Tripped: under-current (lamp out / open circuit, where a low fuse is set) |
| 4 | Tripped: under-voltage |
| 5 | Tripped: over-temperature |

The variable is `onStatus + faultStatus`, but a tripped output is always off, so the sum is never ambiguous. Publish the fault type, not just "fault".

### 1.2 Power state — do not use CAN presence alone

When Joel's laptop is connected by USB, **the PDM keeps transmitting with the key off**. Then `Battery_Voltage` falls towards 0 V and decays, every commanded output reports **4**, and floating analog inputs produce nonsense such as 58 L of fuel.

- **Ignition on = 0x511 present AND `Battery_Voltage` > 10 V.** Below 10 V, suppress lamp faults, fuel, coolant and handbrake/door warnings.
- **Engine running = `Oil_Pressure_Low` == 0.** Battery voltage is not a reliable signal: the alternator does not charge at idle (12.0–12.4 V) and only sometimes reaches 13.3 V.

---

## 2. Signals — current state and rules

### 2.1 Handbrake and doors (C1, from v10.17)

One input with three resistors, decoded from its voltage. The door switches are in parallel, so the PDM cannot tell which door is open.

| State | Measured on C1 | `Handbrake_On` | `Door_Open` |
|---|---|---|---|
| All closed, handbrake off | 4.53 V | 0 | 0 |
| Door open | 3.07 V | 0 | 1 |
| Handbrake on | 2.44 V | 1 | 0 |
| Both | 1.93 V | 1 | 1 |
| Wire to ground | < 1.0 V | — | — (`HbDoor_Fault` = 1) |

- `Handbrake_On` keeps its byte (5) and its meaning, so no mapping change is needed.
- Show `HbDoor_Fault` as a wiring fault, not as the handbrake being on.
- A broken wire reads as "all closed". This cannot be detected.

### 2.2 Engine diagnostics (0x520)

On 2026-09-29 the ignition coil output (O3) tripped on **under-voltage** twice, at 18:00:36 and 18:16:24. The engine died each time. The fuel pump, the supply and the ignition signal were all normal. The cause is not found yet; it is on the coil's circuit, either a short to ground or HT leakage.

Since v10.14 the PDM retries after 0.1 s, so the engine will probably survive. **Every retry increments `IgnCoil_TripCount`.** Show a warning with a timestamp whenever it increases. The timestamps are what will locate the fault (bumps, rpm, blower on …). There have been no trips since 18:34.

### 2.3 Blower (from v10.15)

`0x503` now reaches the PDM, and O11 switches on (status 1). **But it draws only 0.08–0.13 A at 100 % duty**, so the motor is not running. The fault is in the wiring between the PDM and the motor (old switch or resistor pack, a fuse, or the pin) and is being investigated. O11 has no low fuse, so it will not report status 3. Until that is fixed, a `notRunning` verdict based on current is correct.

### 2.4 Lamps

- **Headlights (O7, O14, O15, O16)** have a 1 A low fuse. **Status 3 is the PDM's own lamp-out detection.** The current state is real: right side (O7, O15) = 3, left side (O14, O16) = 2. Joel is leaving it for now.
- Brake, reverse and turn signals have no low fuse, so current-based detection stays on the Pi as before. The park-light threshold of 0.2 A (PR #149) is correct.

### 2.5 Values that are not usable yet

| Signal | Status | Rule |
|---|---|---|
| `Coolant_Temp` (0x510) | **Invalid.** SC1 still reads the wrong input with an mV x-axis. | Keep hidden. |
| `Coolant_In_V` (0x51F) | Raw only. 1.18 V at ~17 °C cold, 0.31 V after ~30 min idle. Shifts about −0.09 V while the alternator charges. | Do not convert to °C on the Pi. The PDM curve will be rebuilt. |
| `Fuel_Level` | Provisional curve, near empty (14–19 L). | Discard when the battery is below 10 V, and average over ≥ 10 s. |
| I1 washer / O12 | I1 floats at 1.7–1.9 V and reads 1 (pressed) at rest, so O12 is on. | Ignore I1 and O12 until fixed. |
| `Engine_RPM`, `Engine_Running` (v10.19) | 0 until Joel confirms the tach wiring and the threshold is calibrated at idle. | Hide rpm until then. |

### 2.6 Oil pressure warning — agreed with Joel 2026-09-29

The switch only answers "pressure or no pressure". It cannot tell "engine stopped" from "engine running without oil", so the alarm must be gated on independent proof that the engine runs.

**Engine running** (do not use oil pressure or battery voltage):
- O3 IGN_COIL current (`0x518` bytes 4–5) **varies** while the points open and close: spread (max − min) over 2 s > 0.3 A and mean between 1.0 and 3.4 A. Stopped = flat, around 0.6 A (points open) or 3.6–4.2 A (points closed). Seen clearly in the 2026-09-29 logs.
- GPS speed > 5 km/h always means running.
- **From v10.19, once the tach is confirmed:** `Engine_Running` (`0x520` bytes 6–7, rpm > 300) replaces the current heuristic. `Engine_RPM` is ignition coil terminal 1 pulses × 30.

| State | Condition | Show | Sound |
|---|---|---|---|
| Key on, engine stopped | `Oil_Pressure_Low` = 1 | red icon, like the original lamp | no |
| **Lamp check failed** | key on, engine stopped, oil reads OK (0) for > 3 s | amber: "Oljetrycksgivaren svarar inte" (a broken wire reads "OK" forever) | one beep |
| Cranking | I15 START (`0x517` byte 6) and 5 s after | icon may be lit | no |
| Armed | engine running and oil OK for 3 s | icon off | — |
| Idle flicker | low < 2 s while running and stationary | amber notice after 3 flickers in 60 s | no |
| **ALARM** | armed, low ≥ 2 s, **engine still running** | red full screen: "LÅGT OLJETRYCK – STÄNG AV MOTORN" | repeating tone until pressure returns or acknowledged |
| Stall | armed, low, but engine no longer running | "Motorn stannade" — not an oil alarm | one beep |

Validate the running detector against `/tmp/pdm_stall.log` and `/tmp/pdm_runlog.log` on the Pi (2026-09-29): O3 current and oil state at 0.1 s resolution, including three stalls.

### 2.7 Unchanged behaviour (from v10.8, still true)

- **Load shedding while cranking:** START active switches off O7, O14, O15, O16 and O11, whatever the Pi commands.
- **The Pi cannot stop the engine:** O3 and O5 are always on with ignition.
- **Horns:** O13 sounds immediately. The O17 air horn needs the button held **> 500 ms** (actually true since v10.16). `Horn_Pulse` blows both.
- Pi → PDM `0x500–0x502`: 1 s timeout. `0x503`: 10 s timeout, default 0.

---

Driving-safety warnings (handbrake/door while moving, coolant, brake, charging): `DASHBOARD_VARNINGAR_2026-09-29.md`.

## 3. Verify on the van

1. `candump can0,511:7FF` gives DLC **8**. With the handbrake on and a door open, bytes 5 and 6 are both `01`.
2. `candump can0,51F:7FF` bytes 6–7 ≈ `0x11B2` (4.53 V) with everything closed.
3. `candump can0,520:7FF` gives trip counts `00 00 00 00` after a clean run.
4. App → blower on: `0x513` byte 2 = `01`.
