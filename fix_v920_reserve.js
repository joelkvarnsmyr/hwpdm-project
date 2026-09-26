// Repurpose O8/O9 as reserve + DBC-safe input rename, preserving v9.19 autotune.
// O8 "IND.TURN" + O9 "WARN.MASTER" = dashboard tell-tale lamps replaced by the
// digital cluster (confirmed by Joel). Real blinker bulbs are on other outputs.
const fs = require('fs');
const src = 'Builds/Elton_v9.19_autotune.HWPDM';
const dst = 'Builds/Elton_v9.20_autotune.HWPDM';

const d = JSON.parse(fs.readFileSync(src, 'utf8'));

// --- structured prop changes (preserve fuses/autotune; only label + enabled) ---
d.OutputHS[7].label = 'RESERVE8'; d.OutputHS[7].enabled = false;  // O8 was enabled+blinking
d.OutputLS[7].label = 'RESERVE8';                                 // LS already disabled
d.OutputHS[8].label = 'RESERVE9';                                 // O9 already disabled
d.OutputLS[8].label = 'RESERVE9';
d.Input[13].label   = 'OIL_PRESS';                                // I14 real input, just drop the dot

// --- flip O8 HS enabled in rawSendData (OP,5,7,"1" -> "0") to match the prop ---
let opFlips = 0;
d.rawSendData = d.rawSendData.map(line => {
  if (line.includes('OP,5,7,"1"')) { opFlips++; return line.replace('OP,5,7,"1"', 'OP,5,7,"0"'); }
  return line;
});

let txt = JSON.stringify(d);

// --- global label replace: catches rawSendData label cmds + any CANStream/other refs ---
const before = {
  'IND.TURN': txt.split('IND.TURN').length - 1,
  'WARN.MASTER': txt.split('WARN.MASTER').length - 1,
  'OIL.PRESS': txt.split('OIL.PRESS').length - 1,
};
txt = txt.split('IND.TURN').join('RESERVE8')
         .split('WARN.MASTER').join('RESERVE9')
         .split('OIL.PRESS').join('OIL_PRESS');

// --- validate ---
const v = JSON.parse(txt);
const dotted = [];
const chk = (arr, k) => (arr || []).forEach((o, i) => {
  const l = o && (o.label || o.name);
  if (l && l.includes('.') && l !== '1.2.3') dotted.push(`${k}[${i}]="${l}"`);
});
chk(v.OutputHS, 'OutputHS'); chk(v.OutputLS, 'OutputLS'); chk(v.Input, 'Input');
const op57 = v.rawSendData.find(l => l.includes('OP,5,7,'));

console.log('label occurrences fixed:', JSON.stringify(before));
console.log('OP,5,7 enabled flips:', opFlips, '| now:', (op57 || '').match(/OP,5,7,"\d"/));
console.log('O8 HS[7]:  label=' + v.OutputHS[7].label + ' enabled=' + v.OutputHS[7].enabled +
            ' | fuse lo/hi/peak=' + v.OutputHS[7].lowFuse + '/' + v.OutputHS[7].highFuse + '/' + v.OutputHS[7].peakFuse);
console.log('O9 HS[8]:  label=' + v.OutputHS[8].label + ' enabled=' + v.OutputHS[8].enabled);
console.log('LS[7]/LS[8] label=' + v.OutputLS[7].label + '/' + v.OutputLS[8].label);
console.log('I14 Input[13] label=' + v.Input[13].label);
console.log('dotted labels remaining:', dotted.length ? dotted.join(', ') : 'NONE (clean)');

if (dotted.length) { console.error('ABORT: dotted labels remain'); process.exit(1); }
if (opFlips !== 1) { console.error('ABORT: expected exactly 1 OP,5,7 enabled flip, got ' + opFlips); process.exit(1); }
if (v.OutputHS[7].enabled !== false || v.OutputHS[8].enabled !== false) { console.error('ABORT: O8/O9 not disabled'); process.exit(1); }

fs.writeFileSync(dst, txt);
console.log('WROTE ' + dst + ' | size ' + fs.statSync(dst).size + ' (src ' + fs.statSync(src).size + ')');
