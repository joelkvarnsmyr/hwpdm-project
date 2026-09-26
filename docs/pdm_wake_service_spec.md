# PDM Wake Service — Specification för Pi-experten

**Datum:** 2026-06-09
**Status:** Planning / hardware ankommer
**Branch-förslag:** `feat/pdm-wake-controller`

## Översikt

Tillåt Pi:n att **väcka och söva PDM** via GPIO → 5V relämodul → high-side wake-signal till PDM PWR-input.

Detta möjliggör:
- 🚪 **Welcome-sequences** vid bilen-unlock (även om tändning är AV)
- 🌅 **Schemalagda shows** via cron (morgon-startup, kvälls-show)
- 📱 **Diagnostik via mobilapp** utan att starta motor
- 🔋 **Smart battery-aware** drift som inte tömmer batteriet
- 🌐 **Remote SSH-access** via Tailscale → wake PDM → läs sensorer → svar → sleep

---

## Arkitektur — separat service, INTE i mqtt-to-can

**Rekommendation:** Bygg som **fristående service** `pdm-power-controller`.

**Varför separat:**
1. **Reliability** — kan väcka PDM även om mqtt-to-can crashar (felsökning!)
2. **Single Responsibility** — service har ett mål, lättare att underhålla
3. **Säkerhet** — egen safety-logik utan beroenden på MQTT-topic-handling
4. **Boot-order** — kan starta före mqtt-to-can (PDM måste vara på FÖRE bridge)

---

## Hårdvaran (för referens)

```
Battery +12V ┬─[Säkring 5A]── kl.15 ────[D1: 1N5822]──┐
             │                                          │
             ├─[Säkring 2A]── Hazard ─────[D2: 1N5822]──┤
             │                                          │
             ├─[Säkring 2A]──[ Relä COM ]               │
             │                  │ (när Pi GPIO HIGH)    │
             │                  ▼                       │
             │              [ Relä NO ]──[D3: 1N5822]──→ PDM PWR
             │                                          │
             │                                          │
             ⏚                                          │
                                                        ▼
                                              (PDM vaknar)

Pi:
  GPIO (t.ex. GPIO4 / pin 7) ─→ Relä-modul IN
  5V (pin 2)                  ─→ Relä-modul VCC
  GND (pin 6)                 ─→ Relä-modul GND
```

**Polaritet på relä-modulen:** De flesta är **active-low** (GPIO HIGH = relä OFF, LOW = ON). Verifiera i koden — annars invertera logiken. Säkrare default: pull-down på GPIO + boot-time delay.

---

## Service-struktur

```
pdm-power-controller/
├── pdm_power/
│   ├── __init__.py
│   ├── main.py                  # entrypoint + DI
│   ├── gpio_relay.py            # GPIO abstraction (lgpio eller RPi.GPIO)
│   ├── mqtt_handler.py          # MQTT topic dispatch
│   ├── power_state.py           # current state (on/off + watchdog timers)
│   ├── battery_monitor.py       # läser MQTT, blockerar wake vid låg V
│   ├── activity_monitor.py      # auto-sleep efter inaktivitet
│   └── safety.py                # pure safety-gate
├── tests/
│   └── test_*.py                # analog till mqtt-to-can
├── pdm-power-controller.service # systemd
├── install.sh
├── requirements.txt
└── README.md
```

---

## MQTT-kontrakt

### Publish to (Pi → service):

| Topic | Payload | Effekt |
|-------|---------|--------|
| `elton/control/pdm/wake` | `on` / `off` | Tvinga PDM på/av |
| `elton/control/pdm/wake_for` | `<seconds>` (t.ex. `300`) | Wake i N sekunder, sen auto-sleep |
| `elton/control/pdm/keepalive` | (anything) | Återställ inaktivitets-timern |
| `elton/control/pdm/policy` | `auto` / `always_on` / `manual` | Drift-läge |

### Subscribe to (service läser):

| Topic | Användning |
|-------|------------|
| `vehicle/battery_voltage` | Blockera wake vid <11.8V |
| `vehicle/ignition_state` | "drive"/"on" = inhibera service (PDM redan på) |
| `pdm/front/device/uptime_s` | Detektera om PDM faktiskt är på |
| `pdm/front/output/+/status` | Activity monitor — om något ändras = aktivitet |

### Publish from (service → MQTT):

| Topic | Payload | Frekvens |
|-------|---------|----------|
| `elton/pdm_power/state` (retained) | JSON `{wake: bool, reason: str, ts: float}` | Vid state-change |
| `elton/pdm_power/health` | JSON `{battery_v: float, can_alive: bool, ...}` | 30s heartbeat |
| `elton/pdm_power/auto_sleep` | `imminent` / `cancelled` | Vid auto-sleep-warning |

---

## Drift-policys

### Policy `auto` (default — rekommenderat)
- Wake när ANY av:
  - Ignition state = "on"/"drive" (auto via hardvara via D1)
  - Hazard på (auto via hardvara via D2)
  - MQTT-kommando `wake/on`
  - Annan inkommande aktivitet via MQTT
- Sleep efter 30 min utan CAN-aktivitet **OCH** ingen wake-source aktiv
- Inhibera sleep om battery <11.8V (vill inte att kunden hittar stillastående bil)

### Policy `always_on`
- Relä alltid HIGH (utvecklingsläge)
- Auto-sleep avstängt
- Användning: aktivt utvecklingsarbete

### Policy `manual`
- Service ignorerar alla auto-triggers
- Endast explicit `wake/on` eller `wake/off` MQTT-kommando
- Användning: felsökning, tester

---

## Safety-features (kritiska)

### 1. **Boot-time delay**

```python
# main.py vid uppstart
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)  # explicit OFF
log.info("Boot — releasing wake (PDM kontroll om finns)")
time.sleep(15)  # vänta 15s för Pi-boot-glitch-skydd
log.info("Service redo, accepterar wake-commands")
```

Pi-GPIO kan **glitcha** under boot — relä klickar. 15s buffer eliminerar det.

### 2. **Battery cut-off**

```python
def can_wake(battery_v, dev_override):
    if dev_override:
        return True, None
    if battery_v < BATTERY_LOW_THRESHOLD_V:
        return False, f"battery too low ({battery_v:.2f}V)"
    if battery_v < BATTERY_WARN_THRESHOLD_V:
        log.warning("battery low (%.2fV), allowing wake but starting watchdog", battery_v)
    return True, None

BATTERY_LOW_THRESHOLD_V = 11.5
BATTERY_WARN_THRESHOLD_V = 11.8
```

### 3. **Watchdog inaktivitets-timer**

```python
class ActivityWatchdog:
    """Auto-sleep efter N sek utan signal från PDM-output topics."""
    def __init__(self, timeout_s: float = 1800.0):
        self.timeout_s = timeout_s
        self.last_activity_ts = time.monotonic()
    
    def on_can_activity(self):
        self.last_activity_ts = time.monotonic()
    
    def should_sleep(self) -> bool:
        return (time.monotonic() - self.last_activity_ts) > self.timeout_s
```

Default timeout 30 min — vid längre tystnad triggas auto-sleep.

### 4. **Sleep-warning + grace period**

```python
def trigger_auto_sleep(self):
    # Publicera varning först
    mqtt.publish("elton/pdm_power/auto_sleep", "imminent")
    log.info("Auto-sleep i 60s om inget pingar")
    time.sleep(60)  # grace period
    
    if not self.has_been_pinged_since():
        log.info("Auto-sleep — släcker relä")
        gpio.set_low(RELAY_PIN)
        mqtt.publish("elton/pdm_power/state", '{"wake":false,"reason":"auto_sleep"}', retain=True)
    else:
        mqtt.publish("elton/pdm_power/auto_sleep", "cancelled")
```

Andra services kan **publish** till `elton/control/pdm/keepalive` för att stoppa auto-sleep.

### 5. **Liveness verification**

```python
def verify_pdm_alive(self) -> bool:
    """Returnerar True om PDM aktivt sänder CAN."""
    last_uptime_msg = mqtt_get_retained("pdm/front/device/uptime_s")
    if last_uptime_msg is None:
        return False
    age_s = time.monotonic() - last_uptime_msg.received_ts
    return age_s < 5.0
```

Använd för att rapportera "wake utan respons" → larm.

---

## Kodskelett — main.py

```python
"""pdm-power-controller entrypoint."""
import os
import signal
import logging
import threading
import time

import paho.mqtt.client as mqtt
import lgpio  # alternativt RPi.GPIO

from .gpio_relay import GpioRelay
from .mqtt_handler import MqttHandler
from .power_state import PowerState
from .battery_monitor import BatteryMonitor
from .activity_monitor import ActivityWatchdog
from .safety import can_wake


SUBSCRIBE = (
    ("elton/control/pdm/+", 0),
    ("vehicle/battery_voltage", 0),
    ("vehicle/ignition_state", 0),
    ("pdm/front/device/uptime_s", 0),
    ("pdm/front/output/+/status", 0),
)


def main():
    log = logging.getLogger("pdm-power")
    relay_pin = int(os.getenv("RELAY_GPIO", "4"))
    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    
    log.info("Booting — relay GPIO=%d, MQTT=%s", relay_pin, mqtt_host)
    
    relay = GpioRelay(pin=relay_pin)
    relay.off()  # explicit off
    time.sleep(15)  # boot grace
    
    state = PowerState()
    battery = BatteryMonitor()
    activity = ActivityWatchdog(timeout_s=1800.0)
    
    client = mqtt.Client(client_id="pdm-power-controller")
    handler = MqttHandler(state, relay, battery, activity, client)
    
    client.on_connect = lambda c, *a: [c.subscribe(t, q) for t, q in SUBSCRIBE]
    client.on_message = lambda c, ud, msg: handler.handle(msg.topic, msg.payload)
    client.connect(mqtt_host, 1883, keepalive=30)
    client.loop_start()
    
    # Periodic health + activity check
    def periodic():
        while True:
            time.sleep(10)
            client.publish("elton/pdm_power/health", state.health_json(), qos=0)
            if state.wake and activity.should_sleep():
                handler.trigger_auto_sleep()
    
    threading.Thread(target=periodic, daemon=True).start()
    
    # Graceful shutdown
    def shutdown(*_):
        log.info("Shutdown — explicit relay off")
        relay.off()
        client.loop_stop()
        client.disconnect()
        relay.cleanup()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    
    signal.pause()  # block forever


if __name__ == "__main__":
    main()
```

---

## Kodskelett — gpio_relay.py

```python
"""GPIO relay abstraction. Supports both lgpio and RPi.GPIO."""
import logging

try:
    import lgpio
    USE_LGPIO = True
except ImportError:
    import RPi.GPIO as GPIO
    USE_LGPIO = False

log = logging.getLogger("pdm-power.gpio")


class GpioRelay:
    """Relay control with active-low awareness (configurable)."""
    
    def __init__(self, pin: int, active_low: bool = True):
        self.pin = pin
        self.active_low = active_low
        if USE_LGPIO:
            self._h = lgpio.gpiochip_open(0)
            lgpio.gpio_claim_output(self._h, pin)
        else:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    def on(self):
        """Aktivera relä (PDM får +12V)."""
        gpio_value = 0 if self.active_low else 1
        self._write(gpio_value)
        log.info("Relay ON (PDM wake) — GPIO%d=%d", self.pin, gpio_value)
    
    def off(self):
        """Släck relä (PDM tappar wake-feed)."""
        gpio_value = 1 if self.active_low else 0
        self._write(gpio_value)
        log.info("Relay OFF (PDM sleep) — GPIO%d=%d", self.pin, gpio_value)
    
    def _write(self, value: int):
        if USE_LGPIO:
            lgpio.gpio_write(self._h, self.pin, value)
        else:
            GPIO.output(self.pin, value)
    
    def cleanup(self):
        if USE_LGPIO:
            lgpio.gpiochip_close(self._h)
        else:
            GPIO.cleanup(self.pin)
```

---

## Tester — analog till mqtt-to-can-mönster

```python
# tests/test_power_state.py
def test_wake_blocks_on_low_battery():
    state = PowerState()
    battery = BatteryMonitor()
    battery.voltage = 11.3  # under threshold
    
    ok, reason = can_wake(battery.voltage, dev_override=False)
    assert not ok
    assert "battery" in reason

def test_dev_override_bypasses_battery_check():
    ok, reason = can_wake(10.0, dev_override=True)
    assert ok
    assert reason is None

# tests/test_activity_watchdog.py
def test_activity_resets_timer(monkeypatch):
    times = [0.0, 100.0, 200.0, 2000.0]
    monkeypatch.setattr(time, "monotonic", lambda: times.pop(0))
    
    w = ActivityWatchdog(timeout_s=1000.0)
    assert not w.should_sleep()  # t=100, within timeout
    w.on_can_activity()           # reset at t=200
    assert not w.should_sleep()   # t=2000, 1800s sedan reset → just under
```

---

## systemd-unit

```ini
# /etc/systemd/system/pdm-power-controller.service
[Unit]
Description=Pi -> PDM power controller (wake/sleep relay)
After=network.target mosquitto.service
Wants=mosquitto.service
Before=mqtt-to-can.service       # mqtt-to-can behöver PDM på

[Service]
Type=simple
User=root  # GPIO access
WorkingDirectory=/home/elton/elton/pdm-power-controller
EnvironmentFile=-/home/elton/elton/pdm-power-controller/.env
ExecStart=/home/elton/elton/pdm-power-controller/venv/bin/python -m pdm_power.main
ExecStop=/home/elton/elton/pdm-power-controller/venv/bin/python -c "from pdm_power.gpio_relay import GpioRelay; GpioRelay(int(__import__('os').getenv('RELAY_GPIO','4'))).off()"
Restart=always
RestartSec=10
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
```

`ExecStop` säkerställer att reläet alltid släcks vid service-stop, även vid krasch.

---

## Testprocedur efter deploy

```bash
# 1. Verifiera GPIO-pin
gpiomon -t 5 0 4   # Lyssna 5s, byt 4 mot din valda GPIO

# 2. Manuell test
mosquitto_pub -h localhost -t elton/control/pdm/wake -m on
# → Förväntat: hör klick från relä, PDM-LED tänds inom 1-2s

# 3. Verifiera PDM faktiskt vaknat
docker exec elton-mosquitto mosquitto_sub -h localhost \
  -t 'pdm/front/device/uptime_s' -C 1 -W 5
# → Förväntat: ett numeriskt värde inom 5s

# 4. Auto-sleep test (kortsekvens)
mosquitto_pub -h localhost -t elton/control/pdm/wake_for -m 10
# → Förväntat: PDM på i 10s, sen sleep-warning, sen sleep

# 5. Battery cut-off test
mosquitto_pub -h localhost -t vehicle/battery_voltage -m 11.0
mosquitto_pub -h localhost -t elton/control/pdm/wake -m on
# → Förväntat: log warning, reläet förblir OFF, MQTT state visar reason="battery too low"
```

---

## Integration med befintlig mqtt-to-can

Inga ändringar **krävs** i mqtt-to-can. Men för bättre UX:

### 1. mqtt-to-can läser PDM-power state
```python
# i mqtt-to-can: lyssna på elton/pdm_power/state
# om wake=false → varna user att deras kommando inte når PDM
# om wake=true men can_alive=false → varna om hardvarufel
```

### 2. Auto-keepalive när light show körs
```python
# i mqtt-to-can pattern runner: publicera keepalive var 30s
# till elton/control/pdm/keepalive
# så att aktiv pattern aldrig auto-sleeper PDM:n
```

### 3. Dash UI knapp för "PDM Wake"
```javascript
// dashboard: lägg till toggle som publicerar
mqtt.publish('elton/control/pdm/wake', isOn ? 'on' : 'off');
```

---

## Cron-exempel för schemalagda shows

```cron
# /etc/cron.d/elton-pdm-schedule
# Wake PDM 30 min innan soluppgång för välkomst-show
0 6 * * * elton mosquitto_pub -h localhost -t elton/control/pdm/wake_for -m 1800

# Kvällshow vid solnedgång (förenklat — använd sunwait för riktigt avancerat)
0 21 * * * elton bash -c '\
  mosquitto_pub -h localhost -t elton/control/pdm/wake -m on && \
  sleep 5 && \
  mosquitto_pub -h localhost -t elton/control/lightshow/enable -m on && \
  mosquitto_pub -h localhost -t elton/control/lightshow/pattern -m welcome_cascade'

# Nattlig auto-sleep om allt är tyst
0 23 * * * elton mosquitto_pub -h localhost -t elton/control/pdm/wake -m off
```

---

## Sammanfattning för Pi-experten

**Vad bygga:**
1. Ny service `pdm-power-controller` (separat repo eller submodule)
2. GPIO-relä-kontroll med active-low support
3. MQTT-handler för wake/sleep-commands + battery/ignition monitoring
4. Watchdog för auto-sleep
5. Safety: boot-delay, battery cut-off, sleep-warning
6. systemd unit med ExecStop för graceful relä-off
7. Tests (target: analog till mqtt-to-can-täckning)
8. README + install.sh

**Vad INTE bygga:**
- Hardvara-felsökning av relämodulen (Joel mockar med)
- HighSpeed switching (relä = max ~10Hz, mer än vad vi behöver)
- PWM på relät (inte stöds)

**Estimat:** 1-2 dagar arbete (mqtt-to-can-mönstret är redan etablerat, mest copy-paste-anpassning)

**Beroenden:**
- `lgpio>=0.2.2` eller `RPi.GPIO>=0.7.1`
- `paho-mqtt>=2.0.0`
- Python 3.10+
