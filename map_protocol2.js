const fs = require('fs');
const d = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const raw = d.rawSendData;

// Now let's build the complete field mapping for each prefix

// OP (OutputHS): Based on cross-referencing OP fields with OutputHS[0]
console.log('=== OP → OutputHS FIELD MAP ===');
const opMap = {
  1: 'lowFuse',        // "0"
  2: 'highFuse',       // "0"
  3: 'peakFuse',       // "0"
  4: 'peakFuseTime',   // "0"
  5: 'enabled',        // "1" (true)
  6: 'stayOnTime',     // "0"
  7: 'turnOnDelay',    // "0"
  8: 'clearTime',      // "10" → wait, JSON says "1"... let me check
  9: 'retries',        // "1"
  10: 'tripMode',      // "0"
  11: '???',           // "0"
  // 12 = function array (subindexed)
  13: 'label',         // "BUSBAR"
  14: 'scaler',        // "100"
  15: 'offset',        // "0"  → wait, JSON offset=0
  16: 'PWMFrequency',  // "100"
  17: 'PWMSoftStartEnable', // "0" (false)
  18: 'PWMSoftStartTime',  // "1" → wait, JSON says "100"
};

// Let me verify with output 1 (BRAKE)
console.log('\nVerifying with OutputHS[1] (BRAKE):');
const op1 = [];
raw.forEach(line => {
  const re = /OP,(\d+),1,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    op1.push({ field: parseInt(m[1]), value: m[2] });
  }
});
op1.forEach(({ field, value }) => console.log(`  OP,${field},1 = "${value}"`));
console.log('OutputHS[1]:');
const o1 = d.OutputHS[1];
console.log(`  label="${o1.label}" enabled=${o1.enabled} lowFuse=${o1.lowFuse} highFuse=${o1.highFuse}`);
console.log(`  peakFuse=${o1.peakFuse} peakFuseTime=${o1.peakFuseTime} retries=${o1.retries}`);
console.log(`  clearTime=${o1.clearTime} stayOnTime=${o1.stayOnTime} turnOnDelay=${o1.turnOnDelay}`);

// The OP data has fields 1-18 AND 20-37 which seem like a SECOND block
// 20-37 map to lowside (OutputLS) perhaps? Let's check
console.log('\n=== Checking if OP 20-37 is OutputLS ===');
const op0_high = [];
raw.forEach(line => {
  const re = /OP,(\d+),0,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    const f = parseInt(m[1]);
    if (f >= 20) op0_high.push({ field: f, value: m[2] });
  }
});
op0_high.forEach(({ field, value }) => console.log(`  OP,${field},0 = "${value}"`));
console.log('OutputLS[0]:');
const ls0 = d.OutputLS[0];
Object.keys(ls0).forEach(k => {
  const v = ls0[k];
  if (Array.isArray(v)) {
    console.log(`  ${k} = [${v.slice(0,3).join(',')}...] (len ${v.length})`);
  } else {
    console.log(`  ${k} = ${JSON.stringify(v)}`);
  }
});

// IP field mapping
console.log('\n=== IP → Input FIELD MAP ===');
const ipMap = {
  1: '??? (mode related?)',   // "1" → mode="1"
  2: '???',                   // "0"
  3: 'enabled',               // "1" → true
  4: 'activeLevel',           // "0"
  5: '???',                   // "0"
  6: '???',                   // "100" → thresholdVoltage is "0.1"... hmm
  7: 'pullResistor',          // "0"
  8: '???',                   // "0"
  9: '???',                   // "1"
  10: 'label',                // "BLOWER"
};

// Check IP for input 1 (HIBEAM)
console.log('\nIP fields for input 1:');
const ip1 = [];
raw.forEach(line => {
  const re = /IP,(\d+),1,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    ip1.push({ field: parseInt(m[1]), value: m[2] });
  }
});
ip1.forEach(({ field, value }) => console.log(`  IP,${field},1 = "${value}"`));
console.log('Input[1]:');
const i1 = d.Input[1];
Object.keys(i1).forEach(k => console.log(`  ${k} = ${JSON.stringify(i1[k])}`));

// GF field mapping - check GenericFunction
console.log('\n=== GF → GenericFunction check ===');
console.log('GF subindexed fields for GF 0:');
const gf0 = [];
raw.forEach(line => {
  const re = /GF,(\d+),0,?(\d*),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    gf0.push({ field: parseInt(m[1]), sub: m[2], value: m[3] });
  }
});
gf0.slice(0, 20).forEach(({ field, sub, value }) =>
  console.log(`  GF,${field},0${sub ? ','+sub : ''} = "${value}"`));
console.log('GenericFunction[0]:');
const g0 = d.GenericFunction[0];
Object.keys(g0).forEach(k => {
  const v = g0[k];
  if (Array.isArray(v)) {
    console.log(`  ${k} = [${v.slice(0,5).join(',')}...] (len ${v.length})`);
  } else {
    console.log(`  ${k} = ${JSON.stringify(v)}`);
  }
});

// Check prefix count matches array lengths
console.log('\n=== PREFIX → ARRAY SIZE CORRELATION ===');
const prefixCounts = {};
raw.forEach(line => {
  const re = /([A-Z]+),\d+,(\d+)/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    const key = m[1];
    const idx = parseInt(m[2]);
    if (!prefixCounts[key]) prefixCounts[key] = new Set();
    prefixCounts[key].add(idx);
  }
});

const arraySizes = {
  OP: 'OutputHS:' + d.OutputHS.length + ' + OutputLS:' + d.OutputLS.length,
  IP: 'Input:' + d.Input.length,
  TI: 'Timer:' + d.Timer.length,
  GF: 'GenericFunction:' + d.GenericFunction.length,
  MC: 'MathsChannel:' + d.MathsChannel.length,
  CO: 'CANOutput:' + d.CANOutput.length,
  CI: 'CANInput:' + d.CANInput.length,
  LG: 'LoggingGroup:' + d.LoggingGroup.length,
  CT: 'Counter:' + d.Counter.length,
  SC: 'SensorCalibration:' + d.SensorCalibration.length,
  TD: 'TwoDTable:' + d.TwoDTable.length,
};

Object.keys(prefixCounts).sort().forEach(k => {
  const indices = [...prefixCounts[k]].sort((a,b) => a-b);
  const info = arraySizes[k] || '';
  console.log(`${k}: indices ${indices[0]}-${indices[indices.length-1]} (${indices.length} unique) ${info}`);
});
