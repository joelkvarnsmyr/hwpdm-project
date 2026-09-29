"""v10.17 — handbroms + dörrar på samma ingång (I16 / C1), spänningsavkodad.

Källa: v10.16. FLASHA FÖRST NÄR MOTSTÅNDEN SITTER — utan pull-up flyter C1 på
~1,9 V, vilket avkodas som "handbroms i + dörr öppen".

KOPPLING (Givarkopplingar-sidan, 2026-09-29)
  C10 5V -> 5,6 kΩ -> C1.  C1 -> 5,6 kΩ -> F9 handbroms -> jord.
  C1 -> 10 kΩ -> alla dörrkontakter parallellt -> jord.  Ingen diod (taklampan
  sitter inte på dörrkontakterna).
  Räknat: 5,00 V allt stängt · 3,21 V dörr · 2,50 V handbroms · 1,95 V båda.

AVKODNING (trösklar mitt emellan, 0,1 V-steg — logikeditorn lagrar konstanter ×10)
  > 4,2 V           allt stängt
  2,9–4,2 V         dörr öppen
  2,2–2,9 V         handbroms i
  1,0–2,2 V         handbroms i + dörr öppen
  < 1,0 V           fel (kabel mot jord före motstånden / kortslutning)
  Trösklarna justeras efter uppmätta värden i 0x51F när allt sitter.

NAMN
  I16   HANDBRAKE_DOOR   (analog, ingen pull)
  GF10  HANDBRAKE        1,0 < V < 2,9           handbromsen i, oavsett dörr
  GF11  DOOR_ONLY        2,9 < V < 4,2           hjälpfunktion
  GF12  DOOR_WITH_HB     1,0 < V < 2,2           hjälpfunktion
  GF13  DOOR_OPEN        GF11 OR GF12            någon dörr öppen
  GF14  HB_DOOR_FAULT    V < 1,0
  DOOR_OPEN delas i två rena AND-kedjor + ett rent OR, så resultatet inte beror på
  hur firmware prioriterar AND/OR i en blandad kedja.

CAN 0x511 PDM_Status (6 -> 8 byte)
  byte 5  HANDBRAKE      (var I16-status — samma betydelse för dashboarden)
  byte 6  DOOR_OPEN      nytt
  byte 7  HB_DOOR_FAULT  nytt

    python build_v10.17_handbroms_dorr.py            # torrkörning
    python build_v10.17_handbroms_dorr.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.16_tuta_fix.HWPDM'
DST = r'Builds\Elton_v10.17_handbroms_dorr.HWPDM'
SCALE = 10                      # logikeditorn: konstant lagras ×10
GT, LT, EQ = 6, 8, 10
AND, OR = [2, 1], [2, 2]        # GF-funktioner lagras med heltal (som GF3/GF4)


def cmp(var, op, volts):
    return [1, int(var), 2, op, 3, int(round(volts * SCALE))]


def flat(terms, joiner):
    body = []
    for i, t in enumerate(terms):
        if i:
            body += joiner
        body += t
    return [len(body) + 1] + body


def set_gf(cfg, n, label, function):
    g, tmpl = cfg['GenericFunction'][n - 1], cfg['GenericFunction'][8]   # GF9 = mall
    assert not g.get('label'), f'GF{n} upptagen ({g.get("label")!r})'
    g['label'] = label
    g['enabled'] = type(tmpl['enabled'])(True)
    g['visibleInDOM'] = type(tmpl['visibleInDOM'])(1)
    g['function'] = function
    g['functionInfix'] = []


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.17 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')

    i16 = cfg['Input'][15]
    assert i16['label'] == 'HANDBRAKE', i16['label']
    i16['label'] = 'HANDBRAKE_DOOR'
    i16['mode'] = type(i16['mode'])(2)
    i16['pullResistor'] = type(i16['pullResistor'])(0)
    print(f'  I16: HANDBRAKE -> HANDBRAKE_DOOR, mode {i16["mode"]} (analog), pull {i16["pullResistor"]}')

    V = v.input_voltage(16)
    gfs = [
        (10, 'HANDBRAKE',     flat([cmp(V, GT, 1.0), cmp(V, LT, 2.9)], AND)),
        (11, 'DOOR_ONLY',     flat([cmp(V, GT, 2.9), cmp(V, LT, 4.2)], AND)),
        (12, 'DOOR_WITH_HB',  flat([cmp(V, GT, 1.0), cmp(V, LT, 2.2)], AND)),
        (13, 'DOOR_OPEN',     flat([[1, v.gf(11), 2, EQ, 1, 1], [1, v.gf(12), 2, EQ, 1, 1]], OR)),
        (14, 'HB_DOOR_FAULT', flat([cmp(V, LT, 1.0)], AND)),
    ]
    for n, label, fn in gfs:
        set_gf(cfg, n, label, fn)
        print(f'  GF{n:<2} {label:<14} {fn}')

    co = cfg['CANOutput'][1]
    assert co['label'] == 'PDM_Status' and int(co['payloadSize']) == 6
    # OBS: listplats != byte. Plats 0 är batteriet i 16 bit (byte 0–1), så plats 4 =
    # byte 5. Plats 4 var I16-status (handbromsen) och byts mot GF10 med samma betydelse.
    for slot, var in ((4, v.gf(10)), (5, v.gf(13)), (6, v.gf(14))):
        co['variableNum'][slot] = type(co['variableNum'][slot])(var)
        co['dataFormat'][slot] = type(co['dataFormat'][slot])(1)
        co['dataMultiplier'][slot] = type(co['dataMultiplier'][slot])(1)
    size = {1: 1, 2: 2}
    assert sum(size[int(f)] for f in co['dataFormat'][:7]) == 8, 'plats 0–6 ska bli exakt 8 byte'
    B.set_field(co, 'payloadSize', 8)
    print(f'  0x511 PDM_Status: 8 byte — b5 HANDBRAKE (GF10), b6 DOOR_OPEN (GF13), b7 HB_DOOR_FAULT (GF14)')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(v, gfs)) else 1


def checks(v, gfs):
    return [
        ('I16 analog, HANDBRAKE_DOOR', lambda c: str(c['Input'][15]['mode']) == '2'
         and c['Input'][15]['label'] == 'HANDBRAKE_DOOR'),
        ('GF10–14 på plats', lambda c: all(c['GenericFunction'][n - 1]['label'] == lab
                                           and c['GenericFunction'][n - 1]['function'] == fn
                                           for n, lab, fn in gfs)),
        ('funktionslängd = första elementet', lambda c: all(
            c['GenericFunction'][n - 1]['function'][0] == len(c['GenericFunction'][n - 1]['function'])
            for n, *_ in gfs)),
        ('trösklar lagrade ×10 (1,0 V = 10)', lambda c: 10 in c['GenericFunction'][9]['function']
         and 29 in c['GenericFunction'][9]['function']),
        ('0x511 byte 5–7 = plats 4–6 (plats 0 är 16 bit)',
         lambda c: [int(x) for x in c['CANOutput'][1]['variableNum'][4:7]] == [v.gf(10), v.gf(13), v.gf(14)]
         and [int(x) for x in c['CANOutput'][1]['dataFormat'][:7]] == [2, 1, 1, 1, 1, 1, 1]
         and int(c['CANOutput'][1]['payloadSize']) == 8),
        ('I16-status inte längre i 0x511', lambda c: v.input_status(16) not in
         [int(x) for x in c['CANOutput'][1]['variableNum'][:7]]),
        ('0x511 byte 0–4 orörda (batteri, stöt, rollover, olja)',
         lambda c: [int(x) for x in c['CANOutput'][1]['variableNum'][:4]] == [6, 82, 83, v.input_status(14)]),
        ('0x51F mäter fortfarande I16-spänningen', lambda c: int(c['CANOutput'][15]['variableNum'][3]) == v.input_voltage(16)),
        ('v10.16 orört: tutan 5000', lambda c: 5000 in [x for x in c['OutputHS'][16]['function'] if isinstance(x, int)]),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
