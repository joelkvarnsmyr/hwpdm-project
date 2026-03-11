// Known mappings from Joel's configurator:
// O7 HIBEAM_R → func references var 164 = Output 14 HS (LOWBEAM_L)
// O4 BRAKE → func references var 577 = Input 4 (BRAKE)
// O6 TURN_R → func references var 587 = Timer 1 (BLINK TMR)
// O2 WIPER_FST → func references var 602 = Input 9 (WIPER FST)
// O13 HORN → func references var 617 = Input 12 (HORN)
// O3 IGN_COIL → func references var 730 = Generic Function 1 (IGN ON)

// === DECODE OUTPUTS ===
// Output 14 HS (0-indexed: 13) = 164
// If each HS output has N properties and starts at base B:
// B + 13*N = 164
// We need another output data point... but let's try common values.
// PDM25 has properties per output: status, current, voltage, percentageTripped,
// blownCount, underCurrent, onTime, offTime, trippedCount = ~9-10 properties?
// Let's try N=11: B + 13*11 = 164 → B = 164 - 143 = 21
//   O1 HS status = 21, O2 = 32, ..., O14 = 21 + 13*11 = 164 ✓
//   O25 HS status = 21 + 24*11 = 285
// Let's try N=10: B + 13*10 = 164 → B = 164 - 130 = 34
// Let's try N=12: B + 13*12 = 164 → B = 164 - 156 = 8

// === DECODE INPUTS ===
// Input 4 (0-indexed: 3) = 577
// Input 9 (0-indexed: 8) = 602
// Input 12 (0-indexed: 11) = 617
// Check: 602 - 577 = 25, index diff = 8-3 = 5, so 25/5 = 5 properties per input
// Check: 617 - 602 = 15, index diff = 11-8 = 3, so 15/3 = 5 ✓
// Input base: 577 - 3*5 = 562
// I1 = 562, I2 = 567, ..., I16 = 562 + 15*5 = 637
// Input range: 562-641 (16 inputs × 5 properties = 80)

// === DECODE TIMERS ===
// Timer 1 (0-indexed: 0) = 587
// Timer base = 587
// If 5 properties per timer: T1=587, T2=592, T3=597, ..., T30=587+29*5=732
// But wait - does the timer range overlap with input range?
// I16 last property = 637+4 = 641. Timer1 = 587. That's INSIDE the input range!
// So timers must have fewer properties... or the numbering is different.

// Let me reconsider. What if inputs and timers are NOT sequential?
// Input 4 status = 577. Timer 1 status = 587.
// Input range: I1=562 to I16_last=641
// Timer 1 = 587 falls between I5(582) and I6(587)... wait!
// I6 = 562 + 5*5 = 587 = Timer1!?

// That can't be right. Let me recalculate.
// I1=562, I2=567, I3=572, I4=577, I5=582, I6=587...
// But Timer1 = 587 = same as I6!
// Unless my assumption of 5 per input is wrong.

// Wait - let me recheck.
// I4=577, I9=602: diff=25, index diff=5, per-input=5 ✓
// I12=617: 617-577 = 40, index diff=8, 40/8=5 ✓
// I6 would be: 577 + 2*5 = 587 = same as Timer1!

// This means Timer1 is NOT at 587 as a timer. Joel set O6 TURN_R to Timer1,
// but maybe he actually set it to I6 (TURN_R input)?!
// That would make sense: O6 TURN_R → I6 (TURN_R), not Timer1.

// Let me reconsider what Joel actually set:
// O6 TURN_R: I asked for Timer1, but 587 = I6.
// Did Joel accidentally set it to I6 instead of Timer1?
// Or did Joel correctly set TURN_R to its input signal I6?

// Let's assume 587 = I6 (TURN_R input). That fits perfectly.
// I1=562, I2=567, I3=572, I4=577, I5=582, I6=587, I7=592,
// I8=597, I9=602, I10=607, I11=612, I12=617, I13=622,
// I14=627, I15=632, I16=637

console.log('=== INPUT VARIABLE IDs (5 properties per input) ===');
const INPUT_BASE = 562;
for (let i = 1; i <= 16; i++) {
  const id = INPUT_BASE + (i-1)*5;
  console.log(`  I${i} = ${id}`);
}

// === DECODE OUTPUTS ===
// O14 HS (index 13) = 164
// Need to figure out properties per output.
// Try various N values:
for (const N of [8, 9, 10, 11, 12, 13, 14, 15]) {
  const base = 164 - 13*N;
  if (base > 0) {
    const o1 = base;
    const o25_last = base + 24*N + N - 1;
    console.log(`  If N=${N}: HS_BASE=${base}, O1=${o1}, O25_last=${o25_last}`);
  }
}

// === DECODE GF ===
// GF1 (index 0) = 730
// If GF is after inputs (last input I16 = 637+4 = 641):
// Some space between 641 and 730...
// Between inputs and GF there might be: Timers (30), Counters (30), Maths (30)
// Timer range: if timers come after inputs...
// 642 to 729 = 88 IDs before GF1
// If timers have 2 properties: 30*2 = 60 → timers 642-701, then counters?
// If timers have 1 property: 30*1 = 30 → timers 642-671
// Then 672-729 = 58 IDs for maths/counters/other
// 30 counters * 1 = 30 → 672-701, then 702-729 = 28 IDs...
// Actually Maths channels 30*1 = 30 → 702-731. GF1=730... close but not exact.

// Let me try: what if between inputs and GF there are:
// Timers: 30 × 2 = 60 (642-701)
// Counters: 30 × 1 = 30 (702-731)
// Then GF1 = 732? But we have 730.
// Or Timers: 30 × 2 = 60 (642-701)
// Maths: 30 × (unknown)
// Actually, maybe timers have properties: currentValue, status = 2 each
// 30*2 = 60 → 642 to 701
// Counters: 30*1 = 30 → 702 to 731
// Hmm, GF1 = 730 falls in counter range if counters start at 702 with 1 property each
// Counter 29 (0-indexed 28) = 702+28 = 730 = GF1? That's a collision.

// Let me try different timer property count:
// Timers 30*3=90: 642-731. GF starts at 732. But GF1=730, before timers end!
// Timers 30*2=60: 642-701.
// Maths 30*1=30: 702-731. GF1=730 inside maths range!
// Counters?

// Actually the ordering might be different. Let me try:
// After inputs (642+):
// LoggingGroups, Timers, Counters, MathsChannels, GenericFunctions, SensorCal...
// Following the rawSendData section order: LG, TI, CT, MC, GF
// LG: 30 × 1 = 30 → 642-671
// TI: 30 × 2 = 60 → 672-731. GF1=730... Timer30 would be 672+29*2=730! Still collision.

// Hmm, let me try TI with 3 properties: 30*3=90 → 672-761. GF1 at 730 inside timer range.
// Timer 20 (0-idx 19): 672+19*3=729. Timer 20 prop 1 = 730 = GF1? No.

// Actually wait. What if property 0 = "Status" and that's what "2" means in the function?
// The function format is: [7, "1", "VAR_ID", "2", "10", "1", "1"]
// Where "2" is the PROPERTY selector. "2" might mean "Status" property.
// So the variable ID might be a BASE id, and property 2 is an offset.

// In that case, variable 730 property 2 = the Status of variable 730.
// And variable 577 property 2 = the Status of variable 577.
// The ID itself is just the variable (not property-offset).

// If properties are accessed by the "2" field, then the variable IDs are:
// NOT spaced by property count. Each variable has ONE id.
// Then Input spacing = 5 might mean something else...

// Wait, I4=577, I9=602, diff=25, 5 apart → spacing is 5 per input.
// But if each variable has 1 ID, why spacing of 5?
// Because each INPUT has 5 PROPERTIES, each with its own ID!
// I4_prop0 = 577, I4_prop1 = 578, I4_prop2 = 579, I4_prop3 = 580, I4_prop4 = 581
// And in the function, "577" with property "2" means: variable I4, show property 2 (Status)
// But that means the "2" in the function is redundant with the property offset...

// No, I think "2" in the function means "this is a Status comparison" and the
// variable ID is the BASE id for the variable (not the specific property).
// The 5-spacing just happens because each input occupies 5 slots in the id space.

// OK new theory: IDs are allocated sequentially, 5 per input:
// I4 base = 577, properties: [577, 578, 579, 580, 581]
// In the function, we reference 577 (base ID) and "2" selects Status property.

// For outputs: O14 HS base = 164, with N properties each.
// For GF: GF1 base = 730.

// I need the Timer ID. Unfortunately O6 was set to I6, not Timer1.
// But I can calculate:
// After HS outputs (25 × N) and before LS outputs...
// Actually, let me just compute the mapping assuming:
// - Constants: 0-1 (False=0, True=1)
// - Global properties: a few
// - HS Outputs: 25 × N
// - LS Outputs: 25 × N
// - Inputs: 16 × 5 starting at 562
// - Then: LG, TI, CT, MC, GF

// O14 HS = 164. If HS starts at base B with N per output:
// B + 13*N = 164
// HS range ends at B + 25*N - 1
// LS starts at B + 25*N with same N per output
// LS range ends at B + 50*N - 1
// Inputs start at 562 = B + 50*N + (global props between LS and inputs)

// Let me try N=11:
// B = 164 - 143 = 21
// HS: 21 to 21+275-1 = 295
// LS: 296 to 296+275-1 = 570
// Input start = 562, but LS ends at 570. That overlaps!

// N=10:
// B = 164 - 130 = 34
// HS: 34 to 34+250-1 = 283
// LS: 284 to 284+250-1 = 533
// Gap: 533 to 562 = 29 slots. Could be globals or other.

// N=9:
// B = 164 - 117 = 47
// HS: 47 to 47+225-1 = 271
// LS: 272 to 272+225-1 = 496
// Gap: 496 to 562 = 66 slots.

// N=12:
// B = 164 - 156 = 8
// HS: 8 to 8+300-1 = 307
// LS: 308 to 308+300-1 = 607
// But input start is 562, which is inside LS range! Overlap!

// N=11 with different base... or maybe LS has different N?
// Or maybe HS and LS share the same ID block?

// Let me try: what if there are NO separate LS IDs?
// Just HS outputs with N properties each:
// N=11: base=21, range 21-295. Then inputs at 562.
// Gap: 296 to 561 = 266 slots. That's for LS(275) + a few.
// 25*11 = 275 for LS starting at 296 → 296 to 570.
// But inputs start at 562, inside LS range again.

// N=10: base=34, HS range 34-283. LS: 284-533. Inputs: 562+
// Gap between LS end (533) and inputs (562) = 29 slots.

// That seems reasonable. N=10 per output (HS and LS).
// 29 gap slots could be: MPDMDevice (16), pinManager, etc.

console.log('\n=== TRYING N=10 per output ===');
const HS_BASE = 34;
const LS_BASE = 34 + 250; // = 284
const INPUT_BASE2 = 562;
const N_OUT = 10;
const N_INP = 5;

console.log('HS Output IDs:');
for (let i = 1; i <= 25; i++) {
  console.log(`  O${i} HS = ${HS_BASE + (i-1)*N_OUT}`);
}
console.log(`\nLS Output IDs:`);
for (let i = 1; i <= 25; i++) {
  console.log(`  O${i} LS = ${LS_BASE + (i-1)*N_OUT}`);
}

// Verify: O14 HS should be 164
console.log(`\nVerification: O14 HS = ${HS_BASE + 13*N_OUT} (expected 164): ${HS_BASE + 13*N_OUT === 164 ? 'OK' : 'FAIL'}`);

// Now figure out what's between inputs (last=641) and GF1 (730)
// Gap: 642 to 729 = 88 slots
// LG: 30 items, TI: 30 items, CT: 30 items → 90 items
// If each has 1 property: 90 slots. 642+90=732. GF1=730 → off by 2.
// If LG has 0: TI(30)+CT(30) = 60. 642+60=702. GF1=730 → off by 28.
// Hmm. Let me try: LG=0 properties (just config, no runtime value)
// TI: 30 × 2 = 60 → 642-701
// CT: 30 × 1 = 30 → 702-731
// GF1 = 730 = Counter 29 (702+28). Collision!

// Try: TI: 30 × 1 = 30 → 642-671
// CT: 30 × 2 = 60 → 672-731
// GF1 = 730 = Counter index 29, prop 0 (672+29*2=730). Collision again!

// Try: after inputs, LG has variables?
// LG: 30 × 1 = 30 → 642-671
// TI: 30 × 1 = 30 → 672-701
// CT: 30 × 1 = 30 → 702-731
// MC: 30 × 1... but GF1=730 is before MC
// GF1=730 falls inside CT range (702-731) as CT[28]

// Unless the order is different. What if:
// LG: no variables (0)
// TI: 30 × 2 = 60 → 642-701
// MC: 30 × ?
// GF: 30 × 1, GF1=730
// CT: after GF

// 702 to 729 = 28 slots before GF1=730
// If MC has 28/30 → less than 1 per MC. Doesn't work.

// What if timers have 3 properties (currentValue, status, ?)?
// TI: 30 × 3 = 90 → 642-731
// Timer 30 = 642+29*3 = 729. GF1=730 = right after timers!
// Then GF base = 732? But GF1=730...

// TI: 30*3=90 → 642-731 means Timer1=642, Timer30=729(last prop)
// If GF1 = 730 = 642+90-2? No...

// Hmm, TI: 30 × 3 → Timer1 base=642, Timer30 base=642+29*3=729
// Timer30 last prop = 731. GF1 = 732? But we have 730.

// What if timers have 2 properties but counters come BEFORE timers?
// LG: 0, CT: 30×1=30 → 642-671, TI: 30×2=60 → 672-731
// Timer1=672, GF1=730 inside timer range.

// OK let me try yet another ordering.
// What if there's no gap between LS and inputs?
// N=10: LS ends at 533. What if there are MORE outputs?
// PDM35 has 35 outputs. PDM25 allocates 35 slots too (we saw 35 entries in arrays).
// 35 HS × 10 = 350 → 34-383
// 35 LS × 10 = 350 → 384-733
// Input base = 734? But we know inputs start at 562. NOPE.

// What if outputs have fewer properties? N=8?
// B = 164 - 13*8 = 164-104 = 60
// HS 25×8=200: 60-259
// LS 25×8=200: 260-459
// Gap: 460-561 = 102 slots before inputs
// That's a lot of gap.

// What if N varies? Let me look at the JSON structure for OutputHS.
// Properties: lowFuse, highFuse, peakFuse, peakFuseTime, enabled, stayOnTime,
// turnOnDelay, clearTime, retries, tripMode, trippedCount, current, voltage,
// status, percentageTripped, blownCount, underCurrent, onTime, offTime,
// offset, scaler, testOutput, PWMFrequency, PWMSoftStartEnable, etc.
// That's way more than 10. But maybe only runtime values get IDs?
// Runtime: status, current, voltage, percentageTripped, trippedCount,
// blownCount, underCurrent, onTime, offTime = 9 properties
// Plus maybe testOutput = 10?

// I'm going in circles. Let me just use the 4 known data points
// and build a lookup table by brute-forcing the most likely mapping.

// KNOWN: O14 HS status = 164,
// Let me check if properties per output = 10 works for ALL scenarios
const GF1_ID = 730;

// With N=10, HS_BASE=34:
// HS: 34 to 283 (25 outputs × 10)
// LS: 284 to 533 (25 outputs × 10)
// Gap: 534 to 561 = 28 mystery slots
// Inputs: 562 to 641 (16 × 5 = 80)
// Post-input: 642 to 729 = 88 slots
// GF1 = 730

// 88 slots for: LG(30), TI(30), CT(30)
// If all have different sizes...
// LG: 30×0=0, TI: 30×2=60 → 642-701, CT: 30×1=30 → 702-731
// GF1=730... Counter[28] = 702+28 = 730. Hmm.

// OR: property-count varies differently.
// LG: 0, TI: 30×1=30 → 642-671, CT: 30×1=30 → 672-701, MC: 30×1=30 → 702-731
// GF1=730 = MC[28] = 702+28 = 730. Still collision.

// What if GF has base 730 and MC is elsewhere?
// Hmm, the section order in rawSendData was: LG, TI, CT, MC, GF
// So GF comes AFTER MC. Let me count:
// If each section variable count:
// LG: 0 (just config, no runtime vars)
// TI: 30×1=30 → 642-671
// CT: 30×1=30 → 672-701
// MC: 30×1=30 → 702-731
// GF: 30×1=30 → 732-761
// But GF1=730, which is 732-2... doesn't match.

// What if some items have 0 variables?
// Let me try: CT has 30×1 but only values, no status.
// LG: 0 vars
// TI: 30×2=60 → 642-701 (currentValue, status)
// CT: 30×1=30 → 702-731 (currentValue only)
// MC: 0 extra (they're functions with values used elsewhere)
// GF: GF1 = 730 falls inside CT. STILL collision.

// WAIT. I just realized: what if the gap before inputs isn't 534-561?
// What if N is NOT 10?

// Let me try completely differently. What if I solve for N using TWO constraints?
// Constraint 1: O14 HS (index 13) base ID = 164
// Constraint 2: I1 base ID = 562
// Assume: HS(25×N) + LS(25×N) + gap = 562 - HS_BASE
// HS_BASE = 164 - 13N
// 164 - 13N + 50N + gap = 562
// 164 + 37N + gap = 562
// 37N + gap = 398
// For N=10: gap=28. For N=11: gap=-9 (impossible).
// So N ≤ 10.
// For N=9: gap=65. For N=8: gap=102. For N=7: gap=139.

// N=10 gives the smallest reasonable gap (28). Let's go with N=10.
// The 28 gap slots (534-561) might be MPDMDevice (16 devices × 1-2 props).

console.log('\n=== FINAL VARIABLE MAP (N=10 per output, N=5 per input) ===');
console.log(`HS base: ${HS_BASE} (O1=${HS_BASE}, O14=${HS_BASE+13*N_OUT}, O25=${HS_BASE+24*N_OUT})`);
console.log(`LS base: ${LS_BASE} (O1 LS=${LS_BASE}, O25 LS=${LS_BASE+24*N_OUT})`);
console.log(`Input base: ${INPUT_BASE2} (I1=${INPUT_BASE2}, I4=${INPUT_BASE2+3*N_INP}, I16=${INPUT_BASE2+15*N_INP})`);
console.log(`Post-input to GF1: ${INPUT_BASE2+16*N_INP} to ${GF1_ID} = ${GF1_ID - (INPUT_BASE2+16*N_INP)} slots`);
console.log(`GF1 = ${GF1_ID}`);
