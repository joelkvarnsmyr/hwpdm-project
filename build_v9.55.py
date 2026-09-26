"""Build Elton_v9.55_fuel_temp_fixes.HWPDM from v9.54.

Changes:
  1. SC1 COOLANT_T variable bugfix: 610 -> 605
     (was pointing to I11 Voltage; should be I10 Voltage where COOLANT_TEMP lives)

  2. I8 WASHER -> FUEL_LEVEL
     - label change
     - enabled: False -> True
     - mode: 0 (digital) -> 2 (analog)
     - EMAValue: 0.05 (smooth out flotation noise)
     - pullResistor: 0 (external 150Ω pull-up needed)

  3. SC2 FUEL_LVL variable update: 620 -> 595 (point to I8 Voltage)

  4. SC2 calibration: standard VW sender response (180Ω empty -> 10Ω full)
     with 150Ω pull-up + 5V supply, inverted: low V = high level

  5. O12 WASHER stays disabled — user can wire washer pump direct or
     reassign to another output later.

Sender wiring assumed:
  PDM 5V (pin C10) ──[150Ω pullup]──┬── PDM I8 input
                                      │
                                      │
                                  VW sender (180Ω empty ... 10Ω full)
                                      │
                                    ⏚ (sender body to tank/chassis)

Voltage at I8:
  Empty (180Ω): V = 5 * 180/(150+180) = 2.727V → 2727 mV
  Half  (~95Ω): V = 5 *  95/(150+ 95) = 1.939V → 1939 mV
  Full  ( 10Ω): V = 5 *  10/(150+ 10) = 0.313V →  313 mV

Tank size assumed: 80L (refine later when known).
SC2 calibratedSensorDataPoint unit: milliliters (so 80000 = 80L).
"""
import json
import shutil

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.54_pwm_enable.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.55_fuel_temp_fixes.HWPDM'

# Tank assumed 80L; modify if user confirms different
TANK_SIZE_ML = 80000


def build_fuel_calibration(tank_size_ml: int = TANK_SIZE_ML):
    """Standard VW sender, 150Ω pull-up, 5V supply.

    Returns (rawSensorDataPoint_mV, calibratedSensorDataPoint_mL).
    rawSensorDataPoint must be monotonically INCREASING (PDM lookup requirement).
    calibratedSensorDataPoint decreases since higher voltage = lower fuel.
    """
    # 20 evenly spaced raw voltage points from 300 to 2750 mV
    raw_lo, raw_hi = 300, 2750
    n_points = 20
    raw = [int(round(raw_lo + (raw_hi - raw_lo) * i / (n_points - 1)))
           for i in range(n_points)]

    # Calibrated: high voltage maps to empty (0), low voltage to full (tank_size)
    # So calibrated[i] = tank_size * (1 - i/(n-1))
    calibrated = [int(round(tank_size_ml * (1 - i / (n_points - 1))))
                  for i in range(n_points)]

    return raw, calibrated


def main():
    shutil.copy(SRC, DST)
    d = json.load(open(DST))

    print('=== 1. SC1 COOLANT_T variable bugfix ===')
    sc1 = d['SensorCalibration'][0]
    print(f"  Before: SC1.variable={sc1['variable']} (was pointing to I11 — wrong)")
    sc1['variable'] = 605  # I10 Voltage
    print(f"  After:  SC1.variable={sc1['variable']} (now I10 Voltage where COOLANT_TEMP lives)")

    print()
    print('=== 2. I8 WASHER -> FUEL_LEVEL ===')
    i8 = d['Input'][7]
    print(f"  Before: label={i8['label']!r} enabled={i8['enabled']} mode={i8['mode']}")
    i8['label'] = 'FUEL_LEVEL'
    i8['enabled'] = True
    i8['mode'] = 2  # analog
    i8['EMAValue'] = 0.05
    i8['EMAEnabled'] = 1
    i8['pullResistor'] = 0  # external pull-up
    i8['thresholdVoltage'] = 1  # not used in analog mode but set sensible value
    i8['hysteresisVoltage'] = 0.1
    i8['activeLevel'] = 0
    print(f"  After:  label={i8['label']!r} enabled={i8['enabled']} mode={i8['mode']} EMA={i8['EMAValue']}")

    print()
    print('=== 3. SC2 FUEL_LVL variable update ===')
    sc2 = d['SensorCalibration'][1]
    print(f"  Before: SC2.variable={sc2['variable']} (was pointing to I13 — wrong)")
    sc2['variable'] = 595  # I8 Voltage
    print(f"  After:  SC2.variable={sc2['variable']} (now I8 Voltage)")

    print()
    print('=== 4. SC2 calibration update (inverted for VW sender) ===')
    raw, calibrated = build_fuel_calibration(TANK_SIZE_ML)
    sc2['rawSensorDataPoint'] = raw
    sc2['calibratedSensorDataPoint'] = calibrated
    print(f"  Tank size: {TANK_SIZE_ML} mL ({TANK_SIZE_ML/1000} L)")
    print(f"  Raw points (mV):       {raw[:3]}...{raw[-3:]}")
    print(f"  Calibrated (mL):       {calibrated[:3]}...{calibrated[-3:]}")
    print(f"  Empty ({raw[-1]} mV) -> {calibrated[-1]} mL")
    print(f"  Full  ({raw[0]} mV) -> {calibrated[0]} mL ({calibrated[0]/1000} L)")

    print()
    print('=== 5. Save ===')
    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))
    print(f"  Written: {DST}")

    print()
    print('=== Verification ===')
    d2 = json.load(open(DST))
    sc1 = d2['SensorCalibration'][0]
    sc2 = d2['SensorCalibration'][1]
    i8 = d2['Input'][7]
    checks = [
        ('SC1.variable=605', sc1['variable'] == 605),
        ('SC2.variable=595', sc2['variable'] == 595),
        (f'I8.label=FUEL_LEVEL', i8['label'] == 'FUEL_LEVEL'),
        (f'I8.enabled=True', i8['enabled'] is True),
        (f'I8.mode=2 (analog)', i8['mode'] == 2),
        ('SC2 raw monotonic', all(sc2['rawSensorDataPoint'][i] < sc2['rawSensorDataPoint'][i+1] for i in range(len(sc2['rawSensorDataPoint'])-1))),
        ('SC2 calibrated decreasing', all(sc2['calibratedSensorDataPoint'][i] > sc2['calibratedSensorDataPoint'][i+1] for i in range(len(sc2['calibratedSensorDataPoint'])-1))),
    ]
    for label, ok in checks:
        print(f"  {'OK' if ok else 'FAIL'}: {label}")

    # File size sanity
    import os
    pre_size = os.path.getsize(SRC)
    post_size = os.path.getsize(DST)
    print(f"  Size: pre={pre_size}, post={post_size}, delta={post_size-pre_size}")


if __name__ == '__main__':
    main()
