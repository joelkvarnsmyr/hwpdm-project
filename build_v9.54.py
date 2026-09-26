"""Build Elton_v9.54_pwm_enable.HWPDM from v9.53.

PWM-enable lämpliga outputs + sätter variableDefault=255 på PWM CANInputs
så att default beteende (Pi tyst) = full brightness.

PWM CANInput variable IDs (CI16-23, Value at offset 0):
  CI16 LowBeam_L_PWM   = 925
  CI17 LowBeam_R_PWM   = 930
  CI18 HiBeam_L_PWM    = 935
  CI19 HiBeam_R_PWM    = 940
  CI20 Park_Lights_PWM = 945
  CI21 Brake_Lights_PWM = 950 (mapped but output not PWM-enabled — safety)
  CI22 Turn_L_PWM      = 955 (samma)
  CI23 Turn_R_PWM      = 960 (samma)

Mappning till outputs:
  O4  PARK       <- CI20 Park_Lights_PWM (945)
  O7  HIBEAM_R   <- CI19 HiBeam_R_PWM    (940)
  O14 LOWBEAM_L  <- CI16 LowBeam_L_PWM   (925)
  O15 LOWBEAM_R  <- CI17 LowBeam_R_PWM   (930)
  O16 HIBEAM_L   <- CI18 HiBeam_L_PWM    (935)

Skipped (safety):
  O6 BRAKE — måste 100% vid fysisk broms
  O24/O25 TURN — måste 100% vid riktiga blinkers

PWM-inställningar per output:
  PWMMappingEnable: True
  PWMMappingVariable: <CI Value var>
  PWMMapping: [0,10,20,30,40,50,60,70,80,90,100] (linjär)
  PWMFrequency: 200 (Hz — glödlampor, under flicker-tröskel)
  PWMSoftStartEnable: True
  PWMSoftStartTime: 0.1 (s — 100ms soft-start sparar glödtråd)
"""
import json
import shutil

SRC = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.53_all_outputs.HWPDM'
DST = r'C:\Users\joel\Documents\Elton LT Wire diagrams\hwpdm-project\Builds\Elton_v9.54_pwm_enable.HWPDM'

# CANInput slot index -> PWM Value variable ID (varID = 850 + (n-1)*5)
PWM_CI_INDEX_TO_VAR = {
    15: 925,   # CI16 LowBeam_L_PWM
    16: 930,   # CI17 LowBeam_R_PWM
    17: 935,   # CI18 HiBeam_L_PWM
    18: 940,   # CI19 HiBeam_R_PWM
    19: 945,   # CI20 Park_Lights_PWM
    20: 950,   # CI21 Brake_Lights_PWM
    21: 955,   # CI22 Turn_L_PWM
    22: 960,   # CI23 Turn_R_PWM
}

# Output index -> PWM Mapping Variable
PWM_ENABLED_OUTPUTS = {
    3:  945,   # O4 PARK       <- CI20 Park_Lights_PWM
    6:  940,   # O7 HIBEAM_R   <- CI19 HiBeam_R_PWM
    13: 925,   # O14 LOWBEAM_L <- CI16 LowBeam_L_PWM
    14: 930,   # O15 LOWBEAM_R <- CI17 LowBeam_R_PWM
    15: 935,   # O16 HIBEAM_L  <- CI18 HiBeam_L_PWM
}

# Linear mapping: input 0-255 → duty 0-100% over 11 evenly spaced points
LINEAR_MAPPING = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def main():
    shutil.copy(SRC, DST)
    d = json.load(open(DST))

    # 1. Set variableDefault=255 for PWM CANInputs (failsafe to full brightness)
    print('=== Setting variableDefault=255 for PWM CANInputs ===')
    for ci_idx in PWM_CI_INDEX_TO_VAR:
        ci = d['CANInput'][ci_idx]
        before = ci.get('variableDefault', 0)
        ci['variableDefault'] = 255
        print(f'  CI{ci_idx+1:2d} {ci["label"]:20s}: variableDefault {before} -> 255')

    # 2. Enable PWM on selected outputs
    print()
    print('=== Enabling PWM mapping on outputs ===')
    for out_idx, pwm_var in PWM_ENABLED_OUTPUTS.items():
        o = d['OutputHS'][out_idx]
        label = o['label']
        before_enable = o.get('PWMMappingEnable', False)
        before_var = o.get('PWMMappingVariable', 1)
        before_freq = o.get('PWMFrequency', 100)
        before_ss = o.get('PWMSoftStartTime', 0)

        o['PWMMappingEnable'] = True
        o['PWMMappingVariable'] = pwm_var
        o['PWMMapping'] = LINEAR_MAPPING[:]
        o['PWMFrequency'] = 200
        o['PWMSoftStartEnable'] = True
        o['PWMSoftStartTime'] = 0.1

        print(f'  O{out_idx+1:2d} {label:12s}: PWMMappingVar {before_var} -> {pwm_var}, '
              f'Freq {before_freq} -> 200, SoftStart {before_ss} -> 0.1')

    # 3. Save
    with open(DST, 'w') as f:
        json.dump(d, f, indent=None, separators=(',', ':'))
    print()
    print(f'Written: {DST}')

    # 4. Verify by re-reading and spot-checking
    print()
    print('=== Verification ===')
    d2 = json.load(open(DST))
    for out_idx, pwm_var in PWM_ENABLED_OUTPUTS.items():
        o = d2['OutputHS'][out_idx]
        ok = (o['PWMMappingEnable'] is True and
              o['PWMMappingVariable'] == pwm_var and
              o['PWMMapping'] == LINEAR_MAPPING and
              o['PWMFrequency'] == 200 and
              o['PWMSoftStartEnable'] is True and
              o['PWMSoftStartTime'] == 0.1)
        status = 'OK' if ok else 'MISMATCH'
        print(f'  O{out_idx+1:2d} {o["label"]:12s}: {status}')

    # Verify CANInput defaults
    for ci_idx in PWM_CI_INDEX_TO_VAR:
        ci = d2['CANInput'][ci_idx]
        ok = ci['variableDefault'] == 255
        print(f'  CI{ci_idx+1:2d} {ci["label"]:20s}: variableDefault={ci["variableDefault"]} {"OK" if ok else "FAIL"}')

    # Verify function arrays untouched
    print()
    print('=== Function arrays untouched (sanity) ===')
    d_pre = json.load(open(SRC))
    for i in [3, 5, 6, 12, 13, 14, 15, 18, 23, 24]:
        pre = d_pre['OutputHS'][i].get('function')
        post = d2['OutputHS'][i].get('function')
        ok = pre == post
        print(f'  O{i+1:2d} {d2["OutputHS"][i]["label"]:12s}: function unchanged = {ok}')


if __name__ == '__main__':
    main()
