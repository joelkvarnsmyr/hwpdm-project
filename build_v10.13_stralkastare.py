"""v10.13 — strålkastarnas toppsäkring + ram med råa ingångsspänningar.

Källa: v10.11 (det som ligger i PDM:en). v10.12 (spolarfixen) tas INTE med — den
bygger på v9.4:s inställningar som är overifierade med dagens +12V-busbar.

1. STRÅLKASTARNA LÖSER UT PÅ ÖVERSTRÖM (uppmätt på bussen 2026-09-29, v10.11)
   Statuskoder (configOutputs.js setOutputStatusIndicator):
     0 Av  1 På  2 Trip överström  3 Trip underström  4 Trip underspänning  5 Trip övertemp
   Vänster sida: O14 LOW_L och O16 HIBEAM_L = 2 (överström) direkt vid varje tillslag.
   Höger sida:   O7 HIBEAM_R = 3, O15 LOW_R = 0,23 A → 3 (underström = trasig lampa/jord).

   Toppsäkringen (20,8 A / 24,3 A) kommer från Joels auto-tune = 1,25 × uppmätt topp.
   Auto-tunen samplar strömmen och missar den verkliga kallstartsspiken i en H4
   (8–10 × driftström, ~40 A i några ms). Mjukstart (PWM-ramp 100) lades dessutom på
   EFTER auto-tunen — LISO hade tid 0. Vid PWM ser varje puls den kalla trådens ström.
   Åtgärd på alla fyra:
     peakFuse        -> 35 A   (PDM25 standardutgång tål 80 A topp)
     PWMSoftStart    -> PÅ, 500 ms. Joel 2026-09-29: "Vi MÅSTE dock ha lite mjukstart
                        på dom. men räcker med en halv sekund." Enheten är ms (GUI:t:
                        min 100, max 10000, steg 100, suffix "ms") — 100 var alltså
                        bara 0,1 s. Löser vänster sida ändå ut med 35 A + 500 ms är
                        det en äkta kortslutning, inte startström.
   Oförändrat: highFuse 5,8/5,9 A, peakFuseTime, lowFuse 1 A. Underströmsvakten är
   det som upptäckte höger sida — den ska sitta kvar.
   En äkta kortslutning skyddas fortfarande: 35 A max i 0,3 s (helljus) / 2 s
   (halvljus), sedan 5,8/5,9 A, 2 omförsök.

2. RÅA INGÅNGSSPÄNNINGAR PÅ BUSSEN (0x51F PDM_InVolt, 10 Hz)
   I1 WASHER, I8 FUEL_LEVEL, I10 COOLANT_TEMP, I16 HANDBRAKE i mV (16 bit, x1000).
   Ingångsspänningen är VOLT som flyttal i PDM:en (input.voltage*0.001).
   Varför: spolaren läser 1 i vila och vi vet inte om spaken slår +12 V eller jord.
   Med spänningen syns svaret direkt — ingen gissning på GUI:ts etiketter. Samma ram
   kalibrerar kylvattnet (I10) och blir handbroms/dörr-muxens mätpunkt (I16).

    python build_v10.13_stralkastare.py            # torrkörning
    python build_v10.13_stralkastare.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.11_perkanal_can.HWPDM'
DST = r'Builds\Elton_v10.13_stralkastare.HWPDM'

HEADLIGHTS = {7: 'HIBEAM_R', 14: 'LOWBEAM_L', 15: 'LOWBEAM_R', 16: 'HIBEAM_L'}
PEAK_A = 35
SOFTSTART_MS = 500
FMT16 = 2
VOLT_SLOT, VOLT_ID, VOLT_HZ = 16, 0x51F, 10
VOLT_INPUTS = (1, 8, 10, 16)


def set_canoutput(cfg, slot, label, can_id, hz, entries):
    """Samma som v10.11 — bevisat att överleva flash via GUI:t."""
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
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.13 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')

    # ── 1. strålkastarna ────────────────────────────────────────────────────
    for n, label in HEADLIGHTS.items():
        o = cfg['OutputHS'][n - 1]
        assert o['label'] == label, f'O{n} är {o["label"]!r}, väntade {label!r}'
        old = (o['peakFuse'], o['PWMSoftStartEnable'], o['PWMSoftStartTime'])
        B.set_field(o, 'peakFuse', PEAK_A)
        B.set_field(o, 'PWMSoftStartEnable', True)
        B.set_field(o, 'PWMSoftStartTime', SOFTSTART_MS)
        print(f'  O{n:<2} {label:<10} topp {old[0]} -> {o["peakFuse"]} A, mjukstart {old[1]}/{old[2]} -> '
              f'{o["PWMSoftStartEnable"]}/{o["PWMSoftStartTime"]} ms   (hög {o["highFuse"]} A, låg {o["lowFuse"]} A, '
              f'topptid {o["peakFuseTime"]} s oförändrat)')

    # ── 2. råa ingångsspänningar ────────────────────────────────────────────
    entries = [(v.input_voltage(n), FMT16, 1000) for n in VOLT_INPUTS]
    set_canoutput(cfg, VOLT_SLOT, 'PDM_InVolt', VOLT_ID, VOLT_HZ, entries)
    names = ', '.join(f'I{n} {cfg["Input"][n - 1]["label"]}' for n in VOLT_INPUTS)
    print(f'  CANOutput {VOLT_SLOT}: 0x{VOLT_ID:03X} PDM_InVolt {VOLT_HZ} Hz — {names} (mV)')

    L.roundtrip_check(cfg)
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(v)) else 1


def checks(v):
    return [
        ('strålkastare topp 35 A',
         lambda c: all(float(c['OutputHS'][n - 1]['peakFuse']) == PEAK_A for n in HEADLIGHTS)),
        ('strålkastare mjukstart på, 500 ms',
         lambda c: all(c['OutputHS'][n - 1]['PWMSoftStartEnable'] in (True, 1, '1')
                       and int(c['OutputHS'][n - 1]['PWMSoftStartTime']) == SOFTSTART_MS
                       for n in HEADLIGHTS)),
        ('underströmsvakten kvar (1 A)',
         lambda c: all(float(c['OutputHS'][n - 1]['lowFuse']) == 1 for n in HEADLIGHTS)),
        ('0x51F PDM_InVolt',
         lambda c: (c['CANOutput'][VOLT_SLOT - 1]['label'] == 'PDM_InVolt'
                    and int(c['CANOutput'][VOLT_SLOT - 1]['CANID']) == VOLT_ID
                    and [int(x) for x in c['CANOutput'][VOLT_SLOT - 1]['variableNum'][:4]]
                    == [v.input_voltage(n) for n in VOLT_INPUTS])),
        ('I10 spänning = var 626 (samma som SC-kartan i minnet)',
         lambda c: v.input_voltage(10) == 626),
        ('v10.11-ramarna orörda',
         lambda c: [c['CANOutput'][i]['label'] for i in (0, 1, 2, 14)]
         == ['PDM_Sensors', 'PDM_Status', 'PDM_OutStatus_1', 'PDM_OutCurrent_7']),
        ('spolaren orörd (I1 som v10.11)',
         lambda c: str(c['Input'][0]['pullResistor']) == '1' and str(c['Input'][0]['activeLevel']) == '0'),
        ('bränslepumpen O5 enabled', lambda c: c['OutputHS'][4]['enabled'] is True),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
