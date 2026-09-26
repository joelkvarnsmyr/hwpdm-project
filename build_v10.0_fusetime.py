"""v10.0 — rätta två toppsäkringstider som står i millisekunder i ett sekundfält.

FÖRSTA bygget på LISO-linjen (konfigurator/firmware 1.3.1). Versionshoppet till
v10.0 markerar brytet: nytt variabelschema och ny buildlinje (GOTLAND -> LISO),
inte en fortsättning på den planerade v9.60 som utgick från v9.59.

SYFTE: detta är medvetet den tråkigaste möjliga ändringen. Den finns för att bevisa
hela script-kedjan (build_lib, VarMap-självtest, typbevarande skrivning, borttagna
härledda fält) på laster där en felutlöst säkring inte kan ställa till skada.

ÄNDRINGAR
  O13 HORN   peakFuseTime 4000 s -> 0.5 s   (50 A i 67 minuter på 2,0 mm² kabel)
  O11 BLOWER peakFuseTime 4000 s -> 5 s     (5 s enligt fläktspecen, motorstart)

Manualen bekräftar att fältet är SEKUNDER ("The Peak Fuse Time has been set to
4 seconds"). Riktningen är åt det säkra hållet: kortare fönster = tätare skydd.
Värsta utfallet är en felutlösning, inte skadad kabel.

MEDVETET UTANFÖR: O1 BUSBAR (10 A/1000 s) och O3 IGN_COIL (12 A/1000 s) har samma
bugg men matar busbar respektive tändspole. En felutlösning där stannar motorn.
De tas när kedjan är beprövad.

    python build_v10.0_fusetime.py            # torrkörning
    python build_v10.0_fusetime.py --write    # bygg
"""
import sys
import build_lib as B

SRC = r'Builds\LISO.HWPDM'
DST = r'Builds\Elton_v10.0_fusetime.HWPDM'

FIXES = [
    # (index, förväntad label, nytt värde, varför)
    # OBS: O13:s falt ar int i denna fil, O11:s ar strang. Darfor heltal pa O13 —
    # set_field vagrar avrunda 0.5 till 0, vilket det annars hade gjort tyst.
    (12, 'HORN',   1, '50 A i 4000 s pa 2,0 mm2 - skyddade i praktiken inte'),
    (10, 'BLOWER', 5, '5 s enligt flaktspecen, tacker motorstart'),
]


def changes(cfg, v):
    log = []
    for idx, label, new, why in FIXES:
        o = cfg['OutputHS'][idx]
        assert o['label'] == label, f'idx{idx} ar {o["label"]!r}, vantade {label!r}'
        before = o['peakFuseTime']
        B.set_field(o, 'peakFuseTime', new)
        log.append(f'O{idx+1} {label}: peakFuseTime {before!r} -> '
                   f'{o["peakFuseTime"]!r}   ({why})')
    return log


def checks():
    def pft(i):
        return lambda c: float(c['OutputHS'][i]['peakFuseTime'])

    return [
        # ── ändringen ──
        ('O13 HORN peakFuseTime = 1', lambda c: pft(12)(c) == 1),
        ('O11 BLOWER peakFuseTime = 5', lambda c: pft(10)(c) == 5),

        # ── inget ANNAT i säkringskedjan rörd ──
        ('O13 peak/high oforandrade (50/25)',
         lambda c: (float(c['OutputHS'][12]['peakFuse']) == 50
                    and float(c['OutputHS'][12]['highFuse']) == 25)),
        ('O11 peak/high oforandrade (16/9)',
         lambda c: (float(c['OutputHS'][10]['peakFuse']) == 16
                    and float(c['OutputHS'][10]['highFuse']) == 9)),
        ('O1 BUSBAR orord (1000)', lambda c: pft(0)(c) == 1000),
        ('O3 IGN_COIL orord (1000)', lambda c: pft(2)(c) == 1000),

        # ── regressionsvakter: kritisk mappning intakt ──
        ('O4 = PARK pa D7', lambda c: c['OutputHS'][3]['label'] == 'PARK'),
        ('O6 = BRAKE pa D9', lambda c: c['OutputHS'][5]['label'] == 'BRAKE'),
        ('O23 STARTER enabled', lambda c: c['OutputHS'][22]['enabled'] is True),
        ('O13 HORN enabled', lambda c: c['OutputHS'][12]['enabled'] is True),
        ('O11 BLOWER enabled', lambda c: c['OutputHS'][10]['enabled'] is True),
        ('O24/O25 blinkers enabled',
         lambda c: c['OutputHS'][23]['enabled'] is True and c['OutputHS'][24]['enabled'] is True),
        ('27 CANInputs kvar', lambda c: sum(1 for x in c['CANInput'] if x.get('enabled')) >= 27),

        # ── kartan håller efteråt ──
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.0 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()

    # Snapshotta O13:s logik före, så vi kan bevisa att bara säkringstiden rörts.
    logic_before = list(cfg['OutputHS'][12]['function'])

    print('\n=== Andringar ===')
    for line in changes(cfg, v):
        print('  ' + line)

    if list(cfg['OutputHS'][12]['function']) != logic_before:
        print('\n*** AVBRYTER: O13:s logik andrades, det var inte meningen ***')
        return 1

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)} (appen raknar om dem)')

    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
