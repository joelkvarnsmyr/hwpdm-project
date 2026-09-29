"""v10.21 — fläkten som ren på/av (PWM av) så den går i kväll.

Källa: v10.20 (innehåller v10.19). Flasha bara denna.

FELSÖKNING 2026-09-29 kväll
  - Appen skickar 0x503 = 03 64 (på, 100 %). Sedan v10.15 når ramen PDM:en.
  - O11 BLOWER står på status 1 (på) men drar bara 0,08–0,13 A.
  - Joel matade fläktkontakten (urtagen ur PDM:en) med 12 V: fläkten startar direkt.
    Motor, kablage och jord är alltså hela. Pinnen stämmer (B8 = O11, projektkartan).
  - O11 är den ENDA utgången med PWM-mappning påslagen (O4 PARK har den av — minnet
    sa fel). PWM-mappningen lades in i v10.4 och har aldrig verifierats i bilen.
    Med vredet (LISO) var O11 en ren på/av-utgång och fläkten gick.
  Slutsats: PWM-vägen ger nästan ingen arbetscykel. Utredd i morgon.

ÅTGÄRD (bara O11)
  PWMMappingEnable  True -> False   (full spänning när logiken är sann)
  PWMSoftStartEnable True -> False  (exakt som när fläkten fungerade)
  Mappningsvariabel, tabell och frekvens står kvar för morgondagens PWM-felsökning.
  Appens på/av (BLW_CMD) styr fortfarande. Hastighetsreglaget gör inget tills vidare.

    python build_v10.21_flakt_pa_av.py            # torrkörning
    python build_v10.21_flakt_pa_av.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.20_laddlampa_bromsvatska.HWPDM'
DST = r'Builds\Elton_v10.21_flakt_pa_av.HWPDM'


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.21 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    print('\n=== Ändringar ===')
    o = cfg['OutputHS'][10]
    assert o['label'] == 'BLOWER' and o['PWMMappingEnable'] is True and o['PWMSoftStartEnable'] is True
    o['PWMMappingEnable'] = False
    o['PWMSoftStartEnable'] = False
    print(f'  O11 BLOWER: PWM-mappning av, mjukstart av (hög {o["highFuse"]} A, '
          f'topp {o["peakFuse"]} A i {o["peakFuseTime"]} s — räcker för motorns startström)')
    others = [i + 1 for i, x in enumerate(cfg['OutputHS']) if x.get('PWMMappingEnable') in (True, 1, '1')]
    print(f'  Utgångar med PWM-mappning kvar: {others or "inga"}')

    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('O11 PWM-mappning och mjukstart av', lambda c: c['OutputHS'][10]['PWMMappingEnable'] is False
         and c['OutputHS'][10]['PWMSoftStartEnable'] is False),
        ('O11 logik orörd (GF1, T2, GF9, BLW_CMD)', lambda c: {v.gf(1), v.timer(2), v.gf(9), v.caninput(28)}
         <= {x for x in c['OutputHS'][10]['function'] if isinstance(x, int)}),
        ('O11 mappningsvariabel kvar för felsökning', lambda c: str(c['OutputHS'][10]['PWMMappingVariable']) == '1011'),
        ('v10.20 orört: O2 på, I13 på, O19 av', lambda c: c['OutputHS'][1]['enabled'] is True
         and c['Input'][12]['enabled'] is True and c['OutputHS'][18]['enabled'] is False),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
