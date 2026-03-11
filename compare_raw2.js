const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const gen = JSON.parse(fs.readFileSync('Elton_v6.0.HWPDM', 'utf8'));

// Check subindex counts for key fields in original
function countSubindexes(raw, prefix, field, idx) {
  let max = -1;
  raw.forEach(line => {
    const re = new RegExp(prefix + ',' + field + ',' + idx + ',(\\d+),', 'g');
    let m;
    while ((m = re.exec(line)) !== null) max = Math.max(max, parseInt(m[1]));
  });
  return max + 1;
}

// OP subindex counts
console.log('=== OP subindex counts (index 0) ===');
for (const f of [12, 19, 31, 38]) {
  const oc = countSubindexes(orig.rawSendData, 'OP', f, 0);
  const gc = countSubindexes(gen.rawSendData, 'OP', f, 0);
  console.log(`  OP,${f}: orig=${oc} gen=${gc} ${oc !== gc ? 'MISMATCH' : 'OK'}`);
}

// GF subindex counts
console.log('\n=== GF subindex counts (index 0) ===');
for (const f of [3, 4]) {
  const oc = countSubindexes(orig.rawSendData, 'GF', f, 0);
  const gc = countSubindexes(gen.rawSendData, 'GF', f, 0);
  console.log(`  GF,${f}: orig=${oc} gen=${gc} ${oc !== gc ? 'MISMATCH' : 'OK'}`);
}

// MC subindex counts
console.log('\n=== MC subindex counts (index 0) ===');
for (const f of [3, 4]) {
  const oc = countSubindexes(orig.rawSendData, 'MC', f, 0);
  const gc = countSubindexes(gen.rawSendData, 'MC', f, 0);
  console.log(`  MC,${f}: orig=${oc} gen=${gc} ${oc !== gc ? 'MISMATCH' : 'OK'}`);
}

// CT (Counter) - check what fields exist in original
console.log('\n=== CT fields in original (index 0) ===');
const ctFields = {};
orig.rawSendData.forEach(line => {
  const re = /CT,(\d+),0[,"].*?"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    const f = parseInt(m[1]);
    if (!ctFields[f]) ctFields[f] = m[2];
  }
});
console.log('Fields found:', Object.keys(ctFields).sort((a,b) => a-b).map(f => `CT,${f}="${ctFields[f]}"`).join(', '));

// CT subindex counts for subindexed fields
console.log('\n=== CT subindex counts (index 0) ===');
for (const f of [8, 13, 18]) {
  const oc = countSubindexes(orig.rawSendData, 'CT', f, 0);
  if (oc > 0) console.log(`  CT,${f}: orig=${oc}`);
}

// Check all CT raw lines for counter 0
console.log('\n=== CT raw lines for counter 0 (original) ===');
orig.rawSendData.forEach((line, li) => {
  if (/CT,\d+,0[,"]/.test(line) && li < 3000) {
    console.log('L' + li + ': ' + line.trim());
  }
});

// IP comparison
console.log('\n=== IP format comparison (index 0) ===');
console.log('ORIG:');
orig.rawSendData.forEach(line => {
  if (/IP,\d+,0[,"]/.test(line)) console.log('  ' + line.trim());
});
console.log('GEN:');
gen.rawSendData.forEach(line => {
  if (/IP,\d+,0[,"]/.test(line)) console.log('  ' + line.trim());
});

// SC comparison for index 0
console.log('\n=== SC subindex counts (index 0) ===');
for (const f of [4, 5]) {
  const oc = countSubindexes(orig.rawSendData, 'SC', f, 0);
  const gc = countSubindexes(gen.rawSendData, 'SC', f, 0);
  console.log(`  SC,${f}: orig=${oc} gen=${gc} ${oc !== gc ? 'MISMATCH' : 'OK'}`);
}
