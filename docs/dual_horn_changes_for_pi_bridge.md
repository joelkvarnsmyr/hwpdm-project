# Dual Horn Support — Pi-bridge ändringar

**Version:** v9.56 (PDM) + DBC v1.1
**Datum:** 2026-06-09

## Översikt

Bilen har nu **två fysiska tutor** anslutna till PDM:
- **O13 HORN_1** — primär tuta (befintlig kabel)
- **O17 HORN_2** — sekundär tuta (ny kabel från PDM C-kontakten)

Båda aktiveras parallellt av den fysiska horn-knappen via `GF8 HORN_MASTER`. Pi kan styra dem separat eller tillsammans via tre CAN-signaler.

## Tre CAN-signaler för flexibel styrning

| Signal | Bit i 0x500 | Effekt | Användning |
|--------|-------------|--------|------------|
| `Horn_Pulse` | byte 3 bit 1 | Båda tutorna samtidigt | Bakåtkompatibel — befintlig `elton/control/horn` MQTT-topic |
| `Horn_1_Pulse` | byte 3 bit 2 | Bara tuta 1 | Sekventiella mönster (melodi, knight rider för horn) |
| `Horn_2_Pulse` | byte 3 bit 3 | Bara tuta 2 | Samma — ger Pi full kontroll över sekvenser |

## Output-logik på PDM-sidan

```
GF8 HORN_MASTER = I12 (HORN button) = True AND Timer2 (CRASH_TMR) = False

O13 HORN_1 ON if:
  GF8 = True                                          (fysisk knapp, ej crash)
  OR (LightShow_Enable AND Horn_Pulse = True)         (Pi blåser båda)
  OR (LightShow_Enable AND Horn_1_Pulse = True)       (Pi blåser bara tuta 1)

O17 HORN_2 ON if:
  GF8 = True                                          (samma knapp triggar båda)
  OR (LightShow_Enable AND Horn_Pulse = True)         (Pi blåser båda)
  OR (LightShow_Enable AND Horn_2_Pulse = True)       (Pi blåser bara tuta 2)
```

**Viktigt:** Crash-detection-säkerheten i originalfunktionen är **bevarad i GF8** — om CRASH_TMR är aktiv blåser inte tutorna även vid fysisk knapp-tryck.

## Bridge-ändringar — `mqtt-to-can`

### 1. `state.py` — lägg till nya cmd-namn

```python
# Update ALL_CMD_NAMES — 14 signaler nu (var 12)
ALL_CMD_NAMES: tuple[str, ...] = (
    "LowBeam_L_Cmd", "LowBeam_R_Cmd",
    "HiBeam_L_Cmd", "HiBeam_R_Cmd",
    "Park_Lights_Cmd",
    "Turn_L_Cmd", "Turn_R_Cmd",
    "Brake_Lights_Cmd", "Reverse_Lights_Cmd",
    "Hazard_Cmd", "Interior_Cmd",
    "Horn_Pulse",        # befintligt — båda tutorna
    "Horn_1_Pulse",      # NEW — bara tuta 1
    "Horn_2_Pulse",      # NEW — bara tuta 2
)
```

### 2. `mqtt_handlers.py` — utöka horn-mappningen

```python
# Befintligt _handle_horn() blir fortfarande "blåser båda" via Horn_Pulse.
# Lägg till nya topic-handlers för individuell kontroll:

_HORN_INDIVIDUAL: dict[str, str] = {
    "elton/control/horn_1": "Horn_1_Pulse",
    "elton/control/horn_2": "Horn_2_Pulse",
}

def _handle_horn_individual(self, topic: str, text: str) -> None:
    """Pulse one specific horn (token-bucket rate limited per-horn)."""
    if text not in ("pulse", "1", "on"):
        return
    cmd_name = _HORN_INDIVIDUAL.get(topic)
    if cmd_name is None:
        return
    # Rate-limit per horn separately
    if not self.horn_limiter.try_consume(key=cmd_name):
        return
    with self.state.lock:
        self.state.cmds[cmd_name] = 1
    # Auto-clear after pulse duration (same as existing _handle_horn)
    def _clear():
        with self.state.lock:
            self.state.cmds[cmd_name] = 0
        self._publish_aggregate()
    timer = threading.Timer(HORN_PULSE_DURATION_S, _clear)
    timer.daemon = True
    timer.start()
```

### 3. Lägg till topic-subscriptions i `main.py`

```python
SUBSCRIBE_TOPICS = (
    ...
    ("elton/control/horn", 0),         # befintligt — båda tutorna
    ("elton/control/horn_1", 0),       # NEW
    ("elton/control/horn_2", 0),       # NEW
    ...
)
```

### 4. `horn_limiter.py` — utöka för per-horn tokens

```python
class HornLimiter:
    """Token bucket; nu med separata tokens per signal-key."""

    def __init__(self, now_fn=time.monotonic):
        self._now = now_fn
        self._buckets: dict[str, float] = {}   # key -> token count
        self._last_refill: dict[str, float] = {}

    def _refill(self, key: str) -> None:
        now = self._now()
        last = self._last_refill.get(key, now)
        elapsed = now - last
        if elapsed <= 0:
            return
        added = elapsed / REFILL_INTERVAL_S
        current = self._buckets.get(key, float(CAPACITY))
        self._buckets[key] = min(float(CAPACITY), current + added)
        self._last_refill[key] = now

    def try_consume(self, key: str = "default") -> bool:
        self._refill(key)
        if self._buckets.get(key, float(CAPACITY)) >= 1.0:
            self._buckets[key] = self._buckets.get(key, float(CAPACITY)) - 1.0
            log.info("horn pulse consumed (key=%s, tokens=%.2f)", key, self._buckets[key])
            return True
        log.info("horn pulse denied (key=%s, tokens=%.2f)", key, self._buckets.get(key, 0))
        return False
```

Nu har varje tuta egen rate-limit. 5 tut per 5 min PER tuta, total max 30 tut/timme.

### 5. Nya pattern — `patterns/horn_melody.py`

```python
"""Horn melody patterns. Use sequential single-horn pulses to create
recognizable tunes from the two-tone horn setup."""
import threading
from ..state import ControlState

PULSE_S = 0.15
GAP_S = 0.08


def _pulse_horn(state: ControlState, horn_num: int, duration_s: float) -> None:
    cmd = f"Horn_{horn_num}_Pulse"
    with state.lock:
        state.cmds[cmd] = 1
    time.sleep(duration_s)
    with state.lock:
        state.cmds[cmd] = 0


def double_tap(state, cancel_event):
    """Quick 'bik-bik' attention signal — both horns twice."""
    for _ in range(2):
        with state.lock:
            state.cmds["Horn_Pulse"] = 1
        if cancel_event.wait(0.12):
            return
        with state.lock:
            state.cmds["Horn_Pulse"] = 0
        if cancel_event.wait(0.1):
            return


def alternating(state, cancel_event, count=4):
    """Tuta 1 -> tuta 2 -> tuta 1 ... — Knight Rider-style horn."""
    for i in range(count * 2):
        horn = (i % 2) + 1
        cmd = f"Horn_{horn}_Pulse"
        with state.lock:
            state.cmds[cmd] = 1
        if cancel_event.wait(PULSE_S):
            return
        with state.lock:
            state.cmds[cmd] = 0
        if cancel_event.wait(GAP_S):
            return


def la_cucaracha(state, cancel_event):
    """Mexican classic — 'tut-tut-tut, taa-taa'."""
    sequence = [
        (1, 0.15), ("gap", 0.05),
        (1, 0.15), ("gap", 0.05),
        (1, 0.15), ("gap", 0.05),
        (2, 0.30), ("gap", 0.1),
        (2, 0.30),
    ]
    for action, duration in sequence:
        if action == "gap":
            if cancel_event.wait(duration):
                return
            continue
        cmd = f"Horn_{action}_Pulse"
        with state.lock:
            state.cmds[cmd] = 1
        if cancel_event.wait(duration):
            with state.lock:
                state.cmds[cmd] = 0
            return
        with state.lock:
            state.cmds[cmd] = 0
```

### 6. Registrera nya patterns i `main.py`

```python
runner = PatternRunner(state, registry={
    "knight_rider": knight_rider_run,
    "hazard_wave": hazard_wave_run,
    "police": police_run,
    "heartbeat": heartbeat_run,
    "welcome_cascade": welcome_cascade_run,
    "beat_sync": beat_sync_bound,
    # NEW horn patterns:
    "horn_double_tap": double_tap,
    "horn_alternating": alternating,
    "horn_la_cucaracha": la_cucaracha,
})
```

## Test-frames (för manuell verifiering med cansend)

```bash
# Båda tutorna (befintligt)
cansend can0 500#0100000002000000   # byte 3 bit 1 = Horn_Pulse

# Bara tuta 1
cansend can0 500#0100000004000000   # byte 3 bit 2 = Horn_1_Pulse

# Bara tuta 2
cansend can0 500#0100000008000000   # byte 3 bit 3 = Horn_2_Pulse

# Alla tre samtidigt (Horn_Pulse + Horn_1 + Horn_2)
cansend can0 500#010000000E000000   # byte 3 bits 1,2,3 = 0x0E
```

## MQTT-topics översikt

| Topic | Payload | Effekt | Rate-limit |
|-------|---------|--------|------------|
| `elton/control/horn` | `pulse` | Båda tutorna (befintligt) | 5/5min totalt |
| `elton/control/horn_1` | `pulse` | Bara tuta 1 | 5/5min per tuta |
| `elton/control/horn_2` | `pulse` | Bara tuta 2 | 5/5min per tuta |
| `elton/control/lightshow/pattern` | `horn_double_tap` | Snabb dubbeltut | (pattern egen takt) |
| `elton/control/lightshow/pattern` | `horn_alternating` | Knight Rider horn | (pattern egen takt) |
| `elton/control/lightshow/pattern` | `horn_la_cucaracha` | Mexikansk melodi | (pattern egen takt) |

## Workflow för deployment

### På Joels sida (PDM-build):
1. ✅ DBC v1.1 finns: `docs/elton_pi_control_v1.1.dbc`
2. ✅ Build finns: `Builds/Elton_v9.56_dual_horn.HWPDM`
3. Öppna v9.56 i PDM-mjukvaran
4. Import DBC v1.1 med **Overwrite UNCHECKED**
5. Verifiera att O13 HORN_1 + O17 HORN_2 visar rätt CAN-input-namn
6. Save + flasha
7. Dra fysisk kabel från PDM O17-pin till tuta 2

### På Pi-experten:
1. Pull DBC v1.1 till `/home/elton/elton/can-bridge/dbc/elton_pi_control_v1.1.dbc`
2. Uppdatera `mqtt-to-can/state.py` med nya cmd-namn (steg 1 ovan)
3. Uppdatera `mqtt-to-can/mqtt_handlers.py` med individuella horn-topics (steg 2-3)
4. Uppdatera `mqtt-to-can/horn_limiter.py` med per-key buckets (steg 4)
5. Lägg till `mqtt-to-can/patterns/horn_melody.py` (steg 5)
6. Registrera nya patterns (steg 6)
7. Add tests i `tests/test_horn_melody.py` (analog till befintliga pattern-tests)
8. `./deploy.sh mqtt-to-can` → systemctl restart

### Verifiera live:
```bash
ssh elton@elton.taila1abdb.ts.net
mosquitto_pub -h localhost -t elton/control/lightshow/enable -m on
sleep 1
mosquitto_pub -h localhost -t elton/control/horn_1 -m pulse    # bara tuta 1
sleep 1
mosquitto_pub -h localhost -t elton/control/horn_2 -m pulse    # bara tuta 2
sleep 1
mosquitto_pub -h localhost -t elton/control/lightshow/pattern -m horn_la_cucaracha
```
