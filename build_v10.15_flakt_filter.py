"""v10.15 — fläkten från appen: CAN-filtret släpper nu in 0x503.

Källa: v10.14 (det som ligger i PDM:en).

FELET (hittat 2026-09-29)
  Pi:n skickar 0x503 = 03 64 .. (Blower_Cmd=1, Pi_Active=1, duty 100 %) med 10 Hz,
  men O11 BLOWER står på status 0. Övriga villkor i O11:s logik är bevisat sanna:
  GF1 (O3/O5 på), GF9 (strålkastarna kommenderas), T2==False (O12 på).
  Kvar blev BLW_CMD — och PDM:ens hårdvarufilter för CAN (`CANInputFilter` F1)
  täcker bara 0x500–0x502. Ramen 0x503 slängs innan CAN-ingångarna ser den, så
  BLW_CMD och BLW_DUTY har stått på default 0 sedan v10.4. GUI:t räknar bara om
  filtren på knapptryck ("optimera"), inte vid spara/flash.

ÅTGÄRD
  F1: 0x500–0x502 -> 0x500–0x503. Inget annat.
  build_lib.uncovered_can_inputs() kontrollerar nu att varje aktiv CAN-ingång täcks.

    python build_v10.15_flakt_filter.py            # torrkörning
    python build_v10.15_flakt_filter.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.14_tandning_retry.HWPDM'
DST = r'Builds\Elton_v10.15_flakt_filter.HWPDM'
NEW_END = 0x503


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.15 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    B.VarMap(cfg).selftest()
    L.roundtrip_check(cfg)

    before = B.uncovered_can_inputs(cfg)
    print(f'\n  Otäckta CAN-ingångar före: {[(n, lab, hex(i)) for n, lab, i in before]}')
    assert {i for *_, i in before} == {NEW_END}, 'väntade att bara 0x503 saknades'

    print('\n=== Ändringar ===')
    f1 = cfg['CANInputFilter'][0]
    assert f1['enabled'] and int(f1['CANIDStart']) == 0x500 and int(f1['CANIDEnd']) == 0x502, f1
    B.set_field(f1, 'CANIDEnd', NEW_END)
    print(f'  CANInputFilter F1: 0x{int(f1["CANIDStart"]):03X}–0x{int(f1["CANIDEnd"]):03X} '
          f'(format {f1["format"]}, standard-ID)')
    after = B.uncovered_can_inputs(cfg)
    print(f'  Otäckta CAN-ingångar efter: {after}')

    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('alla aktiva CAN-ingångar täcks av ett filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('F1 = 0x500–0x503', lambda c: (int(c['CANInputFilter'][0]['CANIDStart']),
                                        int(c['CANInputFilter'][0]['CANIDEnd'])) == (0x500, 0x503)),
        ('inga andra filter aktiva', lambda c: sum(1 for f in c['CANInputFilter'] if f['enabled']) == 1),
        ('v10.14 orört: O3 clearTime 0,1 / retries 10, 0x520',
         lambda c: str(c['OutputHS'][2]['clearTime']) == '0.1'
         and int(float(c['OutputHS'][2]['retries'])) == 10
         and c['CANOutput'][16]['label'] == 'PDM_EngineDiag'),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
