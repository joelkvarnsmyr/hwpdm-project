// populate_pinmanager.js — Populate Pin Manager notes in Elton_v7.2.HWPDM
// Data from ELTON_PDM25V2_KABELMARKNING_v5.6.md

const fs = require('fs');
const path = require('path');

const hwpdmPath = path.join(__dirname, 'Elton_v7.2.HWPDM');
const hwpdm = JSON.parse(fs.readFileSync(hwpdmPath, 'utf8'));

// Pin Manager: 48 notes (noteNumber 0-47)
// Connector A = pins 0-11 (A1=pin0 .. A12=pin11)
// Connector C = pins 12-23 (C1=pin12 .. C12=pin23)
// Connector D = pins 24-35 (D1=pin24 .. D12=pin35)
// Connector B = pins 36-47 (B1=pin36 .. B12=pin47)

// Wait — need to verify the pin-to-noteNumber mapping.
// The configurator uses 4 connectors with 12 pins each = 48 notes.
// From Joel's file, noteNumber 0 had his test note. Let me check the
// connector ordering from the configurator. PDM25 V2 connectors are
// labeled A, B, C, D. The configurator likely maps them in order:
// Connector A pins 1-12 = noteNumber 0-11
// Connector B pins 1-12 = noteNumber 12-23
// Connector C pins 1-12 = noteNumber 24-35
// Connector D pins 1-12 = noteNumber 36-47

// But we need to verify this. Joel's note was on noteNumber 0.
// Looking at the Pin Manager screenshot context: it shows connectors
// in order. Let me use the most logical mapping and verify.

// Actually, the standard Deutsch DT connector order in the configurator
// for PDM25 V2 is typically: A, B, C, D (each 12 pins).
// noteNumber 0-11 = Connector A (A1-A12)
// noteNumber 12-23 = Connector B (B1-B12)
// noteNumber 24-35 = Connector C (C1-C12)
// noteNumber 36-47 = Connector D (D1-D12)

// Format: "role | label | wire_spec | source/destination | notes"

const notes = {};

// === CONNECTOR A (noteNumber 0-11): A1-A12 — All inputs ===
notes[0]  = "I12 HORN | PDM.IN.HORN | 0.75mm² br/bl | Hornknapp via slip ring | Active Low, 10kΩ ext PU till busbar";
notes[1]  = "I10 WIPER SLO | PDM.IN.WIPER.SLO | 0.75mm² gn | E22 torkaromk. kl.53 | Momentary, via busbar";
notes[2]  = "I8 WASHER | PDM.IN.WASHER | 0.75mm² gn/ro | Höger spak (dra) | Momentary, via busbar";
notes[3]  = "I6 TURN R | PDM.IN.TURN-R | 0.75mm² sw/gn | Blinkerspak höger | Momentary, via busbar";
notes[4]  = "I4 BRAKE | PDM.IN.BRAKE | 2.0mm² sw/ro | Bromsljusbrytare | Momentary, bat→switch→I4";
notes[5]  = "I2 HIBEAM | PDM.IN.HIGHBEAM | 0.75mm² ge | E4 helljusspak kl.56b | Latching";
notes[6]  = "I1 BLOWER | PDM.IN.BLOWER | 0.75mm² sw/ge | E9 fläktvred (4.7k+4.7k) | Analog, EMA 5";
notes[7]  = "I3 HAZARD | PDM.IN.HAZARD | 0.75mm² — | Varningsblinkersknapp | Latching, via busbar";
notes[8]  = "I5 TURN L | PDM.IN.TURN-L | 0.75mm² sw/ws | Blinkerspak vänster | Momentary, via busbar";
notes[9]  = "I7 PARK | PDM.IN.PARK | 0.75mm² — | Parkljusswitch | Momentary, via busbar";
notes[10] = "I9 WIPER FST | PDM.IN.WIPER.FST | 0.75mm² sw/gr | E22 torkaromk. kl.53b | Momentary, via busbar";
notes[11] = "I11 COOLANT | PDM.IN.COOLANT | 0.75mm² gn | G2 NTC kyltemp | Analog, 1kΩ PU→5V, EMA 10";

// === CONNECTOR C (noteNumber 12-23): C1-C12 — DT-Green ===
notes[12] = "I16 IGNITION | PDM.IN.IGNITION | 2.5mm² sw/ge | Tändningslås terminal 15 | Momentary Active High";
notes[13] = "I15 START | PDM.IN.START | 2.5mm² sw/ws | Tändningslås terminal 50 | Momentary Active High";
notes[14] = "PDM POWER | PDM.PWR.CTRL | 4mm² ro | Startmotor kl.30 via frånskiljare | Batteri always-on";
notes[15] = "O3 IGN COIL | PDM.OUT.IGNITION | 1.5mm² sw/li | N6 seriemotstånd (tändspole) | Fn: GF1, HS/LS→HS";
notes[16] = "O2 WIPER FST | PDM.OUT.WIPER.FST | 2.5mm² sw/gr | V torkarmotor kl.53b | Fn: I9 Status, HS/LS→HS";
notes[17] = "O1 BUSBAR | PDM.OUT.BUSBAR | 0.75mm² — | Signalbusbar (terminalblock) | Always True, 3.0A fuse, HS/LS→HS";
notes[18] = "GND | PDM.GND.CHASSIS | 10mm² br | Chassijord punkt 12 | Systemjord";
notes[19] = "CAN HIGH | PDM.CAN.H | 0.75mm² ws (tvinnad) | RPi CAN High | 250 kbps";
notes[20] = "CAN LOW | PDM.CAN.L | 0.75mm² sw (tvinnad) | RPi CAN Low | 250 kbps, intern term. aktiv";
notes[21] = "5V REF | PDM.5V.REF | — | Sensorutgång | 100mA max, till I11+I13 PU";
notes[22] = "I13 FUEL LVL | PDM.IN.FUEL.LVL | 0.75mm² li/sw | G bränslegivare | Analog, 100Ω PU→5V, EMA 10";
notes[23] = "I14 REVERSE | PDM.IN.REVERSE | 0.75mm² sw/bl | Backväxelkontakt | Momentary, bat→switch→I14";

// === CONNECTOR D (noteNumber 24-35): D1-D12 — DT-Brown ===
notes[24] = "O17 RESERVE | — | — | Ledig | HS output";
notes[25] = "O21 RPI | PDM.OUT.RPI | 2.0mm² — | Raspberry Pi 5 + CAN HAT | Fn: Always True, Soft Start 2s";
notes[26] = "O24 PARK (F) | PDM.OUT.PARK-F | 1.5mm² gr | M1+M3 sidoljus fram | Fn: I7 Status, dual-pin D3+D10";
notes[27] = "O9 RESERVE | — | — | Ledig | HS output";
notes[28] = "O8 RESERVE | — | — | Ledig | HS output";
notes[29] = "O7 HIBEAM R | PDM.OUT.HIGHBEAM-R | 2.5mm² ws | L2 höger kl.56b | Fn: O15 AND I2";
notes[30] = "O4 BRAKE | PDM.OUT.BRAKE | 2.0mm² sw/ro | M9+M10 bromsljus | Fn: I4 Status, Instant trip, HS/LS→HS";
notes[31] = "O5 FUEL | PDM.OUT.FUEL | 1.5mm² sw | G6 bränslepump | Fn: GF1, Stay On 2s";
notes[32] = "O6 TURN R | PDM.OUT.TURN-R | 1.5mm² sw/gn | M7+M8 blinkers H | Fn: T1 AND (I6 OR I3)";
notes[33] = "O24 PARK (B) | PDM.OUT.PARK-R | 1.5mm² gr/sw | M4+M2 parkljus bak | Dual-pin parallell med D3";
notes[34] = "O20 RADIO ACC | PDM.OUT.RADIO.ACC | 1.5mm² — | Radio ACC | Fn: GF1";
notes[35] = "O16 HIBEAM L | PDM.OUT.HIGHBEAM-L | 2.5mm² ws/sw | L1 vänster kl.56b | Fn: O14 AND I2";

// === CONNECTOR B (noteNumber 36-47): B1-B12 — DT-Black ===
notes[36] = "O19 REVERSE | PDM.OUT.REVERSE | 2.0mm² sw/bl | M16+M17 backljus | Fn: I14 Status";
notes[37] = "O23 STARTER | PDM.OUT.STARTER | 2.5mm² ro/sw | Startrelä terminal 50 | Fn: GF1 AND I15, Stay On 0s";
notes[38] = "O25 TURN L (F) | PDM.OUT.TURN-L-F | 1.5mm² sw/ws | M5 blinkers V fram | Fn: T1 AND (I5 OR I3), dual-pin B3+B10";
notes[39] = "O15 LOWBEAM R | PDM.OUT.LOWBEAM-R | 2.5mm² ge | L2 höger kl.56a | Fn: GF1, Delay 3s";
notes[40] = "O14 LOWBEAM L | PDM.OUT.LOWBEAM-L | 2.5mm² ge/sw | L1 vänster kl.56a | Fn: GF1, Delay 3s";
notes[41] = "O13 HORN | PDM.OUT.HORN | 2.0mm² sw/ge | H1 signalhorn | Fn: I12 Status, Peak 8A/0.5s";
notes[42] = "O10 WIPER SLO | PDM.OUT.WIPER.SLO | 2.5mm² gn | V torkarmotor kl.53 | Fn: I10 Status, Soft Start 1s";
notes[43] = "O11 BLOWER | PDM.OUT.BLOWER | 2.5mm² sw/ge | V2 kupéfläkt | Fn: GF1 AND I1>1V, PWM, Stay On 30s";
notes[44] = "O12 WASHER | PDM.OUT.WASHER | 1.5mm² gn/ro | V5 spolarpump | Fn: I8 Status";
notes[45] = "O25 TURN L (B) | PDM.OUT.TURN-L-R | 1.5mm² sw/ws | M6 blinkers V bak | Dual-pin parallell med B3";
notes[46] = "O22 USB 12V | PDM.OUT.USB12V | 1.5mm² — | 12V USB-uttag | Fn: GF1";
notes[47] = "O18 RADIO MEM | PDM.OUT.RADIO.MEM | 1.0mm² — | Radio permanent minne | Fn: Always True";

// Build the notes array
const pinManagerNotes = [];
for (let i = 0; i < 48; i++) {
  pinManagerNotes.push({
    noteNumber: i,
    noteText: notes[i] || ""
  });
}

hwpdm.pinManager = { notes: pinManagerNotes };

fs.writeFileSync(hwpdmPath, JSON.stringify(hwpdm, null, 2), 'utf8');
console.log('Pin Manager populated with 48 notes in Elton_v7.2.HWPDM');
console.log('Sample notes:');
console.log('  [0]', notes[0]);
console.log('  [12]', notes[12]);
console.log('  [24]', notes[24]);
console.log('  [36]', notes[36]);
