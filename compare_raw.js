const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const gen = JSON.parse(fs.readFileSync('Elton_v6.0.HWPDM', 'utf8'));

// Count OP,19 subindexes in original for O1
let origCount = 0, genCount = 0;
orig.rawSendData.forEach(line => {
  const re = /OP,19,0,(\d+),/g;
  let m;
  while ((m = re.exec(line)) !== null) origCount = Math.max(origCount, parseInt(m[1]) + 1);
});
gen.rawSendData.forEach(line => {
  const re = /OP,19,0,(\d+),/g;
  let m;
  while ((m = re.exec(line)) !== null) genCount = Math.max(genCount, parseInt(m[1]) + 1);
});
console.log('OP,19 subindexes for O1: orig=' + origCount + ' gen=' + genCount);

// Check how many OP,12 subindexes in original for first 5 outputs
console.log('\n=== OP,12 subindex count per output ===');
for (let i = 0; i < 5; i++) {
  let origMax = -1, genMax = -1;
  orig.rawSendData.forEach(line => {
    const re = new RegExp('OP,12,' + i + ',(\\d+),', 'g');
    let m;
    while ((m = re.exec(line)) !== null) origMax = Math.max(origMax, parseInt(m[1]));
  });
  gen.rawSendData.forEach(line => {
    const re = new RegExp('OP,12,' + i + ',(\\d+),', 'g');
    let m;
    while ((m = re.exec(line)) !== null) genMax = Math.max(genMax, parseInt(m[1]));
  });
  console.log('  O' + (i + 1) + ': orig=' + (origMax + 1) + ' gen=' + (genMax + 1));
}

// Show all OP lines for O1 in order in ORIGINAL
console.log('\n=== ORIGINAL: ALL OP lines containing index 0 ===');
orig.rawSendData.forEach((line, li) => {
  if (/OP,\d+,0[,"]/.test(line)) {
    console.log('L' + li + ': ' + line.trim());
  }
});

// Now same for GENERATED
console.log('\n=== GENERATED: ALL OP lines containing index 0 ===');
gen.rawSendData.forEach((line, li) => {
  if (/OP,\d+,0[,"]/.test(line)) {
    console.log('L' + li + ': ' + line.trim());
  }
});

// Compare total rawSendData line counts
console.log('\n=== Line counts ===');
console.log('Original:', orig.rawSendData.length);
console.log('Generated:', gen.rawSendData.length);

// Check GF in original
console.log('\n=== ORIGINAL: GF lines ===');
orig.rawSendData.forEach((line, li) => {
  if (line.includes('GF,')) console.log('L' + li + ': ' + line.trim());
});
