const fs = require('fs');
const d = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));

console.log('=== METADATA ===');
console.log(JSON.stringify(d.MetaData, null, 2));

console.log('\n=== GLOBAL (key settings) ===');
console.log('Device:', d.Global.deviceModel, 'v' + d.Global.deviceModelVersion);
console.log('CAN speed:', d.Global.CANspeed);
console.log('CAN termination:', d.Global.CANtermres);

console.log('\n=== INPUTS (16) ===');
d.Input.forEach((inp, i) => {
  const lbl = inp.label || '(unnamed)';
  console.log(`I${i+1}: mode=${inp.mode} activeLevel=${inp.activeLevel} enabled=${inp.enabled} threshold=${inp.thresholdVoltage}V pull=${inp.pullResistor} label="${lbl}"`);
});

console.log('\n=== HIGH-SIDE OUTPUTS (configured) ===');
d.OutputHS.forEach((out, i) => {
  if (out.enabled || (out.label && out.label.trim() !== '')) {
    console.log(`O${i+1}: low=${out.lowFuse}A high=${out.highFuse}A peak=${out.peakFuse}A peakTime=${out.peakFuseTime}ms enabled=${out.enabled} retries=${out.retries} label="${out.label}"`);
    if (out.function && out.function.length > 0) {
      console.log(`  function: ${JSON.stringify(out.function).slice(0, 300)}`);
      console.log(`  infix: ${JSON.stringify(out.functionInfix).slice(0, 300)}`);
    }
  }
});

console.log('\n=== LOW-SIDE OUTPUTS (configured) ===');
d.OutputLS.forEach((out, i) => {
  if (out.enabled || (out.label && out.label.trim() !== '')) {
    console.log(`LS${i+1}: low=${out.lowFuse}A high=${out.highFuse}A enabled=${out.enabled} label="${out.label}"`);
    if (out.function && out.function.length > 0) {
      console.log(`  function: ${JSON.stringify(out.function).slice(0, 300)}`);
    }
  }
});

console.log('\n=== TIMERS (configured) ===');
d.Timer.forEach((t, i) => {
  if (t.enabled || (t.label && t.label.trim() !== '')) {
    console.log(`T${i+1}: on=${t.onTime}ms off=${t.offTime}ms enabled=${t.enabled} label="${t.label}" type=${t.type}`);
  }
});

console.log('\n=== GENERIC FUNCTIONS (configured) ===');
d.GenericFunction.forEach((gf, i) => {
  if (gf.enabled || (gf.label && gf.label.trim() !== '')) {
    console.log(`GF${i+1}: enabled=${gf.enabled} label="${gf.label}"`);
    console.log(`  function: ${JSON.stringify(gf.function).slice(0, 300)}`);
    console.log(`  infix: ${JSON.stringify(gf.functionInfix).slice(0, 300)}`);
  }
});

console.log('\n=== MATHS CHANNELS (configured) ===');
d.MathsChannel.forEach((mc, i) => {
  if (mc.enabled || (mc.label && mc.label.trim() !== '')) {
    console.log(`MC${i+1}: enabled=${mc.enabled} label="${mc.label}"`);
  }
});

console.log('\n=== CAN OUTPUTS (configured) ===');
d.CANOutput.forEach((co, i) => {
  if (co.enabled) {
    console.log(`CO${i+1}: ID=${co.CANID} freq=${co.frequency}ms ch=${co.CANChannel} label="${co.label}"`);
  }
});

console.log('\n=== CAN INPUTS (configured) ===');
d.CANInput.forEach((ci, i) => {
  if (ci.enabled) {
    console.log(`CI${i+1}: ID=${ci.CANID} format=${ci.dataFormat} label="${ci.label}"`);
  }
});

console.log('\n=== PIN MANAGER NOTES ===');
if (d.pinManager && d.pinManager.notes) {
  console.log(d.pinManager.notes.slice(0, 500));
}
