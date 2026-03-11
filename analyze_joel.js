const fs = require('fs');
const joel = JSON.parse(fs.readFileSync('Elton_v6.2 (joel har lagtin).HWPDM', 'utf8'));

// Show ALL configured outputs with their function arrays
console.log('=== ALL JOEL CONFIGURED OUTPUTS ===');
joel.OutputHS.forEach((o, i) => {
  if (o.enabled && o.label) {
    console.log(`O${i+1} ${o.label}:`);
    console.log(`  function: ${JSON.stringify(o.function)}`);
    console.log(`  functionInfix: ${JSON.stringify(o.functionInfix)}`);
  }
});

// Now check the rawSendData for OP,12 (function) for O4 BRAKE (index 3)
console.log('\n=== JOEL rawSendData: OP,12 for O4 BRAKE (idx=3) ===');
joel.rawSendData.forEach(line => {
  const re = /OP,12,3,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    console.log(`  OP,12,3,${m[1]} = "${m[2]}"`);
  }
});

// And OP,19 (infix) for O4
console.log('\n=== JOEL rawSendData: OP,19 for O4 BRAKE (idx=3) ===');
joel.rawSendData.forEach(line => {
  const re = /OP,19,3,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    if (m[2] !== '0') console.log(`  OP,19,3,${m[1]} = "${m[2]}"`);
  }
});

// Check O2 WIPER FST too
console.log('\n=== JOEL rawSendData: OP,12 for O2 WIPER FST (idx=1) ===');
joel.rawSendData.forEach(line => {
  const re = /OP,12,1,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    console.log(`  OP,12,1,${m[1]} = "${m[2]}"`);
  }
});

console.log('\n=== JOEL rawSendData: OP,19 for O2 WIPER FST (idx=1) ===');
joel.rawSendData.forEach(line => {
  const re = /OP,19,1,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    if (m[2] !== '0') console.log(`  OP,19,1,${m[1]} = "${m[2]}"`);
  }
});

// Also check what a simple "Always True" looks like in Joel's file
console.log('\n=== JOEL rawSendData: OP,12 for O1 BUSBAR (idx=0) ===');
joel.rawSendData.forEach(line => {
  const re = /OP,12,0,(\d+),"([^"]*)"/g;
  let m;
  while ((m = re.exec(line)) !== null) {
    console.log(`  OP,12,0,${m[1]} = "${m[2]}"`);
  }
});

// Check GF1 in Joel's file
console.log('\n=== JOEL GF1 ===');
console.log('function:', JSON.stringify(joel.GenericFunction[0].function));
console.log('functionInfix:', JSON.stringify(joel.GenericFunction[0].functionInfix));
console.log('enabled:', joel.GenericFunction[0].enabled);
console.log('label:', joel.GenericFunction[0].label);

// Compare total rawSendData line count
console.log('\n=== LINE COUNT ===');
console.log('Joel:', joel.rawSendData.length, 'lines');

// Show an infix example decoded
console.log('\n=== INFIX DECODE ATTEMPT ===');
// O4 BRAKE: function=[7,"1","577","2","10","1","1"]
// What if 577 is a packed value?
// 577 in binary = 1001000001
// Or maybe it's a compound encoding?
// Let me check what "I4 Status Equals True" would look like
// I4 = variable ID 5, Status = ?, Equals = operator
// The configurator shows: Variable1 = I4 Status, Condition = Equals, Variable2 = True
// So the function might encode: [type, var1, condition_id, comparison, var2, ...]
console.log('577 decimal = 0x' + (577).toString(16));
console.log('602 decimal = 0x' + (602).toString(16));

// Let me check if the infix format matches a tree structure
// functionInfix for BRAKE: [["1","577","2","10","1","1"],["2","1"],[0],["2","2"],[0]]
// Entry 0: ["1","577","2","10","1","1"] - root node?
// Entry 1: ["2","1"] - left child?
// Entry 2: [0] - leaf?
// Entry 3: ["2","2"] - right child?
// Entry 4: [0] - leaf?

// Try to find pattern: check all Joel functions
console.log('\n=== ALL JOEL FUNCTION ARRAYS ===');
joel.OutputHS.forEach((o, i) => {
  if (o.enabled && o.label && JSON.stringify(o.function) !== '[1]') {
    console.log(`O${i+1} ${o.label}: func=${JSON.stringify(o.function)}`);
    console.log(`  infix=${JSON.stringify(o.functionInfix)}`);
  }
});
