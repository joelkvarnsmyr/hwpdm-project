# Hardwire PDM Internal Logic Reference

Denna dokumentation är extraherad från källkoden i Hardwire Pro PDM Configurator v1.x (Electron App).

## 1. Variabel-ID (Key Mapping)
Variabel-ID:n används i `.HWPDM`-filer för att referera till specifika mätvärden eller tillstånd.

| Grupp | Bas-ID | Stride | Variabler per kanal |
| :--- | :--- | :--- | :--- |
| **OutputHS** | 34 | 20 | Current, Voltage, Status, TripCount, etc. |
| **OutputLS** | 284 | 10 | Current, Status, etc. |
| **Inputs** | 562 | 5 | Voltage, Frequency, Status, OnTime, OffTime |
| **Generic Functions** | 640 | 1 | Status (Boolean) |
| **Timers** | 610 | 1 | Status (Boolean) |

### Exempelberäkning (Input):
`ID = 562 + (InputNumber - 1) * 5`
*   Input 1: 562
*   Input 2: 567
*   Input 16: 637 (Matchar din Elton_v7.2!)

---

## 2. Protokoll-prefix (rawSendData)
Används för att konfigurera enheten via USB/WiFi.

| Prefix | Beskrivning | Exempel på variabler |
| :--- | :--- | :--- |
| `GL` | Global | CAN Speed, Term Resistor, Password Hash |
| `IP` | Inputs | Mode, ActiveLevel, Threshold (x10), PullResistor |
| `OP` | Outputs | Fuses (x1000), Delays (x10), PWM Freq, Label |
| `TI` | Timers | On/Off Time, Reset Condition, Duration |
| `GF` | Generic Functions | Logic Function (Array format) |
| `MC` | Maths Channels | Equation (Postfix notation) |
| `SC` | Sensor Cal | Raw/Calibrated points (x100) |
| `TD` | 2D Tables | X/Y Min/Max (x100), Table Data (x100) |

---

## 3. Hårdvaru-ID (Device Models)
Programmet känner av vilken PDM som används via dessa ID-spann:

*   **10-19**: PDM15 (V1: 10-12, V2: 13-19)
*   **20-29**: PDM25 (V1: 20-22, V2: 23-29)
*   **32-39**: PDM35 (PDM25+ med extra IO)
*   **70-79**: PDM28

---

## 4. Pin Manager (Hardware Mapping)
Pin Manager mappar fysiska kontakter till mjukvaru-index.
*   **Connectors:**
    *   1-4: DTM (Grey, Black, Green, Brown)
    *   5-8: DT (Grey, Black, Green, Brown)
    *   9-10: DTP (Grey, Black)
*   **NoteNumber:** Index (0-47) som mappar anteckningar till specifika pins i `pinManager`-objektet i JSON-filen.

---

## 5. PDF Export Fix (Applicerad 2026-03-08)
En bugg i `src/pinManager.js` gjorde att pin-nummer (1-12) i cirklarna blev osynliga i PDF-exporten.
*   **Orsak:** Texten var för liten (5px) och saknade explicit färg-override vid kloning för vit bakgrund.
*   **Fix:** Vid export tvingas nu `.connectorPinText` till `black`, `12px` och `bold`.
