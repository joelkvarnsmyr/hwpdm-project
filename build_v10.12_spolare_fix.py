"""v10.12 — spolaringangen (I1/A7) tillbaka till VERIFIERADE installningar.

Verifierat pa bussen 2026-09-29 efter flash av v10.11: I1 WASHER last AKTIV utan
att spaken rordes -> O12 spolarpump beordrad pa konstant.

Orsak (mitt fel i v10.6): installningarna kopierades fran LISO:s I8-plats, dar
spolaringangen var AVSTANGD och aldrig provad (pull 1, activeLevel 0). Den
verifierade konfigurationen finns i Elton_v9.4.HWPDM — "sist helverifierade pa
bil", alla 16 ingangar kontrollerade 2026-05-20: pull 2, activeLevel 1, troskel 1 V.
Brytarbeteendet kopieras darifran, med kallans typer.

LARDOM: kopiera ingangsinstallningar bara fran en konfiguration som VERIFIERATS
i bilen (v9.4, eller en ingang som setts fungera live), aldrig fran en avstangd plats.
"""
import sys, json
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.11_perkanal_can.HWPDM'
DST = r'Builds\Elton_v10.12_spolare_fix.HWPDM'
REF = r'Builds\Elton_v9.4.HWPDM'
FIELDS = ('mode', 'pullResistor', 'activeLevel', 'thresholdVoltage',
          'hysteresisVoltage', 'turnOnDelay', 'EMAValue', 'EMAEnabled')

def main():
    write = '--write' in sys.argv
    cfg = B.load(SRC); v = B.VarMap(cfg); v.selftest(); L.roundtrip_check(cfg)
    ref = json.load(open(REF, encoding='utf-8', errors='replace'))['Input'][7]
    assert ref['label'] == 'WASHER' and ref['enabled'], 'v9.4 I8 ar inte den verifierade spolaren'
    i1 = cfg['Input'][0]
    assert i1['label'] == 'WASHER'
    before = {f: i1.get(f) for f in FIELDS}
    for f in FIELDS:
        if f in ref and f in i1:
            i1[f] = ref[f]
    print('\n  I1 WASHER fore :', before)
    print('  I1 WASHER efter:', {f: i1.get(f) for f in FIELDS}, '(= v9.4 I8, verifierad)')
    if not write:
        print('\nTorrkorning.'); return 0
    B.drop_derived(cfg); B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('I1 = v9.4:s verifierade spolare',
         lambda c: all(str(c['Input'][0][f]) == str(ref[f]) for f in FIELDS if f in ref)),
        ('O12 WASHER fortfarande styrd av I1',
         lambda c: any(int(r[1]) == B.VarMap(c).input_status(1)
                       for r in c['OutputHS'][11]['functionInfix'] if L.is_term(r))),
        ('I16 handbroms orord (= I14)',
         lambda c: str(c['Input'][15]['activeLevel']) == str(c['Input'][13]['activeLevel'])),
        ('per-kanalramarna kvar', lambda c: c['CANOutput'][2]['label'] == 'PDM_OutStatus_1'),
        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1

if __name__ == '__main__':
    raise SystemExit(main())
