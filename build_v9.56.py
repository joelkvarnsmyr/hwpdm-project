"""Build Elton_v9.56_dual_horn.HWPDM from v9.55.

Changes:
  1. Create GF8 HORN_MASTER = I12 (HORN button) = True AND Timer2 (CRASH_TMR) = False
     (preserves the original "no horn during crash" safety from v9.55 O13 function)

  2. Enable O17 RESERVE17 -> HORN_2
     - copy fuse settings from O13 HORN as template
     - function: GF8 OR (LSE AND Horn_Pulse) OR (LSE AND Horn_2_Pulse)

  3. Rename O13 HORN -> HORN_1 for symmetry
     - new function: GF8 OR (LSE AND Horn_Pulse) OR (LSE AND Horn_1_Pulse)
     - same physical-button behavior preserved via GF8
     - Pi can pulse it individually via Horn_1_Pulse (new CAN signal)

  Variable IDs:
    I12 (HORN button)              = 617
    Timer2 CRASH_TMR               = 641
    GF8 HORN_MASTER                = 737
    CI1 LightShow_Enable (LSE)     = 850
    CI15 Horn_Pulse                = 920
    CI28 Horn_1_Pulse (after DBC v1.1 import) = 985
    CI29 Horn_2_Pulse (after DBC v1.1 import) = 990

WORKFLOW (user-side):
  1. Open Elton_v9.56_dual_horn.HWPDM in PDM software
  2. Import elton_pi_control_v1.1.dbc with Overwrite Existing CAN Input Data UNCHECKED
     -> populates CI28 (Horn_1_Pulse, var 985) and CI29 (Horn_2_Pulse, var 990)
  3. Verify in GUI:
     - O13 HORN_1 logic shows "CAN Input 28 (Horn_1_Pulse)"
     - O17 HORN_2 logic shows "CAN Input 29 (Horn_2_Pulse)"
  4. Save and flash.
"""
import json
import shutil

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.55_fuel_temp_fixes.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.56_dual_horn.HWPDM'

# Variables
I_HORN_BUTTON = 617    # I12 HORN
T_CRASH_TMR = 641      # Timer2 CRASH_TMR (debounce/crash safety)
GF_HORN_MASTER = 737   # GF8 HORN_MASTER (new)
LSE = 850              # CI1 LightShow_Enable
HORN_PULSE = 920       # CI15 Horn_Pulse (both horns, legacy)
HORN_1_PULSE = 985     # CI28 Horn_1_Pulse (NEW - after DBC v1.1 import)
HORN_2_PULSE = 990     # CI29 Horn_2_Pulse (NEW - after DBC v1.1 import)


def cond_input(var_id, value=True):
    return [1, var_id, 2, 10, 1, 1 if value else 2]


def cond_can(var_id, value=True):
    return [1, var_id, 2, 10, 1, 1 if value else 2]


AND_OP = [2, 1]
OR_OP = [2, 2]


def build_function(parts):
    flat = []
    for p in parts:
        flat.extend(p)
    return [len(flat) + 1] + flat


def build_output_infix(parts):
    """For OutputHS: each cond followed by closer; final terminator [['2','2'],[0]]."""
    result = []
    for p in parts:
        if len(p) == 6:
            result.append(p)
            result.append(['2', '1'])
            result.append([0])
        elif len(p) == 2:
            result.append(p)
    result.append(['2', '2'])
    result.append([0])
    return result


def build_gf_infix(parts):
    """For GenericFunction: each cond followed by closer; final terminator [0, ['2','2'], [0]]."""
    result = []
    for p in parts:
        if len(p) == 6:
            result.append(p)
            result.append(['2', '1'])
            result.append([0])
        elif len(p) == 2:
            result.append(p)
    # GF terminator differs from output
    result.append([0])
    result.append(['2', '2'])
    result.append([0])
    return result


def main():
    shutil.copy(SRC, DST)
    d = json.load(open(DST))

    # 1. GF8 HORN_MASTER = I12 AND NOT Timer2 (crash safety)
    print('=== 1. GF8 HORN_MASTER = I12=True AND Timer2(CRASH)=False ===')
    gf8 = d['GenericFunction'][7]
    gf8_parts = [
        cond_input(I_HORN_BUTTON, True),     # I12 = True (button pressed)
        AND_OP,
        cond_input(T_CRASH_TMR, False),      # Timer2 = False (no crash)
    ]
    gf8['enabled'] = True
    gf8['visibleInDOM'] = True
    gf8['label'] = 'HORN_MASTER'
    gf8['function'] = build_function(gf8_parts)
    gf8['functionInfix'] = build_gf_infix(gf8_parts)
    print(f'  GF8 function: {gf8["function"]}')

    # 2. O13 HORN_1 modification (rename + new function)
    print()
    print('=== 2. O13 HORN -> HORN_1 with new function ===')
    o13 = d['OutputHS'][12]
    o13_parts = [
        cond_input(GF_HORN_MASTER, True),    # GF8 (physical button safe)
        OR_OP,
        cond_can(LSE, True),                 # LightShow_Enable=True
        AND_OP,
        cond_can(HORN_PULSE, True),          # Horn_Pulse=True (both horns legacy)
        OR_OP,
        cond_can(LSE, True),                 # LightShow_Enable=True
        AND_OP,
        cond_can(HORN_1_PULSE, True),        # Horn_1_Pulse=True (only horn 1)
    ]
    o13['label'] = 'HORN_1'
    o13['function'] = build_function(o13_parts)
    o13['functionInfix'] = build_output_infix(o13_parts)
    print(f'  O13 HORN_1: function header={o13["function"][0]} (operands={o13["function"][0]-1})')

    # 3. O17 HORN_2 enable + configure
    print()
    print('=== 3. O17 RESERVE17 -> HORN_2 enable ===')
    o17 = d['OutputHS'][16]
    o17['enabled'] = True
    o17['visibleInDOM'] = True
    o17['label'] = 'HORN_2'
    # Copy fuse settings from O13 template (horn-class load)
    o17['lowFuse'] = 0
    o17['highFuse'] = 25
    o17['peakFuse'] = 50
    o17['peakFuseTime'] = 4000
    o17['tripMode'] = 0
    o17['retries'] = 2
    o17['stayOnTime'] = 0
    o17['turnOnDelay'] = 0
    o17['clearTime'] = 1
    o17['PWMSoftStartEnable'] = 0
    o17['PWMSoftStartTime'] = 100
    # Function: GF8 OR (LSE AND Horn_Pulse) OR (LSE AND Horn_2_Pulse)
    o17_parts = [
        cond_input(GF_HORN_MASTER, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HORN_PULSE, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HORN_2_PULSE, True),
    ]
    o17['function'] = build_function(o17_parts)
    o17['functionInfix'] = build_output_infix(o17_parts)
    print(f'  O17 HORN_2: function header={o17["function"][0]} (operands={o17["function"][0]-1})')
    print(f'  O17 HORN_2: enabled={o17["enabled"]} label={o17["label"]}')

    # Save
    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))
    print()
    print(f'Written: {DST}')

    # Verification
    print()
    print('=== Verification ===')
    d2 = json.load(open(DST))
    checks = [
        ('GF8 enabled', d2['GenericFunction'][7]['enabled'] is True),
        ('GF8 label = HORN_MASTER', d2['GenericFunction'][7]['label'] == 'HORN_MASTER'),
        ('O13 label = HORN_1', d2['OutputHS'][12]['label'] == 'HORN_1'),
        ('O17 enabled', d2['OutputHS'][16]['enabled'] is True),
        ('O17 label = HORN_2', d2['OutputHS'][16]['label'] == 'HORN_2'),
        ('O13 function uses GF8 (var 737)', 737 in d2['OutputHS'][12]['function']),
        ('O17 function uses GF8 (var 737)', 737 in d2['OutputHS'][16]['function']),
        ('O13 function uses Horn_1_Pulse var 985', 985 in d2['OutputHS'][12]['function']),
        ('O17 function uses Horn_2_Pulse var 990', 990 in d2['OutputHS'][16]['function']),
    ]
    for label, ok in checks:
        print(f'  {"OK" if ok else "FAIL"}: {label}')


if __name__ == '__main__':
    main()
