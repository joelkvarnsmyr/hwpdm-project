"""v10.8 — etapp 1 i sin helhet. Rena konfigurationsandringar, ingen hardvara.

1  SYMMETRISERA LAMPPAREN
   O7 HIBEAM_R och O16 HIBEAM_L driver identiska H4-lampor men hade:
       O16: high 5.8 A  peak 20.8 A  tid 0.3 s  softstart 100  lowFuse 0
       O7 : high 13  A  peak 40   A  tid 0.2 s  softstart 0    lowFuse 0.5
   En H4 helljus drar ~5 A, sa 5.8 A ar det riktiga vardet och 13 A skyddar
   ingenting. (13 A satte JAG i v10.1 som "pinnens tak" utan att titta pa
   tvillingen — mitt fel.) O7 far O16:s varden. Samma for halvljusets softstart.

2  lowFuse-POLICY: bara dar EN utgang driver ETT don
   Manualen: lowFuse TRIPPAR utgangen, den varnar inte. For en trasig lampa ar
   det baklanges — man vill veta om det, inte forlora kretsen.
       Behalls:  O14/O15 halvljus, O7/O16 helljus (en lampa per utgang → en
                 trippad utgang ar redan slackt, och trippstatusen sager VILKEN)
       Nollas:   O6 BRAKE (M9+M10), O19 REVERSE (M16+M17), O24/O25 blinkers
                 (fram+bak) — flera lampor per utgang, sa troskeln kan antingen
                 inte se ett enskilt haveri eller slacker de fungerande med.
   Lampovervakningen flyttas till Pi:n via stromtelemetrin (se CAN nedan).

3  CAN-UTGANGAR — 0 av 100 anvandes
   Pi:n fick bara den forformaterade strommen med RAA millivolt och maste
   dubblera hela kalibreringen som redan finns i PDM:en.
       0x510 PDM_Sensors  32-bit SC1 (grader x1000) + 32-bit SC2 (ml)
       0x511 PDM_Status   batterispanning, IMU-flaggor, oljetryck, handbroms

4  IMU: flaggorna exponeras, ingen automatisk frankoppling byggs
   Impact- och rollover-detektering var pa men INGEN logik last flaggorna. Att
   bygga en otestad motoravstangning pa en IMU vars referensram inte ens ar satt
   (zeroSet=false) vore vardslost. Flaggorna gar i stallet ut pa CAN sa Pi:n kan
   varna. ⚠ Referensramen maste nollstallas i GUI:t med fordonet plant.

5  Timer3 START_GRACE + GF3 OIL_OK
   Timer3 fanns men var avstangd, och GF3 saknade grace-fonstret helt.
       GF3 OIL_OK = (I14 == False)  ELLER  (Timer3 > 0)
   Timer3 startar pa I15 START och raknar 5000 ms med resetOnEnd, sa "> 0"
   ar sant precis under uppstartsfonstret. Utan det larmar oljetrycket varje
   gang nyckeln vrids om, innan motorn byggt tryck.

6  LoggingGroup 3 "FAULT_HUNT"
   128 Mb internminne, 2 av 30 grupper anvanda. Tva oforklarade intermittenta
   fel den har veckan hade bada fangats av en logg som gar utan att nagon sitter
   uppkopplad: batterispanning, LightShow_Enable, start, oljetryck, bada
   sensorkurvorna.

7  O2 ALT_EXCITE stangs av
   Den var PA utan att 82 ohm var monterad — utgangen matade ut i tomma luften.
   Generatorn visade sig dessutom fungera sa fort B+ kopplades in, sa
   magnetiseringen behovs kanske inte alls. Enables igen nar motstandet sitter.

    python build_v10.8_etapp1.py            # torrkorning
    python build_v10.8_etapp1.py --write    # bygg
"""
import copy
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.7_stadning.HWPDM'
DST = r'Builds\Elton_v10.8_etapp1.HWPDM'

# fasta variabel-ID i 1.3.1-schemat (variables.js)
VAR_BATT = 6        # Battery Voltage
VAR_IMPACT = 82     # IMU Impact Trigger
VAR_ROLLOVER = 83   # IMU Rollover Trigger
VAR_SC1 = 781       # Sensor Calibration 1 utvarde (kylvatten, grader x1000)
VAR_SC2 = 782       # Sensor Calibration 2 utvarde (bransle, ml)

ID_SENSORS, ID_STATUS = 0x510, 0x511
FMT8, FMT16, FMT32 = 1, 2, 3


def set_canoutput(cfg, slot, label, can_id, hz, entries):
    """Fyll en tom CAN-utgang genom att utga fran dess egen mall.

    entries = [(variabel, dataFormat, multiplikator), ...]  max 8 slots.
    payloadSize raknas ur formaten: 8-bit=1, 16-bit=2, 32-bit=4 byte.
    """
    co = cfg['CANOutput'][slot - 1]
    assert not co.get('label'), f'CANOutput {slot} ar upptagen ({co.get("label")!r})'
    size = {FMT8: 1, FMT16: 2, FMT32: 4}
    total = sum(size[f] for _, f, _ in entries)
    assert total <= 8, f'{total} byte far inte plats i en CAN-ram'

    co['label'] = label
    B.set_field(co, 'CANID', can_id)
    B.set_field(co, 'frequency', hz)
    B.set_field(co, 'CANChannel', 1)
    B.set_field(co, 'format', 0)        # Standard 11-bit
    B.set_field(co, 'sendMode', 0)      # Periodisk
    B.set_field(co, 'payloadSize', total)
    B.set_field(co, 'enabled', True)
    B.set_field(co, 'visibleInDOM', True)
    for i in range(8):
        var, fmt, mult = entries[i] if i < len(entries) else (1, FMT8, 1)
        co['variableNum'][i] = type(co['variableNum'][i])(var)
        co['dataFormat'][i] = type(co['dataFormat'][i])(fmt if i < len(entries) else 1)
        co['dataMultiplier'][i] = type(co['dataMultiplier'][i])(mult)
    return total


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.8 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    O = cfg['OutputHS']
    print('\n=== Andringar ===')

    # ── 1. symmetrisera lampparen ───────────────────────────────────────────
    src, dst = O[15], O[6]          # O16 HIBEAM_L -> O7 HIBEAM_R
    assert src['label'] == 'HIBEAM_L' and dst['label'] == 'HIBEAM_R'
    for f in ('highFuse', 'peakFuse', 'peakFuseTime', 'PWMSoftStartEnable', 'PWMSoftStartTime'):
        B.set_field(dst, f, src[f])
    print(f'  O7 HIBEAM_R: speglad fran O16 — high {dst["highFuse"]} A, '
          f'peak {dst["peakFuse"]} A, tid {dst["peakFuseTime"]} s, softstart {dst["PWMSoftStartTime"]}')
    B.set_field(O[14], 'PWMSoftStartEnable', O[13]['PWMSoftStartEnable'])
    B.set_field(O[14], 'PWMSoftStartTime', O[13]['PWMSoftStartTime'])
    print(f'  O15 LOWBEAM_R: softstart {O[14]["PWMSoftStartTime"]} (matchar O14)')

    # ── 2. lowFuse-policy ───────────────────────────────────────────────────
    for idx, why in ((5, 'M9+M10'), (18, 'M16+M17'), (23, 'fram+bak'), (24, 'fram+bak')):
        if float(O[idx]['lowFuse'] or 0):
            old = O[idx]['lowFuse']
            B.set_field(O[idx], 'lowFuse', 0)
            print(f'  O{idx+1} {O[idx]["label"]}: lowFuse {old} -> 0 ({why}, flera lampor)')
    for idx in (6, 15):
        B.set_field(O[idx], 'lowFuse', 1)
    print(f'  O7/O16 helljus: lowFuse -> 1 A (en lampa per utgang = brukbar lampdetektering)')

    # ── 3+4. CAN-utgangar ───────────────────────────────────────────────────
    n1 = set_canoutput(cfg, 1, 'PDM_Sensors', ID_SENSORS, 5, [
        (VAR_SC1, FMT32, 1),        # kylvatten, grader x1000
        (VAR_SC2, FMT32, 1),        # bransle, ml
    ])
    n2 = set_canoutput(cfg, 2, 'PDM_Status', ID_STATUS, 5, [
        # var 6 ar VOLT som flyttal (batteryVoltage*0.001). Multiplikator 1 hade
        # skickat 13 — hela volt. x1000 ger millivolt, 13300 ryms i 16 bit.
        (VAR_BATT, FMT16, 1000),
        (VAR_IMPACT, FMT8, 1),
        (VAR_ROLLOVER, FMT8, 1),
        (v.input_status(14), FMT8, 1),   # oljetryck
        (v.input_status(16), FMT8, 1),   # handbroms
    ])
    print(f'  CANOutput 1: 0x{ID_SENSORS:03X} PDM_Sensors, 5 Hz, {n1} byte (SC1 + SC2, 32-bit)')
    print(f'  CANOutput 2: 0x{ID_STATUS:03X} PDM_Status,  5 Hz, {n2} byte '
          f'(batteri, IMU-stot, IMU-rollover, olja, handbroms)')

    # ── 5. Timer3 + GF3 ─────────────────────────────────────────────────────
    t3 = cfg['Timer'][2]
    assert t3['label'] == 'START_GRACE'
    t3['enabled'] = True
    B.set_field(t3, 'visibleInDOM', 1)
    gf3 = cfg['GenericFunction'][2]
    assert gf3['label'] == 'OIL_OK'
    i14, t3v = v.input_status(14), v.timer(3)
    gf3['function'] = [15, 1, i14, 2, 10, 1, 2, 2, 2, 1, t3v, 2, 6, 3, 0]
    gf3['enabled'] = True
    B.set_field(gf3, 'visibleInDOM', 1)
    print(f'  Timer3 START_GRACE: aktiverad ({t3["duration"]} ms, resetOnEnd={t3["resetOnEnd"]})')
    print(f'  GF3 OIL_OK: (I14 == False) ELLER (Timer3 > 0)  — grace-fonstret pa plats')

    # ── 6. loggning ─────────────────────────────────────────────────────────
    lg = cfg['LoggingGroup'][2]
    assert not lg.get('label'), f'LoggingGroup 3 ar upptagen ({lg.get("label")!r})'
    tmpl = cfg['LoggingGroup'][1]
    cfg['LoggingGroup'][2] = copy.deepcopy(tmpl)
    lg = cfg['LoggingGroup'][2]
    lg['label'] = 'FAULT_HUNT'
    watch = [VAR_BATT, v.caninput(1), v.input_status(15), i14, VAR_SC1, VAR_SC2]
    lg['variableList'] = [len(watch) + 1] + [type(tmpl['variableList'][1])(x) for x in watch]
    lg['enabled'] = True
    print(f'  LoggingGroup 3 FAULT_HUNT: {len(watch)} variabler '
          f'(batteri, LightShow_Enable, START, olja, SC1, SC2)')

    # ── 7. generatormagnetiseringen ─────────────────────────────────────────
    o2 = O[1]
    assert o2['label'] == 'ALT_EXCITE'
    B.set_field(o2, 'enabled', False)
    print('  O2 ALT_EXCITE: avstangd tills 82 ohm ar monterad')

    L.roundtrip_check(cfg)

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(v, i14, t3v)) else 1


def checks(v, i14, t3v):
    F = ('highFuse', 'peakFuse', 'peakFuseTime', 'PWMSoftStartTime')
    return [
        ('helljusparet identiskt konfigurerat',
         lambda c: all(str(c['OutputHS'][6][f]) == str(c['OutputHS'][15][f]) for f in F)),
        ('O7 highFuse nere pa 5.8 A', lambda c: float(c['OutputHS'][6]['highFuse']) == 5.8),
        ('halvljusparets softstart lika',
         lambda c: str(c['OutputHS'][14]['PWMSoftStartTime']) == str(c['OutputHS'][13]['PWMSoftStartTime'])),
        ('lowFuse nollad pa flerlampsutgangar',
         lambda c: all(float(c['OutputHS'][i]['lowFuse'] or 0) == 0 for i in (5, 18, 23, 24))),
        ('lowFuse kvar pa enlampsutgangar',
         lambda c: all(float(c['OutputHS'][i]['lowFuse'] or 0) > 0 for i in (6, 13, 14, 15))),
        ('0x510 PDM_Sensors aktiv, 8 byte',
         lambda c: (c['CANOutput'][0]['label'] == 'PDM_Sensors'
                    and int(c['CANOutput'][0]['CANID']) == ID_SENSORS
                    and int(c['CANOutput'][0]['payloadSize']) == 8
                    and c['CANOutput'][0]['enabled'] is True)),
        ('0x510 bar SC1 och SC2 som 32-bit',
         lambda c: ([int(x) for x in c['CANOutput'][0]['variableNum'][:2]] == [VAR_SC1, VAR_SC2]
                    and [int(x) for x in c['CANOutput'][0]['dataFormat'][:2]] == [FMT32, FMT32])),
        ('0x511 PDM_Status aktiv, 6 byte',
         lambda c: (c['CANOutput'][1]['label'] == 'PDM_Status'
                    and int(c['CANOutput'][1]['CANID']) == ID_STATUS
                    and int(c['CANOutput'][1]['payloadSize']) == 6)),
        ('0x511 bar batteri + bada IMU-flaggorna',
         lambda c: {VAR_BATT, VAR_IMPACT, VAR_ROLLOVER} <=
                   {int(x) for x in c['CANOutput'][1]['variableNum']}),
        ('batterispanning skickas i mV (x1000)',
         lambda c: [int(x) for x in c['CANOutput'][1]['variableNum']][0] == VAR_BATT
                   and float(c['CANOutput'][1]['dataMultiplier'][0]) == 1000),
        ('Timer3 START_GRACE aktiv', lambda c: c['Timer'][2]['enabled'] is True),
        ('GF3 OIL_OK aktiv med grace-gren',
         lambda c: (c['GenericFunction'][2]['enabled'] is True
                    and t3v in [int(x) for x in c['GenericFunction'][2]['function']]
                    and i14 in [int(x) for x in c['GenericFunction'][2]['function']])),
        ('LoggingGroup 3 FAULT_HUNT aktiv med 6 variabler',
         lambda c: (c['LoggingGroup'][2]['label'] == 'FAULT_HUNT'
                    and c['LoggingGroup'][2]['enabled'] is True
                    and len(c['LoggingGroup'][2]['variableList']) == 7
                    and int(c['LoggingGroup'][2]['variableList'][0]) == 7)),
        ('O2 ALT_EXCITE avstangd', lambda c: c['OutputHS'][1]['enabled'] is False),

        # ── inget av det tidigare rort ──
        ('O5 FUEL enabled, bara GF1',
         lambda c: c['OutputHS'][4]['enabled'] is True
                   and len([r for r in c['OutputHS'][4]['functionInfix'] if L.is_term(r)]) == 1),
        ('I16 HANDBRAKE Active Low', lambda c: int(c['Input'][15]['activeLevel']) == 1),
        ('I8 FUEL_LEVEL analog', lambda c: c['Input'][7]['label'] == 'FUEL_LEVEL'),
        ('I1 WASHER kvar', lambda c: c['Input'][0]['label'] == 'WASHER'),
        ('GF9 LOAD_OK pa alla fyra lampor',
         lambda c: all(any(int(r[1]) == v.gf(9) for r in c['OutputHS'][i]['functionInfix'] if L.is_term(r))
                       for i in (13, 14, 6, 15))),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
