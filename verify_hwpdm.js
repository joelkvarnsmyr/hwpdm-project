const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const gen = JSON.parse(fs.readFileSync('Elton_generated.HWPDM', 'utf8'));

console.log('=== STRUCTURAL COMPARISON ===');
const sections = ['Global', 'Input', 'OutputHS', 'OutputLS', 'Timer', 'GenericFunction',
  'MathsChannel', 'Counter', 'LoggingGroup', 'SensorCalibration', 'TwoDTable',
  'CANKeypad', 'CANInputFilter', 'CANInput', 'CANOutput', 'CANStream',
  'MPDMDevice', 'LINBus', 'pinManager'];

for (const s of sections) {
  const oLen = Array.isArray(orig[s]) ? orig[s].length : (orig[s] ? 'obj' : 'missing');
  const gLen = Array.isArray(gen[s]) ? gen[s].length : (gen[s] ? 'obj' : 'missing');
  const match = oLen === gLen ? 'OK' : 'MISMATCH';
  console.log(`  ${s}: orig=${oLen} gen=${gLen} ${match}`);
}

console.log(`\n  rawSendData: orig=${orig.rawSendData.length} gen=${gen.rawSendData.length}`);

// Compare key output values
console.log('\n=== OUTPUT COMPARISON (label, fuse, enabled, function) ===');
for (let i = 0; i < 25; i++) {
  const o = orig.OutputHS[i];
  const g = gen.OutputHS[i];
  const diffs = [];
  if (o.label !== g.label) diffs.push(`label: "${o.label}" → "${g.label}"`);
  if (o.enabled !== g.enabled) diffs.push(`enabled: ${o.enabled} → ${g.enabled}`);
  if (String(o.highFuse) !== String(g.highFuse)) diffs.push(`highFuse: ${o.highFuse} → ${g.highFuse}`);
  if (JSON.stringify(o.function) !== JSON.stringify(g.function)) diffs.push(`func: ${JSON.stringify(o.function)} → ${JSON.stringify(g.function)}`);

  if (diffs.length > 0) {
    console.log(`  O${i+1} ${g.label}: ${diffs.join(' | ')}`);
  }
}

// Compare input values
console.log('\n=== INPUT COMPARISON ===');
for (let i = 0; i < 16; i++) {
  const o = orig.Input[i];
  const g = gen.Input[i];
  const diffs = [];
  if (o.label !== g.label) diffs.push(`label: "${o.label}" → "${g.label}"`);
  if (o.mode !== g.mode) diffs.push(`mode: ${o.mode} → ${g.mode}`);
  if (o.activeLevel !== g.activeLevel) diffs.push(`active: ${o.activeLevel} → ${g.activeLevel}`);

  if (diffs.length > 0) {
    console.log(`  I${i+1}: ${diffs.join(' | ')}`);
  }
}

// Compare timer
console.log('\n=== TIMER COMPARISON ===');
const ot = orig.Timer[0];
const gt = gen.Timer[0];
console.log(`  T1 orig: on=${ot.onTime} off=${ot.offTime} label=${ot.label} enabled=${ot.enabled}`);
console.log(`  T1 gen:  on=${gt.onTime} off=${gt.offTime} label=${gt.label} enabled=${gt.enabled}`);

// Compare GF1
console.log('\n=== GF1 COMPARISON ===');
const og = orig.GenericFunction[0];
const gg = gen.GenericFunction[0];
console.log(`  GF1 orig: func=${JSON.stringify(og.function)} infix=${JSON.stringify(og.functionInfix)} label="${og.label}" enabled=${og.enabled}`);
console.log(`  GF1 gen:  func=${JSON.stringify(gg.function)} infix=${JSON.stringify(gg.functionInfix)} label="${gg.label}" enabled=${gg.enabled}`);
