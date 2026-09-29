"""v10.1 — lastfällning under start + åtgärda varningar på berörda utgångar.

LASTFÄLLNING
  Ny GF9 "LOAD_OK" = Input 15 (START) Status Equals False
     dvs sann nar startmotorn INTE gar.

  Termen "GF9 Equals True" laggs som AND i VARJE OR-gren hos:
     O14 LOWBEAM_L, O15 LOWBEAM_R   halvljus   ~9 A
     O7  HIBEAM_R,  O16 HIBEAM_L    helljus    ~10 A
     O11 BLOWER                     flakt      ~9 A

  Joel 2026-09-26: bara de stora forbrukarna. Torkare, radio, USB och backljus
  lamnas utanfor — sma poster, inte vart risken.

  FALLS ALDRIG (och rors inte har):
     O6 BRAKE      bromsljusen maste lysa aven vid start i backe
     O24/O25 TURN  varningsblinkers ar en sakerhetsfunktion
     O3 IGN_COIL   motorn behover gnista MEDAN den dras runt
     O5 FUEL       ... och bransle
     O1 BUSBAR     matar bryataringangarna, inkl. START sjalv
     O23 STARTER   sjalvklart
     O4 PARK       2 A ar inte vart att bli osynlig for i morker

VARNINGAR som konfiguratorn flaggade, pa utgangar vi anda ror:
  O7  highFuse 20 A -> 13 A    over pinnens 13 A-grans (manualen: kislet klarar
  O13 highFuse 25 A -> 13 A    20 A men kontakt/pin bara 13 A vid 125 degC)
  O11 stayOnTime 3785.6 -> 0   GUI:t klampade till 300 s. Med 300 s eftergang
                               fortsatter flakten ga genom hela dragningen och
                               lastfallningen blir meningslos — och nar CAN-
                               styrningen kommer skulle appens "av" droja 5 min.

13 A ar pinnens tak, inte ett trimmat varde. Mat verklig strom i konfiguratorn
(tuta / tand helljuset och las av) och sank ytterligare om du vill.

    python build_v10.1_lastfallning.py            # torrkorning
    python build_v10.1_lastfallning.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.0_fusetime.HWPDM'
DST = r'Builds\Elton_v10.1_lastfallning.HWPDM'

GF_SLOT = 9
GF_LABEL = 'LOAD_OK'

# (index, forvantad label) — utgangar som ska fallas under start
SHED = [
    (13, 'LOWBEAM_L'),
    (14, 'LOWBEAM_R'),
    (6,  'HIBEAM_R'),
    (15, 'HIBEAM_L'),
    (10, 'BLOWER'),
]

# (index, label, falt, nytt varde)
VALUE_FIXES = [
    (6,  'HIBEAM_R', 'highFuse',   13),
    (12, 'HORN',     'highFuse',   13),
    (10, 'BLOWER',   'stayOnTime', 0),
]


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.1 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)          # bevisa formatforstaelsen INNAN vi ror nagot

    gf_var = v.gf(GF_SLOT)
    i15 = v.input_status(15)
    print(f'\n  GF{GF_SLOT} {GF_LABEL} -> var {gf_var};  I15 START status -> var {i15}')

    # ── 1. skapa GF9 ────────────────────────────────────────────────────────
    gf = cfg['GenericFunction'][GF_SLOT - 1]
    if gf.get('label'):
        print(f'\n*** AVBRYTER: GF{GF_SLOT} ar upptagen ({gf["label"]!r}) ***')
        return 1
    gf['label'] = GF_LABEL
    gf['enabled'] = True
    gf['visibleInDOM'] = 1
    gf['function'] = [7, 1, i15, 2, 10, 1, 2]      # I15 Status Equals False
    gf['functionInfix'] = []                        # GF lagrar bara platt array
    print(f'\n=== Andringar ===')
    print(f'  GF{GF_SLOT} {GF_LABEL}: skapad = "Input 15 (START) Status Equals False"')

    # ── 2. lagg termen i varje gren ─────────────────────────────────────────
    new_term = L.term(gf_var, value=1)              # GF9 Equals True
    for idx, label in SHED:
        out = cfg['OutputHS'][idx]
        assert out['label'] == label, f'idx{idx} ar {out["label"]!r}, vantade {label!r}'
        before = L.count_branches(out)
        n = L.add_and_term_to_all_branches(out, new_term)
        print(f'  O{idx+1} {label}: termen tillagd i {n} av {before} OR-grenar')
        if n != before:
            print(f'\n*** AVBRYTER: bara {n} av {before} grenar fick termen ***')
            return 1

    # ── 3. vardefixar ───────────────────────────────────────────────────────
    for idx, label, field, new in VALUE_FIXES:
        out = cfg['OutputHS'][idx]
        assert out['label'] == label, f'idx{idx} ar {out["label"]!r}, vantade {label!r}'
        old = out[field]
        B.set_field(out, field, new)
        print(f'  O{idx+1} {label}: {field} {old!r} -> {out[field]!r}')

    L.roundtrip_check(cfg)          # och efterat

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(gf_var, i15)) else 1


def checks(gf_var, i15):
    def has_term_everywhere(idx):
        def f(c):
            out = c['OutputHS'][idx]
            rows = out['functionInfix']
            # dela upp i grenar pa OR och krav att varje gren innehaller gf_var
            branches, cur = [], []
            for r in rows:
                if L.is_or(r):
                    branches.append(cur); cur = []
                else:
                    cur.append(r)
            if cur:
                branches.append(cur)
            branches = [b for b in branches if any(L.is_term(r) for r in b)]
            return bool(branches) and all(
                any(L.is_term(r) and int(r[1]) == gf_var for r in b) for b in branches)
        return f

    ck = [
        (f'GF9 LOAD_OK enabled', lambda c: c['GenericFunction'][8]['enabled'] is True),
        (f'GF9 = I15 Equals False',
         lambda c: [int(t) for t in c['GenericFunction'][8]['function']] == [7, 1, i15, 2, 10, 1, 2]),
    ]
    for idx, label in SHED:
        ck.append((f'O{idx+1} {label}: GF9 i ALLA grenar', has_term_everywhere(idx)))
    ck += [
        ('O7 highFuse = 13', lambda c: float(c['OutputHS'][6]['highFuse']) == 13),
        ('O13 highFuse = 13', lambda c: float(c['OutputHS'][12]['highFuse']) == 13),
        ('O11 stayOnTime = 0', lambda c: float(c['OutputHS'][10]['stayOnTime']) == 0),

        # ── far INTE ha rorts ──
        ('O6 BRAKE utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][5]['functionInfix'])),
        ('O24 TURN_R utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][23]['functionInfix'])),
        ('O25 TURN_L utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][24]['functionInfix'])),
        ('O3 IGN_COIL utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][2]['functionInfix'])),
        ('O5 FUEL utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][4]['functionInfix'])),
        ('O23 STARTER utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][22]['functionInfix'])),
        ('O1 BUSBAR utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][0]['functionInfix'])),
        ('O4 PARK utan GF9',
         lambda c: all(not (L.is_term(r) and int(r[1]) == gf_var)
                       for r in c['OutputHS'][3]['functionInfix'])),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]
    return ck


if __name__ == '__main__':
    raise SystemExit(main())
