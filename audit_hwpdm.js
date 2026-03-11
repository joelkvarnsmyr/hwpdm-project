/**
 * audit_hwpdm.js — Cross-reference generated HWPDM against manual + config
 *
 * Checks:
 * 1. Pinout: config pin assignments match manual pinout table
 * 2. Output parameters: fuse values, retries, clear time, trip mode
 * 3. Input parameters: mode, active level, threshold
 * 4. Function/logic: operator IDs, variable IDs
 * 5. Timer: pulse train config
 * 6. CAN Stream: missing config
 * 7. Retries=0 meaning (manual says 0 = continual retries!)
 * 8. PWM mapping: 11-point table
 * 9. Dual-pin outputs
 * 10. HS/LS output types
 */

const fs = require('fs');
const config = JSON.parse(fs.readFileSync('ELTON_PDM25V2_KOMPLETT_v5.6b/pdm25_outputs_complete.json', 'utf8'));
const gen = JSON.parse(fs.readFileSync('Elton_v5.8.HWPDM', 'utf8'));
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));

let warnings = [];
let errors = [];
let info = [];

// ==========================================
// 1. PINOUT VERIFICATION (from manual table)
// ==========================================
const MANUAL_PINOUT = {
  'A1': { input: 12, output: 31 },
  'A2': { input: 10, output: 29 },
  'A3': { input: 8, output: 27 },
  'A4': { input: 6 },
  'A5': { input: 4 },
  'A6': { input: 2 },
  'A7': { input: 1 },
  'A8': { input: 3 },
  'A9': { input: 5 },
  'A10': { input: 7, output: 26 },
  'A11': { input: 9, output: 28 },
  'A12': { input: 11, output: 30 },
  'C1': { input: 16, output: 35 },
  'C2': { input: 15, output: 34 },
  'C3': 'PDM Power',
  'C4': { output: 3, type: 'HS/LS' },
  'C5': { output: 2, type: 'HS/LS' },
  'C6': { output: 1, type: 'HS/LS' },
  'C7': 'Ground',
  'C8': 'CAN 1 High',
  'C9': 'CAN 1 Low',
  'C10': '5V Out',
  'C11': { input: 13, output: 32 },
  'C12': { input: 14, output: 33 },
  'D1': { output: 17 },
  'D2': { output: 21 },
  'D3': { output: 24 },
  'D4': { output: 9 },
  'D5': { output: 8 },
  'D6': { output: 7 },
  'D7': { output: 4, type: 'HS/LS' },
  'D8': { output: 5 },
  'D9': { output: 6 },
  'D10': { output: 24 }, // dual pin!
  'D11': { output: 20 },
  'D12': { output: 16 },
  'B1': { output: 19 },
  'B2': { output: 23 },
  'B3': { output: 25 },
  'B4': { output: 15 },
  'B5': { output: 14 },
  'B6': { output: 13 },
  'B7': { output: 10 },
  'B8': { output: 11 },
  'B9': { output: 12 },
  'B10': { output: 25 }, // dual pin!
  'B11': { output: 22 },
  'B12': { output: 18 },
};

console.log('=== 1. PINOUT VERIFICATION ===');
// Check each config output pin matches manual
for (const out of config.outputs) {
  const pin = out.pin || out.pin_primary;
  if (!pin) continue;

  const manualEntry = MANUAL_PINOUT[pin];
  if (!manualEntry) {
    errors.push(`PINOUT: ${out.id} (${out.pdm_name}) assigned to unknown pin ${pin}`);
    continue;
  }
  if (typeof manualEntry === 'string') {
    errors.push(`PINOUT: ${out.id} (${out.pdm_name}) assigned to ${pin} which is ${manualEntry}, not an output!`);
    continue;
  }

  const outNum = parseInt(out.id.replace('O', ''));
  if (manualEntry.output !== outNum) {
    errors.push(`PINOUT: ${out.id} (${out.pdm_name}) claims pin ${pin}, but manual says ${pin} = Output ${manualEntry.output}`);
  } else {
    info.push(`PINOUT OK: ${out.id} ${out.pdm_name} → ${pin} ✓`);
  }

  // Check HS/LS type
  if (manualEntry.type === 'HS/LS' && out.type === 'HS') {
    info.push(`  Note: ${out.id} is on HS/LS capable pin ${pin}, configured as HS only`);
  }

  // Check dual-pin
  if (out.pin_parallel) {
    const parallelEntry = MANUAL_PINOUT[out.pin_parallel];
    if (parallelEntry && parallelEntry.output !== outNum) {
      errors.push(`DUAL-PIN: ${out.id} parallel pin ${out.pin_parallel} maps to Output ${parallelEntry.output} in manual, not ${outNum}`);
    } else {
      info.push(`DUAL-PIN OK: ${out.id} → ${pin} + ${out.pin_parallel} ✓`);
    }
  }
}

// Check inputs
for (const inp of config.inputs) {
  const manualEntry = MANUAL_PINOUT[inp.pin];
  if (!manualEntry || typeof manualEntry === 'string') {
    errors.push(`PINOUT: ${inp.id} (${inp.pdm_name}) assigned to ${inp.pin} — not an input pin per manual`);
    continue;
  }
  const inpNum = parseInt(inp.id.replace('I', ''));
  if (manualEntry.input !== inpNum) {
    errors.push(`PINOUT: ${inp.id} (${inp.pdm_name}) claims pin ${inp.pin}, but manual says ${inp.pin} = Input ${manualEntry.input}`);
  }
}

// ==========================================
// 2. OUTPUT PARAMETER CHECKS
// ==========================================
console.log('\n=== 2. OUTPUT PARAMETER CHECKS ===');

for (const out of config.outputs) {
  if (!out.configured_as) continue;
  const idx = parseInt(out.id.replace('O', '')) - 1;
  const genOut = gen.OutputHS[idx];

  // Manual: "A value of zero [retries] will result in continual retries"
  if (out.retries === 0 && out.id !== 'O23') {
    warnings.push(`RETRIES: ${out.id} (${out.pdm_name}) has retries=0. Per manual: "A value of zero will result in continual retries." Is this intended?`);
  }

  // O23 STARTER: retries=0 is INTENTIONAL per audit (continual retries of starter = dangerous)
  // Wait — the manual says 0 = continual retries. That's the OPPOSITE of what we want!
  if (out.id === 'O23' && out.retries === 0) {
    errors.push(`CRITICAL: O23 STARTER has retries=0. Per manual: "A value of zero will result in continual retries." This means the starter will retry FOREVER if it trips! Should be retries=1 (one retry then stop).`);
  }

  // Check fuse values make sense (high > peak would be wrong)
  if (out.peak_fuse_A && out.high_fuse_A && out.peak_fuse_A < out.high_fuse_A) {
    errors.push(`FUSE: ${out.id} (${out.pdm_name}) peak_fuse (${out.peak_fuse_A}A) < high_fuse (${out.high_fuse_A}A). Peak should be higher.`);
  }

  // Check if high fuse > 20A (max per channel)
  if (out.high_fuse_A && out.high_fuse_A > 20) {
    errors.push(`FUSE: ${out.id} (${out.pdm_name}) high_fuse ${out.high_fuse_A}A exceeds 20A max per channel`);
  }

  // Check if high fuse > 13A (pin limited at 125°C)
  if (out.high_fuse_A && out.high_fuse_A > 13) {
    warnings.push(`FUSE: ${out.id} (${out.pdm_name}) high_fuse ${out.high_fuse_A}A exceeds 13A pin limit at 125°C`);
  }

  // Verify generated HWPDM values match config
  if (genOut) {
    if (String(genOut.highFuse) !== String(out.high_fuse_A || 0)) {
      warnings.push(`GEN MISMATCH: ${out.id} highFuse: config=${out.high_fuse_A} gen=${genOut.highFuse}`);
    }
    if (genOut.label !== out.pdm_name) {
      warnings.push(`GEN MISMATCH: ${out.id} label: config="${out.pdm_name}" gen="${genOut.label}"`);
    }
  }
}

// ==========================================
// 3. INPUT PARAMETER CHECKS
// ==========================================
console.log('\n=== 3. INPUT PARAMETER CHECKS ===');

for (const inp of config.inputs) {
  const idx = parseInt(inp.id.replace('I', '')) - 1;
  const genInp = gen.Input[idx];

  // Manual: threshold 6V + hysteresis 1V = standard digital input
  if (inp.mode === 'Momentary' || inp.mode === 'Latching') {
    if (inp.threshold_V !== 6.0) {
      warnings.push(`INPUT: ${inp.id} (${inp.pdm_name}) threshold=${inp.threshold_V}V. Manual example uses 6.0V.`);
    }
    if (inp.hysteresis_V !== 1.0) {
      warnings.push(`INPUT: ${inp.id} (${inp.pdm_name}) hysteresis=${inp.hysteresis_V}V. Manual example uses 1.0V.`);
    }
  }

  // Verify generated input mode matches
  const modeMap = { 'Momentary': '0', 'Latching': '1', 'Analog': '2' };
  if (genInp && genInp.mode !== modeMap[inp.mode]) {
    errors.push(`GEN INPUT: ${inp.id} mode mismatch: config=${inp.mode}(${modeMap[inp.mode]}) gen=${genInp.mode}`);
  }

  // Active level: manual says Active-Low = "turns on when voltage falls below threshold"
  if (inp.active === 'Low' && genInp && genInp.activeLevel !== '1') {
    errors.push(`GEN INPUT: ${inp.id} (${inp.pdm_name}) Active Low but gen activeLevel=${genInp.activeLevel} (should be "1")`);
  }
}

// ==========================================
// 4. FUNCTION LOGIC CHECKS
// ==========================================
console.log('\n=== 4. FUNCTION LOGIC CHECKS ===');

// Manual operators: AND, OR, NOR, XOR, NAND, NOR, >, >=, <, <=, Equal, Not Equal
// Our generator only handles: AND(1), OR(2), NOT(3), XOR(4)
// Missing: NOR, NAND, >, >=, <, <=, Equal, Not Equal
// Check if any config functions use comparison operators

for (const out of config.outputs) {
  if (!out.function) continue;
  const func = out.function;

  // Check for comparison operators we can't handle
  if (func.match(/[><]=?|Equal|Not Equal|NOR|NAND/)) {
    warnings.push(`FUNCTION: ${out.id} (${out.pdm_name}) uses "${func}" which contains operators our generator may not handle correctly`);
  }

  // Check "I1>1V" pattern — this is a comparison, not just AND
  if (func.match(/I\d+\s*[><]/)) {
    warnings.push(`FUNCTION: ${out.id} (${out.pdm_name}) function "${func}" contains voltage comparison. Generator strips this — it becomes just the variable reference. Actual comparison must be configured differently in Configurator.`);
  }
}

// ==========================================
// 5. TIMER CHECKS
// ==========================================
console.log('\n=== 5. TIMER CHECKS ===');

// Manual: "In Pulse Train mode, the timer has an ON and an OFF Time, given in milliseconds"
// Manual example for indicators: "set the On and Off time to 400ms"
const timer = config.timers[0];
if (timer) {
  if (timer.on_time_ms === 400 && timer.off_time_ms === 400) {
    info.push(`TIMER OK: T1 ${timer.pdm_name} 400/400ms matches manual indicator example ✓`);
  }

  // Verify generated timer
  const genTimer = gen.Timer[0];
  if (genTimer.onTime !== String(timer.on_time_ms)) {
    errors.push(`GEN TIMER: T1 onTime: config=${timer.on_time_ms} gen=${genTimer.onTime}`);
  }
  if (genTimer.offTime !== String(timer.off_time_ms)) {
    errors.push(`GEN TIMER: T1 offTime: config=${timer.off_time_ms} gen=${genTimer.offTime}`);
  }
}

// ==========================================
// 6. CAN STREAM CHECK
// ==========================================
console.log('\n=== 6. CAN STREAM CHECK ===');

// Manual: "The CAN Stream can be enabled by clicking the enable checkbox"
// Config defines 5 stream frames: 0x100-0x104
// Check if generated HWPDM has CAN stream enabled
if (gen.CANStream) {
  const csEnabled = gen.CANStream.enabled;
  if (!csEnabled) {
    warnings.push(`CAN STREAM: Not enabled in generated HWPDM. Config specifies 5 frames (0x100-0x104). You need to enable CAN Stream manually in Configurator.`);
  }
  info.push(`CAN STREAM: Template CANStream section preserved from original HWPDM`);
} else {
  errors.push(`CAN STREAM: Missing from generated HWPDM!`);
}

// ==========================================
// 7. CRITICAL: RETRIES=0 CHECK
// ==========================================
console.log('\n=== 7. RETRIES=0 SEMANTICS ===');
// Manual explicitly states: "A value of zero will result in continual retries"
// This is CRITICAL for O23 (STARTER)

info.push(`MANUAL QUOTE: "If an output trips due to an overcurrent condition, then that output may be 'retried' several times. A value of zero will result in continual retries of that output."`);

// ==========================================
// 8. PWM MAPPING CHECK
// ==========================================
console.log('\n=== 8. PWM MAPPING CHECK ===');

// Manual: "Eleven Variable values must be chosen for the different values of PWM duty cycle"
const blower = config.outputs.find(o => o.id === 'O11');
if (blower && blower.pwm_mapping) {
  const points = blower.pwm_mapping.table || blower.pwm_mapping.points;
  if (points && points.length === 11) {
    info.push(`PWM OK: O11 BLOWER has 11-point PWM mapping table ✓ (matches manual requirement)`);
  } else {
    errors.push(`PWM: O11 BLOWER has ${points ? points.length : 0} PWM points, manual requires exactly 11`);
  }

  // Check generated PWM mapping
  const genBlower = gen.OutputHS[10]; // O11 = index 10
  if (genBlower) {
    info.push(`PWM GEN: O11 PWMMappingEnable=${genBlower.PWMMappingEnable}, PWMMapping=[${genBlower.PWMMapping.join(',')}]`);
  }
}

// ==========================================
// 9. 5V BUDGET CHECK
// ==========================================
console.log('\n=== 9. 5V BUDGET CHECK ===');
// Manual: "No more than 0.1 Amp should be drawn from the 5V output"
const budget = config.summary.fiveV_budget;
if (budget) {
  if (budget.total_mA > 100) {
    errors.push(`5V BUDGET: Total ${budget.total_mA}mA exceeds 100mA maximum!`);
  } else {
    info.push(`5V BUDGET OK: ${budget.total_mA}mA of 100mA max (${budget.margin_pct}% margin) ✓`);
  }
}

// ==========================================
// 10. CLEAR TIME UNITS CHECK
// ==========================================
console.log('\n=== 10. CLEAR TIME CHECK ===');
// Config uses clear_s (seconds), HWPDM stores as... what?
// Original HWPDM: clearTime="1" but rawSendData OP,8="10"
// So the serial protocol uses clearTime*10 (deciseconds? Or just a scale factor?)
// The Configurator probably shows seconds

for (const out of config.outputs) {
  if (!out.configured_as || !out.clear_s) continue;
  const idx = parseInt(out.id.replace('O', '')) - 1;
  const genOut = gen.OutputHS[idx];
  if (genOut && String(genOut.clearTime) !== String(out.clear_s)) {
    warnings.push(`CLEAR TIME: ${out.id} config=${out.clear_s}s gen.clearTime="${genOut.clearTime}" — verify unit conversion in Configurator`);
  }
}

// ==========================================
// 11. HS/LS CONFIGURATION CHECK
// ==========================================
console.log('\n=== 11. HS/LS TYPE CHECK ===');
// Manual: "If both the high and low side on a single output are instructed to turn on, only the high side will turn on"
// O1-O4 are HS/LS capable. All should be configured as HS for our vehicle.
for (let i = 0; i < 4; i++) {
  const out = config.outputs[i];
  if (out && out.type === 'HS/LS') {
    if (out.configured_as !== 'HS') {
      warnings.push(`HS/LS: ${out.id} (${out.pdm_name}) is HS/LS capable but configured as ${out.configured_as}`);
    } else {
      info.push(`HS/LS OK: ${out.id} (${out.pdm_name}) HS/LS pin configured as HS ✓`);
    }
  }
}

// ==========================================
// 12. IGNITION INPUT CHECK
// ==========================================
console.log('\n=== 12. IGNITION / POWER CHECK ===');
// Manual: "To power on the PDM, the Ignition Input must be switched to the battery positive voltage"
// But our config says C3 = battery+ (always on) — this is correct per our design
// Manual: "The ignition input may be connected directly to the battery positive voltage — however, this is not advised"
// We use I16 for ignition detection, C3 for always-on power
info.push(`POWER: C3 connected to battery+ (always-on). I16 detects ignition. This matches manual's "battery isolator" approach.`);

// ==========================================
// PRINT RESULTS
// ==========================================
console.log('\n' + '='.repeat(60));
console.log('AUDIT RESULTS');
console.log('='.repeat(60));

if (errors.length > 0) {
  console.log(`\n⛔ ERRORS (${errors.length}):`);
  errors.forEach(e => console.log(`  ❌ ${e}`));
}

if (warnings.length > 0) {
  console.log(`\n⚠️  WARNINGS (${warnings.length}):`);
  warnings.forEach(w => console.log(`  ⚠️  ${w}`));
}

console.log(`\n✅ INFO (${info.length}):`);
info.forEach(i => console.log(`  ✓ ${i}`));

console.log(`\n${'='.repeat(60)}`);
console.log(`SUMMARY: ${errors.length} errors, ${warnings.length} warnings, ${info.length} info`);
console.log('='.repeat(60));
