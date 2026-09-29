"""v10.4 — flakten helt pa CAN. Ingen fysisk ingang.

Joel 2026-09-27: "Vi kan ta bort blower input helt for vi har ingen fysisk.
Bara ha output som ska styras med can enligt tidigare spec."

ANDRINGAR
  I1 / A7     BLOWER -> RESERVE1, avstangd och nollstalld. Ingen kabel finns,
              och villkoret ar redan borttaget ur O11 (Joels GUI-granskning).
              Pinnen blir ledig — kandidat for spolarens ingang senare.

  CI28 BLW_CMD    0x503 byte 0 bit 0,  1 bit,  timeout 1000 ms, default 0
  CI29 BLW_DUTY   0x503 byte 1,        8 bit,  timeout 1000 ms, default 0
              Per docs/superpowers/specs/2026-09-25-blower-can-control-design.md
              i dash-projektet (ram Elton_Ctrl_Climate). Spec:ens BLW_PI_ACTIVE
              och BLW_DUTY-default 100 fanns bara for att lamna over till vredet
              vid CAN-bortfall. Utan vred finns inget att lamna over till, sa
              default 0 = flakten stannar. Joel har accepterat det.

  O11 BLOWER  logik: GF1 AND INTE Timer2 AND GF9 LOAD_OK AND BLW_CMD
              PWM:  mappning fran BLW_DUTY, [0,10,20..100] = rak 1:1
              200 Hz enligt spec:ens rekommendation for borstad DC-motor.

  LASTFALLNINGEN BEHALLS. GF9 ligger kvar i villkoret, sa flakten slapper sina
  ~9 A under dragningen aven i CAN-lage.

VERIFIERAT om PWM-mappningen: GUI:ts element heter PWMMap0, PWMMap10 ... PWMMap100
(configOutputs.js:2007-2020). X-axeln ar alltsa DUTY I PROCENT och det lagrade
vardet ar variabelnivan dar den duty:n nas. [0,10,...,100] ger rak 1:1 for en
0-100-variabel — samma form som O4 PARK redan anvander med Park_Lights_PWM.

    python build_v10.4_flakt_can.py            # torrkorning
    python build_v10.4_flakt_can.py --write    # bygg
"""
import copy
import sys
import build_lib as B
import build_logic as L

SRC = r'Builds\Elton_v10.3_branslefix.HWPDM'
DST = r'Builds\Elton_v10.4_flakt_can.HWPDM'

CLIMATE_ID = 0x503          # 1283
PWM_HZ = 200
LINEAR = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def add_caninput(cfg, slot, template_slot, label, bit_pos, bit_count, default=0):
    """Aktivera en tom CAN-ingang genom att KOPIERA en konfigurerad granne.

    Tomma platser har "tomma" falttyper som skiljer sig fran de konfigurerade
    (samma falla som timerns enabled: int 0 vs bool true). Att djupkopiera en
    fungerande granne och bara andra det som skiljer ger ratt typer overallt
    och kan inte tappa ett falt.
    """
    cis = cfg['CANInput']
    target = cis[slot - 1]
    assert not target.get('label'), \
        f'CI{slot} ar upptagen ({target.get("label")!r}) — vagrar skriva over'
    src = cis[template_slot - 1]
    assert src.get('label'), f'CI{template_slot} ar tom, duger inte som mall'

    new = copy.deepcopy(src)
    new['label'] = label
    B.set_field(new, 'CANID', CLIMATE_ID)
    B.set_field(new, 'bitPosition', bit_pos)
    B.set_field(new, 'bitCount', bit_count)
    B.set_field(new, 'variableDefault', default)
    B.set_field(new, 'enabled', True)
    for f in ('receiveCount', 'timeSinceLastReceive', 'timeoutPercentage',
              'currentValue', 'TestResultRaw', 'TestResultAdjusted'):
        if f in new:
            B.set_field(new, f, 0)
    cis[slot - 1] = new
    return new


def main():
    write = '--write' in sys.argv
    print(f'{"BYGGER" if write else "TORRKORNING"} v10.4 — {SRC} -> {DST}\n')

    cfg = B.load(SRC)
    v = B.VarMap(cfg)
    v.selftest()
    L.roundtrip_check(cfg)

    print('\n=== Andringar ===')

    # ── 1. rensa bort ingangen ──────────────────────────────────────────────
    i1 = cfg['Input'][0]
    assert i1['label'] == 'BLOWER', f'I1 ar {i1["label"]!r}'
    assert i1['enabled'] is False, 'I1 ar aktiverad — kontrollera innan den rensas'
    i1['label'] = 'RESERVE1'
    B.set_field(i1, 'mode', 0)
    B.set_field(i1, 'pullResistor', 0)
    print('  I1 (A7): BLOWER -> RESERVE1, nollstalld. Pinnen ar nu ledig.')

    # ── 2. CAN-ingangar ─────────────────────────────────────────────────────
    # CI15 Horn_Pulse ar en 1-bitsmall, CI16 LowBeam_L_PWM en 8-bitsmall.
    add_caninput(cfg, 28, 15, 'BLW_CMD',  bit_pos=0, bit_count=1, default=0)
    add_caninput(cfg, 29, 16, 'BLW_DUTY', bit_pos=8, bit_count=8, default=0)
    cmd_var, duty_var = v.caninput(28), v.caninput(29)
    print(f'  CI28 BLW_CMD : 0x{CLIMATE_ID:03X} byte 0 bit 0, 1 bit  -> var {cmd_var}')
    print(f'  CI29 BLW_DUTY: 0x{CLIMATE_ID:03X} byte 1, 8 bit       -> var {duty_var}')

    # ── 3. O11 ──────────────────────────────────────────────────────────────
    o11 = cfg['OutputHS'][10]
    assert o11['label'] == 'BLOWER', f'O11 ar {o11["label"]!r}'
    gf1, gf9, t2 = v.gf(1), v.gf(9), v.timer(2)
    L.set_and_chain(o11, [
        L.term(gf1, value=1),       # PDM strommatad
        L.term(t2, value=2),        # ingen krock
        L.term(gf9, value=1),       # inte under start (lastfallning)
        L.term(cmd_var, value=1),   # Pi:n beordrar
    ])
    B.set_field(o11, 'enabled', True)
    B.set_field(o11, 'PWMMappingEnable', True)
    B.set_field(o11, 'PWMMappingVariable', duty_var)
    B.set_field(o11, 'PWMFrequency', PWM_HZ)
    o11['PWMMapping'] = [type(o11['PWMMapping'][0])(x) for x in LINEAR]
    names = {gf1: 'GF1', gf9: 'GF9 LOAD_OK', t2: 'Timer2', cmd_var: 'BLW_CMD'}
    print(f'  O11 BLOWER: {L.describe(o11, names)}')
    print(f'              PWM {PWM_HZ} Hz, duty fran BLW_DUTY, mappning {LINEAR}')

    L.roundtrip_check(cfg)

    if not write:
        print('\nTorrkorning klar. Inget skrevs. Lagg till --write for att bygga.')
        return 0

    removed = B.drop_derived(cfg)
    if removed:
        print(f'\n  harledda falt borttagna: {", ".join(removed)}')
    print()
    B.save(cfg, DST)
    return 0 if B.verify(DST, checks(gf1, gf9, t2, cmd_var, duty_var)) else 1


def checks(gf1, gf9, t2, cmd_var, duty_var):
    def terms(c, i):
        return [r for r in c['OutputHS'][i]['functionInfix'] if L.is_term(r)]

    return [
        ('I1 rensad till RESERVE1, avstangd',
         lambda c: c['Input'][0]['label'] == 'RESERVE1' and c['Input'][0]['enabled'] is False),
        ('CI28 BLW_CMD pa 0x503 bit 0, 1 bit',
         lambda c: (c['CANInput'][27]['label'] == 'BLW_CMD'
                    and int(c['CANInput'][27]['CANID']) == CLIMATE_ID
                    and int(c['CANInput'][27]['bitPosition']) == 0
                    and int(c['CANInput'][27]['bitCount']) == 1
                    and c['CANInput'][27]['enabled'] is True)),
        ('CI29 BLW_DUTY pa 0x503 bit 8, 8 bit',
         lambda c: (c['CANInput'][28]['label'] == 'BLW_DUTY'
                    and int(c['CANInput'][28]['CANID']) == CLIMATE_ID
                    and int(c['CANInput'][28]['bitPosition']) == 8
                    and int(c['CANInput'][28]['bitCount']) == 8
                    and c['CANInput'][28]['enabled'] is True)),
        ('bada nya har 1000 ms timeout, default 0',
         lambda c: all(int(c['CANInput'][i]['timeoutTime']) == 1000
                       and int(c['CANInput'][i]['variableDefault']) == 0
                       for i in (27, 28))),
        ('O11 har exakt 4 villkor i 1 gren',
         lambda c: len(terms(c, 10)) == 4 and L.count_branches(c['OutputHS'][10]) == 1),
        ('O11 villkor = GF1, Timer2, GF9, BLW_CMD',
         lambda c: {int(r[1]) for r in terms(c, 10)} == {gf1, t2, gf9, cmd_var}),
        ('O11 refererar INTE nagon I1-variabel',
         lambda c: all(int(r[1]) not in (581, 582, 583) for r in terms(c, 10))),
        ('O11 PWM fran BLW_DUTY',
         lambda c: (c['OutputHS'][10]['PWMMappingEnable'] is True
                    and int(c['OutputHS'][10]['PWMMappingVariable']) == duty_var)),
        ('O11 mappning ar rak 1:1',
         lambda c: [int(x) for x in c['OutputHS'][10]['PWMMapping']] == LINEAR),
        ('O11 enabled', lambda c: c['OutputHS'][10]['enabled'] is True),
        ('lastfallningen kvar pa halv/helljus',
         lambda c: all(any(int(r[1]) == gf9 for r in terms(c, i)) for i in (13, 14, 6, 15))),

        # ── far inte ha rorts ──
        ('O5 FUEL fortfarande bara GF1', lambda c: len(terms(c, 4)) == 1),
        ('O17 HORN_2 kvar', lambda c: c['OutputHS'][16]['label'] == 'HORN_2'),
        ('I16 HANDBRAKE kvar', lambda c: c['Input'][15]['label'] == 'HANDBRAKE'),
        ('O4 PARK / O6 BRAKE kvar',
         lambda c: c['OutputHS'][3]['label'] == 'PARK' and c['OutputHS'][5]['label'] == 'BRAKE'),

        ('rundgangen haller', lambda c: L.roundtrip_check(c, verbose=False)),
        ('variabelkartan haller', lambda c: B.VarMap(c).selftest(verbose=False)),
    ]


if __name__ == '__main__':
    raise SystemExit(main())
