const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const gen = JSON.parse(fs.readFileSync('Elton_v6.1.HWPDM', 'utf8'));

function countSub(raw, prefix, field, idx) {
  let max = -1;
  raw.forEach(line => {
    const re = new RegExp(prefix + ',' + field + ',' + idx + ',(\\d+),', 'g');
    let m;
    while ((m = re.exec(line)) !== null) max = Math.max(max, parseInt(m[1]));
  });
  return max + 1;
}

console.log('=== LINE COUNTS ===');
console.log('Original:', orig.rawSendData.length);
console.log('Generated:', gen.rawSendData.length);
console.log('Difference:', orig.rawSendData.length - gen.rawSendData.length);

console.log('\n=== SUBINDEX COUNTS ===');
const checks = [
  ['OP', 12, 0, 'OP func O1'],
  ['OP', 19, 0, 'OP infix O1'],
  ['OP', 38, 0, 'OP LS infix O1'],
  ['GF', 3, 0, 'GF func GF1'],
  ['SC', 4, 0, 'SC xValues'],
  ['SC', 5, 0, 'SC yValues'],
];
for (const [p, f, i, desc] of checks) {
  const oc = countSub(orig.rawSendData, p, f, i);
  const gc = countSub(gen.rawSendData, p, f, i);
  const status = oc === gc ? 'OK' : 'MISMATCH';
  console.log(`  ${desc}: orig=${oc} gen=${gc} ${status}`);
}

// Check section order
console.log('\n=== SECTION ORDER ===');
const origOrder = [];
const genOrder = [];
let lastO = '', lastG = '';
orig.rawSendData.forEach(line => {
  const m = line.match(/\$,6,([A-Z]{2}),/);
  if (m && m[1] !== lastO) { origOrder.push(m[1]); lastO = m[1]; }
});
gen.rawSendData.forEach(line => {
  const m = line.match(/\$,6,([A-Z]{2}),/);
  if (m && m[1] !== lastG) { genOrder.push(m[1]); lastG = m[1]; }
});
console.log('Original:', origOrder.join(' → '));
console.log('Generated:', genOrder.join(' → '));

// Check first few OP lines in generated
console.log('\n=== GENERATED: First OP lines ===');
let opCount = 0;
gen.rawSendData.forEach((line, li) => {
  if (line.includes('OP,') && opCount < 10) {
    console.log('L' + li + ': ' + line.trim().substring(0, 100));
    opCount++;
  }
});

// Check OP,12 for O6 (which has a complex function [43,7,4,0,0])
console.log('\n=== GENERATED: OP,12 for O6 (TURN R, func=[43,7,4,0,0]) ===');
gen.rawSendData.forEach(line => {
  const re = /OP,12,5,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    console.log('  OP,12,5,' + m[1] + ' = "' + m[2] + '"');
  }
});

// Verify GF1 function
console.log('\n=== GENERATED: GF lines for GF1 ===');
let gfCount = 0;
gen.rawSendData.forEach((line, li) => {
  if (line.includes('GF,') && line.includes(',0,') && gfCount < 5) {
    console.log('L' + li + ': ' + line.trim().substring(0, 100));
    gfCount++;
  }
});
