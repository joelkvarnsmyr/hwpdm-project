"""v10.19 — varvräknare från tändspolens kl.1 på I7 (A10).

Källa: v10.18 (det som ligger i PDM:en). Flasha när kopplingen sitter.

KOPPLING (Givarkopplingar-sidan, 2026-09-29)
  spolen kl.1 -> 100 kΩ (VID SPOLEN) -> kabel -> A10.
  Vid A10: zener 12 V (BZX55C12V, ring mot A10) och 10 nF X7R, båda mot PDM-jord.
  Motståndet sitter vid spolen: skaver kabeln mot jord kortsluts inte kl.1.

PDM:EN
  Alla ingångar mäter frekvens (variables.js: input[n].frequency, Hz, 0–3000).
  Per ingång: voltage, frequency, status, onTime, offTime -> frequency = 556+5n.
  4-cyl fyrtakt = 2 gnistor per varv -> rpm = Hz × 30 (tomgång 850 rpm ≈ 28 Hz).

  I7   REVERSE -> TACH: enabled, digital, ingen pull, aktiv hög, tröskel 2,5 V,
       EMA AV (utjämning skulle sudda ut pulserna). Tröskeln justeras efter mätning:
       ingången belastar ~55 kΩ, så 12 V genom 100 kΩ ger bara ~4 V i vila.
  GF15 ENGINE_RUN = I7-frekvens > 10 Hz (300 rpm). Konstant lagras ×10 -> 100.
  O19  REVERSE: grenen "I7 status AND T2==False" tas bort — annars blinkar backljusen
       med tändpulserna. Kvar: LightShow_Enable AND Reverse_Lights_Cmd (CAN).
  0x520 PDM_EngineDiag: plats 2–3 (utgångsspänning, stöds inte, alltid 0) ersätts:
       byte 4–5 Engine_RPM   = I7-frekvens × 30  (u16, rpm)
       byte 6–7 Engine_Running = GF15              (u16, 0/1)

    python build_v10.19_varvraknare.py            # torrkörning
    python build_v10.19_varvraknare.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.18_hb_dorr_trosklar.HWPDM'
DST = r'Builds\Elton_v10.19_varvraknare.HWPDM'
SCALE = 10                  # logikeditorn lagrar konstanter ×10
SPARKS_PER_REV = 2          # 4-cyl fyrtakt
RUN_HZ = 10                 # 300 rpm
THRESHOLD_V = 2.5
FMT16 = 2


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.19 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    F7, S7 = v.input_frequency(7), v.input_status(7)
    assert (F7, S7) == (v.input_voltage(7) + 1, v.input_voltage(7) + 2)
    print('\n=== Ändringar ===')

    # ── I7 -> TACH ──────────────────────────────────────────────────────────
    i7 = cfg['Input'][6]
    assert i7['label'] == 'REVERSE' and i7['enabled'] is False, i7['label']
    i7['label'] = 'TACH'
    i7['enabled'] = True
    i7['mode'] = type(i7['mode'])(0)
    i7['pullResistor'] = type(i7['pullResistor'])(0)
    i7['activeLevel'] = type(i7['activeLevel'])(0)
    i7['thresholdVoltage'] = THRESHOLD_V          # flyttal, som hysteres i andra poster
    i7['EMAEnabled'] = False
    print(f'  I7  REVERSE -> TACH: digital, ingen pull, aktiv hög, tröskel {THRESHOLD_V} V, '
          f'hysteres {i7["hysteresisVoltage"]} V, EMA av')

    # ── GF15 ENGINE_RUN ─────────────────────────────────────────────────────
    g, tmpl = cfg['GenericFunction'][14], cfg['GenericFunction'][8]
    assert not g.get('label')
    g['label'] = 'ENGINE_RUN'
    g['enabled'] = type(tmpl['enabled'])(True)
    g['visibleInDOM'] = type(tmpl['visibleInDOM'])(1)
    g['function'] = [7, 1, F7, 2, 6, 3, RUN_HZ * SCALE]
    g['functionInfix'] = []
    print(f'  GF15 ENGINE_RUN = I7 frekvens > {RUN_HZ} Hz ({RUN_HZ * 30} rpm): {g["function"]}')

    # ── O19 REVERSE: bort med I7-grenen ─────────────────────────────────────
    o = cfg['OutputHS'][18]
    assert o['label'] == 'REVERSE'
    branches = L.split_branches(o['functionInfix'])
    keep = [b for b in branches if S7 not in [int(t[1]) for t in b]]
    assert len(branches) == 2 and len(keep) == 1, branches
    rows = []
    for ti, t in enumerate(keep[0]):
        if ti:
            rows.append(list(L.AND_ROW))
        rows.append(t)
    o['functionInfix'] = L.cleanup_infix(rows)
    o['function'] = L.infix_to_function(o['functionInfix'])
    print(f'  O19 REVERSE: {len(branches)} grenar -> 1, kvar: {keep[0]}')

    # ── 0x520 ───────────────────────────────────────────────────────────────
    co = cfg['CANOutput'][16]
    assert co['label'] == 'PDM_EngineDiag'
    for slot, var, mult in ((2, F7, 30), (3, v.gf(15), 1)):
        co['variableNum'][slot] = type(co['variableNum'][slot])(var)
        co['dataFormat'][slot] = type(co['dataFormat'][slot])(FMT16)
        co['dataMultiplier'][slot] = type(co['dataMultiplier'][slot])(mult)
    print(f'  0x520: byte 4–5 Engine_RPM (var {F7} × 30), byte 6–7 Engine_Running (GF15, var {v.gf(15)})')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('I7 TACH: enabled, digital, ingen pull, EMA av, tröskel 2,5 V',
         lambda c: c['Input'][6]['label'] == 'TACH' and c['Input'][6]['enabled'] is True
         and str(c['Input'][6]['mode']) == '0' and str(c['Input'][6]['pullResistor']) == '0'
         and c['Input'][6]['EMAEnabled'] is False and float(c['Input'][6]['thresholdVoltage']) == THRESHOLD_V),
        ('GF15 ENGINE_RUN = frekvens > 10 Hz (lagrat 100)',
         lambda c: c['GenericFunction'][14]['function'] == [7, 1, F7, 2, 6, 3, 100]),
        ('O19 lyssnar inte längre på I7',
         lambda c: S7 not in [x for x in c['OutputHS'][18]['function'] if isinstance(x, int)]),
        ('O19 har kvar CAN-grenen (LightShow AND Reverse_Lights_Cmd)',
         lambda c: {871, 926} <= {x for x in c['OutputHS'][18]['function'] if isinstance(x, int)}),
        ('inget annat använder I7-status',
         lambda c: all(S7 not in [x for x in o2['function'] if isinstance(x, int)] for o2 in c['OutputHS'])
         and all(S7 not in g2['function'] for g2 in c['GenericFunction'])),
        ('0x520 plats 0–3', lambda c: [int(x) for x in c['CANOutput'][16]['variableNum'][:4]]
         == [v.output_tripcount(3), v.output_tripcount(5), F7, v.gf(15)]
         and [float(x) for x in c['CANOutput'][16]['dataMultiplier'][:4]] == [1, 1, 30, 1]),
        ('v10.18 orört: handbroms/dörr-trösklar', lambda c: c['GenericFunction'][9]['function'][-1] == 28
         and c['GenericFunction'][10]['function'][-1] == 38),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
