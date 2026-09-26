"""MALL för ett nytt script-bygge. Kopiera denna fil, döp om, fyll i `changes()`.

Kör utan argument = TORRKÖRNING (läser, självtestar, visar vad som skulle ändras,
skriver INGENTING). Lägg till --write när du är nöjd.

    python build_template.py            # torrkörning
    python build_template.py --write    # skriv DST

VARFÖR denna mall finns: de gamla build_v9.*.py hårdkodar variabel-ID ur
1.2-schemat. Firmware 1.3.1 flyttade allt +21. Den här mallen löser ID symboliskt
via build_lib.VarMap, som BEVISAR sin karta mot filen innan något skrivs.

ARBETSFLÖDE: öppna DST i konfiguratorn, kontrollera att ändringen syns, flasha.
`rawSendData` och `sectionCRCs` tas bort av drop_derived() — verifierat mot app.asar
1.3.1 att appen aldrig läser dem (den raderar dem själv vid inläsning och räknar om
dem ur minnet vid spara). Ingen GUI-rundtur krävs av CRC-skäl.
"""
import sys
import build_lib as B

SRC = r'Builds\LISO.HWPDM'
DST = r'Builds\LISO_next.HWPDM'

# Sektioner som `changes()` rör — deras CRC nollas så GUI:t räknar om dem.
TOUCHED = []            # kvar för invalidate_crc om du nagon gang behover den


def changes(cfg, v):
    """Gör ändringarna. `v` är en verifierad VarMap.

    Regler:
      - Skriv ALLTID via B.set_field() — 1.3.1 lagrar tal som strängar i OutputHS
        men som int i Timer/GF/SensorCalibration/CANInput.
      - Slå upp variabel-ID via v.input_status(n) / v.input_voltage(n) / v.timer(n)
        / v.gf(n) / v.caninput(n) — aldrig hårdkodade nummer.
      - Kontrollera alltid att du är på rätt index INNAN du skriver.

    Returnera en lista med rader som beskriver vad som gjordes (för loggen).
    """
    log = []

    # ── EXEMPEL (avkommentera och anpassa) ───────────────────────────────────
    # O11:s toppsäkringstid står på 4000 SEKUNDER, ska vara 5 enligt specen.
    #
    # o11 = cfg['OutputHS'][10]
    # assert o11['label'] == 'BLOWER', f"idx10 är {o11['label']!r}, väntade BLOWER"
    # before = o11['peakFuseTime']
    # B.set_field(o11, 'peakFuseTime', 5)
    # log.append(f"O11 BLOWER peakFuseTime: {before!r} -> {o11['peakFuseTime']!r}")

    # ── Exempel på variabeluppslag (skriver inget) ───────────────────────────
    log.append(f'(uppslag) I1 spänning = {v.input_voltage(1)}, '
               f'I4 status = {v.input_status(4)}, Timer2 = {v.timer(2)}, '
               f'GF1 = {v.gf(1)}, CI1 = {v.caninput(1)}')

    return log


def checks():
    """Kontroller som körs mot den SKRIVNA filen. (namn, funktion) -> bool.

    Ta alltid med regressionsvakter för det du INTE ville ändra.
    """
    return [
        # ── det ändringen skulle åstadkomma ──
        # ('O11 peakFuseTime = 5', lambda c: str(c['OutputHS'][10]['peakFuseTime']) == '5'),

        # ── regressionsvakter ──
        ('O4 = PARK på D7', lambda c: c['OutputHS'][3]['label'] == 'PARK'),
        ('O6 = BRAKE på D9', lambda c: c['OutputHS'][5]['label'] == 'BRAKE'),
        ('O23 STARTER enabled', lambda c: c['OutputHS'][22]['enabled'] is True),
        ('O13 horn enabled', lambda c: c['OutputHS'][12]['enabled'] is True),
        ('27 CANInputs enabled', lambda c: sum(1 for x in c['CANInput'] if x.get('enabled')) >= 27),
        ('variabelkartan håller efteråt', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKÖRNING"} — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()                      # avbryter om kartan inte stämmer

    print('\n=== Ändringar ===')
    log = changes(cfg, v)
    for line in log:
        print('  ' + line)
    if not any(not l.startswith('(uppslag)') for l in log):
        print('  (inga faktiska ändringar — fyll i changes())')

    if not write:
        print('\nTorrkörning klar. Inget skrevs. Lägg till --write för att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  härledda fält borttagna: {", ".join(removed)} '
              f'(appen räknar om dem själv)')

    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
