"""v10.7 — handbromsens aktivnivå + stadning av reservutgangar.

1. HANDBROMSEN VAR INVERTERAD  (bugg inford i v10.2)
   I16 fick activeLevel = 0 (Active High) genom att kopiera I4 BRAKE rakt av.
   Men I4 ar BATTERIMATAD — bromsljusbrytaren skickar +12V nar man trampar, sa
   Active High ar ratt for den. F9 handbroms ar tvartom en SWITCH-TO-GROUND som
   jordar nar handbromsen dras. Med intern pull-up ger det:
        handbroms AV  -> brytaren oppen -> hog -> visade "pa"
        handbroms PA  -> jordad         -> lag -> visade "av"
   Alltsa tvartom. Ratt varde ar activeLevel = 1 (Active Low).

   `handbroms.yml` sager emot sig sjalv: logikraden sager "active-low" men
   instruktionen sager "samma installningar som I4 BRAKE". Jag foljde det senare.
   I14 OIL.PRESS bevisar monstret — jordande brytare, activeLevel 1, och Joel
   har verifierat att den beter sig ratt i bilen.

   ⚠ activeLevel: 0 = Active High, 1 = Active Low (configInputs.js:829).

2. O21 hette REVERSE — samma namn som O19. Dubbletten gjorde extraktionen
   tvetydig och ar latt att forvaxla i GUI:t. -> RESERVE21.

3. O9 RESERVE9 bar kvarglomd logik som refererar GF7 ANY_FAULT (avstangd).
   Rensas till tom, samma form som O18 RESERVE18 redan har.

4. O18/O21/O22 hade peakFuse = 0, alltsa LAGRE an hogsakringen. Toppsakringen
   blir da meningslos och konfiguratorn varnar. Satts till 2x hogsakringen.
   Alla tre ar avstangda reserver — varderna ar sunda utgangslagen, inte trimning.

    python build_v10.7_stadning.py            # torrkorning
    python build_v10.7_stadning.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.6_spolare.HWPDM'
DST = r'Builds\Elton_v10.7_stadning.HWPDM'

ACTIVE_LOW = 1


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.7 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Andringar ===')

    # ── 1. handbromsen ──────────────────────────────────────────────────────
    i16 = cfg['Input'][15]
    assert i16['label'] == 'HANDBRAKE', f'I16 ar {i16["label"]!r}'
    before = int(i16['activeLevel'])
    assert before == 0, f'I16 activeLevel ar redan {before} — kontrollera innan andring'
    B.set_field(i16, 'activeLevel', ACTIVE_LOW)
    i14 = cfg['Input'][13]
    print(f'  I16 HANDBRAKE: activeLevel 0 (Active High) -> 1 (Active Low)')
    print(f'                 jamfor I14 {i14["label"]}: activeLevel '
          f'{i14["activeLevel"]} — samma brytartyp, verifierad i bilen')

    # ── 2. dubblettnamnet ───────────────────────────────────────────────────
    o21 = cfg['OutputHS'][20]
    o19 = cfg['OutputHS'][18]
    assert o21['label'] == 'REVERSE' and o19['label'] == 'REVERSE', \
        f'vantade dubblett, fick O19={o19["label"]!r} O21={o21["label"]!r}'
    assert o21['enabled'] is False, 'O21 ar aktiverad — vagrar doopa om'
    o21['label'] = 'RESERVE21'
    print(f'  O21 (D2): REVERSE -> RESERVE21 (dubblett mot O19, avstangd)')

    # ── 3. kvarglomd logik ──────────────────────────────────────────────────
    o9 = cfg['OutputHS'][8]
    assert o9['label'].startswith('RESERVE') and o9['enabled'] is False
    o18 = cfg['OutputHS'][17]
    n_before = len([r for r in o9['functionInfix'] if L.is_term(r)])
    o9['function'] = list(o18['function'])              # tom, som O18
    o9['functionInfix'] = [list(r) for r in o18['functionInfix']]
    print(f'  O9 (D4): {n_before} kvarglomda villkor rensade (refererade avstangd GF7)')

    # ── 4. toppsakringar ────────────────────────────────────────────────────
    for idx in (17, 20, 21):
        o = cfg['OutputHS'][idx]
        assert o['enabled'] is False, f'O{idx+1} ar aktiverad — rors inte'
        high = float(o['highFuse'])
        if float(o['peakFuse']) >= high:
            continue
        B.set_field(o, 'peakFuse', high * 2)
        # Aven tiden: de har 5000 s, samma millisekunder-i-ett-sekundfalt som
        # hornets 4000. Ofarligt sa lange utgangen ar avstangd, men enablar man
        # den senare arvs ett toppsakringsfonster pa nastan 1,5 timme.
        old_t = float(o['peakFuseTime'] or 0)
        if not (0 < old_t <= 10):
            B.set_field(o, 'peakFuseTime', 1)
        print(f'  O{idx+1} {o["label"]}: peakFuse 0 -> {o["peakFuse"]} A '
              f'(2x hogsakringen {high:g} A), tid {old_t:g} -> {o["peakFuseTime"]} s')

    L.roundtrip_check(cfg)

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks()) else 1


def checks():
    def terms(c, i):
        return [r for r in c['OutputHS'][i]['functionInfix'] if L.is_term(r)]
    return [
        ('I16 HANDBRAKE ar Active Low',
         lambda c: int(c['Input'][15]['activeLevel']) == ACTIVE_LOW),
        ('I16 har kvar intern pull-up + Momentary',
         lambda c: int(c['Input'][15]['pullResistor']) == 1 and int(c['Input'][15]['mode']) == 0),
        ('I16 matchar nu I14:s aktivniva (samma brytartyp)',
         lambda c: int(c['Input'][15]['activeLevel']) == int(c['Input'][13]['activeLevel'])),
        ('I4 BRAKE OFORANDRAD Active High (batterimatad)',
         lambda c: int(c['Input'][3]['activeLevel']) == 0),
        ('O21 = RESERVE21, inte langre dubblett',
         lambda c: c['OutputHS'][20]['label'] == 'RESERVE21'
                   and c['OutputHS'][18]['label'] == 'REVERSE'),
        ('O9 utan kvarglomd logik', lambda c: len(terms(c, 8)) == 0),
        ('inga peakFuse under highFuse kvar',
         lambda c: all(float(o['peakFuse']) >= float(o['highFuse'])
                       for o in c['OutputHS'][:25] if float(o['highFuse'] or 0) > 0)),
        ('inga orimliga toppsakringstider kvar pa de stadade',
         lambda c: all(0 < float(c['OutputHS'][i]['peakFuseTime']) <= 10 for i in (17, 20, 21))),
        ('alla tre reserver fortfarande avstangda',
         lambda c: all(c['OutputHS'][i]['enabled'] is False for i in (8, 17, 20, 21))),

        # ── inget annat rort ──
        ('O5 FUEL enabled, bara GF1',
         lambda c: c['OutputHS'][4]['enabled'] is True and len(terms(c, 4)) == 1),
        ('I8 FUEL_LEVEL analog kvar', lambda c: c['Input'][7]['label'] == 'FUEL_LEVEL'),
        ('I1 WASHER kvar', lambda c: c['Input'][0]['label'] == 'WASHER'),
        ('O17 HORN_2 kvar', lambda c: c['OutputHS'][16]['label'] == 'HORN_2'),
        ('O11 flakten pa BLW_CMD', lambda c: len(terms(c, 10)) == 4),
        ('GF9 LOAD_OK kvar pa halv/helljus',
         lambda c: all(any(int(r[1]) == 759 for r in terms(c, i)) for i in (13, 14, 6, 15))),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
