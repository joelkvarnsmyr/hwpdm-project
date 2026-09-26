# Elton — Raspberry Pi GPIO: Bromssignaler & Sakerhetsovervakning
**Fordon:** VW LT31 1976 — JSN 398
**Datum:** 2026-03-11
**Version:** 1.0

---

## Oversikt

Raspberry Pi 4 laser fem sakerhetskritiska signaler direkt fran fordonets bromssystem via GPIO. Dessa signaler skickas vidare via CAN-bussen till PDM25 och visas pa dashboarden.

Alla signaler ar enkla kontakter som slutar mot chassijord — inga externa komponenter kravs. RPi:ns inbyggda pull-up-resistorer (~50 kohm) aktiveras i mjukvaran.

---

## GPIO-tilldelning

| Signal | Komponent | GPIO (BCM) | Fysisk pin | CAN-frame |
|--------|-----------|-----------|------------|-----------|
| Oljetryck | F1 | GPIO 4 | Pin 7 | 0x110 byte 0 |
| Kylvatskeniva | F66 | GPIO 17 | Pin 11 | 0x110 byte 1 |
| Bromskrets (dubbel) | F (tryckkontakt) | GPIO 27 | Pin 13 | 0x110 byte 2 |
| Handbroms | F9 | GPIO 22 | Pin 15 | 0x110 byte 3 |
| Bromsvatska niva | F34 | GPIO 23 | Pin 16 | 0x110 byte 4 |

**Spanningsreferens:** 3,3V (Pin 1)
**Jord:** GND (Pin 6, 9, 14 eller 20)

---

## Signallogik

Alla kontakter ar normalt oppna och slutar mot chassijord vid aktivering.

```
3,3V (intern pull-up ~50 kohm)
    |
GPIO-pin ---- Kontakt ---- Chassijord (GND)

Kontakt OPPEN  -> GPIO = HIGH (3,3V) -> Normalt lage -- inget fel
Kontakt SLUTEN -> GPIO = LOW  (0V)   -> Fel / aktivt lage
```

### Per signal

| Signal | LOW betyder | HIGH betyder |
|--------|-------------|--------------|
| F1 Oljetryck | Oljetrycket ar OK | Oljetrycket ar LAGT |
| F66 Kylniva | Nivan ar OK | Nivan ar LAG |
| F Bromskrets | Bada kretsar OK | En krets har tappat tryck |
| F9 Handbroms | Handbromsen ar uppe | Handbromsen ar atdragen |
| F34 Bromsvatska | Nivan ar OK | Nivan ar LAG |

> **OBS:** F1 oljetryck ar inverterad logik — kontakten ar sluten vid normalt tryck och oppnar vid lagt tryck. Kontrollera med multimeter pa den specifika givaren och justera logiken i koden vid behov.

---

## Kabelspec

| Egenskap | Varde |
|---------|-------|
| Dimension | 0,5 mm2 |
| Markning (tejp) | Gron (INST-kablar) |
| Prefix | `RPI.GPIO.xxx` |
| Dragning | Fran respektive kontakt direkt till RPi GPIO-pin |

### Kabeletiketter

| Kabel | Fran | Till |
|-------|------|------|
| `RPI.GPIO.OIL` | F1 | GPIO 4 / Pin 7 |
| `RPI.GPIO.COOL.LVL` | F66 | GPIO 17 / Pin 11 |
| `RPI.GPIO.BRAKE.CIRCUIT` | F (tryckkontakt) | GPIO 27 / Pin 13 |
| `RPI.GPIO.HANDBRAKE` | F9 | GPIO 22 / Pin 15 |
| `RPI.GPIO.BRAKE.FLUID` | F34 | GPIO 23 / Pin 16 |

---

## Bromskretssensorn (F) — viktig begransning

Tryckkontakten F ar ett differenstryckbrytare i ett hydrauliskt T-stycke. Den registrerar **att** en av de tva bromskretsarna har tappat tryck — men kan inte saga **vilken**. Det ar en enda binar signal.

For att skilja pa fram- och bakkrets skulle separata trycksensorer per krets kravas, vilket innebar ingrepp i hydrauliken. Detta ar inte planerat.

---

## Mjukvara — Python-initiering

```python
import RPi.GPIO as GPIO

# Pinnnummer enligt BCM-schema
PINS = {
    "oil_pressure":    4,   # F1
    "coolant_level":   17,  # F66
    "brake_circuit":   27,  # F (dubbel bromskrets)
    "handbrake":       22,  # F9
    "brake_fluid":     23,  # F34
}

GPIO.setmode(GPIO.BCM)

for name, pin in PINS.items():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```

### Lasning och CAN-utsandning

```python
import can
import struct

bus = can.interface.Bus(channel='can0', bustype='socketcan')

def read_safety_signals():
    return {
        "oil_pressure":   GPIO.input(PINS["oil_pressure"]),
        "coolant_level":  GPIO.input(PINS["coolant_level"]),
        "brake_circuit":  GPIO.input(PINS["brake_circuit"]),
        "handbrake":      GPIO.input(PINS["handbrake"]),
        "brake_fluid":    GPIO.input(PINS["brake_fluid"]),
    }

def send_can_frame(signals):
    data = [
        signals["oil_pressure"],     # byte 0
        signals["coolant_level"],    # byte 1
        signals["brake_circuit"],    # byte 2
        signals["handbrake"],        # byte 3
        signals["brake_fluid"],      # byte 4
        0, 0, 0                      # byte 5-7 reserverade
    ]
    msg = can.Message(arbitration_id=0x110, data=data, is_extended_id=False)
    bus.send(msg)
```

---

## CAN-frame 0x110

| Byte | Signal | 0 = | 1 = |
|------|--------|-----|-----|
| 0 | Oljetryck (F1) | OK | LAGT TRYCK |
| 1 | Kylniva (F66) | OK | LAG NIVA |
| 2 | Bromskrets (F) | OK | FEL |
| 3 | Handbroms (F9) | Uppe | Atdragen |
| 4 | Bromsvatska (F34) | OK | LAG NIVA |
| 5-7 | Reserverade | -- | -- |

---

## Atgarder vid larm

| Signal | Allvarlighetsgrad | PDM-atgard | Dashboard |
|--------|------------------|------------|-----------|
| F1 Oljetryck lagt | KRITISK | CAN-kommando stanger O5 (branslepump) | Rod varning + larm |
| F Bromskrets fel | KRITISK | CAN-kommando triggar O9 (varningsoutput) | Rod varning + larm |
| F34 Bromsvatska lag | HOG | Triggar O9 varningsoutput | Rod varning |
| F66 Kylniva lag | HOG | Triggar O9 varningsoutput | Rod varning |
| F9 Handbroms | INFO | Ingen PDM-atgard | Varning om hastighet > 5 km/h |

---

## RPi 40-pin header — pinnutnyttjande

```
         3V3  [ 1] [ 2]  5V
   (fri) GPIO2 [ 3] [ 4]  5V
   (fri) GPIO3 [ 5] [ 6]  GND
    F1   GPIO4 [ 7] [ 8]  GPIO14 (CAN HAT TX)
          GND  [ 9] [10]  GPIO15 (CAN HAT RX)
   F66  GPIO17 [11] [12]  GPIO18
   F    GPIO27 [13] [14]  GND
   F9   GPIO22 [15] [16]  GPIO23  F34
         3V3  [17] [18]  GPIO24 (CAN HAT INT)
 (SPI) GPIO10 [19] [20]  GND
  (SPI) GPIO9 [21] [22]  GPIO25 (CAN HAT INT)
 (SPI)GPIO11  [23] [24]  GPIO8  (CAN HAT CS)
          GND [25] [26]  GPIO7
        (I2C) [27] [28]  (I2C)
   (fri)GPIO5 [29] [30]  GND
   (fri)GPIO6 [31] [32]  GPIO12
  (fri)GPIO13 [33] [34]  GND
  (fri)GPIO19 [35] [36]  GPIO16
  (fri)GPIO26 [37] [38]  GPIO20
          GND [39] [40]  GPIO21
```

**CAN HAT upptar:** GPIO 8, 9, 10, 11 (SPI), GPIO 14, 15 (UART), GPIO 24, 25 (interrupt)
**Bromssignaler:** GPIO 4, 17, 22, 23, 27
**Lediga GPIO:** 2, 3, 5, 6, 12, 13, 16, 19, 20, 21, 26

---

*ELTON Projektet — Hanna Erixon & Joel*
