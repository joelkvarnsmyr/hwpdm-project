const fs = require('fs');
const template = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));

// Count commands per prefix in the original by simple counting
const raw = template.rawSendData;
const counts = {};
raw.forEach(line => {
  const inner = line.replace(/^\$,6,/, '').replace(/,#\s*$/, '');
  // Count occurrences of prefix patterns
  const re = /([A-Z]{2}),\d/g;
  let m;
  while ((m = re.exec(inner)) !== null) {
    counts[m[1]] = (counts[m[1]] || 0) + 1;
  }
});
console.log('=== COMMAND COUNTS (simple count) ===');
Object.entries(counts).sort((a,b) => b[1]-a[1]).forEach(([p,c]) => console.log(`  ${p}: ${c}`));
const totalSimple = Object.values(counts).reduce((a,b) => a+b, 0);
console.log('  TOTAL:', totalSimple);

// Now test regex parsing
const cmdRe = /([A-Z]{2}(?:,(?:\d+|"[^"]*"))*?,"[^"]*")/g;
const regexCounts = {};
let totalRegex = 0;
raw.forEach(line => {
  const inner = line.replace(/^\$,6,/, '').replace(/,#\s*$/, '');
  let m;
  while ((m = cmdRe.exec(inner)) !== null) {
    const prefix = m[1].substring(0, 2);
    regexCounts[prefix] = (regexCounts[prefix] || 0) + 1;
    totalRegex++;
  }
  cmdRe.lastIndex = 0;
});
console.log('\n=== COMMAND COUNTS (regex parse) ===');
Object.entries(regexCounts).sort((a,b) => b[1]-a[1]).forEach(([p,c]) => {
  const diff = c !== counts[p] ? ` DIFF (simple=${counts[p]})` : '';
  console.log(`  ${p}: ${c}${diff}`);
});
console.log('  TOTAL:', totalRegex);

// Show some CS lines to see format
console.log('\n=== CS line examples ===');
let csCount = 0;
raw.forEach(line => {
  if (line.includes('CS,') && csCount < 3) {
    console.log(line.trim());
    csCount++;
  }
});

// Show a problematic line
console.log('\n=== Test parse on CS line ===');
const csLine = raw.find(l => l.includes('CS,6,'));
if (csLine) {
  const inner = csLine.replace(/^\$,6,/, '').replace(/,#\s*$/, '');
  console.log('Inner:', inner);
  const matches = [];
  let m2;
  while ((m2 = cmdRe.exec(inner)) !== null) {
    matches.push(m2[1]);
  }
  console.log('Matches:', matches.length, matches);
}
