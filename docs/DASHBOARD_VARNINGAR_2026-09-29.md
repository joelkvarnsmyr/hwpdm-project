# Dashboard warnings — driving safety

Agreed with Joel 2026-09-29. For the ELTON dashboard agents. The signals come from `PDM_CAN_KONTRAKT_v10.18.md` (v10.18–v10.20) and the Pi's own GPS. **Nothing here needs a PDM change** beyond v10.20.

## 0. Common rules

- **Ignition on** = `0x511` present **and** `Battery_Voltage` > 10 V (contract §1.2). No warning fires with the ignition off.
- **Speed** = GPS (gps-bridge). Use it only with a valid fix. GPS jitters by 1–3 km/h at standstill, so "moving" = **> 5 km/h sustained for 3 s**. If GPS is lost, the moving-warnings fall silent. They must never fire on a lost fix.
- **Engine running**: contract §2.6. Use `Engine_Running` (`0x520` bytes 6–7) once Joel confirms the tachometer. Until then use the ignition-coil current heuristic.
- Log every warning (start, end, max speed) to recorder-bridge. The timestamps are what find intermittent faults.
- Priority when several are active: oil > brake > coolant > handbrake > door > charging.

## 1. Handbrake applied while driving

| Condition | Show | Sound |
|---|---|---|
| moving and `Handbrake_On` = 1 | amber banner "HANDBROMSEN ÄR I" | one chime |
| as above and (> 15 km/h or > 10 s) | red full screen | repeating tone until released |
| released | clear immediately | — |

Source: `0x511` byte 5 (`vehicle/handbrake`, already published). If `HbDoor_Fault` (`0x511` byte 7) = 1, show "Kabelfel handbroms/dörr" instead. A shorted C1 reads as handbrake + door.

## 2. Door open while driving

| Condition | Show | Sound |
|---|---|---|
| moving and `Door_Open` = 1 | red banner "DÖRR ÖPPEN" | chime, repeated every 10 s while it lasts |

Source: `0x511` byte 6. **Not published yet: add it** (`vehicle/door_open`). Only one door switch is wired today, and the PDM cannot tell which door is open, so keep the text generic.

## 3. Coolant too hot

Only when `Coolant_Temp` has been **declared valid by the PDM side**, which it is not yet, because SC1 has not been rebuilt. It is also only active while the engine runs.

| Condition | Show | Sound |
|---|---|---|
| ≥ 105 °C for 5 s | amber "Hög motortemperatur" | one chime |
| ≥ 110 °C | red full screen "MOTORN ÖVERHETTAS – STANNA" | repeating tone |
| back below threshold − 3 °C | clear | — |

The temperature **rises for a few minutes after the engine stops**. That is heat soak around the sender in the head and is normal, so never alarm with the engine stopped: show the value only. A sender in steam, after coolant loss, reads too *low*, which is why a coolant level sensor is planned.

## 4. Brake warning (new in v10.20)

Source: I13 `BRAKE_FAULT`, pin C11, status in `0x517` byte 4. 1 = the original brake warning switch is closed (low fluid or a brake circuit fault). The PDM already applies a 2 s delay against sloshing.

| Condition | Show | Sound |
|---|---|---|
| ignition on and BRAKE_FAULT = 1 | red "BROMSVARNING – kontrollera bromsvätskan" | tone; **3 × repeating if it appears while moving** |

**Never suppress this while driving.** Limitation: the switch is open when all is well, so a broken wire reads "OK". No lamp check is possible. Say so on the settings/diagnostics page.

## 5. Not charging (v10.20)

Source: O2 ALT_EXCITE current, `0x518` bytes 2–3 (mA). O2 feeds the alternator's D+ through 82 Ω, replacing the old charge lamp, so **the O2 current is the charge lamp**: about 150 mA = not charging, about 0 = charging.

| Condition | Show | Sound |
|---|---|---|
| ignition on, engine stopped | charge icon lit (like the old lamp), no warning | no |
| engine running and O2 > 80 mA for 10 s | amber "Generatorn laddar inte" | one chime |
| once the tachometer is confirmed: > 1500 rpm and battery < 12.8 V for 60 s | same warning | one chime |

## 6. Oil pressure

Contract §2.6: state machine, lamp check, and engine-running gating.

## 7. Verify on the van

1. Handbrake applied, drive slowly past 5 km/h: amber, then red.
2. Door open while rolling: red banner with chime.
3. Key on, engine off: charge icon lit, no warning. Start the engine: O2 current drops towards 0 when it charges.
4. Ground C11 with the ignition on: brake warning after about 2 s.
