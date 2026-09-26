"""Delat bibliotek för script-byggda .HWPDM-filer.

BAKGRUND — varför detta finns
-----------------------------
Firmware 1.3.1 flyttade SAMTLIGA variabel-ID med +21 jämfört med 1.2.x. De gamla
`build_v9.*.py`-skripten skriver hårdkodade nummer ur det gamla schemat. Kör man dem
mot en 1.3.1-fil pekas logiken tyst om till FEL variabel — inget felmeddelande,
bara en bil som beter sig konstigt.

Därför löser detta bibliotek variabel-ID symboliskt och **verifierar kartan mot
kända landmärken i filen innan något skrivs**. Stämmer inte kartan avbryts bygget.

Tre fler 1.3.1-fällor som hanteras här:
  1. Numeriska fält är STRÄNGAR i OutputHS ('9', '16', '4000') men INT i Timer/GF/
     SensorCalibration/CANInput. Skriv aldrig rå typ — använd `set_field`.
  2. Nytt `sectionCRCs`-block med en CRC per sektion. Se `invalidate_crc`.
  3. Nya sektioner: CANAnalyser, IMU, sectionCRCs, wiringManager,
     loomProjectLink/Reference (Loom3D-kopplingen). `MPDMDevice` är borta.
"""
import json
import os
import sys

# Windows-konsolen är cp1252 och kvävs på icke-latin1-tecken. Tvinga UTF-8 så att
# utskrifter aldrig kraschar ett bygge som i övrigt lyckats.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, OSError):
    pass

# ── Variabelscheman ──────────────────────────────────────────────────────────
# VERIFIERAT mot konfiguratorns egen källkod (app.asar 1.3.1, src/mainDOM.js):
#
# `convertConfigFileVersion` är en fall-through switch på
# int(MetaData.ConfiguratorVersion utan punkter) — 1.2.7 -> 127, 1.3.1 -> 131.
# Från 127 till 131 sker EXAKT EN transformation: convertConfigVariablesV128toV129
# (mainDOM.js:1874). Övriga steg är no-ops.
#
# ⚠ Den transformationen är INTE en platt +21. Den är styckvis:
#      v < 24            oförändrad
#      24 <= v <= 59     TRANSPONERAD (CAN-mätvärden går från metrik-major till
#                        port-major) — inget offset alls
#      60 <= v <= 69     +12
#      v >= 70           +21   (= +12 för CAN-blocket, +9 för IMU-blocket)
#
# Alla våra logikvariabler (ingångar ~560+, timers ~640+, GF ~730+, CANInput ~850+)
# ligger >= 70 och får därför +21. Konstanten 1 ligger < 24 och är oförändrad.
# Men en accessor i 24–69 hade blivit fel med platt +21 — därför portas appens
# funktion exakt nedan istället för att gissa ett offset.
_LEGACY_MAX_VERSION = 128        # sista versionen i det gamla variabelschemat


def remap_v128_v129(v):
    """Exakt port av mainDOM.js:1884 `remapVariable` (V128 -> V129)."""
    if v is None or v == '':
        return v
    try:
        n = int(v)
    except (TypeError, ValueError):
        return v
    FIRST_CAN, LAST_CAN = 24, 59
    PORTS, PER_PORT = 3, 16
    FIRST_SHIFTED = 60
    CAN_OFFSET = 12
    FIRST_AFTER_IMU = 70
    IMU_OFFSET = 9
    if FIRST_CAN <= n <= LAST_CAN:
        i = n - FIRST_CAN
        return FIRST_CAN + (i % PORTS) * PER_PORT + (i // PORTS)
    if n < FIRST_SHIFTED:
        return n
    return n + CAN_OFFSET + (IMU_OFFSET if n >= FIRST_AFTER_IMU else 0)


def config_version_int(cfg):
    """Samma tolkning som appen: MetaData.ConfiguratorVersion utan punkter.

    OBS: appen använder MetaData.ConfiguratorVersion, INTE
    Global.deviceFirmwareVersion — de skiljer sig (v9.59: 1.2.7 respektive 1.2.3).
    """
    raw = str((cfg.get('MetaData') or {}).get('ConfiguratorVersion', '')).strip()
    if not raw:
        raise VarMapError('Filen saknar MetaData.ConfiguratorVersion — vägrar gissa schema.')
    try:
        return int(raw.replace('.', '')), raw
    except ValueError:
        raise VarMapError(f'Kan inte tolka ConfiguratorVersion {raw!r}.')


class VarMapError(RuntimeError):
    pass


class VarMap:
    """Symboliska variabel-ID för en given config. Verifierar sig själv."""

    def __init__(self, cfg):
        self.version_int, self.version = config_version_int(cfg)
        self.legacy = self.version_int <= _LEGACY_MAX_VERSION
        self._cfg = cfg

    def _map(self, legacy_id):
        """Basformlerna är skrivna i det gamla schemat; översätt vid behov."""
        return legacy_id if self.legacy else remap_v128_v129(legacy_id)

    # Basformler i det gamla (<=128) schemat.
    def input_status(self, n):   return self._map(557 + 5 * n)
    def input_voltage(self, n):  return self._map(555 + 5 * n)
    def timer(self, n):          return self._map(639 + n)
    def gf(self, n):             return self._map(729 + n)
    def caninput(self, n):       return self._map(845 + 5 * n)

    @staticmethod
    def const_true():
        """Konstanten 'alltid sann' (ID 1) — under 24, oförändrad i alla scheman."""
        return 1

    @property
    def offset(self):
        """Effektivt offset för våra logikvariabler (>=70). Endast för utskrift."""
        return 0 if self.legacy else 21

    # ── självtest ────────────────────────────────────────────────────────────
    def selftest(self, verbose=True):
        """Bevisa kartan mot landmärken i filen. Kastar vid avvikelse.

        Landmärkena är valda för att vara stabila: utgångar vars logik vi känner
        från dokumentationen och som funnits oförändrade genom hela v9-serien.
        """
        cfg = self._cfg
        outs = cfg['OutputHS']
        gfs = cfg['GenericFunction']
        problems, checked = [], []

        def nums(fn):
            return {int(v) for v in fn if str(v).lstrip('-').isdigit()}

        def want(label, idx, expect, why):
            if idx >= len(outs) or outs[idx].get('label') != label:
                return                      # landmärket saknas i denna build
            got = nums(outs[idx]['function'])
            missing = {k: v for k, v in expect.items() if v not in got}
            checked.append(f'O{idx+1} {label}')
            if missing:
                problems.append(f'O{idx+1} {label}: saknar {missing} i {sorted(got)} — {why}')

        # BRAKE styrs av bromsljusbrytaren på I4.
        want('BRAKE', 5, {'I4 status': self.input_status(4)},
             'bromsljusbrytaren')
        # TURN_R = Timer1 OCH (I6 ELLER I3-hazard).
        want('TURN_R', 23, {'Timer1': self.timer(1),
                            'I6 status': self.input_status(6),
                            'I3 status': self.input_status(3)},
             'blinkerslogiken')
        # BLOWER läser vredets spänning på I1.
        want('BLOWER', 10, {'I1 voltage': self.input_voltage(1)},
             'fläktvredet')

        # GF4 OIL_OR_CR refererar GF3 → bevisar GF-formeln.
        if len(gfs) > 3 and gfs[3].get('label') == 'OIL_OR_CR':
            got = nums(gfs[3]['function'])
            checked.append('GF4 OIL_OR_CR')
            if self.gf(3) not in got:
                problems.append(f'GF4: saknar GF3={self.gf(3)} i {sorted(got)}')
        # GF6 PARK_OR_HOLD refererar GF5.
        if len(gfs) > 5 and gfs[5].get('label') == 'PARK_OR_HOLD':
            got = nums(gfs[5]['function'])
            checked.append('GF6 PARK_OR_HOLD')
            if self.gf(5) not in got:
                problems.append(f'GF6: saknar GF5={self.gf(5)} i {sorted(got)}')

        # CANInput-formeln mot en enabled CI:s ordningsnummer.
        cis = cfg.get('CANInput', [])
        for i, ci in enumerate(cis):
            if ci.get('enabled') and ci.get('label') == 'Park_Lights_Cmd':
                # O4 PARK ska referera just denna CI.
                got = nums(outs[3]['function'])
                checked.append('CI Park_Lights_Cmd -> O4')
                if self.caninput(i + 1) not in got:
                    problems.append(
                        f'CANInput-formeln: CI{i+1} Park_Lights_Cmd väntas som '
                        f'{self.caninput(i+1)}, finns ej i O4:s logik {sorted(got)}')
                break

        if not checked:
            raise VarMapError('Inga landmärken kunde kontrolleras — vägrar gissa.')
        if problems:
            raise VarMapError(
                f'Variabelkartan stämmer INTE för configVersion {self.version} '
                f'({"gammalt" if self.legacy else "nytt"} schema):\n  ' + '\n  '.join(problems))
        if verbose:
            print(f'  VarMap OK — configVersion {self.version} ({self.version_int}), '
                  f'{"gammalt" if self.legacy else "nytt"} schema (offset {self.offset:+d} '
                  f'för var >= 70), {len(checked)} landmärken: {", ".join(checked)}')
        return True


# ── Typbevarande skrivning ───────────────────────────────────────────────────
def set_field(obj, key, value, *, allow_new=False):
    """Skriv obj[key]=value men BEHÅLL fältets befintliga typ.

    1.3.1 lagrar t.ex. säkringsvärden som strängar ('9') men timervärden som int.
    Skriver man rå typ kan konfiguratorn tolka fältet fel eller tappa det.
    """
    if key not in obj:
        if not allow_new:
            raise KeyError(f'Fältet {key!r} finns inte — sätt allow_new=True om det är meningen.')
        obj[key] = value
        return value
    old = obj[key]
    if isinstance(old, bool):
        new = bool(value)
    elif isinstance(old, str):
        new = str(value)
    elif isinstance(old, int):
        # Typerna är inkonsekventa även inom OutputHS: O11.peakFuseTime är strängen
        # '4000' men O13.peakFuseTime är heltalet 4000. Att tysta trunkera 0.5 -> 0
        # i ett int-fält satte en gång hornets toppsäkringsfönster till noll.
        # Vägra hellre än att tappa data.
        if isinstance(value, float) and not float(value).is_integer():
            raise ValueError(
                f'{key!r} är ett heltalsfält i denna fil men fick {value!r}. '
                f'Avrundning skulle ändra innebörden — välj ett heltal, eller '
                f'kontrollera om fältet är sträng i andra poster (typerna varierar '
                f'mellan poster i samma sektion).')
        new = int(value)
    elif isinstance(old, float):
        new = float(value)
    else:
        new = type(old)(value)
    obj[key] = new
    return new


# ── sectionCRCs ──────────────────────────────────────────────────────────────
# Kodkarta: sektionsnamn → tvåbokstavskod i sectionCRCs.byCode
CRC_CODES = {
    'Global': 'GL', 'OutputHS': 'OP', 'Input': 'IP', 'LoggingGroup': 'LG',
    'Timer': 'TI', 'Counter': 'CT', 'GenericFunction': 'GF',
    'MathsChannel': 'MC', 'SensorCalibration': 'SC', 'TwoDTable': 'TD',
    'CANKeypad': 'CK', 'CANInputFilter': 'CF', 'CANInput': 'CI',
    'CANOutput': 'CO', 'CANStream': 'CS', 'LINBus': 'LN',
}


def drop_derived(cfg):
    """Ta bort de härledda write-only-fälten. Föredra detta framför invalidate_crc.

    VERIFIERAT mot app.asar 1.3.1:
      - Spara (mainDOM.js:1667-1689) räknar om BÅDE `rawSendData`
        (`buildSendConfigArray()`) och `sectionCRCs` (`calculateAllHostConfigCRCs(Host)`)
        ur minnesobjektet `Host` — aldrig ur filen.
      - Läsa (mainDOM.js:2055-2056) gör `delete` på båda.
      - Samtliga 10 referenser till `sectionCRCs` i hela appen är skrivningar plus
        den ena delete. INGENTING läser fältet. Samma för `rawSendData` (2 ref).

    Slutsats: fälten valideras inte. Att utelämna dem är säkert, och renare än att
    lämna stale värden kvar. Ingen GUI-rundtur krävs av CRC-skäl.
    """
    removed = [k for k in ('rawSendData', 'sectionCRCs') if k in cfg]
    for k in removed:
        del cfg[k]
    return removed


def invalidate_crc(cfg, *sections):
    """Nolla CRC för angivna sektioner. Behålls för bakåtkompatibilitet.

    `drop_derived()` är att föredra — fälten läses ändå aldrig (se dess docstring).
    """
    crcs = cfg.get('sectionCRCs')
    if not crcs:
        return []
    zeroed = []
    by_code = crcs.get('byCode', {})
    by_index = crcs.get('byIndex', [])
    codes = list(by_code.keys())
    for sec in sections:
        code = CRC_CODES.get(sec)
        if code and code in by_code:
            by_code[code] = 0
            if code in codes:
                i = codes.index(code)
                if i < len(by_index):
                    by_index[i] = 0
            zeroed.append(f'{sec}({code})')
    return zeroed


# ── Ladda / spara ────────────────────────────────────────────────────────────
def load(path):
    with open(path, encoding='utf-8') as f:
        cfg = json.load(f)
    g = cfg.get('Global', {})
    print(f'  Läste {os.path.basename(path)} — {g.get("deviceModel")}, '
          f'fw {g.get("deviceFirmwareVersion")}, modelVersion {g.get("deviceModelVersion")}')
    return cfg


def save(cfg, path):
    """Skriv kompakt, som konfiguratorn själv gör."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=None, separators=(',', ':'), ensure_ascii=False)
    print(f'  Skrev {path} ({os.path.getsize(path):,} byte)')


def verify(path, checks):
    """Läs tillbaka filen och kör kontrollerna. Returnerar True om allt gick igenom."""
    cfg = load(path)
    ok = True
    print('\n=== Verifiering ===')
    for name, fn in checks:
        try:
            res = bool(fn(cfg))
        except Exception as e:
            res = False
            name = f'{name}  [{type(e).__name__}: {e}]'
        print(f'  [{"OK  " if res else "FEL "}] {name}')
        ok = ok and res
    print('\n' + ('ALLA KONTROLLER OK' if ok else '*** KONTROLLER MISSLYCKADES ***'))
    return ok
