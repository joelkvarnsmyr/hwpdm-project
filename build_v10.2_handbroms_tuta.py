"""v10.2 — handbromsvarning, luftorn med hall-funktion, backljus.

HANDBROMS  I16 / pin C1
  Kopia av I4 BRAKE:s installningar (digital, intern pull-up mot VBat,
  active-low switch-to-ground). Driver ingen PDM-utgang — statusen gar ut pa
  CAN-strommen till Pi-dashboarden. Joel har allt material.

LUFTORN  O17 / pin D1  +  Timer5
  En knapp, tva tutor:
     kort tryck        -> bara vanliga tutan (O13, oforandrad)
     hall over 0,5 s   -> aven luftornet (O17)
  Timer5 HORN_HOLD ar en Duration-timer: den raknar millisekunder fran att
  hornknappen trycks och ligger kvar pa duration tills knappen slapps
  (resetOnEnd=0). O17 kraver att den passerat 500 ms.
  Vanliga tutan ljuder alltid direkt, sa inget gar forlorat i en nodsituation.

  Timervardet ar RAA MILLISEKUNDER (variables.js: units '') — ingen skalning.

BACKLJUS  O19 / pin B1
  Enables. Lokala grenen (I7) borjar fungera nar backvaxelkontaktens kabel dras
  till A10; CAN-grenen fungerar direkt.

MEDVETET UTELAMNADE — de ar INTE bara en flaggvandning:
  O8 WIPER_FST  logiken ar "I9 spanning > 50", alltsa SAMMA ingang som de
                langsamma torkarna. Enables den nu gar torkarna sannolikt
                snabbt sa fort de gar alls. Kraver torkar-muxen eller en egen
                ingang.
  O12 WASHER    logiken ar "I8 status", och I8/A3 ar pa vag att bli
                bransleniva-givaren. Enables den nu skulle branslenivan styra
                spolarpumpen. Spolaren behover en egen ingang forst — A7
                frigors nar flakten gar over till CAN.

    python build_v10.2_handbroms_tuta.py            # torrkorning
    python build_v10.2_handbroms_tuta.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.1_lastfallning.HWPDM'
DST = r'Builds\Elton_v10.2_handbroms_tuta.HWPDM'

HOLD_MS = 1000          # timerns duration
TRIGGER_MS = 500        # luftornet ljuder efter denna tid


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.2 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)

    i12 = v.input_status(12)        # hornknappen
    t5 = v.timer(5)
    t2 = v.timer(2)
    print(f'\n  I12 HORN -> var {i12};  Timer5 -> var {t5};  Timer2 -> var {t2}')
    print('\n=== Andringar ===')

    # ── 1. handbroms pa I16 / C1 ────────────────────────────────────────────
    i16 = cfg['Input'][15]
    assert i16['label'] in ('RESERVE16', ''), f'I16 ar {i16["label"]!r}, vagrar skriva over'
    src = cfg['Input'][3]           # I4 BRAKE som mall
    assert src['label'] == 'BRAKE'
    for f in ('mode', 'pullResistor', 'activeLevel'):
        B.set_field(i16, f, src[f])
    B.set_field(i16, 'enabled', True)
    i16['label'] = 'HANDBRAKE'
    print(f'  I16 (C1): HANDBRAKE — mode={i16["mode"]} pull={i16["pullResistor"]} '
          f'activeLevel={i16["activeLevel"]} (kopia av I4 BRAKE)')

    # ── 2. Timer5 HORN_HOLD ─────────────────────────────────────────────────
    # Joel 2026-09-26: tuta 1 ar en vanlig eltuta, tuta 2 en KOMPRESSORTUTA.
    # Tva olika don, inte ett matchat tvatonspar — darfor ar hall-funktionen
    # ratt: vanliga tutan ljuder alltid direkt, kompressorn bara nar man vill.
    t = cfg['Timer'][4]
    assert not t.get('label'), f'Timer5 ar upptagen ({t.get("label")!r})'
    t['label'] = 'HORN_HOLD'
    # OBS: den OANVANDA timerplatsen lagrar enabled som int 0, men konfigurerade
    # timers (T1, T4) anvander bool true. Vid AKTIVERING av en tom plats galler
    # den konfigurerade grannens typer — satt darfor direkt, inte via set_field.
    t['enabled'] = True
    B.set_field(t, 'visibleInDOM', 1)
    B.set_field(t, 'type', 1)                    # Duration
    B.set_field(t, 'duration', HOLD_MS)
    B.set_field(t, 'onTime', HOLD_MS)            # speglas som i T2/T3
    B.set_field(t, 'offTime', 0)
    B.set_field(t, 'resetOnEnd', 0)              # ligg kvar pa duration
    B.set_field(t, 'startConditionVar1', i12)
    B.set_field(t, 'startConditionCondition', 10)   # Equals
    B.set_field(t, 'startConditionVar2', 1)         # konstanten True
    B.set_field(t, 'resetConditionVar1', i12)
    B.set_field(t, 'resetConditionCondition', 11)   # Not Equal
    B.set_field(t, 'resetConditionVar2', 1)
    print(f'  Timer5 HORN_HOLD: Duration {HOLD_MS} ms, start "I12 Equals True", '
          f'reset "I12 Not Equal True", resetOnEnd=0')

    # ── 3. O17 kompressortuta ───────────────────────────────────────────────
    # Gren 1: hornknappen hallen > 500 ms (och ingen krock)
    # Gren 2: Pi:ns Horn_Pulse — bevarar v9.56:s CAN-styrning
    o17 = cfg['OutputHS'][16]
    assert o17['label'].startswith('RESERVE'), f'O17 ar {o17["label"]!r}'
    o17['label'] = 'HORN_2'
    B.set_field(o17, 'enabled', True)
    ci_show = v.caninput(1)          # LightShow_Enable
    ci_horn = v.caninput(15)         # Horn_Pulse
    rows = [
        L.term(i12, value=1),                          # I12 Equals True
        list(L.AND_ROW),
        L.term(t5, value=TRIGGER_MS, op=6, marker=3),  # Timer5 > 500 ms
        list(L.AND_ROW),
        L.term(t2, value=2),                           # Timer2 Equals False
        list(L.OR_ROW),
        L.term(ci_show, value=1),                      # LightShow_Enable
        list(L.AND_ROW),
        L.term(ci_horn, value=1),                      # Horn_Pulse
    ]
    rows = L.cleanup_infix(rows)
    o17['functionInfix'] = rows
    o17['function'] = L.infix_to_function(rows)
    print(f'  O17 (D1): HORN_2 enabled — "I12 AND Timer5 > {TRIGGER_MS} AND '
          f'INTE Timer2"  ELLER  "LightShow_Enable AND Horn_Pulse"')

    # ── 4. backljus ─────────────────────────────────────────────────────────
    o19 = cfg['OutputHS'][18]
    assert o19['label'] == 'REVERSE'
    B.set_field(o19, 'enabled', True)
    print('  O19 (B1): REVERSE enabled (lokala grenen vantar pa kabel till A10)')

    L.roundtrip_check(cfg)

    names = {i12: 'I12 HORN', t5: 'Timer5', t2: 'Timer2'}
    print(f'\n  O17-logiken lases: {L.describe(o17, names)}')

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(i12, t5, t2)) else 1


def checks(i12, t5, t2):
    def terms(c, i):
        return [r for r in c['OutputHS'][i]['functionInfix'] if L.is_term(r)]

    return [
        ('I16 = HANDBRAKE enabled',
         lambda c: c['Input'][15]['label'] == 'HANDBRAKE' and c['Input'][15]['enabled'] is True),
        ('I16 samma installningar som I4',
         lambda c: all(str(c['Input'][15][f]) == str(c['Input'][3][f])
                       for f in ('mode', 'pullResistor', 'activeLevel'))),
        ('Timer5 HORN_HOLD enabled, Duration',
         lambda c: (c['Timer'][4]['label'] == 'HORN_HOLD'
                    and c['Timer'][4]['enabled'] is True
                    and int(c['Timer'][4]['type']) == 1
                    and int(c['Timer'][4]['duration']) == HOLD_MS)),
        ('Timer5 startar pa I12, resettar pa I12',
         lambda c: (int(c['Timer'][4]['startConditionVar1']) == i12
                    and int(c['Timer'][4]['resetConditionVar1']) == i12
                    and int(c['Timer'][4]['resetConditionCondition']) == 11)),
        ('O17 = HORN_2 enabled', lambda c: c['OutputHS'][16]['label'] == 'HORN_2'
                                 and c['OutputHS'][16]['enabled'] is True),
        ('O17 har 5 villkor i 2 grenar', lambda c: len(terms(c, 16)) == 5 and L.count_branches(c['OutputHS'][16]) == 2),
        ('O17 gren 1 = knapp + timer + crash',
         lambda c: {i12, t5, t2} <= {int(r[1]) for r in terms(c, 16)}),
        ('O17 har CAN-grenen kvar (Horn_Pulse)',
         lambda c: any(int(r[1]) == B.VarMap(c).caninput(15) for r in terms(c, 16))),
        (f'O17 troskel > {TRIGGER_MS} ms',
         lambda c: any(int(r[1]) == t5 and int(r[3]) == 6 and int(r[5]) == TRIGGER_MS
                       for r in terms(c, 16))),
        ('O19 REVERSE enabled', lambda c: c['OutputHS'][18]['enabled'] is True),

        # ── far inte ha rorts ──
        ('O13 vanliga tutan oforandrad (2 grenar, utan Timer5)',
         lambda c: L.count_branches(c['OutputHS'][12]) == 2
                   and all(int(r[1]) != t5 for r in terms(c, 12))),
        ('O8 WIPER_FST fortfarande avstangd', lambda c: c['OutputHS'][7]['enabled'] is False),
        ('O12 WASHER fortfarande avstangd', lambda c: c['OutputHS'][11]['enabled'] is False),
        ('I8 orord (blir bransle i nasta steg)', lambda c: c['Input'][7]['label'] == 'WASHER'),
        ('GF9 LOAD_OK kvar', lambda c: c['GenericFunction'][8]['label'] == 'LOAD_OK'),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
