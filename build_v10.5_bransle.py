"""v10.5 — bransleniva pa I8 / pin A3.

TRE FEL ATGARDAS
  1. I8 stod som WASHER, avstangd, DIGITAL med intern pull-up. Blir FUEL_LEVEL,
     analog (mode 2), pullResistor 0 (extern delare anvands).
  2. SC2 FUEL_LVL pekade pa var 641 = I13 (pin C11, tom) — en stale pekare fran
     eran da I13 var branslegivare. Pekas om till I8:s spanningsvariabel.
  3. SC2:s kurva var GOTLAND-erans: stigande 0 -> 90 L over 500-4300 mV. Det ar
     BAKLANGES for en pull-up-delare, dar full tank ger LAG spanning.

KURVAN RAKNAS UT, INTE KLISTRAS IN
  V(mV) = V_REF * Rs / (R_PULLUP + Rs)

  Den forra kurvan antog att spanningen var linjar med nivan. Det ar den inte —
  delaren ar olinjar, och felet blev upp till 13,5 liter mitt i spannet (visade
  26,5 L vid verkliga 40 L). Har raknas varje punkt ur delarformeln i stallet.

  ⚠ R_FULL, R_EMPTY och TANK_L ar ANTAGANDEN. Nar Joel last av sina tva punkter
  (reservlampan tand, och full tank) andras konstanterna nedan och bygget kors om.
  Metod: las spanningen i konfiguratorn vid de tva tillfallena — ingen tank
  behover tommas.

FYSISKT KVAR INNAN DET MATER NAGOT
  - C10 (5V REF) ar odragen
  - 150 Ohm 0,6 W mellan C10 och A3
  - DEN GAMLA GRON/RODA SPOLARKABELN SITTER KVAR PA A3 och maste bort forst
  - givarens jordkabel till chassipunkt 12, samma som C7

    python build_v10.5_bransle.py            # torrkorning
    python build_v10.5_bransle.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.4_flakt_can.HWPDM'
DST = r'Builds\Elton_v10.5_bransle.HWPDM'

# ── delarens parametrar ──────────────────────────────────────────────────────
V_REF = 5000.0          # mV, PDM:ens 5V-referens
R_PULLUP = 150.0        # Ohm, motstandet mellan C10 och A3
R_FULL = 10.0           # Ohm vid full tank      ⚠ ANTAGANDE
R_EMPTY = 180.0         # Ohm vid tom tank       ⚠ ANTAGANDE
TANK_L = 80.0           # liter                  ⚠ ANTAGANDE
POINTS = 20             # SC-tabellens storlek


def divider_mv(rs):
    return V_REF * rs / (R_PULLUP + rs)


def build_curve():
    """20 punkter, jamnt fordelade i LITER, med spanningen ur delarformeln.

    Returnerar (raw_mV stigande, kalibrerat fallande). Raw maste vara stigande,
    darfor gar vi fran full tank (lag spanning) till tom (hog).
    """
    raw, cal = [], []
    for i in range(POINTS):
        litres = TANK_L * (1 - i / (POINTS - 1))        # 80 -> 0
        rs = R_EMPTY - (R_EMPTY - R_FULL) * (litres / TANK_L)
        raw.append(int(round(divider_mv(rs))))
        cal.append(int(round(litres * 1000)))           # SC lagrar milliliter
    return raw, cal


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.5 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)

    i8_volt = v.input_voltage(8)
    print(f'\n  I8 spanningsvariabel -> var {i8_volt}')
    print('\n=== Andringar ===')

    # ── 1. ingangen ─────────────────────────────────────────────────────────
    i8 = cfg['Input'][7]
    assert i8['label'] == 'WASHER', f'I8 ar {i8["label"]!r}, forvantade WASHER'
    i8['label'] = 'FUEL_LEVEL'
    B.set_field(i8, 'mode', 2)              # analog
    B.set_field(i8, 'pullResistor', 0)      # ingen intern pull — extern delare
    B.set_field(i8, 'enabled', True)
    print(f'  I8 (A3): WASHER -> FUEL_LEVEL, analog, pullResistor 0, enabled')

    # ── 2. sensorkurvan ─────────────────────────────────────────────────────
    sc2 = cfg['SensorCalibration'][1]
    assert sc2['label'] == 'FUEL_LVL', f'SC2 ar {sc2["label"]!r}'
    old_var = sc2['variable']
    B.set_field(sc2, 'variable', i8_volt)
    B.set_field(sc2, 'enabled', True)
    raw, cal = build_curve()
    sc2['rawSensorDataPoint'] = [type(sc2['rawSensorDataPoint'][0])(x) for x in raw]
    sc2['calibratedSensorDataPoint'] = [type(sc2['calibratedSensorDataPoint'][0])(x) for x in cal]
    print(f'  SC2 FUEL_LVL: pekare var {old_var} (I13, tom pin) -> {i8_volt} (I8)')
    print(f'  SC2 kurva omraknad ur delaren:')
    print(f'     full tank  {R_FULL:.0f} ohm -> {divider_mv(R_FULL):.0f} mV -> {TANK_L:.0f} L')
    print(f'     tom tank  {R_EMPTY:.0f} ohm -> {divider_mv(R_EMPTY):.0f} mV -> 0 L')
    print(f'     strom vid full tank: {V_REF/(R_PULLUP+R_FULL):.1f} mA av 100 mA')
    print(f'     raw: {raw}')

    L.roundtrip_check(cfg)

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(i8_volt, raw, cal)) else 1


def checks(i8_volt, raw, cal):
    return [
        ('I8 = FUEL_LEVEL, analog, enabled',
         lambda c: (c['Input'][7]['label'] == 'FUEL_LEVEL'
                    and int(c['Input'][7]['mode']) == 2
                    and c['Input'][7]['enabled'] is True)),
        ('I8 utan intern pull-up (extern delare)',
         lambda c: int(c['Input'][7]['pullResistor']) == 0),
        ('SC2 pekar pa I8 spanning',
         lambda c: int(c['SensorCalibration'][1]['variable']) == i8_volt),
        ('SC2 enabled', lambda c: c['SensorCalibration'][1]['enabled'] is True),
        ('SC2 raw ar stigande',
         lambda c: all(int(a) < int(b) for a, b in
                       zip(c['SensorCalibration'][1]['rawSensorDataPoint'][:-1],
                           c['SensorCalibration'][1]['rawSensorDataPoint'][1:]))),
        ('SC2 liter ar fallande (full = lag spanning)',
         lambda c: all(int(a) > int(b) for a, b in
                       zip(c['SensorCalibration'][1]['calibratedSensorDataPoint'][:-1],
                           c['SensorCalibration'][1]['calibratedSensorDataPoint'][1:]))),
        ('SC2 andpunkter 80 L och 0 L',
         lambda c: (int(c['SensorCalibration'][1]['calibratedSensorDataPoint'][0]) == 80000
                    and int(c['SensorCalibration'][1]['calibratedSensorDataPoint'][-1]) == 0)),
        ('SC2 har 20 punkter',
         lambda c: len(c['SensorCalibration'][1]['rawSensorDataPoint']) == 20),

        # ── far inte ha rorts ──
        ('SC1 COOLANT orord', lambda c: c['SensorCalibration'][0]['label'] == 'COOLANT_T'),
        ('O5 FUEL-pumpen fortfarande bara GF1',
         lambda c: len([r for r in c['OutputHS'][4]['functionInfix'] if L.is_term(r)]) == 1),
        ('O12 WASHER fortfarande avstangd', lambda c: c['OutputHS'][11]['enabled'] is False),
        ('I16 HANDBRAKE kvar', lambda c: c['Input'][15]['label'] == 'HANDBRAKE'),
        ('CI28/29 flakt kvar',
         lambda c: c['CANInput'][27]['label'] == 'BLW_CMD' and c['CANInput'][28]['label'] == 'BLW_DUTY'),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
