"""v10.18 — handbroms/dörr: trösklar efter uppmätta spänningar.

Källa: v10.17 (det som ligger i PDM:en).

UPPMÄTT PÅ C1 2026-09-29 19:49–19:50 (0x51F, motstånden monterade)
  läge                  räknat   uppmätt
  allt stängt           5,00 V   4,53 V   (PDM-ingången belastar ~55 kΩ)
  dörr öppen            3,21 V   3,07 V
  handbroms i           2,50 V   2,44 V
  handbroms + dörr      1,95 V   1,93 V
  v10.17 avkodade alla fyra rätt, men dörr låg bara 0,17 V över gränsen 2,9 V.

NYA GRÄNSER (mitt emellan uppmätta värden, 0,1 V-steg — konstanter lagras ×10)
  stängt / dörr      4,2 -> 3,8 V   (mitt 3,80)   marginal 0,73 / 0,73
  dörr / handbroms   2,9 -> 2,8 V   (mitt 2,76)   marginal 0,27 / 0,36
  handbroms / båda   2,2 V oförändrad (mitt 2,19)  marginal 0,24 / 0,27
  fel                < 1,0 V oförändrad

    python build_v10.18_hb_dorr_trosklar.py            # torrkörning
    python build_v10.18_hb_dorr_trosklar.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.17_handbroms_dorr.HWPDM'
DST = r'Builds\Elton_v10.18_hb_dorr_trosklar.HWPDM'
SCALE = 10
GT, LT = 6, 8
CHANGES = {                        # GF: {(op, gammal volt): ny volt}
    10: {(LT, 2.9): 2.8},                          # HANDBRAKE     1,0 < V < 2,8
    11: {(GT, 2.9): 2.8, (LT, 4.2): 3.8},          # DOOR_ONLY     2,8 < V < 3,8
}


def retune(fn, var, table):
    """Byt konstanter i en platt GF-funktion. Villkor = [1, var, 2, op, 3, konst]."""
    out, hits = list(fn), 0
    for i in range(1, len(out) - 5):
        if out[i] == 1 and out[i + 1] == var and out[i + 2] == 2 and out[i + 4] == 3:
            key = (out[i + 3], out[i + 5] / SCALE)
            if key in table:
                out[i + 5] = int(round(table[key] * SCALE)); hits += 1
    assert hits == len(table), f'hittade {hits} av {len(table)} villkor i {fn}'
    return out


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} v10.18 — {SRC} -> {DST}\n')
    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)
    V = v.input_voltage(16)
    print('\n=== Ändringar ===')
    for n, table in CHANGES.items():
        g = cfg['GenericFunction'][n - 1]
        old = g['function']
        g['function'] = retune(old, V, table)
        print(f'  GF{n} {g["label"]:<10} {old}\n  {"":14}-> {g["function"]}')

    if not write:
        print('\nTorrkörning klar. Inget skrevs.')
        return 0
    B.drop_derived(cfg)
    print()
    B.save(cfg, DST)
    measured = {'stängt': 4.53, 'dörr': 3.07, 'handbroms': 2.44, 'båda': 1.93}
    return 0 if B.verify(DST, [
        ('GF10 HANDBRAKE = 1,0 < V < 2,8',
         lambda c: c['GenericFunction'][9]['function'] == [15, 1, V, 2, GT, 3, 10, 2, 1, 1, V, 2, LT, 3, 28]),
        ('GF11 DOOR_ONLY = 2,8 < V < 3,8',
         lambda c: c['GenericFunction'][10]['function'] == [15, 1, V, 2, GT, 3, 28, 2, 1, 1, V, 2, LT, 3, 38]),
        ('GF12/13/14 orörda', lambda c: c['GenericFunction'][11]['function'][-1] == 22
         and c['GenericFunction'][12]['label'] == 'DOOR_OPEN' and c['GenericFunction'][13]['function'][-1] == 10),
        ('varje uppmätt läge hamnar i rätt band med ≥ 0,2 V marginal',
         lambda c: all(min(abs(m - t) for t in (1.0, 2.2, 2.8, 3.8)) >= 0.2 for m in measured.values())),
        ('alla CAN-ingångar täcks av filter', lambda c: B.uncovered_can_inputs(c) == []),
        ('rundgången håller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan håller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
