const fs = require('fs');
const orig = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const raw = orig.rawSendData;

// Find the line index where each section starts
const sectionStarts = {};
const prefixOrder = [];
let lastPrefix = null;

raw.forEach((line, li) => {
  // Get the first command prefix on this line
  const m = line.match(/\$,6,([A-Z]{2}),/);
  if (m) {
    const prefix = m[1];
    if (prefix !== lastPrefix) {
      if (!sectionStarts[prefix]) {
        sectionStarts[prefix] = li;
        prefixOrder.push(prefix);
      }
      lastPrefix = prefix;
    }
  }
});

console.log('=== Section start lines (in order) ===');
prefixOrder.forEach(p => {
  console.log(`  ${p}: starts at line ${sectionStarts[p]}`);
});

// Also find where each section ends (next section start - 1)
console.log('\n=== Section ranges ===');
for (let i = 0; i < prefixOrder.length; i++) {
  const start = sectionStarts[prefixOrder[i]];
  const end = i + 1 < prefixOrder.length ? sectionStarts[prefixOrder[i + 1]] - 1 : raw.length - 1;
  const count = end - start + 1;
  console.log(`  ${prefixOrder[i]}: lines ${start}-${end} (${count} lines)`);
}

// But sections interleave! OP has both HS and LS per output.
// Let's check if GL and PH are on the same lines
console.log('\n=== Lines 0-3 ===');
raw.slice(0, 4).forEach((line, i) => console.log(`L${i}: ${line.trim()}`));

// Check where OP ends and IP starts
console.log('\n=== Transition from OP to IP ===');
for (let i = 210; i < 230; i++) {
  if (raw[i]) console.log(`L${i}: ${raw[i].trim().substring(0, 80)}`);
}
