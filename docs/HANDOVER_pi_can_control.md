# HANDOVER — Pi → PDM CAN Control

**Status:** ✅ End-to-end verifierat. Pi styr PDM-outputs via CAN. Light show körd live på bilen.
**Datum:** 2026-06-06
**Pi-branch som ska byggas på:** `feat/mqtt-to-can`

---

## TL;DR — vad finns på plats

| Lager | Status | Plats |
|------|--------|-------|
| CAN-protokoll (DBC) | ✅ Klar + validerat | `docs/elton_pi_control_v1.0.dbc` |
| PDM-build med CAN-logik | ✅ Flashad + testad | `Builds/Elton_v9.53_all_outputs.HWPDM` |
| Build-script (reproducerbar) | ✅ | `build_v9.53.py` |
| CAN-bus + Pi-stack | ✅ Verifierat alive | `can0` på Pi, can-bridge service kör |
| End-to-end tester | ✅ Alla pass | Knight Rider sveptes live |
| **`mqtt-to-can` bridge** | 🟡 **Pi-expert tar vid här** | Branch `feat/mqtt-to-can` |
| Dash UI-toggles | 🟡 Senare | - |

---

## CAN-protokoll — kontraktet

CAN-bus: **Standard 11-bit IDs**, **500 kbit/s**, **CAN Bus 1** på PDM (= `can0` på Pi).  
Reserverat ID-range: **0x500–0x50F** (Pi → PDM kommandon).

### 0x500 — `Elton_Ctrl_Lights` (primary)

Pi sänder med **20–50Hz** när show-mode är aktivt. Frames glesare än 1000ms → CANInput timeout → fallback till fysiska brytare (inbyggd safety!).

**Byte 0 — kontroll:**

| Bit | Signal | Beskrivning |
|----|--------|-------------|
| 0 | `LightShow_Enable` | Master gate. 0=normal mode, 1=show mode |
| 1 | `LightShow_Heartbeat` | Toggla varje frame |
| 2 | `Safety_Override` | Bypass speed-interlock (för stationär debug) |

**Byte 1 — framljus & park:**

| Bit | Signal | PDM Output |
|----|--------|------------|
| 0 | `LowBeam_L_Cmd` | O14 |
| 1 | `LowBeam_R_Cmd` | O15 |
| 2 | `HiBeam_L_Cmd` | O16 |
| 3 | `HiBeam_R_Cmd` | O7 |
| 4 | `Park_Lights_Cmd` | O4 |

**Byte 2 — bak & signaler:**

| Bit | Signal | PDM Output |
|----|--------|------------|
| 0 | `Turn_L_Cmd` | O25 |
| 1 | `Turn_R_Cmd` | O24 |
| 2 | `Brake_Lights_Cmd` | O6 |
| 3 | `Reverse_Lights_Cmd` | O19 |
| 4 | `Hazard_Cmd` | sätter både O24 + O25 |

**Byte 3 — kupé & misc:**

| Bit | Signal | PDM Output |
|----|--------|------------|
| 0 | `Interior_Cmd` | (framtida) |
| 1 | `Horn_Pulse` | O13 (försiktigt!) |

### 0x501 — `Elton_Ctrl_PWM` (8 bytes, 0-255 per kanal)

Ett byte per output (LowBeam_L, LowBeam_R, HiBeam_L, HiBeam_R, Park, Brake, Turn_L, Turn_R).  
**Kräver PWM-mode aktiverat på outputs** (default: digital on/off).

### 0x502 — `Elton_Ctrl_Pattern` (autonom mode)

Pi sätter mönster + hastighet + ljusstyrka, PDM kör tidsbasen själv. För framtida bruk.

---

## PDM output-logik (vad varje output gör)

| Output | Mönster | Logik |
|--------|---------|-------|
| **O1 BUSBAR** | Lämnad | Alltid på (infrastruktur) |
| **O2 ALT_EXCITE** | Lämnad | GF1 PWR_ALIVE |
| **O3 IGN_COIL** | Lämnad | GF1 PWR_ALIVE |
| **O4 PARK** | Cat A suppress | `(LSE=F AND PWR=T) OR (LSE=T AND Park_Cmd=T)` |
| **O5 FUEL** | Cat A suppress + override | `(LSE=F AND PWR=T) OR (Safety_Override=T AND PWR=T)` |
| **O6 BRAKE** | Cat B additive | `I4=T OR (LSE=T AND Brake_Cmd=T)` |
| **O7 HIBEAM_R** | Cat B | `I2=T OR (LSE=T AND HiBeam_R_Cmd=T)` |
| **O13 HORN** | Cat B | `(I12=T AND Timer_NotActive) OR (LSE=T AND Horn_Pulse=T)` |
| **O14 LOWBEAM_L** | Cat A suppress | `(LSE=F AND I2=F) OR (LSE=T AND LowBeam_L_Cmd=T)` |
| **O15 LOWBEAM_R** | Cat A suppress | `(LSE=F AND I2=F) OR (LSE=T AND LowBeam_R_Cmd=T)` |
| **O16 HIBEAM_L** | Cat B | `I2=T OR (LSE=T AND HiBeam_L_Cmd=T)` |
| **O19 REVERSE** | Cat B | `(I7=T AND Timer_NotActive) OR (LSE=T AND Reverse_Cmd=T)` |
| **O24 TURN_R** | Cat B + Hazard | `(T1 AND I6) OR (T1 AND I3) OR (LSE AND Turn_R_Cmd) OR (LSE AND Hazard_Cmd)` |
| **O25 TURN_L** | Cat B + Hazard | `(T1 AND I5) OR (T1 AND I3) OR (LSE AND Turn_L_Cmd) OR (LSE AND Hazard_Cmd)` |
| **O23 STARTER** | Lämnad | Original |

**Cat A "suppress" = i show-mode SLÄCKS auto-outputs** (DRL, PARK, fuel pump) — bara CAN-kommandon tänder dem.  
**Cat B "additive" = original fysisk-brytare-logik fungerar ALLTID + CAN ovanpå.**

---

## Test-resultat (live på bilen)

| Test | Frame skickat | Resultat |
|------|---------------|----------|
| Baseline (ingen CAN) | inget | PARK auto-på, övriga av ✓ |
| Show-mode suppress | `500#01 00 00 00 00 00 00 00` | PARK släcktes, allt övrigt off ✓ |
| Individuell tändning | `500#01 08 00 00 ...` | Bara HIBEAM_R tändes ✓ |
| Park override | `500#01 10 00 ...` | PARK tändes via CAN ✓ |
| Hazard via CAN | `500#01 00 10 ...` | TURN_R + TURN_L solid på ✓ |
| Fallback (LSE→0) | `500#00 ...` | Allt återgick till normalt ✓ |
| Knight Rider sweep | Loop med 0x01/0x04/0x08/0x02 | Fysiskt svep L→R→L bekräftat live ✓ |
| Strömdragning | mätt via MQTT | ~4.4A per H4-lampa ✓ |
| Trip-protection | Peak Fuse 30A | Inga overcurrent-trips ✓ |
| Auto-shutoff | sluta sända | Lampor släcks <1s (CANInput timeout) ✓ |

---

## CANInput timeout = inbyggd safety net

CANInput `timeoutTime = 1000ms`. Om Pi/can-bridge slutar sända frames > 1s, går alla CANInput-värden till `variableDefault = 0`. Då:
- `LightShow_Enable` → 0 → suppress-logik avstängd → outputs tillbaka i normalt läge
- Alla `*_Cmd` → 0 → ingen CAN-styrd output kvarstår

**Konsekvens:** Pi-crashar mitt i show = alla lampor släcks inom 1 sek. Bygg INTE separat heartbeat-watchdog — den finns gratis.

---

## Filer + var de ligger

```
C:\Users\joel\Documents\Elton LT Wire diagrams\
├── hwpdm-project\
│   ├── docs\
│   │   ├── elton_pi_control_v1.0.dbc          ← DBC-kontraktet (importerad i PDM)
│   │   ├── pi_can_control_v1.0.md             ← Tidigare design-doc
│   │   ├── HANDOVER_pi_can_control.md         ← DETTA DOKUMENT
│   │   └── hardwire_pdm25_v2.dbc              ← Befintlig RX DBC (PDM→Pi)
│   ├── Builds\
│   │   ├── Elton_v9.53_all_outputs.HWPDM      ← FLASHAD nuvarande
│   │   ├── Elton_v9.52_o7_test.HWPDM          ← rollback-safe
│   │   └── Elton_v9.52_postcan.HWPDM          ← pre-modifikation
│   └── build_v9.53.py                          ← reproducerbar build-script
```

På Pi:n (för referens):
```
/home/elton/elton/can-bridge/dbc/elton_pi_control_v1.0.dbc   ← scp:ad dit
/home/elton/elton/can-bridge/venv/                            ← har cantools + python-can
/tmp/test_v953.sh                                              ← test-skript
/tmp/knight_rider.py                                           ← demo-skript
```

---

## Vad Pi-experten ska bygga på `feat/mqtt-to-can`

### 1. `mqtt-to-can` bridge (ny tjänst)

**Lyssna på MQTT-topics → encode med cantools + DBC → sänd på can0**

```python
# Skeleton — utöka från knight_rider.py-loopen
import can, cantools, paho.mqtt.client as mqtt, threading, time

db = cantools.database.load_file("/home/elton/elton/can-bridge/dbc/elton_pi_control_v1.0.dbc")
bus = can.interface.Bus("can0", interface="socketcan")
msg_lights = db.get_message_by_name("Elton_Ctrl_Lights")

state = {sig.name: 0 for sig in msg_lights.signals}
lock = threading.Lock()

def tx_loop():
    while True:
        with lock:
            state["LightShow_Heartbeat"] ^= 1
            data = msg_lights.encode(state)
        if state["LightShow_Enable"]:
            bus.send(can.Message(arbitration_id=msg_lights.frame_id,
                                  data=data, is_extended_id=False))
        time.sleep(0.05)  # 20Hz

def on_message(client, ud, msg):
    topic_map = {
        "elton/control/lightshow/enable": "LightShow_Enable",
        "elton/control/lights/lowbeam_l": "LowBeam_L_Cmd",
        # ... (utöka för alla)
    }
    field = topic_map.get(msg.topic)
    if not field: return
    with lock:
        state[field] = 1 if msg.payload.decode().lower() in ("on","1","true") else 0

threading.Thread(target=tx_loop, daemon=True).start()
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("elton/control/+/+")
client.loop_forever()
```

### 2. Säkerhetsspärrar (NICE TO HAVE men starkt rekommenderat)

```python
# Innan LightShow_Enable=1 skickas ut på CAN
def safety_check():
    speed = mqtt_get_retained("vehicle/speed", default=999)
    ignition = mqtt_get_retained("vehicle/ignition_state", default="drive")
    if speed > 0 or ignition != "park":
        log.warning("Light show blocked: vehicle moving")
        return False
    return True
```

### 3. Pattern-engine (för konserverade shows)

- Knight Rider sweep (skeleton finns i `/tmp/knight_rider.py`)
- Police mode (försiktigt — laglighet)
- Welcome/Goodbye sequences
- Beat-sync mot Spotify (`media/player/*` MQTT-topics finns redan)

### 4. Dash-UI toggles

- **"Light Show Mode" master toggle** (publicerar till `elton/control/lightshow/enable`)
- **Pattern-väljare** (dropdown med predefined shows)
- **Per-output manual override** (för diagnostik)

### 5. systemd service

```ini
[Unit]
Description=MQTT to CAN bridge for Elton light show
After=network.target mosquitto.service can0-up.service

[Service]
Type=simple
User=elton
ExecStart=/home/elton/elton/can-bridge/venv/bin/python3 /home/elton/elton/mqtt-to-can/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## CAN-format encyclopedia (om bridgen behöver buggfixas)

### PDM CANInput variable ID layout
```
CI_n Value = 850 + (n-1) * 5

CI1  LightShow_Enable        = 850
CI2  LightShow_Heartbeat     = 855
CI3  Safety_Override         = 860
CI4  LowBeam_L_Cmd           = 865
CI5  LowBeam_R_Cmd           = 870
CI6  HiBeam_L_Cmd            = 875
CI7  HiBeam_R_Cmd            = 880
CI8  Park_Lights_Cmd         = 885
CI9  Turn_L_Cmd              = 890
CI10 Turn_R_Cmd              = 895
CI11 Brake_Lights_Cmd        = 900
CI12 Reverse_Lights_Cmd      = 905
CI13 Hazard_Cmd              = 910
CI14 Interior_Cmd            = 915
CI15 Horn_Pulse              = 920
```

### PDM function binary format (för debugging av builds)
```
function = [header, ...operands]
header = operand_count + 1

Condition (Input/Timer/GF):  [1, varID, 2, 10, 1, value]
Condition (CANInput):        [1, varID, 2, 10, 1, value]
                                              ^ 10=Equals (matchar Input/Timer/GF)
                                              ^ AVOID condCode=1 (= AND, X AND False = False alltid)

value: 1 = compare-to-True, 2 = compare-to-False

Operator AND: [2, 1]
Operator OR:  [2, 2]

Precedens: AND > OR (standard boolean)
```

---

## Snabbtest-recept för Pi-experten

```bash
# 1. Verifiera CAN-buss
ssh elton@elton.taila1abdb.ts.net
ip link show can0    # ska visa UP
candump can0 | head  # ska visa PDM:s eget stream

# 2. Skicka manuellt frame
cansend can0 500#0108000000000000   # tänd HIBEAM_R i 1 sek

# 3. Övervaka effekt
docker exec elton-mosquitto mosquitto_sub -h localhost -t 'pdm/front/output/7/+' -v

# 4. Knight Rider demo (sluta-på-allt-genom):
/home/elton/elton/can-bridge/venv/bin/python3 /tmp/knight_rider.py
```

---

## Kända gotchas

1. **CANInput timeout = 1000ms** — frames glesare än det = lampor släcks. Bygg tx_loop på 20-50Hz.
2. **PWM-mode kräver per-output config** — default = digital on/off. För fade-effekter måste outputs sättas i PWM-mode i PDM GUI.
3. **O14/O15 LOWBEAM enabled=True** krävs (vi enablade dem live). Peak Fuse = 30A för H4 inrush.
4. **Bromsljus är säkerhetskritiskt** — om PDM styrs av CAN, fysisk pedalbrytare bör vara kvar. Vi har behållit Input 4 BRAKE i O6-logiken.
5. **Horn-bit kan trolla** — rate-limita i bridgen (max 1 puls/30s).
6. **Vehicle speed gate saknas än** — bridgen bör vägra LightShow_Enable=1 om bilen rör sig.

---

## Versionshistorik

| Version | Datum | Vad |
|---------|-------|-----|
| v1.0 | 2026-06-06 | Initial — DBC + PDM v9.53 + Knight Rider live ✓ |
