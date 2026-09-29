"""v10.10 — SC2:s x-axel i VOLT, inte millivolt.

VERIFIERAT PA BUSSEN 2026-09-29 efter flash av v10.9: 0x510 visade 80,0 L trots
~2 V pa A3. Orsak: ingangsvariabeln ar i volt — variables.js:
    616 Input 8 Voltage  units=V  (float)input[7].voltage*0.001
Kurvan i v10.5 hade x-axeln i mV (312..2727). 2,0 V hamnade darmed under 312 och
klampades till forsta punkten = 80 L. Matarn hade ALLTID visat full tank.
Samma fel finns i SC1 (200..5200) — darfor har kylvattnet alltid visat 120 grader.

Fix: samma delarkurva, x-axeln i volt som flyttal (0.312 .. 2.727). Litervardena
ar oforandrade (x1000, sa 0x510-kontraktet galler). Kalla v10.9.

--- ursprunglig beskrivning (v10.5) ---
v10.5 — bransleniva pa I8 / pin A3.

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

SRC = r'Builds\Elton_v10.9_flakt_timeout.HWPDM'
DST = r'Builds\Elton_v10.10_sc2_volt.HWPDM'

# ── delarens parametrar ──────────────────────────────────────────────────────
V_REF = 5000.0          # mV, PDM:ens 5V-referens
R_PULLUP = 150.0        # Ohm, motstandet mellan C10 och A3
R_FULL = 10.0           # Ohm vid full tank      ⚠ ANTAGANDE
R_EMPTY = 180.0         # Ohm vid tom tank       ⚠ ANTAGANDE
TANK_L = 64.0           # liter — Joel 2026-09-29 (var felaktigt 80)
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
        raw.append(round(divider_mv(rs) / 1000.0, 3))     # VOLT, flyttal
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
    assert i8['label'] == 'FUEL_LEVEL', f'I8 ar {i8["label"]!r}'
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
    sc2['rawSensorDataPoint'] = [float(x) for x in raw]   # flyttal — typen far INTE bevaras (int -> 0)
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
        ('SC2 x-axel i volt (0.3 .. 2.8)',
         lambda c: 0.2 < float(c['SensorCalibration'][1]['rawSensorDataPoint'][0]) < 0.4
                   and 2.6 < float(c['SensorCalibration'][1]['rawSensorDataPoint'][-1]) < 2.8),
        ('SC2 raw ar stigande',
         lambda c: all(float(a) < float(b) for a, b in
                       zip(c['SensorCalibration'][1]['rawSensorDataPoint'][:-1],
                           c['SensorCalibration'][1]['rawSensorDataPoint'][1:]))),
        ('0x510 fortfarande pa (v10.8)', lambda c: c['CANOutput'][0]['label'] == 'PDM_Sensors'),
        ('flakttimeout fortfarande 10 s', lambda c: int(c['CANInput'][27]['timeoutTime']) == 10000),
        ('SC2 liter ar fallande (full = lag spanning)',
         lambda c: all(int(a) > int(b) for a, b in
                       zip(c['SensorCalibration'][1]['calibratedSensorDataPoint'][:-1],
                           c['SensorCalibration'][1]['calibratedSensorDataPoint'][1:]))),
        ('SC2 andpunkter 64 L och 0 L',
         lambda c: (int(c['SensorCalibration'][1]['calibratedSensorDataPoint'][0]) == 64000
                    and int(c['SensorCalibration'][1]['calibratedSensorDataPoint'][-1]) == 0)),
        ('SC2 har 20 punkter',
         lambda c: len(c['SensorCalibration'][1]['rawSensorDataPoint']) == 20),

        # ── far inte ha rorts ──
        ('SC1 COOLANT orord', lambda c: c['SensorCalibration'][0]['label'] == 'COOLANT_T'),
        ('O5 FUEL-pumpen fortfarande bara GF1',
         lambda c: len([r for r in c['OutputHS'][4]['functionInfix'] if L.is_term(r)]) == 1),
        ('O12 WASHER pa (aktiverad i v10.6)', lambda c: c['OutputHS'][11]['enabled'] is True),
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
