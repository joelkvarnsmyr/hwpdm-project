"""
Build Elton_v9.53_all_outputs.HWPDM from Elton_v9.52_o7_test.HWPDM
Adds CAN-control logic to all relevant outputs.

CANInput variable IDs (CI1=850, sequential):
  850 CI1  LightShow_Enable
  851 CI2  LightShow_Heartbeat
  852 CI3  Safety_Override
  853 CI4  LowBeam_L_Cmd
  854 CI5  LowBeam_R_Cmd
  855 CI6  HiBeam_L_Cmd
  856 CI7  HiBeam_R_Cmd
  857 CI8  Park_Lights_Cmd
  858 CI9  Turn_L_Cmd
  859 CI10 Turn_R_Cmd
  860 CI11 Brake_Lights_Cmd
  861 CI12 Reverse_Lights_Cmd
  862 CI13 Hazard_Cmd
  863 CI14 Interior_Cmd
  864 CI15 Horn_Pulse

Format:
  Condition (Input/Timer/GF): [1, varID, 2, 10, 1, 1=True/2=False]
  Condition (CANInput):        [1, varID, 2, 1, 1, 1=True/2=False]
  Operator AND: [2, 1]
  Operator OR:  [2, 2]
  Function header byte = operand_count + 1
  functionInfix output terminator: ['2', '1'], [0], ['2', '2'], [0]
"""
import json
import shutil

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.52_o7_test.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.53_all_outputs.HWPDM'

# CANInput var IDs
# Each CANInput slot has 5 vars (Value at offset 0). Layout: CI_n Value = 850 + (n-1)*5
LSE = 850    # CI1 LightShow_Enable Value
SOR = 860    # CI3 Safety_Override Value
LB_L = 865   # CI4 LowBeam_L_Cmd Value
LB_R = 870   # CI5 LowBeam_R_Cmd Value
HB_L = 875   # CI6 HiBeam_L_Cmd Value
HB_R = 880   # CI7 HiBeam_R_Cmd Value
PARK = 885   # CI8 Park_Lights_Cmd Value
TL = 890     # CI9 Turn_L_Cmd Value
TR = 895     # CI10 Turn_R_Cmd Value
BRK = 900    # CI11 Brake_Lights_Cmd Value
REV = 905    # CI12 Reverse_Lights_Cmd Value
HAZ = 910    # CI13 Hazard_Cmd Value
HORN = 920   # CI15 Horn_Pulse Value


def cond_can(var_id, value=True):
    """CANInput condition: [1, varID, 2, 10, 1, 1or2] - use Equals (10), not AND (1)
    AND-with-False is always False, breaks "Equals False" logic. Use Equals matching
    Input/Timer/GF format."""
    return [1, var_id, 2, 10, 1, 1 if value else 2]


def cond_input(var_id, value=True):
    """Input/Timer/GF condition: [1, varID, 2, 10, 1, 1or2]"""
    return [1, var_id, 2, 10, 1, 1 if value else 2]


# Operators
OR_OP = [2, 2]
AND_OP = [2, 1]


def build_function(parts):
    """parts = list of conditions (6-elem) and operators (2-elem). Returns binary function array."""
    flat = []
    for p in parts:
        flat.extend(p)
    header = len(flat) + 1
    return [header] + flat


def build_infix(parts):
    """Build functionInfix with atom closers and output terminator."""
    result = []
    for p in parts:
        if len(p) == 6:  # condition
            result.append(p)
            result.append(['2', '1'])
            result.append([0])
        elif len(p) == 2:  # operator
            result.append(p)
    # output terminator
    result.append(['2', '2'])
    result.append([0])
    return result


def set_output_function(d, output_idx, parts, output_kind='OutputHS'):
    """Set output function and functionInfix from parts."""
    o = d[output_kind][output_idx]
    o['function'] = build_function(parts)
    o['functionInfix'] = build_infix(parts)


def main():
    shutil.copy(SRC, DST)
    d = json.load(open(DST))

    # ========================================
    # Category A — SUPPRESS in show mode
    # Pattern: (LSE=False AND original) OR (LSE=True AND CAN_cmd)
    # ========================================

    # O4 PARK
    # Original: var 1 = True (always on when PDM powered)
    # New: (LSE=F AND var1=T) OR (LSE=T AND Park_Cmd=T)
    set_output_function(d, 3, [
        cond_can(LSE, False),
        AND_OP,
        cond_input(1, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(PARK, True),
    ])

    # O14 LOWBEAM_L
    # Original: I2 (HIBEAM) = False (= DRL when high beam not pulled)
    # New: (LSE=F AND I2=F) OR (LSE=T AND LowBeam_L_Cmd=T)
    set_output_function(d, 13, [
        cond_can(LSE, False),
        AND_OP,
        cond_input(567, False),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(LB_L, True),
    ])

    # O15 LOWBEAM_R
    # Same as O14 but for right
    set_output_function(d, 14, [
        cond_can(LSE, False),
        AND_OP,
        cond_input(567, False),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(LB_R, True),
    ])

    # ========================================
    # Category B — OR with original (additive)
    # Pattern: original OR (LSE=True AND CAN_cmd)
    # ========================================

    # O5 FUEL (suppress in show mode unless Safety_Override)
    # Original (when enabled): GF1 PWR_ALIVE = True (= always on when PDM powered)
    # New: (LSE=F AND GF1=T) OR (Safety_Override=T AND GF1=T)
    # → Normal mode: fuel pump runs. Show mode: OFF unless explicit override.
    set_output_function(d, 4, [
        cond_can(LSE, False),
        AND_OP,
        cond_input(730, True),
        OR_OP,
        cond_can(SOR, True),
        AND_OP,
        cond_input(730, True),
    ])

    # O6 BRAKE
    # Original: I4 (BRAKE input) = True
    # New: I4=T OR (LSE=T AND Brake_Cmd=T)
    set_output_function(d, 5, [
        cond_input(577, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(BRK, True),
    ])

    # O7 HIBEAM_R - FIX gating (replace user's "LSE=T AND True" with proper)
    # New: I2=T OR (LSE=T AND HiBeam_R_Cmd=T)
    set_output_function(d, 6, [
        cond_input(567, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HB_R, True),
    ])

    # O13 HORN
    # Original: I12=T AND Timer641=F
    # New: original OR (LSE=T AND Horn_Pulse=T)
    set_output_function(d, 12, [
        cond_input(617, True),
        AND_OP,
        cond_input(641, False),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HORN, True),
    ])

    # O16 HIBEAM_L
    # Original: I2=T (same as O7)
    # New: I2=T OR (LSE=T AND HiBeam_L_Cmd=T)
    set_output_function(d, 15, [
        cond_input(567, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HB_L, True),
    ])

    # O19 REVERSE (currently disabled but updating function for when enabled)
    # Original: I7 (REVERSE) = True AND Timer641=F
    # New: original OR (LSE=T AND Reverse_Cmd=T)
    set_output_function(d, 18, [
        cond_input(592, True),
        AND_OP,
        cond_input(641, False),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(REV, True),
    ])

    # O24 TURN_R
    # Original: (T1=T AND I6=T) OR (T1=T AND I3=T) - blink with right stalk OR hazard
    # New: original OR (LSE=T AND Turn_R_Cmd=T) OR (LSE=T AND Hazard_Cmd=T)
    set_output_function(d, 23, [
        cond_input(640, True),
        AND_OP,
        cond_input(587, True),
        OR_OP,
        cond_input(640, True),
        AND_OP,
        cond_input(572, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(TR, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HAZ, True),
    ])

    # O25 TURN_L
    # Original: (T1=T AND I5=T) OR (T1=T AND I3=T)
    # New: original OR (LSE=T AND Turn_L_Cmd=T) OR (LSE=T AND Hazard_Cmd=T)
    set_output_function(d, 24, [
        cond_input(640, True),
        AND_OP,
        cond_input(582, True),
        OR_OP,
        cond_input(640, True),
        AND_OP,
        cond_input(572, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(TL, True),
        OR_OP,
        cond_can(LSE, True),
        AND_OP,
        cond_can(HAZ, True),
    ])

    # Save
    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))

    print(f'Written: {DST}')

    # Verify
    print()
    print('=== Verification — output functions ===')
    for i, label in [(3, 'PARK'), (4, 'FUEL'), (5, 'BRAKE'), (6, 'HIBEAM_R'), (12, 'HORN'),
                     (13, 'LOWBEAM_L'), (14, 'LOWBEAM_R'), (15, 'HIBEAM_L'),
                     (18, 'REVERSE'), (23, 'TURN_R'), (24, 'TURN_L')]:
        o = d['OutputHS'][i]
        fn = o['function']
        print(f'O{i+1:2d} {label:10s}: header={fn[0]} len={len(fn)} (operands={fn[0]-1})')


if __name__ == '__main__':
    main()
