const fs = require('fs');
const d = JSON.parse(fs.readFileSync('Elton.HWPDM', 'utf8'));
const raw = d.rawSendData;

// Group commands by prefix
const groups = {};
raw.forEach(line => {
  const m = line.match(/^\$,6,([A-Z]+),/);
  if (m) {
    const prefix = m[1];
    if (!groups[prefix]) groups[prefix] = [];
    groups[prefix].push(line);
  }
});

// Show count per prefix and first 5 examples
Object.keys(groups).sort().forEach(k => {
  console.log(`\n${k}: ${groups[k].length} commands`);
  groups[k].slice(0, 5).forEach(l => console.log('  ' + l.trim()));
});
