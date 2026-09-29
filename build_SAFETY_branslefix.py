"""AKUT SAKERHETSFIX — ta bort ljusshowens grepp om branslepumpen.

PROBLEM (verifierat 2026-09-27, Joel: "motorn stangs av nar pajen bootat")
  O5 FUEL i LISO:
      (LightShow_Enable == False AND GF1) OR (Safety_Override == True AND GF1)

  Nar Pi:n bootar borjar mqtt-to-can sanda LightShow_Enable=1. Forsta grenen
  blir falsk, andra kraver Safety_Override som defaultar till 0 → BADA grenar
  falska → branslepumpen slas av → motorn dor.

  O3 IGN_COIL ar inte grindad, sa tandningen finns kvar. Motorn gar darfor nagra
  sekunder pa flottorhuset och tynar bort. CANInput-timeouten ar 1000 ms med
  default 0, sa branslet kommer tillbaka nar Pi:n slutar sanda — vilket gor
  beteendet oberakneligt och svart att felsoka.

FIX
  O5 FUEL = GF1 == True        (samma som O3 IGN_COIL)

  En branslepump ska aldrig bero pa en kosmetisk flagga. Vill man ha en
  showsparr hor den hemma pa Pi-sidan — vagra starta showen medan motorn gar —
  inte som en avstangningsvag in i motordriften.

KALLA: Joels GUI-granskade v10.2. Den filen ar dessutom normaliserad av
       konfiguratorn, vilket stadade bort ett hangande OR som mina egna v10.1/
       v10.2 hade (cleanup_infix-buggen, rattad 2026-09-27).

    python build_SAFETY_branslefix.py            # torrkorning
    python build_SAFETY_branslefix.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.2_handbroms_tuta_reviewed by joel.HWPDM'
DST = r'Builds\Elton_v10.3_branslefix.HWPDM'


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} SAKERHETSFIX — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)

    gf1 = v.gf(1)
    ci_show = v.caninput(1)          # LightShow_Enable
    ci_safe = v.caninput(3)          # Safety_Override
    names = {gf1: 'GF1 PWR_ALIVE', ci_show: 'LightShow_Enable', ci_safe: 'Safety_Override'}

    o5 = cfg['OutputHS'][4]
    assert o5['label'] == 'FUEL', f'idx4 ar {o5["label"]!r}, vantade FUEL'

    before = L.describe(o5, names)
    print('=== O5 FUEL ===')
    print(f'  FORE:  {before}')

    # Sanity: bekrafta att problemet verkligen ser ut som vi tror innan vi skriver
    refs = {int(r[1]) for r in o5['functionInfix'] if L.is_term(r)}
    assert ci_show in refs, 'O5 refererar inte LightShow_Enable — kontrollera filen'

    L.set_and_chain(o5, [L.term(gf1, value=1)])
    print(f'  EFTER: {L.describe(o5, names)}')

    o3 = cfg['OutputHS'][2]
    print(f'\n  (O3 IGN_COIL till jamforelse: {L.describe(o3, names)})')

    L.roundtrip_check(cfg)

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(gf1, ci_show, ci_safe)) else 1


def checks(gf1, ci_show, ci_safe):
    def o5terms(c):
        return [r for r in c['OutputHS'][4]['functionInfix'] if L.is_term(r)]

    return [
        ('O5 FUEL har EXAKT ett villkor', lambda c: len(o5terms(c)) == 1),
        ('O5 FUEL = GF1 Equals True',
         lambda c: (int(o5terms(c)[0][1]) == gf1 and int(o5terms(c)[0][3]) == 10
                    and int(o5terms(c)[0][5]) == 1)),
        ('O5 refererar INTE LightShow_Enable',
         lambda c: all(int(r[1]) != ci_show for r in o5terms(c))),
        ('O5 refererar INTE Safety_Override',
         lambda c: all(int(r[1]) != ci_safe for r in o5terms(c))),
        ('O5 FUEL enabled', lambda c: c['OutputHS'][4]['enabled'] is True),
        ('O5 har en enda gren', lambda c: L.count_branches(c['OutputHS'][4]) == 1),

        # O5 ska nu se ut precis som tandspolen
        ('O5 matchar O3 IGN_COILs form',
         lambda c: ([int(t) for t in c['OutputHS'][4]['function']]
                    == [int(t) for t in c['OutputHS'][2]['function']])),

        # ── inget annat far ha rorts ──
        ('O3 IGN_COIL oforandrad', lambda c: c['OutputHS'][2]['enabled'] is True),
        ('O23 STARTER oforandrad', lambda c: c['OutputHS'][22]['enabled'] is True),
        ('O1 BUSBAR oforandrad', lambda c: c['OutputHS'][0]['enabled'] is True),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),
        ('27 CANInputs kvar', lambda c: sum(1 for x in c['CANInput'] if x.get('enabled')) >= 27),
        ('inga andra utgangar andrade antal grenar',
         lambda c: all(L.count_branches(c['OutputHS'][i]) == n for i, n in
                       ((2, 1), (22, 1), (23, 4), (24, 4)))),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
