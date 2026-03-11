const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const gen = JSON.parse(fs.readFileSync('Elton_v6.2.HWPDM', 'utf8'));

function countSub(raw, prefix, field, idx) {
  let max = -1;
  raw.forEach(line => {
    const re = new RegExp(prefix + ',' + field + ',' + idx + ',(\\d+),', 'g');
    let m;
    while ((m = re.exec(line)) !== null) max = Math.max(max, parseInt(m[1]));
  });
  return max + 1;
}

// Count commands per prefix
function countCommands(raw) {
  const counts = {};
  raw.forEach(line => {
    const re = /([A-Z]{2}),\d/g;
    let m;
    while ((m = re.exec(line)) !== null) {
      counts[m[1]] = (counts[m[1]] || 0) + 1;
    }
  });
  return counts;
}

console.log('=== LINE & COMMAND COUNTS ===');
console.log('Lines: orig=' + orig.rawSendData.length + ' gen=' + gen.rawSendData.length);
const oc = countCommands(orig.rawSendData);
const gc = countCommands(gen.rawSendData);
const allPrefixes = [...new Set([...Object.keys(oc), ...Object.keys(gc)])].sort();
let totalO = 0, totalG = 0;
for (const p of allPrefixes) {
  const o = oc[p] || 0;
  const g = gc[p] || 0;
  totalO += o; totalG += g;
  const status = o === g ? 'OK' : 'DIFF';
  if (status === 'DIFF') console.log(`  ${p}: orig=${o} gen=${g} ${status}`);
}
console.log('Total commands: orig=' + totalO + ' gen=' + totalG);

// Subindex checks
console.log('\n=== SUBINDEX COUNTS ===');
const checks = [
  ['OP', 12, 0, 'O1 func'], ['OP', 12, 5, 'O6 func (complex)'],
  ['OP', 19, 0, 'O1 HS infix'], ['OP', 38, 0, 'O1 LS infix'],
  ['GF', 3, 0, 'GF1 func'],
];
for (const [p, f, i, desc] of checks) {
  const o2 = countSub(orig.rawSendData, p, f, i);
  const g2 = countSub(gen.rawSendData, p, f, i);
  console.log(`  ${desc}: orig=${o2} gen=${g2} ${o2 === g2 ? 'OK' : 'MISMATCH'}`);
}

// Section order
const origOrder = []; const genOrder = [];
let lastO2 = '', lastG2 = '';
orig.rawSendData.forEach(line => {
  const m = line.match(/\$,6,([A-Z]{2}),/);
  if (m && m[1] !== lastO2) { origOrder.push(m[1]); lastO2 = m[1]; }
});
gen.rawSendData.forEach(line => {
  const m = line.match(/\$,6,([A-Z]{2}),/);
  if (m && m[1] !== lastG2) { genOrder.push(m[1]); lastG2 = m[1]; }
});
console.log('\n=== SECTION ORDER ===');
console.log('Orig:', origOrder.join(' → '));
console.log('Gen: ', genOrder.join(' → '));

// Verify O6 function
console.log('\n=== O6 (TURN R) function verification ===');
gen.rawSendData.forEach(line => {
  const re = /OP,12,5,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    console.log('  OP,12,5,' + m[1] + ' = "' + m[2] + '"');
  }
});

// Verify GF1
console.log('\n=== GF1 verification ===');
gen.rawSendData.forEach(line => {
  if (line.includes('GF,1,0,"1"') || line.includes('GF,2,0,"IGN')) {
    console.log('  ' + line.trim().substring(0, 100));
  }
  if (line.includes('GF,3,0,0,"17"')) {
    console.log('  ' + line.trim().substring(0, 100));
  }
});

// Check for any duplicate GF,1,0 entries
console.log('\n=== Checking for duplicate GF,1,0 ===');
let gf10count = 0;
gen.rawSendData.forEach(line => {
  const re = /GF,1,0,"/g;
  let m;
  while ((m = re.exec(line)) !== null) gf10count++;
});
console.log('  GF,1,0 occurrences:', gf10count, gf10count === 1 ? 'OK' : 'DUPLICATE!');
