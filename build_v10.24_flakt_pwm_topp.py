"""v10.24 — fläktens hastighetsstyrning: 100 % fungerar.

Källa: v10.23 (PWM på, mjukstart av, 100 Hz, hög 8 A) — flashad 2026-09-29 kväll.

UPPMÄTT med v10.23 (hastighet stegad via elton/control/blower/speed):
  från stilla -> 100 : 0,10 A (motorn står, status 1)
  från stilla ->  50 : 3,03 A      från stilla -> 30 : 1,66 A
  30 -> 100          : 1,56 A (= kvar på 30 %)
  70 -> 100          : 3,58 A (≈ kvar på 70 %)
  => Vid styrvärde exakt 100 behåller PDM:en föregående duty. Tabellens sista punkt
     (PWMMap100) är 100, och ett värde LIKA MED sista punkten hamnar i inget intervall
     (ändpunkten nås aldrig). Från stilla = 0 % -> 0,1 A. Det förklarar också v10.4–v10.20:
     appen skickade 100 hela tiden, fläkten startade aldrig. Mjukstarten var troligen oskyldig.

ÅTGÄRD (bara O11)
  PWMMapping [0,10,...,90,100] -> [0,10,...,90,101]
  Styrvärde 100 hamnar nu i sista intervallet: 90 + 10·(100−90)/(101−90) ≈ 99 % duty.
  Monotont stigande — uppfyller configOutputs.js validatePWMMapping.

    python build_v10.24_flakt_pwm_topp.py            # torrkörning
    python build_v10.24_flakt_pwm_topp.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.23_flakt_pwm_test.HWPDM'
DST = r'Builds\Elton_v10.24_flakt_pwm_topp.HWPDM'
NEW_MAP = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 101]


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.24 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    B.VarMap(cfg).selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')
    o = cfg['OutputHS'][10]
    assert o['label'] == 'BLOWER' and o['PWMMappingEnable'] is True
    assert [int(x) for x in o['PWMMapping']] == list(range(0, 101, 10))
    t = type(o['PWMMapping'][0])
    old = list(o['PWMMapping'])
    o['PWMMapping'] = [t(x) for x in NEW_MAP]
    print(f'  O11 PWMMapping {old} -> {o["PWMMapping"]}')
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('O11 tabell slutar på 101', lambda c: [float(x) for x in c['OutputHS'][10]['PWMMapping']] == NEW_MAP),
        ('tabellen monotont stigande', lambda c: all(a < b for a, b in zip(NEW_MAP, NEW_MAP[1:]))),
        ('O11 i övrigt som v10.23', lambda c: c['OutputHS'][10]['PWMMappingEnable'] is True
         and c['OutputHS'][10]['PWMSoftStartEnable'] is False and float(c['OutputHS'][10]['highFuse']) == 8),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
