"""v10.6 — spolaren flyttad till I1 / pin A7, och O12 aktiverad igen.

Joel 2026-09-29: "Washer var redan programmerad och klar som input, men jag
flyttade den till ingang 1 pa den DT-kontakten nu istallet."

Spolarspakens kabel sitter alltsa nu pa A7 i stallet for A3. Det gar ihop:
  - A3 / I8  frigjordes for branslegivaren i v10.5
  - A7 / I1  frigjordes nar flakten gick over till CAN i v10.4
Spolaren far darmed en egen ingang utan att na multiingang-planen, och den
planen kan genomforas senare utan att nagot av detta star i vagen.

ANDRINGAR
  I1 / A7   RESERVE1 -> WASHER. Digital, intern pull-up mot VBat, active-low.
            Exakt de installningar spolaren hade pa A3 (mode 0, pull 1, level 0).

  O12 / B9  WASHER. Logiken pekade fortfarande pa I8 — som nu ar
            BRANSLENIVAGIVAREN. Hade utgangen aktiverats i det laget skulle
            bransletanken ha styrt spolarpumpen. Pekas om till I1 och enables.

Timer2-termen (krockspar) behalls, samma form som utgangen hade forut.

    python build_v10.6_spolare.py            # torrkorning
    python build_v10.6_spolare.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.5_bransle.HWPDM'
DST = r'Builds\Elton_v10.6_spolare.HWPDM'


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.6 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)

    i1_stat, i8_stat, t2 = v.input_status(1), v.input_status(8), v.timer(2)
    print(f'\n  I1 status -> var {i1_stat};  I8 status -> var {i8_stat};  Timer2 -> var {t2}')
    print('\n=== Andringar ===')

    # ── 1. ingangen ─────────────────────────────────────────────────────────
    i1 = cfg['Input'][0]
    assert i1['label'] == 'RESERVE1', f'I1 ar {i1["label"]!r}, forvantade RESERVE1'
    i1['label'] = 'WASHER'
    B.set_field(i1, 'mode', 0)              # digital
    B.set_field(i1, 'pullResistor', 1)      # intern 10k -> VBat
    B.set_field(i1, 'activeLevel', 0)       # active-low, switch-to-ground
    B.set_field(i1, 'enabled', True)
    print('  I1 (A7): RESERVE1 -> WASHER, digital, intern pull-up, active-low')

    # ── 2. utgangen ─────────────────────────────────────────────────────────
    o12 = cfg['OutputHS'][11]
    assert o12['label'] == 'WASHER', f'O12 ar {o12["label"]!r}'
    before = {int(r[1]) for r in o12['functionInfix'] if L.is_term(r)}
    assert i8_stat in before, \
        f'O12 refererar inte I8 ({i8_stat}) — kontrollera innan den pekas om'
    L.set_and_chain(o12, [
        L.term(i1_stat, value=1),   # spolarspaken
        L.term(t2, value=2),        # ingen krock
    ])
    B.set_field(o12, 'enabled', True)
    names = {i1_stat: 'I1 WASHER', t2: 'Timer2'}
    print(f'  O12 (B9): pekad om fran I8 till I1, enabled')
    print(f'            {L.describe(o12, names)}')

    L.roundtrip_check(cfg)

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(i1_stat, i8_stat, t2)) else 1


def checks(i1_stat, i8_stat, t2):
    def terms(c, i):
        return [r for r in c['OutputHS'][i]['functionInfix'] if L.is_term(r)]

    return [
        ('I1 = WASHER, digital, enabled',
         lambda c: (c['Input'][0]['label'] == 'WASHER'
                    and int(c['Input'][0]['mode']) == 0
                    and c['Input'][0]['enabled'] is True)),
        ('I1 intern pull-up, active-low',
         lambda c: int(c['Input'][0]['pullResistor']) == 1
                   and int(c['Input'][0]['activeLevel']) == 0),
        ('O12 WASHER enabled', lambda c: c['OutputHS'][11]['enabled'] is True),
        ('O12 har 2 villkor i 1 gren',
         lambda c: len(terms(c, 11)) == 2 and L.count_branches(c['OutputHS'][11]) == 1),
        ('O12 styrs av I1', lambda c: any(int(r[1]) == i1_stat for r in terms(c, 11))),
        ('O12 refererar INTE LANGRE I8 (branslegivaren)',
         lambda c: all(int(r[1]) != i8_stat for r in terms(c, 11))),
        ('O12 har kvar Timer2-sparren',
         lambda c: any(int(r[1]) == t2 for r in terms(c, 11))),

        # ── branslet far inte ha rorts ──
        ('I8 fortfarande FUEL_LEVEL analog',
         lambda c: c['Input'][7]['label'] == 'FUEL_LEVEL' and int(c['Input'][7]['mode']) == 2),
        ('SC2 pekar fortfarande pa I8 spanning',
         lambda c: int(c['SensorCalibration'][1]['variable']) == 616),

        # ── inget annat rort ──
        ('O5 FUEL-pumpen fortfarande bara GF1', lambda c: len(terms(c, 4)) == 1),
        ('O11 flakten pa BLW_CMD', lambda c: len(terms(c, 10)) == 4),
        ('I16 HANDBRAKE kvar', lambda c: c['Input'][15]['label'] == 'HANDBRAKE'),
        ('O17 HORN_2 kvar', lambda c: c['OutputHS'][16]['label'] == 'HORN_2'),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
