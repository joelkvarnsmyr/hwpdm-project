"""Build Elton_v9.59_radio_removed.HWPDM from v9.58.

Joel 2026-06-12: the radio is fed from the battery busbar directly (always-on,
not through the PDM which powers down). O20 RADIO_ACC is therefore obsolete:
    O20 (pin D11): label RADIO_ACC -> RESERVE20, enabled True -> False.
Nothing else is touched.

(Timer2 CRASH_TMR / Timer3 START_GRACE question from v9.58 is still OPEN —
not addressed here, awaiting Joel's check against the live GUI.)
"""
import json

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.58_washer_enables.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.59_radio_removed.HWPDM'


def main():
    d = json.load(open(SRC))

    o20 = d['OutputHS'][19]
    assert o20['label'] == 'RADIO_ACC', f'idx19 is {o20["label"]!r}, expected RADIO_ACC'
    print(f'  O20 before: label={o20["label"]!r} enabled={o20["enabled"]}')
    o20['label'] = 'RESERVE20'
    o20['enabled'] = False
    print(f'  O20 after:  label={o20["label"]!r} enabled={o20["enabled"]}')

    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))
    print(f'\nWritten: {DST}')

    print('\n=== Verification ===')
    d2 = json.load(open(DST))
    checks = [
        ('O20 = RESERVE20 disabled', d2['OutputHS'][19]['label'] == 'RESERVE20' and d2['OutputHS'][19]['enabled'] is False),
        # regression guards — v9.58 state untouched
        ('O5 FUEL enabled', d2['OutputHS'][4]['enabled'] is True),
        ('O8 WIPER_FST enabled', d2['OutputHS'][7]['enabled'] is True),
        ('O11 BLOWER enabled', d2['OutputHS'][10]['enabled'] is True),
        ('O19 REVERSE enabled', d2['OutputHS'][18]['enabled'] is True),
        ('O14/O15 LOWBEAM enabled', d2['OutputHS'][13]['enabled'] is True and d2['OutputHS'][14]['enabled'] is True),
        ('I16 WASHER intact', d2['Input'][15]['label'] == 'WASHER'),
        ('O12 WASHER enabled', d2['OutputHS'][11]['enabled'] is True),
        ('O13/O17 dual horn intact', d2['OutputHS'][12]['label'] == 'HORN_1' and d2['OutputHS'][16]['label'] == 'HORN_2'),
    ]
    ok = True
    for name, res in checks:
        print(f'  [{"OK" if res else "FAIL"}] {name}')
        ok = ok and res
    print(f'\n{"ALL CHECKS PASSED" if ok else "*** CHECKS FAILED ***"}')
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
