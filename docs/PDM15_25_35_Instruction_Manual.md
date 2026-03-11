# PDM15/25/35 — Instruction Manual

**Hardwire Electronics**
www.hardwire-electronics.co.uk
*Version 1 — 23/6/25*

---

## Change Log

| Version | Author   | Date           | Changes         |
|---------|----------|----------------|-----------------|
| 1.0     | George S | 23rd June 2025 | Initial Release |

---

## Contents

- [Introduction](#introduction)
  - [Specification](#specification)
- [System Overview Diagram](#system-overview-diagram)
- [Installation](#installation)
  - [Mounting](#mounting)
  - [Pinout](#pinout)
  - [Battery Positive](#battery-positive)
  - [Battery Negative](#battery-negative)
  - [5V Output](#5v-output)
  - [Ignition Input](#ignition-input)
  - [Inputs](#inputs)
  - [Outputs](#outputs)
  - [CAN Bus Wiring](#can-bus-wiring)
- [Configuration Software](#configuration-software)
  - [Connection](#connection)
  - [Configuration Files](#configuration-files)
  - [General](#general)
  - [Inputs](#inputs-1)
  - [Outputs](#outputs-1)
- [Timers](#timers)
- [Counters](#counters)
- [Maths Channels](#maths-channels)
- [Generic Functions](#generic-functions)
- [Sensor Calibrations](#sensor-calibrations)
- [2D Tables](#2d-tables)
- [CAN Keypads](#can-keypads)
- [CAN Bus Basics](#can-bus-basics)
- [CAN Inputs](#can-inputs)
- [CAN Outputs](#can-outputs)
- [CAN Output Stream](#can-output-stream)
- [Data Logging](#data-logging)
- [Monitoring](#monitoring)
- [Logging](#logging)
- [Firmware Updates](#firmware-updates)
- [Examples](#examples)

---

## Introduction

A PDM (Power Distribution Module) is a device used to replace conventional relays and fuses in a vehicle electrical system. The Hardwire Electronics PDM takes inputs in the form of physical switches, analogue voltages, or CAN bus messages, and provides power to different electronic devices — such as radiator fans, fuel pumps, ECUs and headlights — using user defined logic functions. The current being drawn from each connected device is continuously monitored. If the measured current is too high due to a fault, the PDM switches off the respective output to prevent further damage to the wiring loom or the connected device. The PDM can then retry the output to see if the fault has cleared, or the user can manually reset the outputs via an input switch.

PDMs offer distinct advantages over conventional systems using fuse boards and relays:

- Greatly simplifies system wiring and reduces system component count, overall saving you money when labour/time is accounted for.
- Reduces the weight of the electrical system.
- Provides increased reliability over traditional systems using mechanical relays.
- Solid state technology removes the problem of relay contact corrosion and relay bouncing in vibration heavy applications.
- Smart features such as indicator and wiper motor modes remove the need for extra control units.
- Current draw can be monitored and logged to pre-emptively detect faults.
- CAN bus communication allows your PDM to send/receive data from other CAN bus devices in the vehicle, such as the vehicle ECU. This paves the way for advanced control/safety strategies such as automatic engine cut offs, fuel pump cut offs, radiator fan control and more.
- Easy integration with popular CAN bus keypads, improving system reliability and functionality.

---

## Specification

### Controller Module

#### General

| Parameter             | Value                                           |
|-----------------------|-------------------------------------------------|
| **Size**              | 200x160x54mm                                    |
| **Weight**            | PDM15 – 645g \| PDM25 – 690g \| PDM35 – 735g   |

#### Operating Levels

| Parameter                  | Value                    |
|----------------------------|--------------------------|
| **Operating Temperature**  | -55 to 90°C [-67 to 194°F] |
| **Operating Voltage**      | 4–32V                    |
| **Quiescent Current**      | 4–5mA                    |
| **Operating Current**      | 210mA at 12V             |
| **5V Output Current**      | 100mA maximum            |

#### Construction

| Parameter        | Value                          |
|------------------|--------------------------------|
| **Construction** | Glass Fibre reinforced plastic |
| **IP Rating**    | IP67 Water and dust ingress protection |
| **Connectors**   | 4x Deutsch DT 12-pin           |

#### Inputs

| Parameter                  | Value                                                                       |
|----------------------------|-----------------------------------------------------------------------------|
| **Type**                   | 16 analogue inputs which can also service as digital inputs                 |
| **Measurement Range**      | Each input can measure voltages between 0–28V, independent of battery voltage |
| **Measurement Resolution** | 12-bit or 0.01V                                                             |
| **Frequency Measurement**  | Automatic frequency measurement up to 300Hz                                |
| **Protection**             | Fully protected for input voltages between -24V to 40V                      |
| **Added Features**         | Configure as active high or low. Configurable Hysteresis voltage. Latching or momentary operation. |

#### Outputs

| Parameter                    | PDM15                                                                   | PDM25                                                                   | PDM35                                                                   |
|------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **Type**                     | 4 high/low side outputs 80A peak, 20A continuous, with reverse current protection (Pin-limited to 13A @125degC). 11 high side outputs 80A peak, 20A continuous (Pin-limited to 13A @125degC). | 4 high/low side outputs 80A peak, 20A continuous, with reverse current protection (Pin-limited to 13A @125degC). 21 high side outputs 80A peak, 20A continuous (Pin-limited to 13A @125degC). | 4 high/low side outputs 80A peak, 20A continuous, with reverse current protection (Pin-limited to 13A @125degC). 31 high side outputs 80A peak, 20A continuous (Pin-limited to 13A @125degC). |
| **Combined**                 | 120A combined output maximum current                                    |                                                                         |                                                                         |
| **Output current control steps** | 100mA                                                               |                                                                         |                                                                         |
| **Protection**               | Each output is overcurrent, overtemperature, load dump and reverse polarity protected. |                                                                         |                                                                         |
| **Soft Start**               | PWM soft start can be enabled on outputs to limit inrush current        |                                                                         |                                                                         |
| **PWM**                      | Each output can be Pulse Width Modulated based on a user defined variable. This can limit the speed of radiator fans, fuel pumps, and dim lights. 1000Hz maximum PWM frequency. |                                                                         |                                                                         |
| **Added Features**           | Outputs can be configured to stay on for a specified time after the input is removed, useful for thermo-fans. Outputs can be retried multiple times after an over-current event is detected. |                                                                         |                                                                         |

#### CAN Bus

| Parameter                | Value                                                                      |
|--------------------------|----------------------------------------------------------------------------|
| **Interface**            | 1x CAN2.0A/B ports                                                         |
| **Bus Speed**            | 50, 100, 125, 250, 500, 1000 kbps                                          |
| **Termination Resistor** | CAN bus port has software selectable CAN termination resistor              |
| **DBC File Import**      | Easily Import DBC files to configure the CAN inputs of the PDM             |
| **Input Stream**         | 100x inputs, fully customisable variable parsing with bit masking, math functions, and compound CAN message filtering |
| **Output Stream**        | 100x Outputs, Fully customisable CAN frame construction with math functions |

#### CAN Keypad

| Parameter     | Value                                                                           |
|---------------|---------------------------------------------------------------------------------|
| **Supported** | Blink Marine, Grayhill, Motec, Haltech and Marlin CAN keypads. Up to four keypads can be used at once. |

#### Logging

| Parameter   | Value                                                                                                  |
|-------------|--------------------------------------------------------------------------------------------------------|
| **Storage** | 128Mb of onboard flash storage for logging PDM data                                                    |
| **Speed**   | 1Hz to 50Hz                                                                                            |
| **Viewing** | Data can be downloaded and graphed via the Hardwire Electronics PDM configurator software or exported as a .CSV file and graphed in external software |

#### Functions

| Parameter             | Value                                                                    |
|-----------------------|--------------------------------------------------------------------------|
| **Output Functions**  | Each Output can be switched with a user defined function                 |
| **Logical Operators** | AND, OR, NOR, XOR, NAND, NOR, >, >=, <, <=, Equal, Not Equal           |

#### Timers

| Parameter    | Value                                           |
|--------------|-------------------------------------------------|
| **Pulse**    | On/Off Square wave, useful for indicators, wipers etc |
| **Duration** | Start/Stop/Reset Timer from 0–49 days           |

#### Maths Channels

| Parameter                  | Value                                                                     |
|----------------------------|---------------------------------------------------------------------------|
| **Mathematical Operators** | Addition, Subtraction, Multiplication, Division, Modulus                  |
| **Binary Operators**       | AND, OR, XOR, Left Shift, Right Shift                                     |
| **Functions**              | Choose, Min, Max, Sin, Cos, Tan, Floor, Ceil, Abs, Asin, Acos, Ln, Log, Pow, Sqrt |

#### Counters

| Parameter | Value                                                             |
|-----------|-------------------------------------------------------------------|
| **Type**  | Increment, decrement, and reset based on user defined conditions  |

#### Sensor Calibration

| Parameter | Value                                                       |
|-----------|-------------------------------------------------------------|
| **Type**  | 20-point Sensor Calibration Tables for sensor linearisation |

#### 2D Tables

| Parameter | Value                                    |
|-----------|------------------------------------------|
| **Type**  | 20x20 2D map tables for advanced behaviour |

#### IMU

| Parameter          | Value                                    |
|--------------------|------------------------------------------|
| **Rotation**       | 3-axis rotational position measurement 0.1° resolution |
| **Gyroscope**      | 2000°/s 3-axis measurement               |
| **Accelerometer**  | -8g to 8g 3-axis measurement             |

#### PCB Temperature

| Parameter | Value                        |
|-----------|------------------------------|
| **Type**  | PCB temperature measurement  |

#### RTC

| Parameter | Value                                                                          |
|-----------|--------------------------------------------------------------------------------|
| **Type**  | Real Time Clock with battery backup for 30 days. Used to store the correct time and date for data logs. |

#### USB

| Parameter  | Value                                   |
|------------|-----------------------------------------|
| **Type**   | USB 2.0 compliant with Mini-B           |
| **Driver** | Integrated driver with Windows 10/11    |

#### PC App

| Parameter         | Value                                                                                                                              |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------|
| **Name**          | Hardwire Electronics Pro PDM Configurator Software                                                                                 |
| **Compatibility** | Windows 10/11 machines                                                                                                             |
| **Connectivity**  | Easy connection to the PDM with USB and windows integrated drivers. No unreliable USB-serial converter needed. Alternatively connect via a Kvaser USB to CAN Device. |

---

## System Overview Diagram

*Figure 1 – Typical installation of a PDM in a vehicle electrical system.*

```
                        [ Isolator ]
                             |
         ┌───────────────────┴───────────────────────┐
         │                                           [Battery]
    PDM Power                Output Power
    12-24V                   12-24V           Ground
         │
    Analogue 0-28V ──► Inputs ──► Hardwire Electronics ◄──► CAN 1 ◄──► e.g. ECU, Keypad,
                                   PDM15/25/35                            USB to CAN
                                        │
                                    Output
                             ┌──────┬──────┐
                           [Light] [Fan] [Pump]
                                           │
                                          12V
```

---

## Installation

### Mounting

The PDM should be mounted in a well-ventilated area to cool the unit when under heavy load. Care should be taken to mount the PDM in a location which minimises the exposure to water and dirt. In most cases, mounting the PDM next to the ECU is the most efficient method, as the wires running between both units are kept to a minimum to save on weight.

Around 100mm of clearance should be maintained both on top and in front of the PDM to allow room for the wiring loom and USB to be connected without excess strain. It is recommended to mount the PDM on rubber mounts to minimise the vibration coupling from the vehicle to the PDM. This will help with IMU data.

*Dimensions (mm): 200 x 160 x 54.53 — Mounting hole spacing: 144 x 70 (centre-to-centre)*

---

### Pinout

Connectors are labelled A, B, C, D.

| Colour | Pin | Description          | Notes                                                          |
|--------|-----|----------------------|----------------------------------------------------------------|
|        | A1  | Input 12 / Output 31 | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | A2  | Input 10 / Output 29 | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | A3  | Input 8 / Output 27  | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | A4  | Input 6              | 0-27V, 40K pull Down / 200K pull up                            |
|        | A5  | Input 4              | 0-27V, 40K pull Down / 200K pull up                            |
|        | A6  | Input 2              | 0-27V, 40K pull Down / 200K pull up                            |
|        | A7  | Input 1              | 0-27V, 40K pull Down / 200K pull up                            |
|        | A8  | Input 3              | 0-27V, 40K pull Down / 200K pull up                            |
|        | A9  | Input 5              | 0-27V, 40K pull Down / 200K pull up                            |
|        | A10 | Input 7 / Output 26  | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | A11 | Input 9 / Output 28  | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | A12 | Input 11 / Output 30 | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | C1  | Input 16 / Output 35 | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | C2  | Input 15 / Output 34 | 0-27V, 40K pull Down / 200K pull up, 20A High Side, 1KHz PWM* |
|        | C3  | PDM Power            | 4V – 32V                                                       |
|        | C4  | Output 3             | 20A High/Low side, 1KHz PWM*                                   |
|        | C5  | Output 2             | 20A High/Low side, 1KHz PWM*                                   |
|        | C6  | Output 1             | 20A High/Low side, 1KHz PWM*                                   |
|        | C7  | Ground               |                                                                |
|        | C8  | CAN 1 High           |                                                                |
|        | C9  | CAN 1 Low            |                                                                |
|        | C10 | 5V Out               | 100mA Maximum                                                  |
|        | C11 | Input 13 / Output 32 | 0-27V, 40K pull Down / 200K pull up                            |
|        | C12 | Input 14 / Output 33 | 0-27V, 40K pull Down / 200K pull up                            |
|        | D1  | Output 17            | 20A High Side, 1KHz PWM*                                       |
|        | D2  | Output 21            | 20A High Side, 1KHz PWM*                                       |
|        | D3  | Output 24            | 20A High Side, 1KHz PWM*                                       |
|        | D4  | Output 9             | 20A High Side, 1KHz PWM*                                       |
|        | D5  | Output 8             | 20A High Side, 1KHz PWM*                                       |
|        | D6  | Output 7             | 20A High Side, 1KHz PWM*                                       |
|        | D7  | Output 4             | 20A High/Low side, 1KHz PWM*                                   |
|        | D8  | Output 5             | 20A High Side, 1KHz PWM*                                       |
|        | D9  | Output 6             | 20A High Side, 1KHz PWM*                                       |
|        | D10 | Output 24            | 20A High Side, 1KHz PWM*                                       |
|        | D11 | Output 20            | 20A High Side, 1KHz PWM*                                       |
|        | D12 | Output 16            | 20A High Side, 1KHz PWM*                                       |
|        | B1  | Output 19            | 20A High Side, 1KHz PWM*                                       |
|        | B2  | Output 23            | 20A High Side, 1KHz PWM*                                       |
|        | B3  | Output 25            | 20A High Side, 1KHz PWM*                                       |
|        | B4  | Output 15            | 20A High Side, 1KHz PWM*                                       |
|        | B5  | Output 14            | 20A High Side, 1KHz PWM*                                       |
|        | B6  | Output 13            | 20A High Side, 1KHz PWM*                                       |
|        | B7  | Output 10            | 20A High Side, 1KHz PWM*                                       |
|        | B8  | Output 11            | 20A High Side, 1KHz PWM*                                       |
|        | B9  | Output 12            | 20A High Side, 1KHz PWM*                                       |
|        | B10 | Output 25            | 20A High Side, 1KHz PWM*                                       |
|        | B11 | Output 22            | 20A High Side, 1KHz PWM*                                       |
|        | B12 | Output 18            | 20A High Side, 1KHz PWM*                                       |

*\*Limited by maximum current capacity of contact and pin*

---

### Battery Positive

The PDM powers connected devices via the M8 stud protruding from the top of the enclosure. The PDM current can peak at upwards of 180 Amps, therefore an appropriate gauge copper wire must be used to attach to the M8 stud to avoid excess heat and voltage drop. It is recommended to use at least 2 AWG wire with the supplied ring terminal.

Care must be taken when tightening the retaining nut on the stud. The recommended torque to use is 8Nm — **exceeding this could damage the internal circuit board.**

### Battery Negative

Under normal operating conditions, the current flow through the ground pin of the PDM is low. However, when a load dump occurs, the current flow can be much higher. Therefore, it is recommended that at least 20 AWG wire be used.

### 5V Output

One pin (C10) on the PDM 15/25/35 is a dedicated 5V output. The 5V output is over current and short circuit protected. No more than 0.1 Amp should be drawn from the 5V output to avoid excessive heating of the internal circuitry. The 5V output can be used to connect to analogue voltage sensors such as thermal sensors.

### Ignition Input

To power on the PDM, the Ignition Input must be switched to the battery positive voltage. This input can be wired directly to the accessory input of an ignition key barrel, or alternatively to another dedicated switch. The ignition input may be connected directly to the battery positive voltage — however, this is not advised as the battery will slowly discharge over time when the vehicle is not in use. A battery isolator may be used to combat this problem.

### Inputs

The PDM has 16 inputs which can measure analogue voltages between 0–28V with a sample resolution of 12-bit or 0.007V. The inputs are sampled at a high rate, which allows the frequency of the input signal to be measured up to 300Hz.

The great flexibility of the PDM Inputs allows analogue, digital, switched 12V and switched ground inputs to be measured with ease.

### Outputs

The PDM has 4x High/Low side outputs, meaning that they can output the positive battery voltage to source current OR put the output to ground to sink current. Internal circuitry stops both the high and low side being activated at the same time on any given output.

These outputs are also reverse current protected, meaning that when the voltage present on the output is greater than the battery voltage, the output does not allow current to flow back into the output. This is useful when driving wiper motors with low/high speed windings. Each output has current sensing, thermal overload protection, static discharge protection, short circuit protection and over/under voltage protection. The remainder of the outputs are just high sided.

The outputs are able to switch on and off incredibly quickly, which reduces heat build up when using the output in PWM mode. The outputs have a continuous current rating of 20 Amps (limited by the current capacity of the contact and pin to 13A at 125degC). Multiple outputs of the same type can be joined together to increase the current capacity.

### CAN Bus Wiring

The CAN bus is designed to be extremely robust and fault tolerant, however to ensure the best reliability, it is necessary to follow best practices when wiring up a CAN bus network. The physical CAN bus is constructed with two wires, CAN high and CAN low. The wires should be twisted around each other at approximately 1 twist per 1"/2 cm of length, to help mitigate electrical interference on the CAN bus.

Each end of the CAN bus **MUST** have a 120Ω termination resistor installed between the CAN high and CAN low lines. The two termination resistors are effectively wired in parallel, resulting in a total of 60Ω of resistance between the CAN high and CAN low lines. It is important to verify that there is approximately 60Ω of resistance between the CAN high and CAN low lines. Some CAN bus devices will have a CAN termination resistor installed internally. The Hardwire PDM has software selectable CAN termination resistors on the CAN bus port. If the PDM CAN termination resistor is used, then the PDM must be placed at the end of the CAN bus.

Care must be taken to ensure that the physical wiring of the CAN bus meets the following requirements:

- The maximum bus length must not exceed 25m
- The CAN bus must be terminated at each end with a 120Ω resistor. The PDM has a software selectable CAN termination resistor.
- CAN bus 'stubs' must be no longer than 30cm in length
- Twisted pair wire must be used for the CAN bus with a minimum of one twist per 3cm.

---

## Configuration Software

The Hardwire Electronics Configuration Software has been designed with ease of use in mind. There are five main sections to the software: Connection, Configuration, Monitor, Logging, Update and Pin Manager. Each section can be accessed via the tabs at the left of the screen in the sidebar.

The software can be found on the supplied USB drive, or on the Hardwire Electronics Website in the downloads section: https://www.hardwire-electronics.co.uk/downloads

### Connection

If you don't have a PDM, but would still like to access the software, select a model from the Offline Mode select box.

If the PDM configuration has been locked with a password, you will be prompted to enter the password to gain access. If you have forgotten your password, then you will need to reflash the PDM with new firmware.

#### USB

Plug in to the PDM with the provided USB cable. Navigate to the Connection Tab and click on the drop down menu under USB Connection. The PDM can then be selected from the list. It will show as a COM device. Now click connect. If a successful connection has been made, then the USB connection status will update in the sidebar, and the Tx and Rx values will begin to count up.

#### USB to CAN

In addition to connecting via the USB cable, you can connect to the PDM using a USB to CAN device. Hardwire Electronics supports the Kvaser USB to CAN devices. You will need to make sure that the PDM is already configured to the correct CAN bus speed with the correct CAN termination resistor settings. Install the device drivers for the Kvaser USB to CAN device before proceeding.

If the PDM and CAN bus is configured correctly, you should be able to select the USB to CAN devices from the drop down menu, and then click connect. If successful, the software will show 'Connected' at the bottom of the screen.

### Configuration Files

To configure the PDM and connected NIO Power Modules, connect to the PDM via USB and navigate to the Configuration Tab.

#### Save Configuration

Pressing Save at the top of the screen will prompt the user to locate a directory on the PC in which to save the configuration file. Configuration files should have a `.HWPDM` file extension.

#### Load Configuration

Likewise, pressing Load will prompt the user to navigate to a configuration file which can then be loaded into the configuration software.

#### Send Configuration

Press the Send button to send the current configuration to the PDM, and press Retrieve to retrieve the configuration currently on the PDM.

#### Retrieve Configuration

When retrieving the configuration from the PDM, if any changes are detected between the current configuration on the PC and the configuration on the PDM, then the user will be given a choice to either maintain the current configuration on the PC, or alternatively to overwrite the configuration on the PC and load in the configuration from the PDM onto the PC.

### General

In the General tab, the user can configure the general settings for the PDM.

#### CAN Bus Settings

At the top of the tab, the user can select the CAN termination resistor and CAN speed the CAN bus. Enabling the CAN termination resistor will add a 120 Ohm resistance between CAN high and CAN low.

#### Reset Function

The Reset function is used to reset tripped outputs which have either tripped from over current or under current. More information is given on configuring functions later in the instruction manual. When the Reset function evaluates to 'True', each tripped output on the PDM and each NIO Power Module will reset, so that normal operation can resume.

#### Cut Off Function

The Cut Off function is used to turn off every output on the PDM. This feature is a useful safety feature, to disable the entire vehicle electrical system if a problem occurs. When the Cut Off function evaluates as 'True', each output is immediately turned off. The outputs will remain turned off until the PDM power is turned off and back on again, or until the Reset function is triggered.

#### Password

Once you have completed your PDM setup, you can lock the configuration with a password. To add a password, click enter new password and check the box to enable it. Each time you connect to the PDM, you will be prompted to enter the password again. If you forget the password, the PDM must be updated with new firmware to wipe the PDM clean.

---

## Inputs

### Voltage / Frequency

The PDM inputs are able to measure both the voltage and frequency of the input signal. The inputs have a voltage measurement range of 0–28V, and a frequency measurement range of 0–300Hz. The frequency measurements are performed automatically, and will work with any periodic waveform between 0 and 300Hz, irrespective of the peak to peak voltage or DC offset value.

### Mode

The inputs may be set to Momentary or Latched Mode. This feature makes it possible to use a simple push button switch to activate components such as fans and switches with one button press to turn the component on and off.

- **Momentary Mode:** When the input voltage passes the threshold voltage, the input will turn on.
- **Latched Mode:** When the input voltage passes the threshold voltage, the input will toggle its state from Off to On, or from On to Off.

### Active Level

Each input can be programmed as Active-High or Active-Low.

- **Active-High** causes the input to turn on when the voltage rises above the threshold.
- **Active-Low** causes the input to turn on when the voltage falls below the threshold.

### Threshold Voltage

Each input operates as an analogue input. Inputs are active whenever the voltage present on the input passes the Threshold Voltage.

### Hysteresis Voltage

A Hysteresis Voltage can be set, so that once an input is turned on, it does not turn off again until the voltage drops below the Threshold Voltage plus the Hysteresis Voltage. This helps to reduce the effect of voltage noise problems falsely triggering an input and may also be used in conjunction with a thermo-sensor and radiator fan to stop fan flickering.

### Turn On Delay

A turn on delay can be set, so that the input is triggered after the delay period has passed.

### EMA Filter

An EMA (Exponential Moving Average) filter can be applied to the input voltage. This can help to smooth out noisy input voltages. A higher EMA value will smooth the input voltage more.

---

## Outputs

This section will detail how to configure an output for the PDM. Navigate to the Output Tab to configure the outputs. Some PDM outputs are both High/Low sided. HS denotes High side, LS denotes Low side. If both the high and low side on a single output are instructed to turn on, only the high side will turn on. The low side will remain off until the high side is turned off.

### Output Status

| Value | Meaning               |
|-------|-----------------------|
| 0     | Off                   |
| 1     | On                    |
| 2     | Tripped Over Current  |
| 3     | Tripped Under Current |

### Output Current

How much current is flowing through the output.

### Output Voltage

The voltage on the output pin.

### Output Load

Ratio of the High Fuse current threshold to the output current, expressed as a percentage. If the load reaches 100%, it will trip from over current.

### Output Test

The user can manually test each output. The output must be enabled and configured in order to test it.

### Output Enable

Enables or Disables the output. Pressing 'Expand' will open up the full configuration settings for that output.

### Trip Mode

- **Instant Trip:** This mode will instantly turn the output off if the current flowing through the output goes over the current threshold. Good for devices that need instant overcurrent protection.
- **Normal Trip:** This mode acts like a conventional fuse and allows small current spikes over the current threshold without tripping. Useful for devices that draw current in short bursts, such as ignition coils.

### Low Fuse

The low fuse setting will trip if the current falls below the threshold for over 1 second continuously. If this functionality is not needed then the value should be set to 0.

### High Fuse

The high fuse setting comes into effect after the peak fuse time has elapsed, and sets the current limit for an output working at steady state. If the current exceeds this value, then the output will trip.

### Peak Fuse & Peak Fuse Time

The peak fuse setting determines the maximum current that an output can provide before it trips in the initial turn-on phase of the output. The length of the turn-on phase is determined by the peak fuse time setting. The peak fuse setting is used to allow large inrush currents without tripping the output. When turning on loads such as radiator fans or fuel pumps, the initial current draw from the device can often double or triple the steady state current draw.

### Stay On Time

After an output is commanded to turn off, the output will remain switched on for the stay on time, before turning off.

### Turn On Delay

This will delay the turn on of the output once the logic function evaluates to True.

### Clear Time

If an output trips, the output will not be retried until the 'clear time' has passed. This is to allow time for an output device to perhaps cool down or reset itself before being turned back on.

### Retries

If an output trips due to an overcurrent condition, then that output may be 'retried' several times to try and reestablish normal operation of the output. The output channel will be retried for the number of times specified by this setting. A value of zero will result in continual retries of that output.

### Functions

Output Functions are used to control if an output should be On or Off. The PDM evaluates the logic function; if the function evaluates to True then the output will turn On, if the output evaluates to False then the output will turn Off.

### PWM

All outputs on the Power Modules are PWM (Pulse Width Modulation) capable. Advanced, high speed switching circuitry allows for PWM operation at up to 1KHz with minimal heat dissipation. PWM is used to vary the average voltage present on the output. This is useful for varying the speed or intensity of motors or lights.

```
Duty Cycle % = (On Time / Period) × 100
```

### Frequency

The PWM frequency dictates the speed at which the outputs are turned on and off. A higher frequency can result in smoother operation of the device which is being driven. Frequency is equal to 1/Period.

### Mapping

To vary the PWM duty cycle, it is necessary to 'map' the required value of duty cycle to a PDM variable. As the PDM variable changes, the PWM duty cycle changes. To configure the PWM Mapping, first select a PDM variable from the drop down list. Eleven Variable values must be chosen for the different values of PWM duty cycle. The duty cycle value is linearly interpolated between the values given.

### Soft Start Time

Soft Start is a feature used to slowly turn on a device, by ramping the duty cycle on the output from 0% to 100% over a specified period. This results in the average voltage on the output increasing from 0% to 100%, slowly turning the device on. This feature is useful for starting devices such as radiator fans, which inherently have a large mechanical inertia.

---

## Timers

The PDM has up to 30 individual Timers, which can be used in output functions to achieve advanced functionality such as Flashing indicator lights, Intermittent wiper motors, and more. To configure a Timer, go to the Timer Tab and click 'Add.' This will add a Timer into the current configuration. The Timer can then be given a label and be enabled.

### Pulse Train

In Pulse Train mode, the timer has an ON and an OFF Time, given in milliseconds. When the timer is enabled, it will run automatically in the background, switching state from ON to OFF at the given intervals. It is up to the user to use the state of the timer in the output function.

### Duration

In Duration mode, the timer has a start and reset condition. When the start condition is met, it will begin counting. The value of the time will be the milliseconds elapsed since the start. The Timer will continue running until it reaches the duration value which is set, or until the reset condition is met. If Reset on End is selected, the timer will go back to 0 once the duration has elapsed. If the Reset on End is not selected, the timer value will stay at the duration value until the reset condition is met.

---

## Counters

The PDM has up to 30 individual Counters. Counters are variables which can be incremented or decremented, and are triggered by logic expressions, such as when an input status equals true. Counters can be used for more advanced functionality, such as incrementing a number every time a button is pressed, and then using the value of the counter to produce different PDM output behaviors.

To configure a counter, go to the Counter Tab and click 'Add.' The counter can then be given a label and enabled. Click 'Expand' to expand the configuration for the counter. Counters are always given a Start Value. This is the value which the Counter starts from when the device is powered up, or when the counter is reset.

The Loop Around Value is the maximum or minimum value that the counter will count to before looping back to the Start Value.

The Counter can be Incremented, Decremented, or Reset, based on three logic expressions. When the logic expression evaluates to 'True', the counter will Increment, Decrement, or Reset.

The Counters can count between a value of -2147483647 and +2147483647.

---

## Maths Channels

The PDM has up to 30 Maths Channels. Maths Channels are an advanced feature which allow the user to create their own mathematical expressions which are evaluated by the PDM. The value of the Maths Channels can then be used as needed.

To configure a Maths Channel, go to the Maths Channel Tab and click 'Add.' The Maths Channel can then be given a label and be enabled. Click 'Expand' to configure the functionality of the Maths Channel.

The structure of the mathematical equation is similar to that of logic functions. It is important to be aware of 'order of operations' when constructing an equation. Values are converted to 32-bit floating point when used in the mathematical equations. For Bitwise operations, the operands will be converted to unsigned 32-bit numbers.

### Mathematical Operators

| Operator          | Description                                                                     |
|-------------------|---------------------------------------------------------------------------------|
| Constant/Variable | A constant is a fixed number; a variable changes and can be selected from the PDM variable list. |
| Addition          | Adds the two operands together.                                                 |
| Subtraction       | Subtracts the second operand from the first.                                    |
| Division          | Divides the equation section by the divisor.                                    |
| Modulus           | Performs the modulo operation; gives the remainder when divided by the divisor. |

### Bitwise Operators

| Operator           | Description                                          |
|--------------------|------------------------------------------------------|
| AND                | Returns the bitwise AND operation of the two operands |
| OR                 | Returns the bitwise OR operation of the two operands  |
| XOR (Exclusive OR) | Returns the bitwise XOR operation of the two operands |
| Left Shift <<      | Shifts the equation section to the left by between 0–32 |
| Right Shift >>     | Shifts the equation section to the right by between 0–32 |

### Function Operations

| Function | Description                                                              |
|----------|--------------------------------------------------------------------------|
| Choose   | If the condition is true, returns the first value; otherwise returns the second. |
| Min      | Returns the smallest of the two values                                   |
| Max      | Returns the largest of the two values                                    |
| Sin      | Returns the sine of the value (Radians)                                  |
| Cos      | Returns the cosine of the value (Radians)                                |
| Tan      | Returns the tangent of the value (Radians)                               |
| Floor    | Returns the nearest whole number below the value                         |
| Ceil     | Returns the nearest whole number above the value                         |
| Abs      | Keeps the value of the number, but always returns it as a positive value |
| Asin     | Returns the arc sine of the value (Radians)                              |
| Acos     | Returns the arc cosine of the value (Radians)                            |
| Ln       | Returns the natural logarithm of the value                               |
| Log      | Returns the Log 10 of the value                                          |
| Pow      | Returns the base value to the power of the exponent value                |
| Sqrt     | Returns the square root of the value                                     |

---

## Generic Functions

Generic functions operate in a similar fashion to the functions found in the global reset, global cutoff, and output sections. The function is evaluated constantly by the PDM, and the result (either 1 or 0) can be used elsewhere in the PDM for more advanced behaviour.

---

## Sensor Calibrations

Sensor calibrations allow one to take a raw value/sensor reading and scale/offset its value at different points. This can be used, for example, to linearise a temperature sensor, or to scale a throttle position sensor between 0 and 100%.

Select the raw sensor value (this can be any variable in the PDM), and then use the arrows to adjust the calibrated value to your desired place. Each raw sensor value will map to the calibrated value according to the graph, with linear interpolation between the points.

---

## 2D Tables

The PDM has 5 individual 20x20 2D Tables. 2D tables allow you to take two input variables and map their values to an output.

First start by selecting your two input variables. The output value can be used for radiator fan PWM duty cycle %, for example. You can then select the range that these variables will fall within.

**Keyboard shortcuts:**
- SHIFT + Up/Down: Inc/Dec by 1
- SHIFT + Left/Right: Inc/Dec by 0.1
- CTRL + Arrow: Change Selection
- CTRL + L: Interpolate Vertically
- CTRL + H: Interpolate Horizontally
- CTRL + D: Interpolate 2D

Clicking the 3D button allows you to view the table in 3-Dimensions.

---

## CAN Keypads

Using CAN bus 1, the PDM can communicate with up to 4 individual CAN bus Keypads. The PDM is able to communicate with the following keypad devices:

- Blink Marine CANOpen 4-15 button keypads
- Grayhill CANOpen 6-20 button keypads
- Motec 6-20 button keypads
- Marlin Technology J1939 8 button keypad

Keypads are a great way to control the functionality of the Power Distribution System. The Keypad buttons can be used to control the state of multiple outputs, and the LED indicators on each button provide visual indicators to the user.

To install a Keypad into the system, make sure that the CAN bus lines are connected, and that the wiring is done in accordance with the instructions given in the CAN bus wiring section. It is important that the Keypads do not have the same ID. It is also important that all of the Keypads are configured to run at the same CAN bus speed.

### Keypad Configuration

To configure a Keypad, go to the CAN Keypad tab and select one of the four available Keypads to configure. Click the enable button to enable the keypad, and select the appropriate CAN bus which the Keypad is installed on.

Choose the keypad which is being used from the drop down menu. Choose the appropriate ID which the keypad is configured to. Make sure to observe that the Keypad ID is entered in the decimal format in the configuration software.

If the Keypad is to be powered by an output on the PDM, set up that output and enable it. Press 'Send' to send the configuration to the PDM.

**If the Keypad does not light up, check the following:**

- The CAN bus speed of the Keypad and PDM is identical
- The CAN bus is wired correctly in accordance with the recommendations given in the CAN bus wiring section
- The correct CAN bus is selected in the Keypad configuration
- The ID of the Keypad is the same as the ID in the Keypad configuration

### Keypad Button Configuration

Each Keypad Button can be given a label and be enabled. Click the 'Expand' Button to configure the operation of the Keypad Button.

The Mode of the button can be either Momentary, Latched, or States.

- **Momentary Mode:** The Keypad Button State will be True when the button is pressed, and False when it is not pressed.
- **Latched Mode:** The Keypad Button State will toggle between True and False each time the Button is pressed.
- **States Mode:** Each time the Button is pressed, the Button State will increment. The number of states can be set between 1 and 3. When the Button State reaches the limit, it will return back to 0.

**Hold To Reset** is used to reset the Button state back to 0 when the button is held for one second.

For each Button State, the Button Colour and functionality can be set. The first drop down menu selects which colour the Button will be in that state. The second drop down menu selects a variable which is used to say when the button is that colour.

The Keypad Dial setting is used with the Blink Marine PKP-3500-SI-MT Keypads which have two rotary encoder dials on them. Each dial can take a value of between 0-16. The LED Ring around the outside of the dial indicates what the dial value is. The Dial can have a minimum and maximum value.

### Pass Key

As a layer of security for the Power Distribution System, a Pass Key can be added to the Keypads. If the Pass Key is enabled, then the Keypads will not be operational until the correct sequence of Keypad Buttons has been pressed. This can stop unwanted users from potentially starting up a vehicle and driving it away.

---

## CAN Bus Basics

Controller Area Network (CAN) Bus is a communication protocol designed to allow different devices to communicate with each other in a robust manner. CAN bus covers both the physical wiring, and how the data is sent/received.

For a full detailed video explanation of the CAN Bus, check out the beginners guide available via the QR code in the printed manual.

---

## CAN Inputs

The PDM has one user accessible CAN bus port, which can be used to interface with other devices in the vehicle — such as ECUs, Digital Dashboards, Sensors, and more. Up to 100 individual CAN Inputs can be configured, spread across either CAN bus port.

The CAN bus on a vehicle can become heavily crowded with CAN messages from different devices on the bus. Configurable hardware filters are used in the PDM to decipher frames of interest so that the processor is not overloaded with processing unwanted CAN messages. These filters only allow CAN frames with specific IDs to pass through for the processor to deal with, others are discarded automatically.

### CAN Configuration Files

To store the configuration of the CAN inputs on the PDM, the configuration can be saved as a file. A CAN Configuration file can also be loaded into software if needed. The CAN Configuration files are specific to the Hardwire Electronics PDMs.

### DBC File Loader

.DBC Files are a standard used to specify how CAN messages are sent on a CAN bus. The configuration software allows one to load up a DBC file, and choose which signals are required. Press 'Import .DBC File', and select the DBC file which needs to be loaded. A new window will appear which shows all of the available signals in the DBC file. Once all the required signals have been selected, press Import. This will automatically configure the PDM CAN Filters and CAN Inputs.

### CAN Bus Filter Configuration

The PDM has 10 dedicated hardware based CAN Filters. Each Filter can filter either Standard or Extended ID CAN messages. The Filters have a Start and End CAN ID. CAN Messages with an ID within the Filter range pass through, and those that do not are discarded. Filters can be enabled and disabled by clicking the checkbox.

### CAN Input Configuration

To add a CAN Input, click the 'Add' Button. Up to 100 CAN Inputs can be added to the configuration. The CAN Input can be given a Label and a Unit. The CAN ID Format can be selected as either a Standard or Extended ID.

The aim of the CAN Input is to parse off the appropriate data from the payload bytes of the CAN message. A CAN Message can have up to 8 payload bytes.

#### Test Data

Test data has been added to the bottom of the configuration window to make configuring the CAN Inputs easier. The test data is simply 8 data bytes which mimic the data that would reach the CAN Input.

#### Message Filter

In addition to filtering the CAN messages by ID, the PDM can also further filter the CAN messages by data in the payload. This is useful when a device on the CAN bus uses compound or segmented CAN messages to send data. Usually, the first byte of the payload acts as a 'sub ID', and increments in value for each data type being sent.

#### Payload Size

A CAN message can have between 0 and 8 data bytes. The CAN Input payload size must exactly match the payload size of the CAN Input for the message to be received.

#### Data Format

- **Signed data:** can have negative values
- **Unsigned data:** positive only

The data can also have a different size, between 8 and 32 bits.

#### Bit Position

The Bit Position chooses the bit which the data is parsed from. Bit 0 is the least significant bit, and bit 7 is the most significant bit.

#### Bit Count

The Bit Count sets how many bits are parsed, starting from the Bit Position Value.

#### Endianness

Endianness describes the order that data bytes are sent for multiple byte variables.

- **Big Endian:** the most significant byte is sent first with the least significant byte after.
- **Little Endian:** the least significant byte is sent first with the most significant byte after.

#### Multiplier

The Multiplier takes the raw variable value and multiplies it with a constant. The Multiplier value can range from 0.0001 to 1000.

#### Offset

After the raw value has passed the multiplier step, an offset can be added. This can be used to adjust the value for calibration purposes.

#### Timeout

The Timeout value is how long the current CAN value is valid for in milliseconds. If it is known that data should be received every 0.5s, but no data is received for 1s, then it can be assumed that an error has occurred. The CAN variable value will then return to a default value.

#### Default Value

The Default Value is the initial value of the CAN Input on device start up, or when the timeout has occurred.

---

## CAN Outputs

The PDM has up to 100 individual user defined CAN Outputs. In addition to the user defined CAN Outputs, the user can enable the CAN Output stream, which sends preformatted data at a regular interval.

### CAN Stream

The CAN Stream data format can be found in the download section of the Hardwire Electronics Website. There is also a .DBC file which corresponds to the CAN Output stream. The CAN Stream can be enabled by clicking the enable checkbox.

### User CAN Outputs

A CAN Output can be added by clicking the 'Add' Button. A Label can then be given to that CAN Output. Click 'Expand' to further configure the CAN Output.

#### CAN Bus Selection

On the PDM15/25/35 this is restricted to CAN Bus 1.

#### CAN ID

The CAN Message ID format can then be selected as either Standard or Extended, and the value for the ID can be chosen.

#### Send Mode

CAN Outputs can either be sent periodically, or be sent on a trigger.

- **Periodic:** The CAN Output will send at the interval defined by Send Frequency.
- **Triggered:** The CAN Output will send every time the Trigger variable goes from False to True.

#### Payload

A CAN Message can have between 0 and 8 bytes. The Payload is filled with PDM Variables. An 8-bit value will take up 1 byte, a 16-bit value will take up 2 bytes, etc.

A Multiplier can be added to the data to be sent. This is used to preserve precision in the sent data.

---

## CAN Output Stream

In addition to the customisable CAN outputs, there is an option to enable the PDM CAN stream. The PDM CAN stream is a collection of PDM variables which have been placed in a user friendly format which can be exported as a DBC file and used by other devices on the bus. You can select the data you want to send out to minimize bus load. You can also vary the send rate of the data for the same effect. An offset can be applied to the CAN stream IDs if needed, to help avoid any CAN ID clashes.

---

## Data Logging

The PDM has 128Mb of on-board flash storage for logging data. This logged data can be downloaded and viewed on the PC to diagnose issues, and ensure that each electrical component in the vehicle is functioning correctly.

To enable data logging on the PDM, navigate to the Configuration tab and then to the Data logging tab. A Logging Group can be added by clicking the 'Add' Button. A Label can then be given to that Logging Group. Click 'Expand' to further configure the Logging Group.

Each Logging Group is responsible for data logging a collection of variables. These variables are logged at the Logging Speed, which can be changed between 1–20Hz. The variables are logged whenever the Logging Condition evaluates to True.

Logging more variables at higher speed will consume the data logging memory more quickly. Fast changing variables such as output currents and input voltages should be logged at higher speeds, whereas slow changing variables such as PCB temperature should be logged at low speeds. Each time the PDM is restarted, or a new configuration is sent, a new data log will start. Data logs are numbered in ascending order. When the data logging memory is full, the data log will start to overwrite the oldest data stored in memory.

---

## Monitoring

One of the distinct advantages of using a Solid State Power Distribution System over a conventional relay and fuse system, is that the exact state of the electrical system can be monitored and logged in real time – a necessity in high reliability, high performance applications.

### Graph View

One of the easiest ways to visualise the different variables is with a Live Graph. To add a graph, navigate to the Monitor Tab and to Graph View and click 'Add.' To add a variable to the graph, click on the drop-down menu and select an appropriate variable. Then press 'Add'.

Live data gathering from the PDM can be halted at any moment by pressing the 'Stop' button at the top of the graph window. With the live graphing of variables stopped, the buttons at the top of the graph may be used to zoom in/out, save images of the graph, or to export the graph as a .csv file for viewing on external software. The graph windows can be resized, docked, and tabbed by clicking and dragging on the top of the graphing window.

### Variable View

Navigate to the Variable View Tab. To make it easier to look at multiple collections of variables, one can add a variable 'Group.' Each group can be given a name. Click expand, and then add variables to the group in the drop down menu.

Variable Groups can be saved to a file to make it easier to get the collection of variables you want to look at as quickly as possible. Each individual variable can be given a different colour as the user wishes.

### CAN Bus Analyser

Being able to easily see what CAN bus messages are on the CAN bus is important when configuring a Power Distribution System. Hardwire Electronics have solved this problem by introducing a CAN Bus analyser feature into the software. To start the CAN Bus Analyser, navigate to the monitor tab and to CAN Bus analyser, then click start.

The CAN Bus Analyser removes all CAN Bus Filters on the PDM CAN Bus port, allowing all CAN messages to be received. The CAN Bus Analyser can run in:

- **Continuous View Mode:** CAN messages are received and shown in order.
- **Fixed View Mode:** Only the latest CAN Bus message with each unique ID is displayed.

CAN Bus messages can be sent onto the CAN Bus using the CAN Transmit options at the bottom.

When the CAN Bus Analyser is running, the data can be logged in real time to a CSV file.

---

## Logging

The Hardwire Electronics Configurator software can download data log files from a PDM and display the data in a graphical format. To retrieve data logs, connect to the PDM and navigate to the data logging tab. Click on the button 'Retrieve Log Info' to retrieve a list of the data logs stored on the PDM. To view a data log, select the data log and then click the button 'Load Log.' This will start the process of downloading the data log from the PDM.

To view the data log, click on the button 'Add Graph' to add a new graph into the window. Select a data log from the list. Now select the variables from the data log which you wish to view. The graph can be scaled by adjusting the Y-Min and Y-Max values.

To export the data log, click on the export button. This will allow you to save the data log as a .csv file, which can then be loaded into alternative datalogging or spreadsheet software.

Multiple data logs can be loaded into the configurator software and be viewed on multiple graphs.

---

## Firmware Updates

Software updates allow the user to take advantage of the newest features available for the PDM. To update the firmware on either device, make sure that the PDM is connected to the PC, and that the Power Module is communicating with the PDM.

### PDM Firmware Update

To update the PDM firmware, click the 'Select File' button. Click on the appropriate .bin file PDM Firmware. Click the 'Update' Button to commence the update process. The green bar will start to move to indicate that the update is taking place. Once the update is complete, the PDM will restart and attempt to reconnect to the PC to resume normal operation.

If the firmware update fails, you will see the power indicator on the PDM turn red. Restart the PDM and the configuration software, connect via USB again and then restart the firmware update.

---

## Examples

This section aims to provide a number of examples of how the PDM can be set up. The examples assume that you have a PDM connected and working properly.

### 1. Basic Input Setup

This example shows a basic setup for a PDM Input, so that the input triggers when 12V is applied.

- Mode: Momentary
- Active Level: Active High
- Threshold Voltage: 6.0V
- Hysteresis Voltage: 1.0V
- Turn On Delay: 0.0s

### 2. ECU Triggered Input

This example demonstrates the typical procedure to have an ECU output trigger a PDM input. Most ECU outputs are low-sided, meaning that they switch ground onto the output. When the output is not triggered, this leaves the output 'floating', meaning that the voltage on the output is undefined. If this is tied to a PDM input, the voltage measurement in this case will settle to around 1.5–2V due to the internal biasing resistors inside the PDM.

The PDM Input is configured to be active low, so that when the ECU output is driven to ground, the input on the PDM triggers. The Threshold Voltage is set to 1V. The Hysteresis voltage is set to 0.2V.

### 3. Latching Input Setup

This example shows a set up for an input configured in Latching Mode. In Latching Mode, the input status toggles every time the input is triggered. In this case, the threshold voltage is set to 6V and the input is set to active high, so each time the voltage rises above 6V, the input toggles state. This setup is useful for latching an input on when pressing a momentary button switch.

### 4. Basic Output Setup

This example will show how to set up a simple output that turns on when a button on a CAN bus Keypad is pressed. This example is based on the configuration of a typical Radiator Fan with the following parameters:

| Parameter             | Value |
|-----------------------|-------|
| Nominal Current Draw  | 17A   |
| Start Up Current Peak | 36A   |

The current draw of the motor quickly rises to a peak of 36A, before gradually falling to 17A.

**Suggested configuration:**

- Trip Mode: Normal
- Low Fuse: 0.0A
- High Fuse: 20.0A
- Peak Fuse: 40.0A
- Peak Fuse Time: 4.0s
- Stay On Time: 0.0s
- Clear Time: 0.0s
- Retries: 2

The Peak Fuse is set to 40A which is 4A above the peak current draw of the Fan to allow some room for error. The High Fuse has been set to 20A which is 3A above the nominal current draw. The Peak Fuse Time has been set to 4 seconds to allow time for the current draw to come down to below the High Fuse threshold.

> **Note:** When setting up an output, it may take some time to tune these values. Effects such as temperature and component age/condition can all affect the current draw. It is therefore necessary to add approximately 10–20% margin on the current trip limits.

### Indicator/Turn Signal Setup

To set up left and right Indicators with Hazard light functionality:

1. First add a timer to the configuration and set the On and Off time to 400ms.
2. Configure the CAN Bus Keypad or Inputs so that the Indicator Button and Hazard Button both latch on when the button is pressed.
3. The Output for the Indicator can then be configured.

Timer 1 simply alternates between the On and Off state every 400ms. The status of the Timer can be AND'd with the status of the Indicator button. When both the Timer and Button status is true, the output will be on, and when either or both are false, the output will be off.

### PWM Fan Control Setup

In this example, an output has been configured to control a radiator fan using PWM. The output function is set so that the output will turn on if either CAN Keypad 1 Button 1 Status is equal to true, or if the coolant temperature (received via CAN) is above 80 degrees C.

The PWM mapping variable is set to be the CAN Input Coolant Temperature Value. The higher the coolant temperature, the higher the duty cycle, and hence speed, of the fan.

### Video Examples

Hardwire Electronics has a number of educational videos on their YouTube Channel. Scan the QR code in the printed manual to access them.

---

*www.hardwire-electronics.co.uk*
*PDM15/25/35 Instruction Manual v.1*
