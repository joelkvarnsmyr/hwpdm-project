const fs = require('fs');
const d = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));

// === MAP PREFIX → JSON SECTION ===
// GL = Global, OP = OutputHS, IP = Input, TI = Timer, GF = GenericFunction,
// MC = MathsChannel, CO = CANOutput, CI = CANInput, CS = CANStream,
// CK = CANKeypad(?), CF = CANInputFilter(?), SC = SensorCalibration,
// TD = TwoDTable, LG = LoggingGroup, CT = Counter, PH = ?

// Let's verify by matching known values

console.log('=== OP (OutputHS) field mapping ===');
// OP,13,0,"BUSBAR" → OutputHS[0].label = "BUSBAR"
// Let's find all OP commands for index 0
const raw = d.rawSendData;
const op0 = [];
raw.forEach(line => {
  const re = /OP,(\d+),0,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    op0.push({ field: parseInt(m[1]), value: m[2] });
  }
});
console.log('OP fields for output 0:');
op0.forEach(({ field, value }) => console.log(`  OP,${field},0 = "${value}"`));
console.log('\nOutputHS[0] JSON:');
const o0 = d.OutputHS[0];
Object.keys(o0).forEach(k => {
  const v = o0[k];
  if (Array.isArray(v)) {
    console.log(`  ${k} = [${v.slice(0,5).join(',')}${v.length > 5 ? '...' : ''}] (len ${v.length})`);
  } else {
    console.log(`  ${k} = ${JSON.stringify(v)}`);
  }
});

console.log('\n=== IP (Input) field mapping ===');
const ip0 = [];
raw.forEach(line => {
  const re = /IP,(\d+),0,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    ip0.push({ field: parseInt(m[1]), value: m[2] });
  }
});
console.log('IP fields for input 0:');
ip0.forEach(({ field, value }) => console.log(`  IP,${field},0 = "${value}"`));
console.log('\nInput[0] JSON:');
const i0 = d.Input[0];
Object.keys(i0).forEach(k => {
  console.log(`  ${k} = ${JSON.stringify(i0[k])}`);
});

console.log('\n=== TI (Timer) field mapping ===');
const ti0 = [];
raw.forEach(line => {
  const re = /TI,(\d+),0,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    ti0.push({ field: parseInt(m[1]), value: m[2] });
  }
});
console.log('TI fields for timer 0:');
ti0.forEach(({ field, value }) => console.log(`  TI,${field},0 = "${value}"`));
console.log('\nTimer[0] JSON:');
const t0 = d.Timer[0];
Object.keys(t0).forEach(k => {
  const v = t0[k];
  if (Array.isArray(v)) {
    console.log(`  ${k} = [${v.slice(0,5).join(',')}${v.length > 5 ? '...' : ''}] (len ${v.length})`);
  } else {
    console.log(`  ${k} = ${JSON.stringify(v)}`);
  }
});

console.log('\n=== GL (Global) field mapping ===');
const gl = [];
raw.forEach(line => {
  const re = /GL,(\d+)(?:,(\d+))?,"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    gl.push({ field: parseInt(m[1]), sub: m[2], value: m[3] });
  }
});
console.log('GL fields:');
gl.forEach(({ field, sub, value }) => console.log(`  GL,${field}${sub !== undefined ? ','+sub : ''} = "${value}"`));
console.log('\nGlobal JSON:');
Object.keys(d.Global).forEach(k => {
  console.log(`  ${k} = ${JSON.stringify(d.Global[k])}`);
});
