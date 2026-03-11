const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));

// Count all lines per prefix in original
const prefixCounts = {};
orig.rawSendData.forEach(line => {
  const re = /([A-Z]{2}),/g;
  let m;
  const seen = new Set();
  while ((m = re.exec(line)) !== null) {
    if (!seen.has(m[1])) {
      seen.add(m[1]);
      prefixCounts[m[1]] = (prefixCounts[m[1]] || 0) + 1;
    }
  }
});
console.log('=== Lines containing each prefix (ORIGINAL) ===');
Object.entries(prefixCounts).sort((a,b) => b[1]-a[1]).forEach(([p,c]) => console.log(`  ${p}: ${c} lines`));

// Check LG format
console.log('\n=== LG (LoggingGroup) raw lines for index 0 ===');
orig.rawSendData.forEach((line, li) => {
  if (/LG,\d+,0[,"]/.test(line)) console.log('L' + li + ': ' + line.trim());
});

// Check CS (CANStream) format
console.log('\n=== CS (CANStream) raw lines (all) ===');
orig.rawSendData.forEach((line, li) => {
  if (/CS,/.test(line)) console.log('L' + li + ': ' + line.trim());
});

// Check CO (CANOutput) format - first few
console.log('\n=== CO (CANOutput) raw lines for index 0 ===');
orig.rawSendData.forEach((line, li) => {
  if (/CO,\d+,0[,"]/.test(line)) console.log('L' + li + ': ' + line.trim());
});

// Check CI (CANInput) format - first few
console.log('\n=== CI (CANInput) raw lines for index 0 ===');
orig.rawSendData.forEach((line, li) => {
  if (/CI,\d+,0[,"]/.test(line)) console.log('L' + li + ': ' + line.trim());
});

// Check CK (CANKeypad) format
console.log('\n=== CK (CANKeypad) raw lines (all) ===');
let ckCount = 0;
orig.rawSendData.forEach((line, li) => {
  if (/CK,/.test(line)) { ckCount++; if (ckCount <= 5) console.log('L' + li + ': ' + line.trim()); }
});
console.log(`  Total CK lines: ${ckCount}`);

// Check CF (CANInputFilter) format
console.log('\n=== CF (CANInputFilter) raw lines for index 0 ===');
orig.rawSendData.forEach((line, li) => {
  if (/CF,\d+,0[,"]/.test(line)) console.log('L' + li + ': ' + line.trim());
});

// Check TD (TwoDTable) format
console.log('\n=== TD (TwoDTable) raw lines for index 0 ===');
let tdCount = 0;
orig.rawSendData.forEach((line, li) => {
  if (/TD,\d+,0[,"]/.test(line) || /TD,\d+,0,/.test(line)) {
    tdCount++;
    if (tdCount <= 10) console.log('L' + li + ': ' + line.trim());
  }
});
console.log(`  Total TD lines for index 0: ${tdCount}`);
