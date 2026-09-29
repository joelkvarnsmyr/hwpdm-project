# PDM ↔ Pi CAN contract — PDM build v10.8

**Date:** 2026-09-29
**Audience:** agents working in `C:\Projects\Code\elton_dash\ELTON-Dashboard-Project` (can-bridge, mqtt-to-can, companion, driver-dash)
**PDM:** Hardwire PDM25 V2, firmware / configurator **1.3.1**, build `Builds/Elton_v10.8_etapp1.HWPDM`
**Machine-readable:** `docs/elton_pdm_telemetry_v10.8.dbc` (this repo) — new PDM→Pi frames

This document is the source of truth for what the PDM sends and accepts after v10.8. Several things changed that affect the dashboard. Read §1 first.

---

## 1. What changed — action required

| # | Change | What the dashboard must do |
|---|---|---|
| 1 | **Two new PDM→Pi frames, 0x510 and 0x511**, carrying calibrated values | Decode them (§2). Stop re-deriving coolant/fuel from raw input millivolts |
| 2 | **`LightShow_Enable` no longer touches the fuel pump** | Nothing breaks — but remove any code/assumption that the show mode stops the engine. It used to (see §5.1) |
| 3 | **Lamp-out detection moved to the Pi** | The PDM no longer trips multi-bulb outputs on low current. Implement detection from per-output current (§4) |
| 4 | **Load shedding during cranking** | Low/high beams and the blower switch **off while the starter is engaged**. Do not report this as a fault (§5.2) |
| 5 | **Blower is CAN-only on 0x503** | Two of the four signals in the blower spec are used. No knob fallback exists (§3) |
| 6 | **Handbrake input now exists** | `Handbrake_On` on 0x511 (§2.2) |
| 7 | **Second horn is a compressor air horn** | `Horn_Pulse` blows **both** horns including the air horn (§5.4) |

---

## 2. PDM → Pi

All frames: CAN bus 1, **11-bit standard IDs**, periodic **5 Hz**. Multi-byte values are **big-endian (Motorola)** — the configurator's non-LE formats; its own DBC export places them with the Motorola start-bit convention. The PDM packs `wire = value × multiplier`.

### 2.1 `0x510 PDM_Sensors` — 8 bytes

| Bytes | Signal | Type | Scale | Unit | Source |
|---|---|---|---|---|---|
| 0–3 | `Coolant_Temp` | **int32 signed** | 0.001 | °C | Sensor Calibration 1 (var 781) |
| 4–7 | `Fuel_Level` | int32 | 0.001 | L | Sensor Calibration 2 (var 782) |

- **`Coolant_Temp` is INVALID in v10.8.** SC1 still reads the wrong input (I11 WIPER_PARK). Fixed in v10.9 once the sender has been measured. Show "--" until then.
- Treat as **signed** — sub-zero coolant readings are normal in a Swedish winter.
- **`Fuel_Level` curve is provisional.** It assumes a 10–180 Ω sender and an 80 L tank. It will be recalibrated against two real fills; expect the value to shift then. Current reading ~2.0 V at the input ≈ 37.6 L.

### 2.2 `0x511 PDM_Status` — 6 bytes

| Bytes | Signal | Type | Scale | Unit | Source |
|---|---|---|---|---|---|
| 0–1 | `Battery_Voltage` | uint16 | 0.001 | V | var 6 (sent ×1000 = mV) |
| 2 | `IMU_Impact` | uint8 | 1 | 0/1 | var 82, latching |
| 3 | `IMU_Rollover` | uint8 | 1 | 0/1 | var 83, latching |
| 4 | `Oil_Pressure_Low` | uint8 | 1 | 0/1 | I14 status, pin C12 |
| 5 | `Handbrake_On` | uint8 | 1 | 0/1 | I16 status, pin C1 |

- **`IMU_*` are informational only.** The PDM takes no action on them — there is **no crash cutoff**. The IMU reference frame has not been zeroed, so treat values with suspicion until it is.
- **`Oil_Pressure_Low` = 1 with the engine off is correct** (no pressure → switch closed). Warn only when the engine is running. The PDM also computes `GF3 OIL_OK` with a 5 s start-grace window (§5.3); it is not on the bus yet — if you want it, ask and it goes into 0x511.
- **`Handbrake_On`**: the F9 → C1 cable may not be fitted yet. A constant 0 does not mean the input is broken.

### 2.3 Existing preformatted stream (unchanged)

Base ID `0x1000`, one frame per variable block, still enabled. Per-output current / status / trip data continue to come from here. **Input 8 raw voltage (frame 42)** is still sent but is now superseded by `Fuel_Level` on 0x510.

⚠ Firmware 1.3.1 **shifted all PDM variable IDs by +21** (for IDs ≥ 70) versus 1.2.x. If anything on the Pi decodes the stream by *variable number* rather than by frame position, re-check it against `can-bridge/dbc/elton_pdm25_v2.dbc` — that file predates 1.3.1.

---

## 3. Pi → PDM

### 3.1 `0x500–0x502` — lights, PWM, patterns (unchanged)

As in `elton_pi_control_v1.1.dbc`. CAN input timeout **1000 ms**, default 0 → local control resumes.

**Not imported into the PDM:** `Horn_1_Pulse` and `Horn_2_Pulse` (DBC v1.1 bits 26–27). Sending them has no effect. See §5.4.

### 3.2 `0x503 Elton_Ctrl_Climate` — blower

Implements `docs/superpowers/specs/2026-09-25-blower-can-control-design.md` **with one simplification: there is no physical knob**, so the handover-to-knob machinery is not wired.

| Byte | Bits | Signal | PDM uses it? | Timeout default |
|---|---|---|---|---|
| 0 | bit 0 | `Blower_Cmd` | **yes** — CAN input 28 `BLW_CMD` | **0** |
| 0 | bit 1 | `Blower_Pi_Active` | no — ignored | — |
| 1 | 0–7 | `Blower_Duty` 0–100 % | **yes** — CAN input 29 `BLW_DUTY` | **0** |
| 2 | 0–7 | `Climate_Alive` | no | — |

Output 11 logic:

```
O11 BLOWER = PWR_ALIVE AND NOT CRASH_TMR AND LOAD_OK AND BLW_CMD
PWM 200 Hz, duty = BLW_DUTY, linear 1:1 map [0,10,…,100]
```

Consequences:

- **Frame stale > 1 s → blower stops.** The spec's `BLW_DUTY` default of 100 existed to hand over to the knob; there is no knob, so the default is 0. Accepted by Joel.
- **"Lämna till vredet" is being removed** (Joel, 2026-09-29) — there is no physical knob. The CAN input holds its last value for the whole timeout window, so the timeout decides how long a dropout the blower rides out; the next build raises it from 1000 ms.
- `Blower_Cmd=1` is already sent only when Pi_Active=1 and duty>0, so no bridge change is needed for correct behaviour.
- The blower is switched **off during cranking** regardless of the command (`LOAD_OK`, §5.2). `notRunning`/`noCurrent` verdicts must ignore that window.

---

## 4. Lamp-out detection — now the Pi's job

The PDM's *low fuse* **trips** an output when current falls below a threshold. That is backwards for a lamp: a warning is wanted, not a dead circuit. From v10.8 the low fuse is **0 (disabled)** on outputs driving more than one bulb:

| Output | Load | Low fuse |
|---|---|---|
| O6 BRAKE | M9 + M10 | 0 — **Pi detects** |
| O19 REVERSE | M16 + M17 | 0 — **Pi detects** |
| O24 TURN_R | front + rear | 0 — **Pi detects** |
| O25 TURN_L | front + rear | 0 — **Pi detects** |
| O14/O15 low beam, O7/O16 high beam | one bulb each | kept (1 A) — PDM trips, trip status tells which side |

Suggested Pi logic, per output, from the stream's per-output current:

- Only evaluate while the output **status is on** and **not cranking** (I15 START inactive).
- Learn the healthy current once (or configure it). Warn when current drops below ~60 % of healthy for > 2 s — that is one bulb of two gone.
- Turn signals: evaluate on the **on-phase** of the 400/400 ms blink only.
- Turn signals are **LED** — currents are small; use relative, not absolute, thresholds.

---

## 5. Behavioural facts the dashboard should know

### 5.1 The engine stop is gone

Before v10.3 the fuel pump was `(NOT LightShow_Enable AND PWR_ALIVE) OR (Safety_Override AND PWR_ALIVE)`. Booting the Pi asserted `LightShow_Enable` and **the engine died**. Now:

```
O5 FUEL = PWR_ALIVE
```

No CAN signal can stop the engine. If a show interlock is wanted, implement it on the Pi (**refuse to start a show while the engine runs**) — never as a PDM output condition.

### 5.2 Load shedding during cranking

`GF9 LOAD_OK = START input inactive`. It gates **O14/O15 low beam, O7/O16 high beam, O11 blower** in every branch, including the CAN branches. While the starter turns, those outputs are off even if the Pi commands them on. **Never** gated: brake lights, turn/hazard, ignition coil, fuel pump, starter.

### 5.3 Oil pressure start grace

`GF3 OIL_OK = (oil switch open) OR (Timer3 START_GRACE > 0)`. Timer3 starts on the START input and runs 5 s. Use the same grace on the Pi if you warn on `Oil_Pressure_Low`, or ask for `OIL_OK` to be added to 0x511.

### 5.4 Horns

| Output | Device | Button | CAN |
|---|---|---|---|
| O13 HORN | electric horn | sounds immediately | `LightShow_Enable AND Horn_Pulse` |
| O17 HORN_2 | **compressor air horn** | only after the button is **held > 500 ms** (Timer5) | `LightShow_Enable AND Horn_Pulse` |

`Horn_Pulse` blows **both**, including the air horn. For melody-style light shows that is probably not wanted. Separate control needs `Horn_1_Pulse`/`Horn_2_Pulse` imported into the PDM — ask if required. The D1 cable to the air horn may not be fitted yet.

### 5.5 Onboard logging

LoggingGroup 3 `FAULT_HUNT` records battery voltage, `LightShow_Enable`, START, oil switch, SC1, SC2 to the PDM's flash continuously. If the dashboard sees an unexplained event, note the timestamp — the log can be pulled with the configurator afterwards.

---

## 6. I/O snapshot (v10.8)

| Pin | Channel | Function | Notes |
|---|---|---|---|
| A7 | I1 | WASHER | moved from A3 on 2026-09-29 |
| A3 | I8 | FUEL_LEVEL (analog) | 150 Ω pull-up from 5V REF |
| A2 | I10 | COOLANT_TEMP (analog) | not calibrated yet (v10.9) |
| C12 | I14 | OIL.PRESS | verified in the van |
| C1 | I16 | HANDBRAKE | active-low; cable may be missing |
| B8 | O11 | BLOWER | CAN-only, §3.2 |
| B9 | O12 | WASHER | driven by I1 |
| D1 | O17 | HORN_2 | compressor horn, hold > 500 ms |
| C5 | O2 | ALT_EXCITE | **disabled** until the 82 Ω resistor is fitted |

---

## 7. Verify before trusting

These were designed from the configurator source, not captured on the wire:

1. `candump can0,510:7FF,511:7FF` — frames present at ~5 Hz, lengths 8 and 6.
2. `Battery_Voltage` ≈ multimeter reading at the battery (expect ~12.6 V engine off, ~13.3 V running).
3. Byte order: `Fuel_Level` should decode to ~37.6 L at the current fill. A number in the millions means the byte order is wrong.
4. Cold engine in winter: `Coolant_Temp` negative, not ~4.29 × 10⁶ (after v10.9).
5. Best cross-check: in the configurator, **CAN Outputs → export DBC**, and diff it against `elton_pdm_telemetry_v10.8.dbc`.

Report mismatches back to the PDM side rather than working around them in the bridge.
