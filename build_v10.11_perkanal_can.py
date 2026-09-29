"""v10.11 — per-kanalstatus via CAN-utgangar + handbromsen som oljetrycket.

1. PER-KANALDATA FLYTTAS TILL CAN-UTGANGAR
   Konfigurator 1.3.1 tommer streamens per-kanalramar (bugg: configCANStream.js:191
   + getNameWithoutLabel, se project-minnet). Verifierat pa bussen 2026-09-29: alla
   ramar 0x1006-0x1032 ar 00..00. Buggen kors vid VARJE spara och sandning, sa den
   gar inte att ratta i filen.

   Beslut (Joel lat mig valja): CAN-utgangar i stallet for att patcha appen.
     - CAN-utgangar laser tillbaka variabeln som numeriskt `value` ur GUI:t
       (configCANOutputs.js) — 0x510/0x511 overlevde en flash via GUI:t och visar
       ratt varden pa bussen.
     - En patchad app skrivs over tyst av auto-uppdateringen (app-update.yml).
     - Streamen far sta kvar: ram 0x1000-0x1002 har data, och fixar Hardwire
       buggen kommer resten tillbaka.

   Samma variabler som streamen hade — samma betydelse for dashboarden.
     0x512-0x515  PDM_OutStatus_1..4   status O1-O25, 8 bit, 10 Hz
     0x516-0x517  PDM_InStatus_1..2    status I1-I16, 8 bit, 10 Hz
     0x518-0x51E  PDM_OutCurrent_1..7  strom O1-O25, 16 bit mA (x1000), 5 Hz
   Utgangsstrom ar AMPERE SOM FLYTTAL i PDM:en (output.HS.current*0.001) —
   darfor x1000, annars skickas hela ampere. Samma falla som batterispanningen.
   Alla 41 variabelnummer kontrollerade mot appens variables.js, 0 avvikelser.

2. HANDBROMSEN (I16) = OLJETRYCKETS INSTALLNINGAR
   I16 laste 1 (atdragen) utan kabel. v10.7 hade vant activeLevel enligt GUI:ts
   etiketter, men de beter sig inte som de ar markta i bilen. I16 hade dessutom
   arvt bromsljusets troskel 6 V / hysteres 1 V. I14 OIL.PRESS sitter pa samma
   typ av jordande brytare och ar VERIFIERAD i bilen — dess brytarbeteende kopieras
   rakt av. Kontroll efter flash: utan kabel ska handbromsen lasa 0.

    python build_v10.11_perkanal_can.py            # torrkorning
    python build_v10.11_perkanal_can.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.10_sc2_volt.HWPDM'
DST = r'Builds\Elton_v10.11_perkanal_can.HWPDM'

FMT8, FMT16 = 1, 2
SWITCH_FIELDS = ('mode', 'pullResistor', 'activeLevel', 'thresholdVoltage',
                 'hysteresisVoltage', 'turnOnDelay', 'EMAValue', 'EMAEnabled')


def set_canoutput(cfg, slot, label, can_id, hz, entries):
    co = cfg['CANOutput'][slot - 1]
    assert not co.get('label'), f'CANOutput {slot} upptagen ({co.get("label")!r})'
    size = {FMT8: 1, FMT16: 2}
    total = sum(size[f] for _, f, _ in entries)
    assert total <= 8
    co['label'] = label
    B.set_field(co, 'CANID', can_id)
    B.set_field(co, 'frequency', hz)
    B.set_field(co, 'CANChannel', 1)
    B.set_field(co, 'format', 0)
    B.set_field(co, 'sendMode', 0)
    B.set_field(co, 'payloadSize', total)
    B.set_field(co, 'enabled', True)
    B.set_field(co, 'visibleInDOM', True)
    for i in range(8):
        var, fmt, mult = entries[i] if i < len(entries) else (1, FMT8, 1)
        co['variableNum'][i] = type(co['variableNum'][i])(var)
        co['dataFormat'][i] = type(co['dataFormat'][i])(fmt)
        co['dataMultiplier'][i] = type(co['dataMultiplier'][i])(mult)
    return total


def plan(v):
    """(slot, label, id, hz, entries) for varje ny ram."""
    frames = []
    slot = 3
    for k, first in enumerate(range(1, 26, 8)):                      # status O1-O25
        outs = list(range(first, min(first + 8, 26)))
        frames.append((slot, f'PDM_OutStatus_{k+1}', 0x512 + k, 10,
                       [(v.output_status(n), FMT8, 1) for n in outs])); slot += 1
    for k, first in enumerate((1, 9)):                               # status I1-I16
        frames.append((slot, f'PDM_InStatus_{k+1}', 0x516 + k, 10,
                       [(v.input_status(n), FMT8, 1) for n in range(first, first + 8)])); slot += 1
    for k, first in enumerate(range(1, 26, 4)):                      # strom O1-O25
        outs = list(range(first, min(first + 4, 26)))
        frames.append((slot, f'PDM_OutCurrent_{k+1}', 0x518 + k, 5,
                       [(v.output_current(n), FMT16, 1000) for n in outs])); slot += 1
    return frames


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.11 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Andringar ===')

    # ── 1. CAN-utgangar ─────────────────────────────────────────────────────
    frames = plan(v)
    for slot, label, cid, hz, entries in frames:
        n = set_canoutput(cfg, slot, label, cid, hz, entries)
        print(f'  CANOutput {slot:>2}: 0x{cid:03X} {label:<17} {hz:>2} Hz  {n} byte')
    load = sum(hz for *_, hz, _ in frames)
    print(f'  = {len(frames)} ramar, {load} ramar/s extra pa bussen')

    # ── 2. handbromsen ──────────────────────────────────────────────────────
    i14, i16 = cfg['Input'][13], cfg['Input'][15]
    assert i14['label'] == 'OIL.PRESS' and i16['label'] == 'HANDBRAKE'
    # Kopiera KALLANS typ: I14 ar den bevisat fungerande konfigurationen, och
    # set_field skulle vagra 0.5 -> int (I16:s hysteres ar lagrad som heltal).
    for f in SWITCH_FIELDS:
        if f in i14 and f in i16:
            i16[f] = i14[f]
    print(f'  I16 HANDBRAKE: brytarbeteende kopierat fran I14 OIL.PRESS — '
          f'pull={i16["pullResistor"]} activeLevel={i16["activeLevel"]} '
          f'troskel={i16["thresholdVoltage"]} V hysteres={i16["hysteresisVoltage"]} V')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkorning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(v, frames)) else 1


def checks(v, frames):
    ck = []
    for slot, label, cid, hz, entries in frames:
        def f(c, slot=slot, label=label, cid=cid, entries=entries):
            co = c['CANOutput'][slot - 1]
            return (co['label'] == label and int(co['CANID']) == cid and co['enabled'] is True
                    and [int(x) for x in co['variableNum'][:len(entries)]] == [e[0] for e in entries])
        ck.append((f'0x{cid:03X} {label}', f))
    ck += [
        ('stromramar skickar mA (x1000)',
         lambda c: all(float(c['CANOutput'][s - 1]['dataMultiplier'][0]) == 1000
                       for s, lab, *_ in frames if 'Current' in lab)),
        ('0x510/0x511 orörda', lambda c: c['CANOutput'][0]['label'] == 'PDM_Sensors'
                                         and c['CANOutput'][1]['label'] == 'PDM_Status'),
        ('O24 TURN_R status ar var 255 (verifierad mot appen)',
         lambda c: 255 in [int(x) for x in c['CANOutput'][4]['variableNum']]),
        ('I16 = I14 brytarbeteende',
         lambda c: all(str(c['Input'][15][f]) == str(c['Input'][13][f])
                       for f in SWITCH_FIELDS if f in c['Input'][13])),
        ('I14 oljetrycket orort', lambda c: c['Input'][13]['label'] == 'OIL.PRESS'),
        ('streamen fortfarande pa', lambda c: c['CANStream']['enabled'] is True),
        ('bransle SC2 i volt kvar',
         lambda c: float(c['SensorCalibration'][1]['rawSensorDataPoint'][0]) < 1),
        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]
    return ck


if __name__ == '__main__':
    raise SystemExit(main())
