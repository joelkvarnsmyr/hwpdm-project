"""v10.9 — flaktens CAN-timeout 1000 ms -> 10 000 ms.

Joel 2026-09-29: "10 s ar bra, lagg in det i nasta build."

Manualen: "The Timeout value is how long the current CAN value is valid for."
CAN-ingangen HALLER sitt senast mottagna varde under hela timeout-fonstret och
faller forst darefter till default (0). Med 1000 ms stannade flakten sa fort
mqtt-to-can startades om. Pi:n sander 0x503 med 10 Hz, sa 10 s ror inget i
normal drift — det avgor bara hur langt avbrott flakten rider igenom.

  Omstart av mqtt-to-can  -> flakten gar vidare utan blink
  Pi:n dor pa riktigt     -> flakten stannar efter 10 s
  Nyckeln ur              -> flakten stannar direkt (PDM:en tappar strom)

Bara CI28 BLW_CMD och CI29 BLW_DUTY. Ljuskommandona pa 0x500-0x502 behaller
1000 ms — dar ar snabb aterfall till lokal styrning det onskade beteendet.

    python build_v10.9_flakt_timeout.py            # torrkorning
    python build_v10.9_flakt_timeout.py --write    # bygg
"""
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.8_etapp1.HWPDM'
DST = r'Builds\Elton_v10.9_flakt_timeout.HWPDM'
TIMEOUT_MS = 10000


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.9 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    B.VarMap(cfg).selftest()
    L.roundtrip_check(cfg)
    print('\n=== Andringar ===')

    for slot, label in ((28, 'BLW_CMD'), (29, 'BLW_DUTY')):
        ci = cfg['CANInput'][slot - 1]
        assert ci['label'] == label, f'CI{slot} ar {ci["label"]!r}, vantade {label!r}'
        old = ci['timeoutTime']
        B.set_field(ci, 'timeoutTime', TIMEOUT_MS)
        print(f'  CI{slot} {label}: timeout {old} -> {ci["timeoutTime"]} ms')

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, [
        ('BLW_CMD timeout 10 s', lambda c: int(c['CANInput'][27]['timeoutTime']) == TIMEOUT_MS),
        ('BLW_DUTY timeout 10 s', lambda c: int(c['CANInput'][28]['timeoutTime']) == TIMEOUT_MS),
        ('default fortfarande 0 pa bada',
         lambda c: all(int(c['CANInput'][i]['variableDefault']) == 0 for i in (27, 28))),
        ('ljuskommandona orörda (1000 ms)',
         lambda c: all(int(c['CANInput'][i]['timeoutTime']) == 1000 for i in range(27))),
        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]) else 1


if __name__ == '__main__':
    raise SystemExit(main())
