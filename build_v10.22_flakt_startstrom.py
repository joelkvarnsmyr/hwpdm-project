"""v10.22 — fläkten tål motorns startström.

Källa: v10.21. Flasha bara denna.

UPPMÄTT 2026-09-29 kväll (v10.21, PWM och mjukstart av, full spänning):
  O11 BLOWER -> status 2 (Trip överström) direkt vid tillslag, 0 A, retries (2) slut.
  En borstmotor drar kortvarigt flera gånger driftströmmen (stillastående rotor).
  Toppsäkringen var 16 A. Mjukstarten som skulle begränsa startströmmen gav i stället
  0,1 A i v10.4–v10.20 — den utreds i morgon ihop med PWM.

ÅTGÄRD (bara O11)
  peakFuse      16  -> 40 A   (PDM25 standardutgång tål 80 A topp)
  peakFuseTime   5  -> 1 s    (startströmmen är över på några tiondelar)
  highFuse       9  -> 12 A   (under kontaktens 13 A)
  retries        2  -> 3

    python build_v10.22_flakt_startstrom.py            # torrkörning
    python build_v10.22_flakt_startstrom.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.21_flakt_pa_av.HWPDM'
DST = r'Builds\Elton_v10.22_flakt_startstrom.HWPDM'
NEW = {'peakFuse': 40, 'peakFuseTime': 1, 'highFuse': 12, 'retries': 3}


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.22 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    B.VarMap(cfg).selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')
    o = cfg['OutputHS'][10]
    assert o['label'] == 'BLOWER' and o['PWMMappingEnable'] is False
    for k, val in NEW.items():
        old = o[k]
        B.set_field(o, k, val)
        print(f'  O11 {k}: {old} -> {o[k]}')
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('O11 säkringar', lambda c: all(float(c['OutputHS'][10][k]) == val for k, val in NEW.items())),
        ('O11 fortfarande utan PWM/mjukstart', lambda c: c['OutputHS'][10]['PWMMappingEnable'] is False
         and c['OutputHS'][10]['PWMSoftStartEnable'] is False),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
