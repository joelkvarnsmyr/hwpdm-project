"""Build Elton_v9.57_lowbeam_fix.HWPDM from v9.56.

BUGFIX ONLY — no logic changes.

Problem:
  In build files v9.53-v9.56 the two low-beam outputs were left disabled:
    O14 LOWBEAM_L  enabled=False
    O15 LOWBEAM_R  enabled=False
  Joel enabled them by hand in the GUI to drive on live, but every freshly
  *built* file would silently turn the headlights off again on the next flash.

Fix:
  Set O14 (idx 13) and O15 (idx 14) enabled=True so the built artifact matches
  the live, validated vehicle state. Nothing else is touched.

NOTE on dual-horn DBC import:
  The on-disk v9.56 file does NOT yet contain the DBC v1.1 CAN inputs
  (CI28 Horn_1_Pulse / CI29 Horn_2_Pulse) — those are populated when you import
  elton_pi_control_v1.1.dbc in the GUI. v9.57 inherits that same state, so after
  loading v9.57 you must STILL import the DBC v1.1 (Overwrite UNCHECKED) before
  the individual-horn signals resolve. The dual-horn output LOGIC (O13/O17
  functions) is already baked into the file from v9.56 and is preserved here.

WORKFLOW (user-side):
  1. Open Elton_v9.57_lowbeam_fix.HWPDM in PDM software
  2. Import elton_pi_control_v1.1.dbc  (Overwrite Existing CAN Input Data UNCHECKED)
  3. Verify O13 HORN_1 / O17 HORN_2 show CAN Input 28 / 29
  4. Verify O14 LOWBEAM_L and O15 LOWBEAM_R are ENABLED (green)
  5. Save and flash.
"""
import json
import shutil

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.56_dual_horn.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.57_lowbeam_fix.HWPDM'


def main():
    shutil.copy(SRC, DST)
    d = json.load(open(SRC))

    print('=== v9.57 LOWBEAM enable fix ===')
    o14 = d['OutputHS'][13]
    o15 = d['OutputHS'][14]
    print(f'  before: O14 {o14["label"]!r} enabled={o14["enabled"]} | '
          f'O15 {o15["label"]!r} enabled={o15["enabled"]}')

    # sanity: make sure we are flipping the right outputs
    assert o14['label'] == 'LOWBEAM_L', f'idx13 is {o14["label"]!r}, expected LOWBEAM_L'
    assert o15['label'] == 'LOWBEAM_R', f'idx14 is {o15["label"]!r}, expected LOWBEAM_R'

    o14['enabled'] = True
    o15['enabled'] = True
    print(f'  after:  O14 {o14["label"]!r} enabled={o14["enabled"]} | '
          f'O15 {o15["label"]!r} enabled={o15["enabled"]}')

    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))
    print(f'\nWritten: {DST}')

    # Verification
    print('\n=== Verification ===')
    d2 = json.load(open(DST))
    checks = [
        ('O14 LOWBEAM_L enabled', d2['OutputHS'][13]['enabled'] is True),
        ('O15 LOWBEAM_R enabled', d2['OutputHS'][14]['enabled'] is True),
        ('O7 HIBEAM_R still enabled', d2['OutputHS'][6]['enabled'] is True),
        ('O16 HIBEAM_L still enabled', d2['OutputHS'][15]['enabled'] is True),
        # dual-horn logic from v9.56 preserved
        ('O13 label = HORN_1', d2['OutputHS'][12]['label'] == 'HORN_1'),
        ('O17 HORN_2 enabled', d2['OutputHS'][16]['enabled'] is True),
        ('GF8 HORN_MASTER preserved', d2['GenericFunction'][7]['label'] == 'HORN_MASTER'),
    ]
    ok = True
    for name, res in checks:
        print(f'  [{"OK" if res else "FAIL"}] {name}')
        ok = ok and res
    print(f'\n{"ALL CHECKS PASSED" if ok else "*** CHECKS FAILED ***"}')


if __name__ == '__main__':
    main()
