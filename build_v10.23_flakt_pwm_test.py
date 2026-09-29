"""v10.23 — fläktens hastighetsstyrning, test 1: PWM på, mjukstart av, 100 Hz.

Källa: Builds/Elton_v10.21_flakt_pa_av_fusefix.HWPDM — JOELS fil, det som ligger i
PDM:en (O11 hög 15 A, topp 20 A / 5 s; fläkten går på/av, 4,3 A).

VAD VI VET
  - v10.4–v10.20: PWM-mappning PÅ + mjukstart PÅ (1000 ms) + 200 Hz -> 0,1 A, stod still.
  - v10.21 + Joels säkringar: PWM AV, mjukstart AV -> går, 4,3 A.
  - Tabellen är rätt: configOutputs.js validatePWMMapping/calculatePWMMappingDirection —
    PWMMap{duty} = styrvariabelns värde där den duty:n nås. [0,10..100] + BLW_DUTY 100 = 100 %.
  - v9.4 (sista helt verifierade bygget) körde fläkten med PWM-mappning på 100 Hz.
  Kvar som misstänkta: mjukstarten, eller 200 Hz.

TEST 1 (detta bygge, bara O11)
  PWMMappingEnable   False -> True   (BLW_DUTY, tabell [0,10..100] — oförändrad)
  PWMSoftStartEnable False (oförändrad — mjukstarten hålls borta)
  PWMFrequency       200 -> 100 Hz   (som v9.4)
  highFuse           15 -> 8 A       (fläkten drar 4,3 A; 15 A låg över kontaktens 13 A)
  Topp 20 A / 5 s (Joels) räcker för startströmmen — orört.
  Utfall: följer strömmen appens hastighet -> PWM fungerar, mjukstarten var boven.
          0,1 A igen -> felet sitter i PWM-vägen/variabeln, test 2 delar upp det.

    python build_v10.23_flakt_pwm_test.py            # torrkörning
    python build_v10.23_flakt_pwm_test.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.21_flakt_pa_av_fusefix.HWPDM'
DST = r'Builds\Elton_v10.23_flakt_pwm_test.HWPDM'


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.23 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    B.drop_derived(cfg)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')
    o = cfg['OutputHS'][10]
    assert o['label'] == 'BLOWER' and o['PWMMappingEnable'] is False and float(o['highFuse']) == 15
    assert [int(x) for x in o['PWMMapping']] == list(range(0, 101, 10))
    assert str(o['PWMMappingVariable']) == str(v.caninput(29))
    o['PWMMappingEnable'] = True
    o['PWMSoftStartEnable'] = False
    B.set_field(o, 'PWMFrequency', 100)
    B.set_field(o, 'highFuse', 8)
    print(f'  O11 BLOWER: PWM-mappning på (BLW_DUTY var {o["PWMMappingVariable"]}), mjukstart av, '
          f'{o["PWMFrequency"]} Hz, hög {o["highFuse"]} A, topp {o["peakFuse"]} A / {o["peakFuseTime"]} s')

    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('O11 PWM på, mjukstart av, 100 Hz, hög 8 A', lambda c: c['OutputHS'][10]['PWMMappingEnable'] is True
         and c['OutputHS'][10]['PWMSoftStartEnable'] is False
         and float(c['OutputHS'][10]['PWMFrequency']) == 100 and float(c['OutputHS'][10]['highFuse']) == 8),
        ('Joels topp 20 A / 5 s kvar', lambda c: float(c['OutputHS'][10]['peakFuse']) == 20
         and float(c['OutputHS'][10]['peakFuseTime']) == 5),
        ('v10.20 orört: O2 på, I13 på, TACH', lambda c: c['OutputHS'][1]['enabled'] is True
         and c['Input'][12]['enabled'] is True and c['Input'][6]['label'] == 'TACH'),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
