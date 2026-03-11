/**
 * generate_hwpdm.js
 *
 * Generates a PDM25 V2 HWPDM config file from pdm25_outputs_complete.json
 *
 * Usage: node generate_hwpdm.js [input.json] [output.hwpdm]
 * Default: pdm25_outputs_complete.json → Elton_generated.HWPDM
 *
 * Protocol mapping (rawSendData):
 *   GL = Global, OP = OutputHS(1-18) + OutputLS(20-37), IP = Input,
 *   TI = Timer, GF = GenericFunction, MC = MathsChannel,
 *   CO = CANOutput, CI = CANInput, CS = CANStream,
 *   CK = CANKeypad, CF = CANInputFilter, SC = SensorCalibration,
 *   TD = TwoDTable, LG = LoggingGroup, CT = Counter, PH = ?
 *
 * OP field map (OutputHS):
 *   1=lowFuse, 2=highFuse, 3=peakFuse, 4=peakFuseTime,
 *   5=enabled(bool→"1"/"0"), 6=stayOnTime, 7=turnOnDelay,
 *   8=clearTime(*10), 9=retries, 10=tripMode, 11=?(always 0),
 *   12=function[](subindexed), 13=label, 14=scaler, 15=offset,
 *   16=PWMFrequency, 17=PWMSoftStartEnable, 18=PWMSoftStartTime
 *   19=functionInfix[](subindexed)
 *
 * OP field map (OutputLS, same index, offset +19):
 *   20=lowFuse, 21=highFuse, 22=peakFuse, 23=peakFuseTime,
 *   24=enabled, 25=stayOnTime, 26=turnOnDelay, 27=clearTime(*10),
 *   28=retries, 29=tripMode, 30=?(always 0),
 *   31=function[](subindexed), 32=label, 33=scaler, 34=offset,
 *   35=PWMFrequency, 36=PWMSoftStartEnable, 37=PWMSoftStartTime
 *
 * IP field map:
 *   1=mode, 2=?(0), 3=?(related to mode), 4=activeLevel,
 *   5=?(0), 6=?(100, maybe EMA percentage), 7=pullResistor,
 *   8=?(0), 9=?(1), 10=label
 *
 * TI field map:
 *   1=onTime, 2=offTime, 3=enabled, 4=label, 5=visibleInDOM,
 *   6=type, 7-17=start/reset conditions, 18=duration
 */

const fs = require('fs');
const path = require('path');

// --- Automatic Versioning Logic ---
const buildsDir = 'Builds';
let latestMajor = 7;
let latestMinor = 2;

if (fs.existsSync(buildsDir)) {
  const files = fs.readdirSync(buildsDir);
  files.forEach(file => {
    const match = file.match(/Elton_v(\d+)\.(\d+)\.HWPDM/);
    if (match) {
      const major = parseInt(match[1], 10);
      const minor = parseInt(match[2], 10);
      if (major > latestMajor || (major === latestMajor && minor > latestMinor)) {
        latestMajor = major;
        latestMinor = minor;
      }
    }
  });
}

// Increment minor version for the next build
const nextVersion = `${latestMajor}.${latestMinor + 1}`;
const defaultOutputFile = path.join(buildsDir, `Elton_v${nextVersion}.HWPDM`);

// --- Load template (existing HWPDM as skeleton) and source config ---
const inputFile = process.argv[2] || 'ELTON_PDM25V2_KOMPLETT_v5.6b/pdm25_outputs_complete.json';
const templateFile = process.argv[3] || 'Elton.HWPDM';
const outputFile = process.argv[4] || defaultOutputFile;

console.log(`Input:    ${inputFile}`);
console.log(`Template: ${templateFile}`);
console.log(`Output:   ${outputFile}`);

if (!fs.existsSync(inputFile)) {
  console.error(`Error: Input file not found: ${inputFile}`);
  process.exit(1);
}
if (!fs.existsSync(templateFile)) {
  console.error(`Error: Template file not found: ${templateFile}`);
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const template = JSON.parse(fs.readFileSync(templateFile, 'utf8'));

// --- Helper: parse function string into configurator's function format ---
//
// The Hardwire PDM Configurator uses a FLAT LINE-BASED comparison format:
//   "Always True" → function=[1], functionInfix=[[0]]
//   "I4 Status"   → function=[7,"1","577","2","10","1","1"]
//                    functionInfix=[["1","577","2","10","1","1"]]
//
// Single comparison (6 tokens): ["1", varKeyId, "2", condCode, "1"/"3", val]
//
// Compound format — FLAT INFIX [6-token][2-token] pattern:
//   "A AND B"      → [15, comp_A, "2","1", comp_B]
//   "A AND B OR C" → [23, comp_A, "2","1", comp_B, "2","2", comp_C]
//     ["2","1"] = AND joiner, ["2","2"] = OR joiner
//
//
// Variable ID mapping (verified from unpacked-app/src/variables.js):
//   HS Outputs: Current base=70, stride=7. Status = 73 + (N-1)*7
//   LS Outputs: Current base=315, stride=7. Status = 318 + (N-1)*7
//   Inputs:     Voltage base=560, stride=5. Status = 562 + (N-1)*5
//   Timers:     base=640, stride=1. Timer1=640, Timer2=641, ..., Timer30=669
//   GFs:        base=730, stride=1. GF1=730, GF2=731, ..., GF30=759
//   True=1, False=2

const CONFIGURATOR_VAR_IDS = {};

// Inputs: Voltage base=560, stride=5. Status = Voltage+2
for (let i = 1; i <= 16; i++) {
  const voltageId = String(560 + (i - 1) * 5);
  const statusId = String(562 + (i - 1) * 5);
  CONFIGURATOR_VAR_IDS[`I${i}`] = statusId;
  CONFIGURATOR_VAR_IDS[`I${i} Status`] = statusId;
  CONFIGURATOR_VAR_IDS[`I${i} Voltage`] = voltageId;
}

// HS Outputs: Status base=73, stride=7
for (let i = 1; i <= 25; i++) {
  const statusId = String(73 + (i - 1) * 7);
  CONFIGURATOR_VAR_IDS[`O${i}`] = statusId;
  CONFIGURATOR_VAR_IDS[`O${i} Status`] = statusId;
  CONFIGURATOR_VAR_IDS[`O${i} HS`] = statusId;
}

// LS Outputs: Status base=318, stride=7
for (let i = 1; i <= 25; i++) {
  const statusId = String(318 + (i - 1) * 7);
  CONFIGURATOR_VAR_IDS[`O${i} LS`] = statusId;
}

// Timers: base=640, stride=1
for (let i = 1; i <= 30; i++) {
  const id = String(640 + (i - 1));
  CONFIGURATOR_VAR_IDS[`Timer${i}`] = id;
  CONFIGURATOR_VAR_IDS[`T${i}`] = id;
}

// Generic Functions: base=730, stride=1
for (let i = 1; i <= 30; i++) {
  const id = String(730 + (i - 1));
  CONFIGURATOR_VAR_IDS[`GF${i}`] = id;
}

// Counters: base=670, stride=1
for (let i = 1; i <= 30; i++) {
  const id = String(670 + (i - 1));
  CONFIGURATOR_VAR_IDS[`Counter${i}`] = id;
  CONFIGURATOR_VAR_IDS[`CT${i}`] = id;
}

// MathsChannels: base=700, stride=1
for (let i = 1; i <= 30; i++) {
  const id = String(700 + (i - 1));
  CONFIGURATOR_VAR_IDS[`MC${i}`] = id;
  CONFIGURATOR_VAR_IDS[`Maths Channel ${i}`] = id;
}

// SensorCalibrations: base=760, stride=1
for (let i = 1; i <= 10; i++) {
  const id = String(760 + (i - 1));
  CONFIGURATOR_VAR_IDS[`SC${i}`] = id;
  CONFIGURATOR_VAR_IDS[`Sensor Calibration ${i}`] = id;
}

// Accelerometer & Gyro variables (from variables.js keys 60-69)
CONFIGURATOR_VAR_IDS['AccTotal'] = '60';
CONFIGURATOR_VAR_IDS['Acceleration Total'] = '60';
CONFIGURATOR_VAR_IDS['AccX'] = '61';
CONFIGURATOR_VAR_IDS['AccY'] = '62';
CONFIGURATOR_VAR_IDS['AccZ'] = '63';
CONFIGURATOR_VAR_IDS['GyroX'] = '67';
CONFIGURATOR_VAR_IDS['GyroY'] = '68';
CONFIGURATOR_VAR_IDS['GyroZ'] = '69';

// Battery / Device variables
CONFIGURATOR_VAR_IDS['BatteryVoltage'] = '6';
CONFIGURATOR_VAR_IDS['Battery Voltage'] = '6';
CONFIGURATOR_VAR_IDS['FiveVoltRail'] = '7';
CONFIGURATOR_VAR_IDS['TotalCurrent'] = '5';

// Build a single comparison line (6 tokens).
// Format: ["1", varKeyId, "2", conditionCode, "1"/"3", var2Key/constValue]
//   Position 0: "1" = Variable reference type marker
//   Position 1: variable key ID (string)
//   Position 2: "2" = Condition type marker
//   Position 3: condition code ("10"=Equals, "6"=>, "7"=>=, "8"=<, "9"=<=, "11"=NotEqual)
//   Position 4: "1" = Variable2 type, "3" = Numeric constant type
//   Position 5: Variable2 key ID or constant*10
function makeComparison(varId, condCode, compareType, compareValue) {
  condCode = condCode || "10";       // default: Equals
  compareType = compareType || "1";  // default: compare to Variable2
  compareValue = compareValue || "1"; // default: True (key=1)
  return ["1", varId, "2", condCode, compareType, compareValue];
}

function makeAlwaysTrueFunction() {
  // Explicit "True Equals True" comparison line so the UI shows a clean logic row
  // instead of empty "..." with confusing default dropdowns.
  // True = variable key 1.
  return {
    func: [7, "1", "1", "2", "10", "1", "1"],
    infix: [["1", "1", "2", "10", "1", "1"]]
  };
}

// Resolve a variable name to its configurator ID
function resolveVarId(name) {
  // Try exact match first
  if (CONFIGURATOR_VAR_IDS[name]) return CONFIGURATOR_VAR_IDS[name];
  // Try without Status suffix
  const clean = name.replace(/\s*Status\s*/gi, '').trim();
  if (CONFIGURATOR_VAR_IDS[clean]) return CONFIGURATOR_VAR_IDS[clean];
  if (CONFIGURATOR_VAR_IDS[clean + ' Status']) return CONFIGURATOR_VAR_IDS[clean + ' Status'];
  console.warn(`  WARNING: Unknown variable "${name}", defaulting to Always True`);
  return null;
}

function hasValue(v) {
  return v !== undefined && v !== null && String(v).trim() !== '';
}

// Parse a function expression string into the configurator's line-based format.
//
// The configurator uses a FLAT infix format:
//   functionInfix = [ [6-token comparison], [2-token joiner], [6-token comparison], ... ]
//   function = [length+1, ...flat(functionInfix)]
//
// Where comparison = ["1", varId, "2", "10", "1", "1"]  (Variable Equals True)
// And joiner = ["2", "1"] (AND) or ["2", "2"] (OR)
//
// The app's serialFunctionToFunctionLines() parses the 1D function array by:
//   - Removing the leading length byte
//   - Taking 6 tokens as comparison, then 2 tokens as joiner, repeating
//
// Compound expressions like "A AND (B OR C)" are flattened to "A AND B OR C"
// The PDM evaluates with AND having higher precedence than OR.
function parseFunction(funcStr) {
  if (!funcStr || funcStr === 'null') {
    return { func: [1], infix: [[0]] };
  }
  if (funcStr === 'Always True' || funcStr === 'ALWAYS_TRUE' || funcStr === 'True') {
    return makeAlwaysTrueFunction();
  }

  // Condition codes for comparison operators
  const COND_CODES = {
    '=': '10', '==': '10', 'Equals': '10',
    '>': '6',
    '>=': '7',
    '<': '8',
    '<=': '9',
    '!=': '11', '<>': '11', 'Not Equal': '11'
  };

  // Parse terms with comparison operators first (e.g., "I1>1V", "I1>=2.5V")
  // Store parsed term info: { varName, property, condCode, constValue } or just { varName }
  const termInfos = new Map(); // original term string → parsed info

  // Match patterns like "I1>1V", "AccX>30", "BatteryVoltage<10", "I1 Voltage>=2.5V"
  // Extended to support AccX/AccY/AccZ/AccTotal/BatteryVoltage + negative constants
  const compRegex = /^((?:I|O|Timer|T|GF|MC|SC|CT|Counter)\d+|AccX|AccY|AccZ|AccTotal|Acceleration Total|BatteryVoltage|Battery Voltage|TotalCurrent|FiveVoltRail)(?:\s*(Voltage|Status))?\s*(>=|<=|>|<|!=|=)\s*(-?[\d.]+)\s*V?$/i;

  // Tokenize: split on AND/OR while keeping operators, strip parentheses
  // First, extract comparison terms before splitting
  let working = funcStr
    .replace(/[()]/g, ' ')            // Remove parentheses (flatten)
    .replace(/\s+/g, ' ')
    .trim();

  // Re-parse: split on AND/OR, preserving them as operators
  let funcForParsing = funcStr
    .replace(/[()]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const tokens = funcForParsing
    .split(/\b(AND|OR)\b/)
    .map(s => s.trim())
    .filter(Boolean);

  // Build flat list of {type: 'var'|'op', ...parsed info}
  const parts = [];
  for (const tok of tokens) {
    if (tok === 'AND' || tok === 'OR') {
      parts.push({ type: 'op', value: tok });
      continue;
    }

    // Try to match comparison expression (e.g., "I1>1V", "AccX>30", "BatteryVoltage<10")
    const cMatch = tok.match(compRegex);
    if (cMatch) {
      const varName = cMatch[1];
      const property = (cMatch[2] || '').toLowerCase();
      const operator = cMatch[3];
      const constVal = parseFloat(cMatch[4]);
      // For input variables with comparison, default to Voltage; for others use direct key
      const isInput = /^I\d+$/i.test(varName);
      const useVoltage = isInput && property !== 'status';
      const varKey = useVoltage ? `${varName} Voltage` : (property === 'voltage' ? `${varName} Voltage` : varName);
      parts.push({
        type: 'var',
        value: varName,
        varKey: varKey,
        condCode: COND_CODES[operator] || '10',
        compareType: '3',                        // constant
        compareValue: String(Math.round(constVal * 10))  // constant × 10
      });
    } else {
      // Check for "Variable Equals True/False" pattern
      const equalsMatch = tok.match(/^(.+?)\s+Equals\s+(True|False)\s*$/i);
      if (equalsMatch) {
        const varName = equalsMatch[1].trim();
        const boolVal = equalsMatch[2].toLowerCase() === 'true' ? '1' : '2'; // True=key1, False=key2
        parts.push({
          type: 'var',
          value: varName,
          condCode: '10',           // Equals
          compareType: '1',         // Variable2 type
          compareValue: boolVal     // True=1 or False=2
        });
      } else {
        // Simple variable reference (e.g., "GF1", "I4 Status", "Timer1")
        // Default: Equals True
        const clean = tok.replace(/\s*Status\s*/gi, '').replace(/=\s*True/gi, '').trim();
        if (clean) {
          parts.push({ type: 'var', value: clean });
        }
      }
    }
  }

  // Resolve variable IDs and build comparison list
  const comparisons = [];
  let currentPart = null;
  for (const part of parts) {
    if (part.type === 'var') {
      if (currentPart) {
        // Previous variable without an operator
        const varId = part.varKey ? resolveVarId(part.varKey) : resolveVarId(currentPart.value);
        if (varId) {
          comparisons.push({
            varId,
            condCode: currentPart.condCode,
            compareType: currentPart.compareType,
            compareValue: currentPart.compareValue,
            joiner: null
          });
        }
      }
      currentPart = part;
    } else if (part.type === 'op') {
      if (currentPart) {
        const varId = currentPart.varKey ? resolveVarId(currentPart.varKey) : resolveVarId(currentPart.value);
        if (varId) {
          comparisons.push({
            varId,
            condCode: currentPart.condCode,
            compareType: currentPart.compareType,
            compareValue: currentPart.compareValue,
            joiner: part.value
          });
        }
        currentPart = null;
      }
    }
  }
  // Last variable
  if (currentPart) {
    const varId = currentPart.varKey ? resolveVarId(currentPart.varKey) : resolveVarId(currentPart.value);
    if (varId) {
      comparisons.push({
        varId,
        condCode: currentPart.condCode,
        compareType: currentPart.compareType,
        compareValue: currentPart.compareValue,
        joiner: null
      });
    }
  }

  if (comparisons.length === 0) {
    console.warn(`  WARNING: No valid variables in "${funcStr}", defaulting to Always True`);
    return makeAlwaysTrueFunction();
  }

  // Build functionInfix (2D) and function (1D)
  const OP_CODES = { 'AND': '1', 'OR': '2' };
  const infixLines = [];
  const flatTokens = [];

  for (let i = 0; i < comparisons.length; i++) {
    const c = comparisons[i];
    const comp = makeComparison(c.varId, c.condCode, c.compareType, c.compareValue);
    infixLines.push(comp);
    flatTokens.push(...comp);

    // Add joiner after this comparison (if not last)
    if (i < comparisons.length - 1) {
      const joiner = comparisons[i].joiner || 'AND';
      const joinerLine = ["2", OP_CODES[joiner]];
      infixLines.push(joinerLine);
      flatTokens.push(...joinerLine);
    }
  }

  const func = [flatTokens.length + 1, ...flatTokens];

  return { func, infix: infixLines };
}

// --- Map trip mode string to numeric ---
function tripModeToNum(mode) {
  if (!mode) return 0;
  const m = mode.toLowerCase();
  if (m === 'normal') return 0;
  if (m === 'instant') return 1;
  if (m === 'latching' || m === 'latch') return 2;
  return 0;
}

// --- Map input mode string to numeric ---
function inputModeToNum(mode) {
  if (!mode) return 0;
  const m = mode.toLowerCase();
  if (m === 'momentary') return 0;
  if (m === 'latching') return 1;
  if (m === 'analog') return 2;
  return 0;
}

// --- Map active level ---
function activeLevelToNum(active) {
  if (!active) return 0;
  if (active.toLowerCase() === 'low') return 1;
  return 0; // High = 0
}

// --- Build OutputHS array (25 entries, padded to 35) ---
function buildOutputHS() {
  const outputs = [];

  for (let i = 0; i < 35; i++) {
    const src = config.outputs && config.outputs[i];

    if (src && src.configured_as) {
      const parsed = parseFunction(src.function);
      const pwmMapping = src.pwm_mapping ? src.pwm_mapping.table.map(p => p.duty_pct) :
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

      // Pad PWM mapping to 11 entries
      while (pwmMapping.length < 11) pwmMapping.push(0);

      const peakTimeMs = hasValue(src.peak_time_s) ? Number(src.peak_time_s) * 1000 : 5000;

      outputs.push({
        lowFuse: String(src.low_fuse_A || 0),
        highFuse: String(src.high_fuse_A || 0),
        peakFuse: String(src.peak_fuse_A || 0),
        peakFuseTime: String(peakTimeMs),
        enabled: src.configured_as !== null && src.function !== null,
        stayOnTime: String(src.stay_on_s ? src.stay_on_s * 1000 : 0),
        turnOnDelay: String(src.turn_on_delay_s ? src.turn_on_delay_s * 1000 : 0),
        clearTime: String(src.clear_s || 1),
        retries: String(src.retries != null ? src.retries : 1),
        tripMode: String(tripModeToNum(src.trip_mode)),
        trippedCount: 0,
        current: 0,
        voltage: 0,
        status: 0,
        percentageTripped: 0,
        blownCount: 0,
        underCurrent: 0,
        onTime: 0,
        offTime: 0,
        function: parsed.func,
        functionInfix: parsed.infix,
        offset: 0,
        scaler: 100,
        label: src.pdm_name || '',
        testOutput: 0,
        PWMFrequency: src.pwm ? "100" : "100",
        PWMSoftStartEnable: src.soft_start || false,
        PWMSoftStartTime: String(src.soft_start_s ? src.soft_start_s * 1000 : 100),
        PWMFrequencyMode: 0,
        PWMFrequencyModeVariable: 1,
        PWMMappingEnable: src.pwm && src.pwm_mapping ? true : false,
        PWMMappingVariable: src.pwm_mapping && src.pwm_mapping.source
          ? (CONFIGURATOR_VAR_IDS[src.pwm_mapping.source] || "1")
          : "1",
        PWMMapping: pwmMapping,
        controlSource: 0,
      });
    } else {
      // Empty/reserve output - copy from template or use defaults
      const tmpl = template.OutputHS[i] || template.OutputHS[template.OutputHS.length - 1];
      outputs.push({
        ...tmpl,
        label: src ? src.pdm_name : (tmpl.label || ''),
        enabled: false,
      });
    }
  }

  return outputs;
}

// --- Build OutputLS array (35 entries, mostly empty for PDM25) ---
function buildOutputLS() {
  // PDM25 V2: O1-O4 can be HS or LS, O5-O25 are HS only
  // For our config, all are configured as HS, so LS mirrors labels but is disabled
  const outputs = [];

  for (let i = 0; i < 35; i++) {
    const tmpl = template.OutputLS[i] || template.OutputLS[template.OutputLS.length - 1];
    const src = config.outputs && config.outputs[i];
    outputs.push({
      ...tmpl,
      enabled: false,
      label: src ? src.pdm_name : (tmpl.label || ''),
    });
  }

  return outputs;
}

// --- Build Input array (16 entries) ---
function buildInputs() {
  const inputs = [];

  for (let i = 0; i < 16; i++) {
    const src = config.inputs && config.inputs[i];

    if (src) {
      const modeStr = String(src.mode || '').toLowerCase();
      const isAnalog = modeStr === 'analog';
      const threshold = hasValue(src.threshold_V) ? Number(src.threshold_V) : (isAnalog ? 1.0 : 0);
      let hysteresis = hasValue(src.hysteresis_V) ? Number(src.hysteresis_V) : (isAnalog ? 0.2 : 0);
      if (threshold > 0 && hysteresis >= threshold) {
        hysteresis = Math.max(0, threshold - 0.1);
      }

      inputs.push({
        mode: String(inputModeToNum(src.mode)),
        voltage: 0,
        frequency: 0,
        status: 0,
        onTime: 0,
        offTime: 0,
        thresholdVoltage: String(threshold),
        hysteresisVoltage: String(hysteresis),
        turnOnDelay: String(src.delay_s ? src.delay_s * 1000 : 0),
        EMAValue: src.ema_filter ? String(src.ema_filter / 1000) : "0.01",
        EMAEnabled: src.ema_filter > 0,
        pullResistor: "0",
        enabled: true,
        activeLevel: String(activeLevelToNum(src.active)),
        label: src.pdm_name || '',
      });
    } else {
      inputs.push({
        ...template.Input[i],
        enabled: true,
        label: '',
      });
    }
  }

  return inputs;
}

// --- Build Timer array (30 entries) ---
function buildTimers() {
  const timers = [];

  for (let i = 0; i < 30; i++) {
    const src = config.timers && config.timers[i];
    const tmpl = template.Timer[i] || template.Timer[template.Timer.length - 1];

    if (src && src.enabled) {
      const isDuration = (src.mode || '').toLowerCase() === 'duration';

      // Parse start condition if provided (e.g., "GF2 Equals True")
      let startVar1 = "1", startCondition = "1", startVarOrConst = 0, startVar2 = "1", startConst = 0;
      if (src.start_condition) {
        const startParsed = parseTimerCondition(src.start_condition);
        startVar1 = startParsed.var1;
        startCondition = startParsed.condCode;
        startVarOrConst = startParsed.varOrConst;
        startVar2 = startParsed.var2;
        startConst = startParsed.constVal;
      }

      // Parse reset condition if provided
      let resetVar1 = "1", resetCondition = "1", resetVarOrConst = 0, resetVar2 = "1", resetConst = 0;
      if (src.reset_condition) {
        const resetParsed = parseTimerCondition(src.reset_condition);
        resetVar1 = resetParsed.var1;
        resetCondition = resetParsed.condCode;
        resetVarOrConst = resetParsed.varOrConst;
        resetVar2 = resetParsed.var2;
        resetConst = resetParsed.constVal;
      }

      timers.push({
        ...tmpl,
        onTime: String(src.on_time_ms || 0),
        offTime: String(src.off_time_ms || 0),
        enabled: true,
        label: src.pdm_name || '',
        visibleInDOM: true,
        type: isDuration ? "1" : "0",   // 0=Pulse Train, 1=Duration
        duration: isDuration ? String(src.duration_ms || 10000) : "10",
        startConditionVar1: startVar1,
        startConditionCondition: startCondition,
        startConditionVarOrConst: startVarOrConst,
        startConditionVar2: startVar2,
        startConditionConst: startConst,
        resetConditionVar1: resetVar1,
        resetConditionCondition: resetCondition,
        resetConditionVarOrConst: resetVarOrConst,
        resetConditionVar2: resetVar2,
        resetConditionConst: resetConst,
        resetOnEnd: src.reset_on_end || false,
        currentValue: 0,
      });
    } else {
      timers.push({
        ...tmpl,
        enabled: false,
      });
    }
  }

  return timers;
}

// Parse a timer start/reset condition string into individual fields
// Examples: "GF2 Equals True", "I1 Voltage > 5V", "Timer1 Equals True"
function parseTimerCondition(condStr) {
  const COND_MAP = {
    '=': '10', '==': '10', 'Equals': '10', 'equals': '10',
    '>': '6', '>=': '7', '<': '8', '<=': '9',
    '!=': '11', 'Not Equal': '11'
  };

  // Try "Var Equals True/False"
  const eqMatch = condStr.match(/^(.+?)\s+(?:Equals|=)\s+(True|False)\s*$/i);
  if (eqMatch) {
    const varName = eqMatch[1].trim();
    const boolVal = eqMatch[2].toLowerCase() === 'true' ? '1' : '2';
    const varId = resolveVarId(varName);
    return {
      var1: varId || '1',
      condCode: '10',       // Equals
      varOrConst: 0,        // 0 = compare to Variable
      var2: boolVal,         // 1=True, 2=False
      constVal: 0
    };
  }

  // Try "Var > constant" (e.g., "I1 Voltage > 5V")
  const compMatch = condStr.match(/^(.+?)\s*(>=|<=|>|<|!=|=)\s*(-?[\d.]+)\s*V?\s*$/i);
  if (compMatch) {
    const varName = compMatch[1].trim();
    const operator = compMatch[2];
    const constVal = parseFloat(compMatch[3]);
    const varId = resolveVarId(varName);
    return {
      var1: varId || '1',
      condCode: COND_MAP[operator] || '10',
      varOrConst: 1,        // 1 = compare to Constant
      var2: '1',
      constVal: Math.round(constVal * 10)
    };
  }

  // Default: True Equals True
  console.warn(`  WARNING: Could not parse timer condition "${condStr}"`);
  return { var1: '1', condCode: '10', varOrConst: 0, var2: '1', constVal: 0 };
}

// --- Build GenericFunction array (30 entries) ---
function buildGenericFunctions() {
  const gfs = [];

  for (let i = 0; i < 30; i++) {
    const src = config.generic_functions && config.generic_functions[i];
    const tmpl = template.GenericFunction[i] || template.GenericFunction[template.GenericFunction.length - 1];

    if (src) {
      const parsed = parseFunction(src.function);
      gfs.push({
        visibleInDOM: true,
        currentValue: 0,
        enabled: true,
        label: src.pdm_name || '',
        function: parsed.func,
        functionInfix: parsed.infix,
      });
    } else {
      gfs.push({
        ...tmpl,
        enabled: false,
      });
    }
  }

  return gfs;
}

// --- Build MathsChannel array (30 entries) ---
function buildMathsChannels() {
  const channels = [];
  const cfgChannels = config.maths_channels || [];

  // Build lookup: MC index (0-based) → config entry
  const cfgMap = {};
  cfgChannels.forEach(src => {
    const idx = parseInt(src.id.replace(/\D/g, ''), 10) - 1; // MC1 → 0
    cfgMap[idx] = src;
  });

  for (let i = 0; i < 30; i++) {
    const tmpl = template.MathsChannel[i] || template.MathsChannel[template.MathsChannel.length - 1];
    const src = cfgMap[i];

    if (src) {
      // Build equationArray and postfix from config
      let equationArray = [];
      let equationArrayPostfix = [];
      let equationLines = [];

      if (src.id === 'MC1' && src.equation === 'Sqrt(AccX*AccX + AccY*AccY + AccZ*AccZ)') {
        // G-force magnitude: Sqrt(AccX² + AccY² + AccZ²)
        // Infix: Sqrt( AccX * AccX + AccY * AccY + AccZ * AccZ )
        equationArray = [4,14, 5,0, 2,61, 3,2, 2,61, 3,0, 2,62, 3,2, 2,62, 3,0, 2,63, 3,2, 2,63, 5,1, 0,0];
        // Postfix: AccX AccX * AccY AccY * + AccZ AccZ * + Sqrt END
        equationArrayPostfix = [2,61, 2,61, 3,2, 2,62, 2,62, 3,2, 3,0, 2,63, 2,63, 3,2, 3,0, 4,14, 0,0];
        // Split into display lines
        equationLines = [[4,14, 5,0, 2,61, 3,2, 2,61, 3,0, 2,62, 3,2, 2,62, 3,0, 2,63, 3,2, 2,63, 5,1, 0,0]];
      }

      channels.push({
        ...tmpl,
        visibleInDOM: true,
        currentValue: 0,
        enabled: true,
        label: src.pdm_name || '',
        equationArray: equationArray,
        equationLines: equationLines,
        equationArrayPostfix: equationArrayPostfix,
      });
      console.log(`  MC${i + 1}: ${src.pdm_name} = ${src.equation}`);
    } else {
      channels.push({ ...tmpl });
    }
  }

  return channels;
}

// --- Build SensorCalibration array (10 entries) ---
function buildSensorCalibrations() {
  const calibrations = [];
  const cfgCalibrations = config.sensor_calibrations || [];

  const cfgMap = {};
  cfgCalibrations.forEach(src => {
    const idx = parseInt(src.id.replace(/\D/g, ''), 10) - 1; // SC1 → 0
    cfgMap[idx] = src;
  });

  for (let i = 0; i < 10; i++) {
    const tmpl = template.SensorCalibration[i] || template.SensorCalibration[template.SensorCalibration.length - 1];
    const src = cfgMap[i];

    if (src) {
      // Convert voltage to millivolts (×1000) for rawSensorDataPoint
      const rawPoints = (src.raw_voltage || []).map(v => Math.round(v * 1000));
      // Calibrated values × 1000 for calibratedSensorDataPoint
      const calPoints = (src.calibrated_values || []).map(v => Math.round(v * 1000));

      // Pad to 20 entries
      while (rawPoints.length < 20) rawPoints.push(0);
      while (calPoints.length < 20) calPoints.push(0);

      calibrations.push({
        ...tmpl,
        visibleInDOM: true,
        currentValue: 0,
        enabled: true,
        label: src.pdm_name || '',
        variable: src.input_voltage_key || 1,
        rawSensorDataPoint: rawPoints,
        calibratedSensorDataPoint: calPoints,
      });
      console.log(`  SC${i + 1}: ${src.pdm_name} (input key=${src.input_voltage_key}, ${src.units})`);
    } else {
      calibrations.push({ ...tmpl });
    }
  }

  return calibrations;
}

// --- Build Counter array (30 entries) ---
function buildCounters() {
  const counters = [];
  const cfgCounters = config.counters || [];

  const cfgMap = {};
  cfgCounters.forEach(src => {
    const idx = parseInt(src.id.replace(/\D/g, ''), 10) - 1; // Counter1 → 0
    cfgMap[idx] = src;
  });

  for (let i = 0; i < 30; i++) {
    const tmpl = template.Counter[i] || template.Counter[template.Counter.length - 1];
    const src = cfgMap[i];

    if (src) {
      counters.push({
        ...tmpl,
        visibleInDOM: true,
        currentValue: 0,
        enabled: true,
        label: src.pdm_name || '',
        startValue: 0,
        endValue: 0,
        endValueEnable: 0,
        INCEnable: 1,
        INCvariable1: src.inc_variable1 || 1,
        INCcondition: src.inc_condition_code || 1,
        INCvarCond: src.inc_var_or_const || 0,
        INCvariable2: src.inc_variable2 || 1,
        INCconstant: src.inc_constant || 0,
        DECEnable: 0,
        DECvariable1: 1,
        DECcondition: 1,
        DECvarCond: 0,
        DECvariable2: 1,
        DECconstant: 0,
        RSTEnable: 0,
        RSTvariable1: 1,
        RSTcondition: 1,
        RSTvarCond: 0,
        RSTvariable2: 1,
        RSTconstant: 0,
      });
      console.log(`  CT${i + 1}: ${src.pdm_name} (INC when key=${src.inc_variable1} cond=${src.inc_condition_code} val=${src.inc_variable2})`);
    } else {
      counters.push({ ...tmpl });
    }
  }

  return counters;
}

// --- Build LoggingGroup array (30 entries) ---
function buildLoggingGroups() {
  const groups = [];
  const cfgGroups = config.logging_groups || [];

  const cfgMap = {};
  cfgGroups.forEach(src => {
    const idx = parseInt(src.id.replace(/\D/g, ''), 10) - 1; // LG1 → 0
    cfgMap[idx] = src;
  });

  for (let i = 0; i < 30; i++) {
    const tmpl = template.LoggingGroup[i] || template.LoggingGroup[template.LoggingGroup.length - 1];
    const src = cfgMap[i];

    if (src) {
      groups.push({
        ...tmpl,
        visibleInDOM: true,
        label: src.pdm_name || '',
        triggerPeriod: src.trigger_period_ms || 0,
        triggerConstVar: src.trigger_const_var || 0,
        triggerVariable1: src.trigger_variable1 || 0,
        triggerCondition: src.trigger_condition || 0,
        triggerVariable2: src.trigger_variable2 || 0,
        triggerConst: src.trigger_const || 0,
        variableList: src.variables || [1],
        enabled: true,
      });
      console.log(`  LG${i + 1}: ${src.pdm_name} (${src.trigger_period_ms}ms, ${(src.variables || []).length} vars)`);
    } else {
      groups.push({ ...tmpl });
    }
  }

  return groups;
}

// --- Build Global settings ---
function buildGlobal() {
  const gs = config.general_settings || {};
  const canIdx = canSpeedToIndex(gs.can_bus_speed_kbps || 250);
  const termEnabled = gs.can_termination_enabled ? 1 : 0;

  // GC (Global Cutoff) — cuts ALL outputs when condition is TRUE
  let gcEnabled = false;
  let gcFunc = [1];
  let gcInfix = [[0]];
  if (gs.global_cutoff_enabled && gs.global_cutoff_function) {
    const parsed = parseFunction(gs.global_cutoff_function);
    gcEnabled = true;
    gcFunc = parsed.func;
    gcInfix = parsed.infix;
    console.log(`  GC enabled: ${gs.global_cutoff_function}`);
    console.log(`    GCfunction: [${gcFunc.join(',')}]`);
  }

  // GR (Global Reset) — resets all tripped outputs when condition is TRUE
  let grEnabled = false;
  let grFunc = [1];
  let grInfix = [[0]];
  if (gs.global_reset_enabled && gs.global_reset_function) {
    const parsed = parseFunction(gs.global_reset_function);
    grEnabled = true;
    grFunc = parsed.func;
    grInfix = parsed.infix;
    console.log(`  GR enabled: ${gs.global_reset_function}`);
  }

  return {
    ...template.Global,
    // PDM25 V2 has 1 CAN bus: CANspeed[0] = speed index directly
    CANspeed: [canIdx, canIdx, canIdx],
    // CANtermres[0] = PDM internal termination
    CANtermres: [termEnabled, 0, 0],
    passwordEnabled: gs.password_set || false,
    passwordEntered: true,
    GCenabled: gcEnabled,
    GCfunction: gcFunc,
    GCfunctionInfix: gcInfix,
    GRenabled: grEnabled,
    GRfunction: grFunc,
    GRfunctionInfix: grInfix,
  };
}

function canSpeedToIndex(kbps) {
  // From mainWindow.html select options: 1=1000, 2=500, 3=250, 4=125, 5=100 kbit/s
  const map = { 1000: 1, 500: 2, 250: 3, 125: 4, 100: 5 };
  return map[kbps] || 3; // default 250 kbit/s
}

// --- Build CANStream ---
function buildCANStream() {
  const cs = JSON.parse(JSON.stringify(template.CANStream)); // deep clone
  const csConfig = config.can_stream;
  if (!csConfig || !csConfig.enabled) return cs;

  cs.enabled = true;
  cs.CANChannel = String(csConfig.can_channel || '1');
  cs.baseID = csConfig.base_ext_id || 4096;

  console.log(`  CAN Stream enabled on channel ${cs.CANChannel}, baseID=${cs.baseID}`);

  if (csConfig.frames) {
    for (const fc of csConfig.frames) {
      const i = fc.index;
      if (i >= 0 && i < cs.frame.length) {
        cs.frame[i].enabled = fc.enabled !== false;
        cs.frame[i].sendRate = fc.send_rate_hz || 10;
        console.log(`    Frame ${i}: ${fc.name} @ ${cs.frame[i].sendRate}Hz [${fc.enabled ? 'ON' : 'OFF'}]`);
      }
    }
  }

  return cs;
}

// --- Build rawSendData ---
// Strategy: Parse template rawSendData into individual commands.
// For sections we modify (GL, OP, IP, TI, GF): generate our own commands.
// For sections we DON'T modify: re-emit template commands verbatim.
// Pack commands into lines (matching original ~3-4 per line).
//
// Section order: GL, PH, OP, IP, LG, TI, CT, MC, GF, SC, TD, CK, CF, CI, CO, CS, EC
//
// IMPORTANT: Original OP order is ALL HS first (OP,1-19 for i=0..24),
// THEN ALL LS (OP,20-38 for i=0..24). NOT interleaved per output.

function parseTemplateCommands() {
  // Parse all commands from template rawSendData
  // Each command is a string like: OP,12,0,0,"1" or GL,6,"0"
  const sectionCommands = {};

  template.rawSendData.forEach(line => {
    // Strip $,6, prefix and ,#\n suffix
    const inner = line.replace(/^\$,6,/, '').replace(/,#\s*$/, '');

    // Split into individual commands. Commands are separated by commas between
    // quoted values and the next prefix. Match: PREFIX,field,...,"value"
    const cmdRe = /([A-Z]{2}(?:,(?:\d+|"[^"]*"))*?,"[^"]*")/g;
    let m;
    while ((m = cmdRe.exec(inner)) !== null) {
      const cmd = m[1];
      const prefix = cmd.substring(0, 2);
      if (!sectionCommands[prefix]) sectionCommands[prefix] = [];
      sectionCommands[prefix].push(cmd);
    }
  });

  return sectionCommands;
}

function buildRawSendData(hwpdm) {
  const allCommands = []; // flat list of command strings

  function add(prefix, field, index, value) {
    allCommands.push(`${prefix},${field},${index},"${value}"`);
  }

  function addSub(prefix, field, index, subIndex, value) {
    allCommands.push(`${prefix},${field},${index},${subIndex},"${value}"`);
  }

  function addGlobal(field, value) {
    allCommands.push(`GL,${field},"${value}"`);
  }

  function addGlobalSub(field, sub, value) {
    allCommands.push(`GL,${field},${sub},"${value}"`);
  }

  // Helper: copy commands from template for a given prefix
  const templateCmds = parseTemplateCommands();
  function copySection(prefix) {
    if (templateCmds[prefix]) {
      allCommands.push(...templateCmds[prefix]);
    }
  }

  // --- GL (Global) ---
  addGlobalSub(1, 0, hwpdm.Global.CANspeed[0]);
  addGlobalSub(2, 0, hwpdm.Global.CANtermres[0]);
  addGlobal(6, "0");
  addGlobalSub(7, 0, hwpdm.Global.CANspeed[1]);
  addGlobal(8, "0");
  addGlobalSub(9, 0, hwpdm.Global.CANspeed[2]);
  addGlobal(12, "0");
  for (let k = 0; k < 4; k++) {
    addGlobalSub(13, k, hwpdm.Global.CANKeypadKey[k]);
  }

  // PH (unknown prefix, appears once between GL and OP)
  allCommands.push('PH,1,"0"');

  // --- OP: ALL HS first (fields 1-19 for outputs 0-24) ---
  for (let i = 0; i < 25; i++) {
    const hs = hwpdm.OutputHS[i];

    add('OP', 1, i, hs.lowFuse);
    add('OP', 2, i, hs.highFuse);
    add('OP', 3, i, hs.peakFuse);
    add('OP', 4, i, hs.peakFuseTime);
    add('OP', 5, i, hs.enabled ? "1" : "0");
    add('OP', 6, i, hs.stayOnTime);
    add('OP', 7, i, hs.turnOnDelay);
    add('OP', 8, i, String(parseInt(hs.clearTime || "1") * 10));
    add('OP', 9, i, hs.retries);
    add('OP', 10, i, hs.tripMode);
    add('OP', 11, i, "0");

    const hsFunc = hs.function || [1];
    for (let s = 0; s < hsFunc.length; s++) {
      addSub('OP', 12, i, s, String(hsFunc[s]));
    }

    add('OP', 13, i, hs.label);
    add('OP', 14, i, String(hs.scaler || 100));
    add('OP', 15, i, String(hs.offset || 0));
    add('OP', 16, i, hs.PWMFrequency || "100");
    add('OP', 17, i, hs.PWMSoftStartEnable ? "1" : "0");
    add('OP', 18, i, hs.PWMSoftStartTime || "1");

    // OP,19 functionInfix in rawSendData is always 11 zeros
    // (configurator reads infix from JSON property, not rawSendData)
    for (let s = 0; s < 11; s++) {
      addSub('OP', 19, i, s, "0");
    }
  }

  // --- OP: THEN ALL LS (fields 20-38 for outputs 0-24) ---
  for (let i = 0; i < 25; i++) {
    const ls = hwpdm.OutputLS[i];

    add('OP', 20, i, ls.lowFuse);
    add('OP', 21, i, ls.highFuse);
    add('OP', 22, i, ls.peakFuse);
    add('OP', 23, i, ls.peakFuseTime);
    add('OP', 24, i, ls.enabled ? "1" : "0");
    add('OP', 25, i, ls.stayOnTime);
    add('OP', 26, i, ls.turnOnDelay);
    add('OP', 27, i, String(parseInt(ls.clearTime || "1") * 10));
    add('OP', 28, i, ls.retries);
    add('OP', 29, i, ls.tripMode);
    add('OP', 30, i, "0");

    const lsFunc = ls.function || [1];
    for (let s = 0; s < lsFunc.length; s++) {
      addSub('OP', 31, i, s, String(lsFunc[s]));
    }

    add('OP', 32, i, ls.label);
    add('OP', 33, i, String(ls.scaler || 100));
    add('OP', 34, i, String(ls.offset || 0));
    add('OP', 35, i, ls.PWMFrequency || "100");
    add('OP', 36, i, ls.PWMSoftStartEnable ? "1" : "0");
    add('OP', 37, i, ls.PWMSoftStartTime || "1");

    for (let s = 0; s < 11; s++) {
      addSub('OP', 38, i, s, "0");
    }
  }

  // --- IP (Inputs) ---
  for (let i = 0; i < 16; i++) {
    const inp = hwpdm.Input[i];
    add('IP', 1, i, inp.mode);
    add('IP', 2, i, "0");
    add('IP', 3, i, inp.mode === "1" ? "1" : (inp.mode === "2" ? "1" : "0"));
    add('IP', 4, i, inp.activeLevel);
    add('IP', 5, i, "0");
    add('IP', 6, i, "100");
    add('IP', 7, i, inp.pullResistor);
    add('IP', 8, i, "0");
    add('IP', 9, i, "1");
    add('IP', 10, i, inp.label);
  }

  // --- LG (LoggingGroups) - generated from hwpdm ---
  for (let i = 0; i < 30; i++) {
    const lg = hwpdm.LoggingGroup[i];
    add('LG', 1, i, lg.enabled ? "1" : "0");
    add('LG', 2, i, lg.label || '');
    add('LG', 3, i, String(lg.triggerPeriod || 0));
    add('LG', 4, i, String(lg.triggerConstVar || 0));
    add('LG', 5, i, String(lg.triggerVariable1 || 0));
    add('LG', 6, i, String(lg.triggerCondition || 0));
    add('LG', 7, i, String(lg.triggerVariable2 || 0));
    add('LG', 8, i, String(lg.triggerConst || 0));
    const varList = lg.variableList || [1];
    for (let s = 0; s < varList.length; s++) {
      addSub('LG', 9, i, s, String(varList[s]));
    }
    add('LG', 10, i, lg.visibleInDOM ? "1" : "0");
  }

  // --- TI (Timers) ---
  for (let i = 0; i < 30; i++) {
    const ti = hwpdm.Timer[i];
    add('TI', 1, i, ti.onTime);
    add('TI', 2, i, ti.offTime);
    add('TI', 3, i, ti.enabled ? "1" : "0");
    add('TI', 4, i, ti.label);
    add('TI', 5, i, ti.visibleInDOM ? "1" : "0");
    add('TI', 6, i, ti.type);
    add('TI', 7, i, ti.startConditionVar1);
    add('TI', 8, i, String(ti.startConditionVarOrConst));
    add('TI', 9, i, ti.startConditionVar2);
    add('TI', 10, i, String(ti.startConditionConst));
    add('TI', 11, i, ti.startConditionCondition);
    add('TI', 12, i, ti.resetConditionVar1);
    add('TI', 13, i, String(ti.resetConditionVarOrConst));
    add('TI', 14, i, ti.resetConditionVar2);
    add('TI', 15, i, String(ti.resetConditionConst));
    add('TI', 16, i, ti.resetConditionCondition);
    add('TI', 17, i, ti.resetOnEnd ? "1" : "0");
    add('TI', 18, i, ti.duration);
  }

  // --- CT (Counters) - generated from hwpdm ---
  for (let i = 0; i < 30; i++) {
    const ct = hwpdm.Counter[i];
    add('CT', 1, i, String(ct.startValue || 0));
    add('CT', 2, i, String(ct.endValue || 0));
    add('CT', 3, i, String(ct.endValueEnable || 0));
    add('CT', 4, i, ct.enabled ? "1" : "0");
    add('CT', 5, i, String(ct.INCEnable || 0));
    add('CT', 6, i, String(ct.INCvariable1 || 1));
    add('CT', 7, i, String(ct.INCcondition || 1));
    add('CT', 8, i, String(ct.INCvarCond || 0));
    add('CT', 9, i, String(ct.INCvariable2 || 1));
    add('CT', 10, i, String(ct.INCconstant || 0));
    add('CT', 11, i, String(ct.DECEnable || 0));
    add('CT', 12, i, String(ct.DECvariable1 || 1));
    add('CT', 13, i, String(ct.DECcondition || 1));
    add('CT', 14, i, String(ct.DECvarCond || 0));
    add('CT', 15, i, String(ct.DECvariable2 || 1));
    add('CT', 16, i, String(ct.DECconstant || 0));
    add('CT', 17, i, String(ct.RSTEnable || 0));
    add('CT', 18, i, String(ct.RSTvariable1 || 1));
    add('CT', 19, i, String(ct.RSTcondition || 1));
    add('CT', 20, i, String(ct.RSTvarCond || 0));
    add('CT', 21, i, String(ct.RSTvariable2 || 1));
    add('CT', 22, i, String(ct.RSTconstant || 0));
    add('CT', 23, i, ct.visibleInDOM ? "1" : "0");
    add('CT', 24, i, ct.label || '');
  }

  // --- MC (MathsChannels) - generated from hwpdm ---
  for (let i = 0; i < 30; i++) {
    const mc = hwpdm.MathsChannel[i];
    add('MC', 1, i, mc.enabled ? "1" : "0");
    add('MC', 2, i, mc.label || '');
    // MC,3 = equationArray, padded to 100 sub-entries
    const eqArr = mc.equationArray || [];
    for (let s = 0; s < 100; s++) {
      addSub('MC', 3, i, s, String(eqArr[s] || 0));
    }
    add('MC', 4, i, mc.visibleInDOM ? "1" : "0");
  }

  // --- GF (GenericFunctions) ---
  for (let i = 0; i < 30; i++) {
    const gf = hwpdm.GenericFunction[i];
    add('GF', 1, i, gf.enabled ? "1" : "0");
    add('GF', 2, i, gf.label);

    const func = gf.function || [1];
    for (let s = 0; s < 100; s++) {
      addSub('GF', 3, i, s, String(func[s] || 0));
    }

    add('GF', 4, i, "1");
  }

  // --- SC (SensorCalibration) - generated from hwpdm ---
  for (let i = 0; i < 10; i++) {
    const sc = hwpdm.SensorCalibration[i];
    add('SC', 1, i, sc.enabled ? "1" : "0");
    add('SC', 2, i, sc.label || '');
    add('SC', 3, i, String(sc.variable || 1));
    // SC,4 = rawSensorDataPoint, SC,5 = calibratedSensorDataPoint (20 entries each, interleaved)
    const rawPts = sc.rawSensorDataPoint || [];
    const calPts = sc.calibratedSensorDataPoint || [];
    for (let s = 0; s < 20; s++) {
      addSub('SC', 4, i, s, String(rawPts[s] || 0));
      addSub('SC', 5, i, s, String(calPts[s] || 0));
    }
  }
  copySection('TD');
  copySection('CK');
  copySection('CF');
  copySection('CI');
  copySection('CO');
  // --- CS (CAN Stream) — generate from hwpdm.CANStream instead of copying template ---
  {
    const cs = hwpdm.CANStream;
    // Global settings: CS,1=enabled, CS,2=channel, CS,3=baseID
    allCommands.push(`CS,1,"${cs.enabled ? 1 : 0}"`);
    allCommands.push(`CS,2,"${cs.CANChannel}"`);
    allCommands.push(`CS,3,"${cs.baseID}"`);

    // Per-frame: CS,4,frame=enabled, CS,5,frame=sendRate
    // Per-signal: CS,6,frame,signal=variable, CS,7=type, CS,8=endianness,
    //             CS,9=startBit, CS,10=length, CS,11=factor(×1000), CS,12=offset
    for (let f = 0; f < cs.frame.length; f++) {
      const fr = cs.frame[f];
      allCommands.push(`CS,4,${f},"${fr.enabled ? 1 : 0}"`);
      allCommands.push(`CS,5,${f},"${fr.sendRate}"`);

      for (let s = 0; s < fr.signal.length; s++) {
        const sig = fr.signal[s];
        allCommands.push(`CS,6,${f},${s},"${sig.variable}"`);
        allCommands.push(`CS,7,${f},${s},"${sig.type}"`);
        allCommands.push(`CS,8,${f},${s},"${sig.endianness}"`);
        allCommands.push(`CS,9,${f},${s},"${sig.startBit}"`);
        allCommands.push(`CS,10,${f},${s},"${sig.length}"`);
        allCommands.push(`CS,11,${f},${s},"${Math.round(sig.factor * 1000)}"`);
        allCommands.push(`CS,12,${f},${s},"${sig.offset}"`);
      }
    }
    const enabledCount = cs.frame.filter(f => f.enabled).length;
    console.log(`  CS: Generated ${enabledCount} enabled frames (${cs.frame.length} total)`);
  }

  // --- EC (end marker) ---
  if (templateCmds['EC']) copySection('EC');

  // --- Pack commands into lines (3-4 commands per line, matching original format) ---
  const lines = [];
  for (let i = 0; i < allCommands.length; i += 4) {
    const batch = allCommands.slice(i, Math.min(i + 4, allCommands.length));
    lines.push('$,6,' + batch.join(',') + ',#\n');
  }

  return lines;
}

// --- Assemble the HWPDM file ---
console.log('Building HWPDM from config...');

const hwpdm = {
  MetaData: {
    ...template.MetaData,
    lastSaved: new Date().toISOString(),
  },
  Global: buildGlobal(),
  Input: buildInputs(),
  OutputHS: buildOutputHS(),
  OutputLS: buildOutputLS(),
  Timer: buildTimers(),
  LoggingGroup: buildLoggingGroups(),
  Counter: buildCounters(),
  MathsChannel: buildMathsChannels(),
  GenericFunction: buildGenericFunctions(),
  SensorCalibration: buildSensorCalibrations(),
  TwoDTable: template.TwoDTable,
  CANKeypad: template.CANKeypad,
  CANInputFilter: template.CANInputFilter,
  CANInput: template.CANInput,
  CANOutput: template.CANOutput,
  CANStream: buildCANStream(),
  MPDMDevice: template.MPDMDevice,
  LINBus: template.LINBus,
  pinManager: template.pinManager,
  rawSendData: [], // Will be populated
};

// Build rawSendData
console.log('Generating rawSendData protocol stream...');
hwpdm.rawSendData = buildRawSendData(hwpdm);

// --- Validate ---
console.log('\n=== VALIDATION ===');
console.log(`OutputHS: ${hwpdm.OutputHS.length} entries (expected 35)`);
console.log(`OutputLS: ${hwpdm.OutputLS.length} entries (expected 35)`);
console.log(`Input: ${hwpdm.Input.length} entries (expected 16)`);
console.log(`Timer: ${hwpdm.Timer.length} entries (expected 30)`);
console.log(`GenericFunction: ${hwpdm.GenericFunction.length} entries (expected 30)`);
console.log(`MathsChannel: ${hwpdm.MathsChannel.length} entries (expected 30)`);
console.log(`Counter: ${hwpdm.Counter.length} entries (expected 30)`);
console.log(`LoggingGroup: ${hwpdm.LoggingGroup.length} entries (expected 30)`);
console.log(`SensorCalibration: ${hwpdm.SensorCalibration.length} entries (expected 10)`);
console.log(`rawSendData: ${hwpdm.rawSendData.length} lines`);

// Show configured outputs
console.log('\n=== CONFIGURED OUTPUTS ===');
hwpdm.OutputHS.forEach((o, i) => {
  if (o.enabled) {
    const lowFuseNote = parseFloat(o.lowFuse) > 0 ? ` lowFuse=${o.lowFuse}A` : '';
    const stayOnNote = parseInt(o.stayOnTime) > 0 ? ` stayOn=${o.stayOnTime}ms` : '';
    const delayNote = parseInt(o.turnOnDelay) > 0 ? ` delay=${o.turnOnDelay}ms` : '';
    console.log(`  O${i + 1}: ${o.label} | ${o.highFuse}A | func=${JSON.stringify(o.function)} | soft_start=${o.PWMSoftStartEnable}${lowFuseNote}${stayOnNote}${delayNote}`);
  }
});

// Show configured inputs
console.log('\n=== CONFIGURED INPUTS ===');
hwpdm.Input.forEach((inp, i) => {
  if (inp.label) {
    const modes = ['Momentary', 'Latching', 'Analog'];
    console.log(`  I${i + 1}: ${inp.label} | mode=${modes[parseInt(inp.mode)] || inp.mode} | active=${inp.activeLevel === "1" ? "Low" : "High"} | thresh=${inp.thresholdVoltage}V`);
  }
});

// Show timer
console.log('\n=== CONFIGURED TIMERS ===');
hwpdm.Timer.forEach((t, i) => {
  if (t.enabled) {
    console.log(`  T${i + 1}: ${t.label} | on=${t.onTime}ms off=${t.offTime}ms`);
  }
});

// Show GF
console.log('\n=== CONFIGURED GENERIC FUNCTIONS ===');
hwpdm.GenericFunction.forEach((gf, i) => {
  if (gf.enabled) {
    console.log(`  GF${i + 1}: ${gf.label} | func=${JSON.stringify(gf.function)}`);
  }
});

// Show MathsChannels
console.log('\n=== CONFIGURED MATHS CHANNELS ===');
hwpdm.MathsChannel.forEach((mc, i) => {
  if (mc.enabled) {
    console.log(`  MC${i + 1}: ${mc.label} | eqLen=${mc.equationArray.length} | postfixLen=${mc.equationArrayPostfix.length}`);
  }
});

// Show Counters
console.log('\n=== CONFIGURED COUNTERS ===');
hwpdm.Counter.forEach((ct, i) => {
  if (ct.enabled) {
    console.log(`  CT${i + 1}: ${ct.label} | INC: var1=${ct.INCvariable1} cond=${ct.INCcondition} var2=${ct.INCvariable2}`);
  }
});

// Show LoggingGroups
console.log('\n=== CONFIGURED LOGGING GROUPS ===');
hwpdm.LoggingGroup.forEach((lg, i) => {
  if (lg.enabled) {
    console.log(`  LG${i + 1}: ${lg.label} | ${lg.triggerPeriod}ms | vars=${JSON.stringify(lg.variableList)}`);
  }
});

// Show SensorCalibrations
console.log('\n=== CONFIGURED SENSOR CALIBRATIONS ===');
hwpdm.SensorCalibration.forEach((sc, i) => {
  if (sc.enabled) {
    console.log(`  SC${i + 1}: ${sc.label} | inputKey=${sc.variable} | raw=[${sc.rawSensorDataPoint.slice(0, 3).join(',')}...] | cal=[${sc.calibratedSensorDataPoint.slice(0, 3).join(',')}...]`);
  }
});

// --- Write output ---
fs.writeFileSync(outputFile, JSON.stringify(hwpdm, null, 2));
console.log(`\nWritten to: ${outputFile} (${(fs.statSync(outputFile).size / 1024).toFixed(0)} KB)`);
