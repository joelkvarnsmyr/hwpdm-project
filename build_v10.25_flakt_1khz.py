"""v10.25 — fläktens PWM 100 Hz -> 1000 Hz (tystare, jämnare på låga varv).

Källa: v10.24 (fläkten fungerar fullt ut).

Joel 2026-09-29: "låter rätt dåligt när man kör dimmat... typ elektroniskt... som att
den kämpar". 100 Hz ligger mitt i hörbart område — motorn vibrerar i PWM-takten och får
vridmomentet i ryck. Manualen (PWM): "PWM operation at up to 1KHz with minimal heat
dissipation" och "A higher frequency can result in smoother operation".

ÅTGÄRD (bara O11): PWMFrequency 100 -> 1000 Hz. Inget annat.
Komplement (fysiskt, valfritt): frihjulsdiod 1N5822 över motorn, katod (ring) mot
PDM-plus, anod mot jord.

    python build_v10.25_flakt_1khz.py            # torrkörning
    python build_v10.25_flakt_1khz.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.24_flakt_pwm_topp.HWPDM'
DST = r'Builds\Elton_v10.25_flakt_1khz.HWPDM'
FREQ = 1000


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.25 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    B.VarMap(cfg).selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')
    o = cfg['OutputHS'][10]
    assert o['label'] == 'BLOWER' and float(o['PWMFrequency']) == 100
    old = o['PWMFrequency']
    B.set_field(o, 'PWMFrequency', FREQ)
    print(f'  O11 PWMFrequency {old} -> {o["PWMFrequency"]} Hz')
    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('O11 1000 Hz', lambda c: float(c['OutputHS'][10]['PWMFrequency']) == FREQ),
        ('O11 i övrigt som v10.24', lambda c: c['OutputHS'][10]['PWMMappingEnable'] is True
         and float(c['OutputHS'][10]['PWMMapping'][-1]) == 101 and float(c['OutputHS'][10]['highFuse']) == 8),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
