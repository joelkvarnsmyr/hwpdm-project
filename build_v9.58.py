"""Build Elton_v9.58_washer_enables.HWPDM from v9.57.

Two changes, both decided by Joel 2026-06-11:

1. ENABLED-DRIFT FIX — bake the live GUI state into the file:
     O5  FUEL       enabled=True   (was hand-enabled in GUI after every flash)
     O8  WIPER_FST  enabled=True
     O11 BLOWER     enabled=True
     O19 REVERSE    enabled=True
   (O10 WIPER_SLO was already True in file.)

2. WASHER RESCUE — the washer stalk lost its input when I8 became FUEL_LEVEL
   (v9.55). Joel wants the washer kept, on a new pin:
     I16 (pin C1) — free since v9.21 (PWR moved to ignition lock; ignition is
     sensed physically via C3, confirmed ignition-switched by Joel 2026-06-11).
     I16 gets v9.4-era I8 WASHER settings: momentary, active-low (switch-to-
     GND), pull resistor "2", threshold 1V / hyst 0.2V, EMA 0.01.
     O12 WASHER: enabled=True, function var 597 (I8) -> 637 (I16). The rest of
     the O12 logic (incl. var 641 / Timer1 BLINK_TMR term) is unchanged from
     the v9.4 config that ran on the car.

NOT changed (flagged for Joel instead):
   Timer2 CRASH_TMR and Timer3 START_GRACE are enabled=False in v9.53-v9.57
   but were True in v9.4. Possibly more GUI-drift, possibly intentional —
   do not silently re-enable safety logic from a script.

NOTE: rawSendData in the output file stays stale (harmless — the configurator
ignores it on load and rebuilds on send/save; see HWPDM_FORMAT_REVERSE_
ENGINEERING.md, verified 2026-06-11). Opening + saving in the GUI heals it.

WORKFLOW (user-side):
  1. Open Elton_v9.58_washer_enables.HWPDM in PDM software
  2. Import elton_pi_control_v1.1.dbc (Overwrite Existing CAN Input Data UNCHECKED)
  3. Verify O14/O15 LOWBEAM enabled, O5/O8/O11/O19 enabled, I16=WASHER, O12 enabled
  4. Save (this regenerates rawSendData) and flash.
  5. Physical: washer stalk wire moves to pin C1 (I16).
"""
import json

I16_VAR = 637   # 562 + 15*5
I8_VAR = 597    # 562 + 7*5

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.57_lowbeam_fix.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.58_washer_enables.HWPDM'


def replace_var(node, old, new):
    """Recursively replace variable id old->new in nested function arrays.
    Handles both string and numeric encodings. Returns replacement count."""
    n = 0
    if isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, list):
                n += replace_var(v, old, new)
            elif v == old or v == str(old):
                node[i] = str(new) if isinstance(v, str) else new
                n += 1
    return n


def main():
    d = json.load(open(SRC))

    print('=== v9.58: enabled-drift fix + washer rescue ===\n')

    # --- 1. enabled-drift ---
    for idx, want_label in [(4, 'FUEL'), (7, 'WIPER_FST'), (10, 'BLOWER'), (18, 'REVERSE')]:
        o = d['OutputHS'][idx]
        assert o['label'] == want_label, f'idx{idx} is {o["label"]!r}, expected {want_label!r}'
        print(f'  O{idx+1:<2} {o["label"]:<10} enabled {o["enabled"]} -> True')
        o['enabled'] = True

    # --- 2. washer rescue ---
    i16 = d['Input'][15]
    assert i16['label'] == 'RESERVE16', f'I16 is {i16["label"]!r}, expected RESERVE16'
    i16.update({
        'label': 'WASHER',
        'enabled': True,
        'mode': '0',              # momentary
        'activeLevel': '1',       # active low (switch-to-GND, same as other stalk inputs)
        'pullResistor': '2',      # same as v9.4 I8 WASHER
        'thresholdVoltage': '1',
        'hysteresisVoltage': '0.2',
        'EMAValue': '0.01',
        'EMAEnabled': False,
        'turnOnDelay': '0',
    })
    print(f'  I16 RESERVE16 -> WASHER (momentary, active-low, pull "2")')

    o12 = d['OutputHS'][11]
    assert o12['label'] == 'WASHER', f'idx11 is {o12["label"]!r}, expected WASHER'
    n_f = replace_var(o12['function'], I8_VAR, I16_VAR)
    n_i = replace_var(o12['functionInfix'], I8_VAR, I16_VAR)
    assert n_f == 1, f'expected 1 var replacement in O12.function, got {n_f}'
    assert n_i == 1, f'expected 1 var replacement in O12.functionInfix, got {n_i}'
    o12['enabled'] = True
    print(f'  O12 WASHER enabled=True, function var {I8_VAR} (I8) -> {I16_VAR} (I16)')

    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))
    print(f'\nWritten: {DST}')

    # --- verification ---
    print('\n=== Verification ===')
    d2 = json.load(open(DST))
    o12v = d2['OutputHS'][11]
    flat = json.dumps(o12v['function']) + json.dumps(o12v['functionInfix'])
    checks = [
        ('O5 FUEL enabled', d2['OutputHS'][4]['enabled'] is True),
        ('O8 WIPER_FST enabled', d2['OutputHS'][7]['enabled'] is True),
        ('O10 WIPER_SLO still enabled', d2['OutputHS'][9]['enabled'] is True),
        ('O11 BLOWER enabled', d2['OutputHS'][10]['enabled'] is True),
        ('O19 REVERSE enabled', d2['OutputHS'][18]['enabled'] is True),
        ('I16 label = WASHER', d2['Input'][15]['label'] == 'WASHER'),
        ('I16 enabled + active-low', d2['Input'][15]['enabled'] is True and d2['Input'][15]['activeLevel'] == '1'),
        ('O12 WASHER enabled', o12v['enabled'] is True),
        ('O12 references I16 (637), not I8 (597)', '637' in flat and '597' not in flat),
        ('O12 Timer1 term (641) preserved', '641' in flat),
        # regression guards — v9.57 fix and dual horn untouched
        ('O14 LOWBEAM_L still enabled', d2['OutputHS'][13]['enabled'] is True),
        ('O15 LOWBEAM_R still enabled', d2['OutputHS'][14]['enabled'] is True),
        ('O13 HORN_1 / O17 HORN_2 intact', d2['OutputHS'][12]['label'] == 'HORN_1' and d2['OutputHS'][16]['label'] == 'HORN_2'),
        ('GF8 HORN_MASTER preserved', d2['GenericFunction'][7]['label'] == 'HORN_MASTER'),
        ('I8 FUEL_LEVEL untouched', d2['Input'][7]['label'] == 'FUEL_LEVEL'),
    ]
    ok = True
    for name, res in checks:
        print(f'  [{"OK" if res else "FAIL"}] {name}')
        ok = ok and res
    print(f'\n{"ALL CHECKS PASSED" if ok else "*** CHECKS FAILED ***"}')
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
