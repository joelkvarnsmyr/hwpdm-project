const fs = require('fs');
const d = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const raw = d.rawSendData;

// DEFINITIVE FIELD MAPPINGS - verified by cross-referencing rawSendData values with JSON

// === OP: OutputHS (1-18) + OutputLS (20-37) ===
// OP fields 1-18 → OutputHS[idx], fields 20-37 → OutputLS[idx]
// Verified: OP,13,0="BUSBAR" → OutputHS[0].label="BUSBAR"
//           OP,32,0="BUSBAR" → OutputLS[0].label="BUSBAR"

const HS_MAP = {
  1: 'lowFuse',
  2: 'highFuse',
  3: 'peakFuse',
  4: 'peakFuseTime',
  5: 'enabled',          // "1"→true, "0"→false
  6: 'stayOnTime',
  7: 'turnOnDelay',
  8: 'clearTime',         // OP,8,0="10" but JSON clearTime="1"... might be retries*10?
  9: 'retries',
  10: 'tripMode',
  11: '???_11',
  12: 'function',         // subindexed: OP,12,idx,subidx,"value"
  13: 'label',
  14: 'scaler',
  15: 'offset',
  16: 'PWMFrequency',
  17: 'PWMSoftStartEnable',
  18: 'PWMSoftStartTime',
};

// Now let me verify clearTime properly
console.log('=== VERIFYING OP FIELD 8 ===');
for (let i = 0; i < 5; i++) {
  const vals = [];
  raw.forEach(line => {
    const re = new RegExp(`OP,8,${i},"([^"]*)"`, 'g');
    let m;
    while ((m = re.exec(line)) !== null) vals.push(m[1]);
  });
  console.log(`OP,8,${i} = ${vals.join(',')}  JSON clearTime=${d.OutputHS[i].clearTime}`);
}

// Let's also verify OP,5 (enabled) mapping
console.log('\n=== VERIFYING OP FIELD 5 (enabled) ===');
for (let i = 0; i < 10; i++) {
  const vals = [];
  raw.forEach(line => {
    const re = new RegExp(`OP,5,${i},"([^"]*)"`, 'g');
    let m;
    while ((m = re.exec(line)) !== null) vals.push(m[1]);
  });
  console.log(`OP,5,${i} = ${vals.join(',')}  JSON enabled=${d.OutputHS[i].enabled} label=${d.OutputHS[i].label}`);
}

// Check OP,19 which wasn't in our map (it's function subindexed?)
console.log('\n=== OP,19 (subindexed, functionInfix?) ===');
const op19 = [];
raw.forEach(line => {
  const re = /OP,19,(\d+),(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    op19.push({ idx: m[1], sub: m[2], value: m[3] });
  }
});
op19.slice(0, 10).forEach(({ idx, sub, value }) =>
  console.log(`  OP,19,${idx},${sub} = "${value}"`));
console.log('OutputHS[0].functionInfix:', d.OutputHS[0].functionInfix);

// Check OP,12 (function array)
console.log('\n=== OP,12 (subindexed, function array?) ===');
const op12 = [];
raw.forEach(line => {
  const re = /OP,12,(\d+),(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    op12.push({ idx: m[1], sub: m[2], value: m[3] });
  }
});
op12.slice(0, 10).forEach(({ idx, sub, value }) =>
  console.log(`  OP,12,${idx},${sub} = "${value}"`));
console.log('OutputHS[0].function:', d.OutputHS[0].function);

// Now check IP mapping more carefully
console.log('\n=== IP FIELD MAP VERIFICATION ===');
// IP,1=mode? IP,3=enabled? IP,4=activeLevel?
// Input[0]: mode="1" enabled=true activeLevel="0" label="BLOWER"
// IP,1,0="1" IP,3,0="1" IP,4,0="0" IP,10,0="BLOWER"
// Input[1]: mode="0" enabled=true activeLevel="0" label="HIBEAM"
// IP,1,1="0" IP,3,1="0" IP,10,1="HIBEAM"
// Wait - IP,3,1="0" but enabled=true? Let me check
console.log('Input[1].enabled:', d.Input[1].enabled);
// Hmm maybe IP,3 isn't enabled. Let's check all inputs
for (let i = 0; i < 16; i++) {
  const ipVals = {};
  raw.forEach(line => {
    for (let f = 1; f <= 10; f++) {
      const re = new RegExp(`IP,${f},${i},"([^"]*)"`, 'g');
      let m;
      while ((m = re.exec(line)) !== null) {
        ipVals[f] = m[1];
      }
    }
  });
  const inp = d.Input[i];
  console.log(`Input[${i}]: IP1=${ipVals[1]} IP2=${ipVals[2]} IP3=${ipVals[3]} IP4=${ipVals[4]} IP5=${ipVals[5]} IP6=${ipVals[6]} IP7=${ipVals[7]} IP8=${ipVals[8]} IP9=${ipVals[9]} IP10=${ipVals[10]} | mode=${inp.mode} thresh=${inp.thresholdVoltage} hyst=${inp.hysteresisVoltage} delay=${inp.turnOnDelay} pull=${inp.pullResistor} enabled=${inp.enabled} active=${inp.activeLevel} label=${inp.label}`);
}
