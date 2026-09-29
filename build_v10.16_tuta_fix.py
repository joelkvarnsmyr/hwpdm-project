"""v10.16 — kompressortutans 0,5 s-gräns var 50 ms.

Källa: v10.15 (det som ligger i PDM:en).

FELET (mitt, från v10.2)
  O17 HORN_2 kräver Timer5 HORN_HOLD > 500 ms. Jag lagrade konstanten som 500.
  Men logikeditorn lagrar konstanter ×10 och visar dem /10:
    configOutputFunction.js:511  functionLine.push(Constant.value*10)
    configOutputFunction.js:472  Constant.setValue(functionLine[5]/10)
  Bekräftat mot LISO: fläktens "I1 Voltage > 1.00" står lagrad som 10.
  Lagrat 500 = "> 50.00" i GUI:t = 50 ms. Kompressortutan gick alltså in nästan direkt.

ÅTGÄRD
  Timer5 > 500 ms lagras som 5000. Inget annat ändras.
  (Övriga numeriska konstanter jag skrivit: GF3 OIL_OK "T3 > 0" — 0 ×10 = 0, rätt.)

    python build_v10.16_tuta_fix.py            # torrkörning
    python build_v10.16_tuta_fix.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.15_flakt_filter.HWPDM'
DST = r'Builds\Elton_v10.16_tuta_fix.HWPDM'
HOLD_MS = 500
CONST_SCALE = 10          # logikeditorns lagringsskala för konstanter


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.16 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')

    o = cfg['OutputHS'][16]
    assert o['label'] == 'HORN_2', o['label']
    t5 = v.timer(5)
    hits = [r for r in o['functionInfix'] if L.is_term(r) and int(r[1]) == t5 and int(r[3]) == 6]
    assert len(hits) == 1 and int(hits[0][5]) == HOLD_MS, hits
    hits[0][5] = type(hits[0][5])(HOLD_MS * CONST_SCALE)
    o['function'] = L.infix_to_function(o['functionInfix'])
    print(f'  O17 HORN_2: Timer5 > {HOLD_MS} lagrat som {HOLD_MS * CONST_SCALE} '
          f'(GUI visar {HOLD_MS * CONST_SCALE / CONST_SCALE:.2f} = {HOLD_MS} ms)')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('O17: Timer5 > 5000 i både infix och function',
         lambda c: [1, t5, 2, 6, 3, 5000] in [[int(x) for x in r] for r in c['OutputHS'][16]['functionInfix'] if L.is_term(r)]
         and 5000 in [x for x in c['OutputHS'][16]['function'] if isinstance(x, int)]),
        ('inget 500 kvar i O17', lambda c: 500 not in [x for x in c['OutputHS'][16]['function'] if isinstance(x, int)]),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
