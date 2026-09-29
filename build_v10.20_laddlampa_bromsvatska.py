"""v10.20 — laddningslampa, bromsvätskevarning, bort med det som inte finns.

Källa: v10.19 (varvräknaren). Innehåller alltså v10.19 — flasha bara denna.

1. O2 ALT_EXCITE PÅ (Joel 2026-09-29: 82 Ω sitter, andra änden till generatorns D+,
   samma pin och sladd som den gamla laddningslampan).
   O2 har varit AV sedan v10.8 — generatorn har alltså saknat magnetiseringsström och
   bara kunnat ladda på remanens vid högre varv. Troligen därför den inte laddar på
   tomgång (12,0–12,4 V uppmätt). Strömmen i O2 är nu laddningslampan:
   ~0,15 A = laddar inte (eller motorn står), ~0 A = laddar. Redan på CAN: 0x518 b2–3.

2. I13 BRAKE_FAULT PÅ (pin C11) för originalets bromsvarningskontakt, som jordar vid fel.
   Brytarbeteendet kopieras från I14 OIL.PRESS — samma typ av jordande kontakt,
   VERIFIERAD i bilen. Plus turnOnDelay 2 s: bromsvätska skvalpar vid inbromsning och
   i kurvor, en flottör blinkar annars till. Status på CAN: 0x517 byte 4.

3. O19 REVERSE -> RESERVE19, av. Bilen har inga backljus (Joel 2026-09-29).
   Logiken töms (samma form som RESERVE9).

4. O14 LOWBEAM_L lyssnade på LowBeam_R_Cmd (CAN-ingång 5) i CAN-grenen — fel sedan LISO.
   Byts till LowBeam_L_Cmd (CAN-ingång 4) så appen kan styra halvljusen var för sig.

    python build_v10.20_laddlampa_bromsvatska.py            # torrkörning
    python build_v10.20_laddlampa_bromsvatska.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.19_varvraknare.HWPDM'
DST = r'Builds\Elton_v10.20_laddlampa_bromsvatska.HWPDM'
SWITCH_FIELDS = ('mode', 'pullResistor', 'activeLevel', 'thresholdVoltage',
                 'hysteresisVoltage', 'EMAValue', 'EMAEnabled')
BRAKE_DELAY_S = 2


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.20 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    CI_L, CI_R = v.caninput(4), v.caninput(5)
    assert cfg['CANInput'][3]['label'] == 'LowBeam_L_Cmd' and cfg['CANInput'][4]['label'] == 'LowBeam_R_Cmd'
    print('\n=== Ändringar ===')

    # 1. O2
    o2 = cfg['OutputHS'][1]
    assert o2['label'] == 'ALT_EXCITE' and o2['enabled'] is False
    assert o2['function'] == [7, 1, v.gf(1), 2, 10, 1, 1], o2['function']
    o2['enabled'] = True
    print(f'  O2  ALT_EXCITE: på (logik PWR_ALIVE, hög {o2["highFuse"]} A, topp {o2["peakFuse"]} A)')

    # 2. I13
    i13, i14 = cfg['Input'][12], cfg['Input'][13]
    assert i13['label'] == 'BRAKE_FAULT' and i14['label'] == 'OIL.PRESS'
    for f in SWITCH_FIELDS:
        i13[f] = i14[f]
    i13['turnOnDelay'] = BRAKE_DELAY_S
    i13['enabled'] = True
    print(f'  I13 BRAKE_FAULT: på, brytarbeteende från I14 (pull {i13["pullResistor"]}, aktiv låg, '
          f'tröskel {i13["thresholdVoltage"]} V), fördröjning {BRAKE_DELAY_S} s')

    # 3. O19
    o19, o9 = cfg['OutputHS'][18], cfg['OutputHS'][8]
    assert o19['label'] == 'REVERSE'
    o19['label'] = 'RESERVE19'
    o19['enabled'] = False
    o19['functionInfix'] = [[0]]
    o19['function'] = [1]
    assert o9['functionInfix'] == [[0]] and o9['function'] == [1]
    print('  O19 REVERSE -> RESERVE19: av, logik tömd')

    # 4. O14
    o14 = cfg['OutputHS'][13]
    assert o14['label'] == 'LOWBEAM_L'
    hits = [r for r in o14['functionInfix'] if L.is_term(r) and int(r[1]) == CI_R]
    assert len(hits) == 1, hits
    hits[0][1] = type(hits[0][1])(CI_L)
    o14['function'] = L.infix_to_function(o14['functionInfix'])
    print(f'  O14 LOWBEAM_L: CAN-grenen LowBeam_R_Cmd ({CI_R}) -> LowBeam_L_Cmd ({CI_L})')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    ints = lambda f: [x for x in f if isinstance(x, int)]
    return 0 if B.verify(DST, [
        ('O2 ALT_EXCITE på', lambda c: c['OutputHS'][1]['enabled'] is True),
        ('I13 = I14 brytarbeteende + 2 s', lambda c: c['Input'][12]['enabled'] is True
         and all(str(c['Input'][12][f]) == str(c['Input'][13][f]) for f in SWITCH_FIELDS)
         and int(c['Input'][12]['turnOnDelay']) == BRAKE_DELAY_S),
        ('O19 RESERVE19 av, ingen logik', lambda c: c['OutputHS'][18]['label'] == 'RESERVE19'
         and c['OutputHS'][18]['enabled'] is False and c['OutputHS'][18]['function'] == [1]),
        ('O14 vänster: LowBeam_L_Cmd, inte R', lambda c: CI_L in ints(c['OutputHS'][13]['function'])
         and CI_R not in ints(c['OutputHS'][13]['function'])),
        ('O15 höger: fortfarande LowBeam_R_Cmd', lambda c: CI_R in ints(c['OutputHS'][14]['function'])),
        ('v10.19 orört: TACH, ENGINE_RUN, 0x520', lambda c: c['Input'][6]['label'] == 'TACH'
         and c['GenericFunction'][14]['label'] == 'ENGINE_RUN'
         and int(c['CANOutput'][16]['variableNum'][2]) == v.input_frequency(7)),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
