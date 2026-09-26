# Pi → PDM CAN Control — Developer Handover v1.0

> Pi-sidan kan nu styra PDM-outputs via CAN. Detta dokument beskriver
> kontraktet (DBC), arkitekturen, vad som är gjort, vad som återstår,
> och vad ni kan bygga med det.
>
> **Status:** DBC importerad till PDM. Output-funktioner och Pi-bridge ej byggda.
> **Author:** Joel + Claude (2026-06-05)
> **Filer:** `docs/elton_pi_control_v1.0.dbc` (denna mappen)

---

## TL;DR

- 3 nya CAN-meddelanden definierade (0x500–0x502) för **Pi → PDM-kommandon**
- Pi kan nu styra **14 olika ljus/funktioner** via CAN (alla truckens primära ljus)
- Master enable-bit + heartbeat = inbyggd säkerhet mot rogue commands
- Använder befintlig `can0`-buss på Pi och PDM:s `CAN Bus 1`
- Återstår: modifiera PDM output-funktioner att respektera CAN, bygga Pi-side bridge

---

## Vad detta möjliggör

| Use case | Beskrivning |
|----------|-------------|
| **Tesla-style ljusshow** | Koreografisk blink-sekvens från Pi, ev. synkad mot musik |
| **Dash-knapp tänder ljus** | Touch på driver-dash → MQTT → CAN → PDM → output |
| **Welcome/Goodbye-sekvens** | Vid unlock/power-off triggas mjuk fade in/out |
| **Beat-sync med Spotify** | Pi läser BPM från media-metadata, blinkar i takt |
| **GPS-event-trigger** | "Kommer hem" → kort ljus-greeting |
| **Voice-control** | "Hey Elton, tänd kupén" → STT → action |
| **Pattern-mode** | PDM kör autonomt pattern (Pi sätter mode, sen släpper) |
| **Hazard-shortcut** | Dash-knapp för hazard utan att leta efter fysisk knapp |
| **Diagnostic toggle** | Test alla lampor via mobilapp (utan att starta bilen) |
| **Schemalagda actions** | Cron-jobb på Pi (t.ex. "tänd kupén kl 06:00") |

---

## Arkitektur

```
┌─────────────┐         ┌────────────┐         ┌─────────────┐         ┌──────────┐
│  Driver-    │  MQTT   │   mqtt-    │   CAN   │     PDM     │ output  │ Lampor   │
│  Dash UI    │ ──────► │  to-can    │ ──────► │             │ ──────► │  i bilen │
│  (touch)    │         │  bridge    │  0x500  │ CAN Inputs  │  HS     │          │
└─────────────┘         └────────────┘         │  + Logic    │         └──────────┘
                                               │  + Outputs  │
                                               └─────────────┘
       ▲                                              │
       │                                              │ CAN
       │              MQTT                            ▼
┌─────────────┐    ┌───────────────┐         ┌────────────┐
│  Mosquitto  │ ◄──┤  can-bridge   │ ◄───────┤  PDM CAN   │
│   broker    │    │ (befintlig)   │         │   Stream   │
└─────────────┘    └───────────────┘         └────────────┘
```

**Riktning 1 (befintligt):** PDM sänder status (outputs, inputs, IMU, etc.) via CAN. `can-bridge` decodar och publicerar på MQTT.

**Riktning 2 (NYTT):** Pi sänder kommandon via MQTT → ny `mqtt-to-can` bridge → CAN → PDM:s CAN Inputs → ändrar output-state.

---

## CAN-meddelanden (kontraktet)

### Översikt

| ID | Namn | DLC | Riktning | Frekvens (rekommendation) |
|----|------|-----|----------|---------------------------|
| **0x500** | `Elton_Ctrl_Lights` | 8 bytes | Pi → PDM | 10-50 Hz när enable=1, annars tyst |
| **0x501** | `Elton_Ctrl_PWM` | 8 bytes | Pi → PDM | Som ovan, för dim/fade |
| **0x502** | `Elton_Ctrl_Pattern` | 8 bytes | Pi → PDM | Engångs-set vid pattern-byte |

CAN-bus: **CAN Bus 1** på PDM (= `can0` på Pi), 500 kbit/s, Standard 11-bit IDs.

### 0x500 — Elton_Ctrl_Lights (primary)

**Byte 0 — kontrollbits:**

| Bit | Signal | Funktion |
|-----|--------|----------|
| 0 | `LightShow_Enable` | Master gate. Om 0 ignoreras alla andra kommando-bits |
| 1 | `LightShow_Heartbeat` | Toggla på varje frame. PDM kan övervaka liveness |
| 2 | `Safety_Override` | Bypass speed>0-interlock. Användning: stationär debug |
| 3-7 | (reserverade) | För framtida bruk |

**Byte 1 — framljus & park:**

| Bit | Signal | PDM Output |
|-----|--------|------------|
| 0 | `LowBeam_L_Cmd` | O14 LOWBEAM_L |
| 1 | `LowBeam_R_Cmd` | O15 LOWBEAM_R |
| 2 | `HiBeam_L_Cmd` | O16 HIBEAM_L |
| 3 | `HiBeam_R_Cmd` | O7 HIBEAM_R |
| 4 | `Park_Lights_Cmd` | O4 PARK |
| 5-7 | (reserverade) | |

**Byte 2 — signaler & bak:**

| Bit | Signal | PDM Output |
|-----|--------|------------|
| 0 | `Turn_L_Cmd` | O25 TURN_L |
| 1 | `Turn_R_Cmd` | O24 TURN_R |
| 2 | `Brake_Lights_Cmd` | O6 BRAKE |
| 3 | `Reverse_Lights_Cmd` | O19 REVERSE |
| 4 | `Hazard_Cmd` | Sätter både O24 OCH O25 |
| 5-7 | (reserverade) | |

**Byte 3 — kupé & misc:**

| Bit | Signal | PDM Output |
|-----|--------|------------|
| 0 | `Interior_Cmd` | (Framtida output) |
| 1 | `Horn_Pulse` | O13 HORN |
| 2-7 | (reserverade) | |

**Bytes 4-7:** Reserverade för framtida bruk.

### 0x501 — Elton_Ctrl_PWM (dim levels)

8 bytes, en per output, värde 0-255 (0 = av, 255 = full).

| Byte | Signal | Output |
|------|--------|--------|
| 0 | `LowBeam_L_PWM` | O14 |
| 1 | `LowBeam_R_PWM` | O15 |
| 2 | `HiBeam_L_PWM` | O16 |
| 3 | `HiBeam_R_PWM` | O7 |
| 4 | `Park_Lights_PWM` | O4 |
| 5 | `Brake_Lights_PWM` | O6 |
| 6 | `Turn_L_PWM` | O25 |
| 7 | `Turn_R_PWM` | O24 |

> ⚠️ **PWM kräver att PDM-output är konfigurerad i PWM-mode** (default är digital
> on/off). Detta är inte aktiverat i v9.52 — behöver enabling per output om
> dim-funktioner ska användas.

### 0x502 — Elton_Ctrl_Pattern (autonom mönster-spelning)

För framtida bruk. Tänkt så att Pi kan säga "kör Knight Rider-mönster med
hastighet X, ljusstyrka Y" och PDM hanterar timingen själv (avlastar Pi från
real-time-krav).

| Byte | Signal | Beskrivning |
|------|--------|-------------|
| 0 | `Pattern_ID` | 0=off, 1=KnightRider, 2=AltFlash, 3=Heartbeat, 4=Sweep, etc. (definieras vid implementation) |
| 1 | `Pattern_Speed` | 0-255 → 0=stop, 255=max snabbhet |
| 2 | `Pattern_Brightness` | 0-100 → procent |
| 3 | `Pattern_Phase` | Sync-fas för multi-bil-koordination (framtida) |

---

## Vad är gjort

✅ **DBC-fil skapad och validerad**
   - `docs/elton_pi_control_v1.0.dbc`
   - 27 signaler i 3 meddelanden
   - Validerat med `cantools` (encode/decode roundtrip OK)

✅ **DBC importerad till PDM v9.52**
   - CAN Bus 1
   - Offset 0
   - Alla 3 frames + alla signaler valda

---

## Vad återstår

### På PDM-sidan (en bil-build behövs)

**1. Modifiera output-funktioner att respektera CAN-kommandon**

För varje styrbar output, utöka funktionen med OR-logik:

```
O14 LOWBEAM_L:
  (befintlig funktion) OR (LightShow_Enable AND LowBeam_L_Cmd)

O15 LOWBEAM_R:
  (befintlig funktion) OR (LightShow_Enable AND LowBeam_R_Cmd)

O16 HIBEAM_L:
  (befintlig funktion) OR (LightShow_Enable AND HiBeam_L_Cmd)

O7  HIBEAM_R:
  (befintlig funktion) OR (LightShow_Enable AND HiBeam_R_Cmd)

O4  PARK:
  (befintlig funktion) OR (LightShow_Enable AND Park_Lights_Cmd)

O6  BRAKE:
  (befintlig funktion) OR (LightShow_Enable AND Brake_Lights_Cmd)

O25 TURN_L:
  (befintlig funktion) OR (LightShow_Enable AND (Turn_L_Cmd OR Hazard_Cmd))

O24 TURN_R:
  (befintlig funktion) OR (LightShow_Enable AND (Turn_R_Cmd OR Hazard_Cmd))

O19 REVERSE (om aktiverad):
  (befintlig funktion) OR (LightShow_Enable AND Reverse_Lights_Cmd)

O13 HORN:
  (befintlig funktion) OR (LightShow_Enable AND Horn_Pulse)
```

**Master-gate via `LightShow_Enable`** är kritiskt — det skyddar mot att ett
trasigt eller test-CAN-frame oavsiktligt aktiverar ljus.

**2. (Optional) Lägg till liveness-timeout för CAN-kommandon**

Om Pi crashar mitt i en sekvens kan en output fastna "ON". Mitigering:

```
Timer N: CAN_LIGHTSHOW_TIMEOUT
  Mode: Duration
  Set Time: 0.5 s
  Trigger: LightShow_Heartbeat (på edge)

Generic Function: CAN_LIGHTSHOW_ALIVE
  Function: TimerN = Active

Modifiera ALLA OR-tillägg ovan till:
  ... OR (LightShow_Enable AND CAN_LIGHTSHOW_ALIVE AND <Cmd>)
```

Då släcks alla CAN-styrda outputs automatiskt om Pi tappar heartbeat > 500ms.

### På Pi-sidan (ny tjänst behövs)

**1. `mqtt-to-can` bridge** — ny Python-tjänst som:
- Lyssnar på MQTT-topics under `elton/control/lights/+`
- Bygger CAN-frames med rätt bit-positionering (via `cantools` + DBC)
- Sänder på `can0` med vald frekvens

**2. MQTT-topics att definiera:**

| Topic | Värde | Effekt |
|-------|-------|--------|
| `elton/control/lightshow/enable` | `"on"` / `"off"` | Sätter master gate |
| `elton/control/lightshow/pattern` | JSON eller string | Startar predefinerat mönster |
| `elton/control/lights/lowbeam_l` | `"on"` / `"off"` | Tänd/släck enskild lampa |
| `elton/control/lights/<all_outputs>` | `"on"` / `"off"` | etc. |
| `elton/control/horn` | `"pulse"` | En kort horn-puls |

**3. Pattern-engine** (i Pi eller PDM):
- Beat detection från Spotify metadata via befintlig `media/player/*` MQTT
- Choreografi-state-machine (Knight Rider, Heartbeat, etc.)
- Tidsbas + faser

**4. Driver-dash UI**:
- Toggle för "Light Show Mode" master switch
- Pattern-väljare
- Manual override per output (för testing)

### Update DBC i can-bridge service

`/home/elton/elton/can-bridge/dbc/elton_pdm25_v2.dbc` används av befintlig
RX-bridge. Lägg till `elton_pi_control_v1.0.dbc` antingen som separat fil
eller merge in i huvud-DBC:n så `cantools` kan användas för ENCODE i den
nya bridgen.

---

## Implementation guide — Pi-bridge

### Beroenden

```bash
pip install python-can cantools paho-mqtt
```

### Minimal proof-of-concept

```python
#!/usr/bin/env python3
"""
mqtt-to-can bridge — translates MQTT control topics to CAN frames.
"""
import can
import cantools
import paho.mqtt.client as mqtt
import threading
import time

DBC_PATH = "/home/elton/elton/can-bridge/dbc/elton_pi_control_v1.0.dbc"
CAN_INTERFACE = "can0"
MQTT_HOST = "localhost"

db = cantools.database.load_file(DBC_PATH)
bus = can.interface.Bus(CAN_INTERFACE, bustype="socketcan")
msg_lights = db.get_message_by_name("Elton_Ctrl_Lights")

# Shared state — protected by lock
state_lock = threading.Lock()
state = {
    "LightShow_Enable": 0,
    "LightShow_Heartbeat": 0,
    "Safety_Override": 0,
    "LowBeam_L_Cmd": 0, "LowBeam_R_Cmd": 0,
    "HiBeam_L_Cmd": 0, "HiBeam_R_Cmd": 0,
    "Park_Lights_Cmd": 0,
    "Turn_L_Cmd": 0, "Turn_R_Cmd": 0,
    "Brake_Lights_Cmd": 0, "Reverse_Lights_Cmd": 0,
    "Hazard_Cmd": 0, "Interior_Cmd": 0, "Horn_Pulse": 0,
}

def tx_loop():
    """Send Elton_Ctrl_Lights at 20Hz when enabled."""
    while True:
        with state_lock:
            state["LightShow_Heartbeat"] ^= 1  # toggle
            data = msg_lights.encode(state)
        if state["LightShow_Enable"]:
            bus.send(can.Message(
                arbitration_id=msg_lights.frame_id,
                data=data,
                is_extended_id=False))
        time.sleep(0.05)  # 20Hz

def on_message(client, userdata, msg):
    """Map MQTT topic to state field."""
    topic_map = {
        "elton/control/lightshow/enable": "LightShow_Enable",
        "elton/control/lights/lowbeam_l": "LowBeam_L_Cmd",
        "elton/control/lights/lowbeam_r": "LowBeam_R_Cmd",
        # ... (utöka för alla)
    }
    field = topic_map.get(msg.topic)
    if not field:
        return
    value = 1 if msg.payload.decode().lower() in ("on", "1", "true") else 0
    with state_lock:
        state[field] = value

threading.Thread(target=tx_loop, daemon=True).start()

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_HOST, 1883)
client.subscribe("elton/control/+/+")
client.loop_forever()
```

### Knight Rider example

```python
import time, can, cantools

db = cantools.database.load_file("elton_pi_control_v1.0.dbc")
bus = can.interface.Bus("can0", bustype="socketcan")
msg = db.get_message_by_name("Elton_Ctrl_Lights")

lights = ["Park_Lights_Cmd", "LowBeam_L_Cmd", "HiBeam_L_Cmd", "HiBeam_R_Cmd",
          "LowBeam_R_Cmd", "Brake_Lights_Cmd", "Reverse_Lights_Cmd"]

def send(active_idx, heartbeat):
    payload = {k: 0 for k in db.signals_for_message(msg.name)}
    payload["LightShow_Enable"] = 1
    payload["LightShow_Heartbeat"] = heartbeat
    if 0 <= active_idx < len(lights):
        payload[lights[active_idx]] = 1
    bus.send(can.Message(arbitration_id=msg.frame_id,
                         data=msg.encode(payload),
                         is_extended_id=False))

hb = 0
while True:
    for i in range(len(lights)):
        send(i, hb := hb ^ 1)
        time.sleep(0.08)
    for i in range(len(lights)-1, -1, -1):
        send(i, hb := hb ^ 1)
        time.sleep(0.08)
```

### Beat-sync mot Spotify (skiss)

```python
# Lyssna på media/player/track för BPM-info via librespot
# Beräkna nästa beat i framtiden, schedule frame sends

import librosa  # eller använd Spotify Web API audio-analysis
# beats = librosa.beat.beat_track(...)
# for beat_time in beats:
#   schedule(beat_time, lambda: pulse_all_lights())
```

---

## Säkerhet & policy

### Hård spärr för publik väg

Light show får ALDRIG aktivera på allmän väg. Pi-bridgen ska kolla:

```python
# Innan LightShow_Enable=1 skickas:
vehicle_speed = mqtt_get_retained("vehicle/speed", default=999)
ignition = mqtt_get_retained("vehicle/ignition_state", default="drive")
if vehicle_speed > 0 or ignition != "park":
    log.warning("Light show blocked — vehicle moving")
    return
```

### Skydd mot externa angripare

Just nu öppen MQTT-broker = vem som helst med tillgång kan styra ljus. Acceptabelt
internt (Tailscale-protected), men om bilen exponeras externt → addera ACL eller
auth token.

### Failsafe vid Pi-crash

Två lager:

1. **Heartbeat-timeout i PDM** (se "Vad återstår" → liveness-timeout). Stänger ner
   CAN-output efter 500ms utan heartbeat.
2. **Stale-state detection i Pi**: om mqtt-to-can-bridgen får ingen kommando på
   >5 sek, sätt alla `*_Cmd=0`.

### Brandskydd för Horn

`Horn_Pulse` är frestande för "fun" men är extremt störande. Lägg in en
rate-limiter i Pi-bridgen: max 1 pulse per 30 sek, max 5 pulser per timme.

### Bromsljus & blinkers

Dessa är **säkerhetskritiska**. CAN-kontroll OK för ljusshow när bilen står still,
men aldrig under körning. PDM:s funktioner ska prioritera fysiska inputs över
CAN. Dubbelkolla att OR-logiken (befintlig OR CAN) inte kan **förhindra** en
fysisk trigger.

---

## Troubleshooting

### Inga CAN-frames når PDM

```bash
# Verifiera att Pi sänder
cansend can0 500#0101000000000000
candump can0,500:7FF -t a   # ska visa frames

# Verifiera att PDM tar emot (om Hardwire's mjukvara har diagnostik-vy)
# Annars: monitor PDM-output via befintlig can-bridge — om Pi-frame triggar
# en output förändring så ser man det i mqtt under pdm/front/output/+/status
```

### PDM signal heter inte vad jag förväntar

Vid DBC-import kan PDM:s mjukvara döpa om signaler (t.ex. lowercase). Verifiera
i PDM:s "CAN Input Signals" lista att signalnamnen som används i output-funktionerna
matchar.

### Heartbeat blinkar inte

Om PDM:s liveness-timer aldrig firar trots att Pi sänder — kolla att
`LightShow_Heartbeat` faktiskt växlar varje frame, inte är konstant. Vissa
Pi-bridges glömmer toggle om man bara skickar samma encoded payload upprepat.

### Frames sänds men outputs ändras inte

Felsök i denna ordning:
1. PDM CAN Input filter aktiverat? (Filter 1 enabled på sidan vi visade)
2. CAN Input Signal `LightShow_Enable` läses som 1? (PDM-diagnostik om finns)
3. Output-funktionen modifierad med OR-tillägget?
4. Output enabled i builden?

---

## Referenser

- **DBC-fil:** `docs/elton_pi_control_v1.0.dbc`
- **Befintlig PDM-DBC:** `docs/hardwire_pdm25_v2.dbc` (för RX-strömmen från PDM)
- **PDM build där DBC importerades:** `Builds/Elton_v9.52_naming_fixes.HWPDM`
   (eller efterföljande build med output-funktion-modifieringar)
- **CAN-bus inspect runbook:** se `inspect-can-stream.md`
- **can-bridge service-config:** `/home/elton/elton/can-bridge/`

---

## Versionshistorik

| Version | Datum | Ändring |
|---------|-------|---------|
| v1.0 | 2026-06-05 | Initial DBC + dokumentation. 0x500-0x502 reserverat. |

Framtida versioner reserveras under samma ID-range (0x500-0x50F) med extra
meddelanden vid behov. Större brytande ändringar = v2.0 med ny ID-range
(t.ex. 0x520-0x52F).
