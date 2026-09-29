"""v10.14 — tändspole och bensinpump: snabba omförsök + diagnosram.

Källa: v10.13 (det som ligger i PDM:en).

1. MOTORSTOPPEN 2026-09-29 (fångade på bussen, 0,1 s upplösning)
   18:16:24.5  O3 IGN_COIL status 1 -> 4 (Trip Under Voltage), 2,07 A -> 0 A
   18:16:26.5  O3 status 4 -> 1 — exakt clearTime (2 s) senare. Motorn redan död.
   Samtidigt: batteri stadigt 13,4 V, O5 pumpen gick hela tiden, PDM:en startade
   inte om, tändsignalen (C3) låg kvar. Bara O3 löste ut. Stoppet 18:00:36 har samma
   signatur. Orsaken sitter på O3:s krets (kortis mot jord / högspänningsläckage) och
   letas fysiskt — detta bygge gör bara att motorn överlever medan vi letar.

   O3 IGN_COIL och O5 FUEL:
     clearTime  2/3 s -> 0,1 s (vid tomgång ~3 uteblivna gnistor i stället för stopp)
     retries    3/2 -> 10      (GUI 1.3.1: 10 = "Infinite", configOutputs.js:1515.
                                Manualen säger 0 = oändligt, men GUI:t visar 0 som 0 —
                                10 är säkert åt båda hållen: minst 10 försök.)
   Med retries 3 låstes tändningen AV efter fjärde utlösningen tills nyckeln vreds om
   — farligt på väg. En äkta kortslutning skyddas fortfarande av utgångens egen
   strömbegränsning; tripMode Normal (manualen: "useful for ... ignition coils").

2. DIAGNOSRAM 0x520 PDM_EngineDiag (20 Hz) — så snabba omförsök inte döljer felet
     O3 tripCount, O5 tripCount (16 bit, rått antal)
     O3 spänning, O5 spänning (16 bit mV, x1000 — V som flyttal i PDM:en)
   tripCount = output[n].HS.tripCount (variables.js:1757), var 74+7(n-1) i gamla schemat.

    python build_v10.14_tandning_retry.py            # torrkörning
    python build_v10.14_tandning_retry.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.13_stralkastare.HWPDM'
DST = r'Builds\Elton_v10.14_tandning_retry.HWPDM'

ENGINE = {3: 'IGN_COIL', 5: 'FUEL'}
CLEAR_S = 0.1
RETRIES = 10
FMT16 = 2
DIAG_SLOT, DIAG_ID, DIAG_HZ = 17, 0x520, 20


def set_canoutput(cfg, slot, label, can_id, hz, entries):
    """Samma som v10.11/v10.13 — bevisat att överleva flash via GUI:t."""
    co = cfg['CANOutput'][slot - 1]
    assert not co.get('label'), f'CANOutput {slot} upptagen ({co.get("label")!r})'
    total = 2 * len(entries)
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
        var, fmt, mult = entries[i] if i < len(entries) else (1, 1, 1)
        co['variableNum'][i] = type(co['variableNum'][i])(var)
        co['dataFormat'][i] = type(co['dataFormat'][i])(fmt)
        co['dataMultiplier'][i] = type(co['dataMultiplier'][i])(mult)
    return total


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.14 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')

    for n, label in ENGINE.items():
        o = cfg['OutputHS'][n - 1]
        assert o['label'] == label, f'O{n} är {o["label"]!r}, väntade {label!r}'
        old = (o['clearTime'], o['retries'])
        # Typerna blandas i filen: GUI-sparade poster har strängar ('2', '0.3'), andra int.
        # O3:s clearTime är int 2 och set_field vägrar (rätt) avrunda 0,1 dit. Skriv GUI:ts
        # egen form — sträng — som O5 och alla GUI-sparade utgångar redan har.
        o['clearTime'] = str(CLEAR_S)
        B.set_field(o, 'retries', RETRIES)
        print(f'  O{n} {label:<9} clearTime {old[0]} -> {o["clearTime"]} s, retries {old[1]} -> '
              f'{o["retries"]}   (tripMode {o["tripMode"]}, hög {o["highFuse"]} A orört)')

    entries = [(v.output_tripcount(3), FMT16, 1), (v.output_tripcount(5), FMT16, 1),
               (v.output_voltage(3), FMT16, 1000), (v.output_voltage(5), FMT16, 1000)]
    set_canoutput(cfg, DIAG_SLOT, 'PDM_EngineDiag', DIAG_ID, DIAG_HZ, entries)
    print(f'  CANOutput {DIAG_SLOT}: 0x{DIAG_ID:03X} PDM_EngineDiag {DIAG_HZ} Hz — '
          f'O3/O5 tripCount (var {entries[0][0]}, {entries[1][0]}), '
          f'O3/O5 spänning mV (var {entries[2][0]}, {entries[3][0]})')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(v, entries)) else 1


def checks(v, entries):
    return [
        ('O3/O5 clearTime 0,1 s',
         lambda c: all(float(c['OutputHS'][n - 1]['clearTime']) == CLEAR_S for n in ENGINE)),
        ('O3/O5 retries 10 (Infinite)',
         lambda c: all(int(float(c['OutputHS'][n - 1]['retries'])) == RETRIES for n in ENGINE)),
        ('O3/O5 fortfarande enabled',
         lambda c: all(c['OutputHS'][n - 1]['enabled'] is True for n in ENGINE)),
        ('tripCount-variablerna ligger mellan status och nästa utgång',
         lambda c: v.output_tripcount(3) == v.output_status(3) + 1
         and v.output_current(4) == v.output_tripcount(3) + 3),
        ('0x520 PDM_EngineDiag',
         lambda c: (c['CANOutput'][DIAG_SLOT - 1]['label'] == 'PDM_EngineDiag'
                    and int(c['CANOutput'][DIAG_SLOT - 1]['CANID']) == DIAG_ID
                    and [int(x) for x in c['CANOutput'][DIAG_SLOT - 1]['variableNum'][:4]]
                    == [e[0] for e in entries])),
        ('v10.13 orört: strålkastare 35 A / 500 ms, 0x51F',
         lambda c: float(c['OutputHS'][13]['peakFuse']) == 35
         and int(c['OutputHS'][13]['PWMSoftStartTime']) == 500
         and c['CANOutput'][15]['label'] == 'PDM_InVolt'),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
