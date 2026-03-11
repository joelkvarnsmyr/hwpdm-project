const fs = require('fs');
const d = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const raw = d.rawSendData;

// Check every section boundary for cross-contamination
const sections = [
  ['GL', 0, 2],
  ['OP', 3, 242],
  ['IP', 243, 283],
  ['LG', 284, 356],
  ['TI', 357, 489],
  ['CT', 490, 666],
  ['MC', 667, 1675],
  ['GF', 1676, 2685],
  ['SC', 2686, 2825],
  ['TD', 2826, 3570],
  ['CK', 3571, 4042],
  ['CF', 4043, 4060],
  ['CI', 4061, 4558],
  ['CO', 4559, 5543],
  ['CS', 5544, 11379],
];

for (let s = 0; s < sections.length - 1; s++) {
  const [name, start, end] = sections[s];
  const [nextName] = sections[s + 1];
  const lastLine = raw[end];
  if (lastLine && lastLine.includes(nextName + ',')) {
    console.log(`BOUNDARY: ${name} line ${end} bleeds into ${nextName}:`);
    console.log('  ' + lastLine.trim().substring(0, 120));
  }
}

// Also check first line of each section
for (const [name, start, end] of sections) {
  const firstLine = raw[start];
  const prevSection = sections.find(s => s[2] === start - 1);
  if (prevSection && firstLine) {
    const prevName = prevSection[0];
    if (firstLine.includes(prevName + ',')) {
      console.log(`BOUNDARY: ${name} line ${start} starts with ${prevName} data:`);
      console.log('  ' + firstLine.trim().substring(0, 120));
    }
  }
}
