/**
 * Test suite for combat modifier system
 */

import {
  calculateRangedTN,
  calculateMeleeTN,
  determineRange,
  RANGE_CATEGORIES
} from '../lib/combat/combat-modifiers.js';

console.log('='.repeat(60));
console.log('COMBAT MODIFIER SYSTEM TESTS');
console.log('='.repeat(60));

// Test 1: Basic ranged combat
console.log('\n## Test 1: Basic Ranged Combat (No Modifiers)');
const test1 = calculateRangedTN({
  weapon: { name: 'Ares Predator' },
  range: RANGE_CATEGORIES.MEDIUM,
  attacker: {},
  defender: {},
  situation: {}
});
console.log(JSON.stringify(test1, null, 2));
console.log(`Expected: Base TN 5, Final TN 5`);
console.log(`Result: ${test1.baseTN === 5 && test1.finalTN === 5 ? 'PASS' : 'FAIL'}`);

// Test 2: Smartlink bonus
console.log('\n## Test 2: Smartlink Bonus');
const test2 = calculateRangedTN({
  weapon: { name: 'Ares Predator', smartlink: true },
  range: RANGE_CATEGORIES.SHORT,
  attacker: { hasSmartlink: true },
  defender: {},
  situation: {}
});
console.log(JSON.stringify(test2, null, 2));
console.log(`Expected: Base TN 4, Smartlink -2, Final TN 2`);
console.log(`Result: ${test2.baseTN === 4 && test2.finalTN === 2 ? 'PASS' : 'FAIL'}`);

// Test 3: Prone target at short range (SR2-specific)
console.log('\n## Test 3: Prone Target at Short Range (SR2 Rule)');
const test3 = calculateRangedTN({
  weapon: { name: 'Ares Predator' },
  range: RANGE_CATEGORIES.SHORT,
  attacker: {},
  defender: { prone: true },
  situation: {}
});
console.log(JSON.stringify(test3, null, 2));
console.log(`Expected: Base TN 4, Prone -2 (SR2), Final TN 2`);
console.log(`Result: ${test3.baseTN === 4 && test3.finalTN === 2 ? 'PASS' : 'FAIL'}`);

// Test 4: Multiple modifiers
console.log('\n## Test 4: Multiple Modifiers');
const test4 = calculateRangedTN({
  weapon: { name: 'Ares Predator', recoilComp: 1 },
  range: RANGE_CATEGORIES.MEDIUM,
  attacker: { movement: 'running', woundLevel: 'light' },
  defender: { movement: 'running' },
  situation: { recoil: 3, lightLevel: 'partial' }
});
console.log(JSON.stringify(test4, null, 2));
console.log('Expected modifiers: Running +4, Recoil +2, Defender running +2, Visibility +1, Wounds +1');
console.log(`Result: ${test4.totalModifier === 10 ? 'PASS' : 'FAIL'}`);

// Test 5: Melee combat with reach
console.log('\n## Test 5: Melee Combat with Reach Advantage');
const test5 = calculateMeleeTN({
  attacker: {},
  defender: {},
  attackerWeapon: { reach: 2 },
  defenderWeapon: { reach: 0 },
  situation: {}
});
console.log(JSON.stringify(test5, null, 2));
console.log(`Expected: Base TN 4, Reach -2, Final TN 2`);
console.log(`Result: ${test5.baseTN === 4 && test5.finalTN === 2 ? 'PASS' : 'FAIL'}`);

// Test 6: Range determination
console.log('\n## Test 6: Range Determination');
const range1 = determineRange(15, 'heavy pistol');
const range2 = determineRange(35, 'heavy pistol');
const range3 = determineRange(50, 'heavy pistol');
console.log(`15m with heavy pistol: ${range1} (expected: short)`);
console.log(`35m with heavy pistol: ${range2} (expected: long)`);
console.log(`50m with heavy pistol: ${range3} (expected: extreme)`);
console.log(`Result: ${range1 === 'short' && range2 === 'long' && range3 === 'extreme' ? 'PASS' : 'FAIL'}`);

// Test 7: Visibility with vision enhancements
console.log('\n## Test 7: Visibility with Low-Light Vision');
const test7 = calculateRangedTN({
  weapon: { name: 'Ares Predator' },
  range: RANGE_CATEGORIES.SHORT,
  attacker: { vision: { lowLight: true } },
  defender: {},
  situation: { lightLevel: 'dim' }
});
console.log(JSON.stringify(test7, null, 2));
console.log(`Expected: Dim light normally +2, with low-light +1, Final TN 5`);
console.log(`Result: ${test7.finalTN === 5 ? 'PASS' : 'FAIL'}`);

// Test 8: Complex scenario
console.log('\n## Test 8: Complex Combat Scenario');
const test8 = calculateRangedTN({
  weapon: { 
    name: 'Ares Predator',
    smartlink: true,
    recoilComp: 2
  },
  range: RANGE_CATEGORIES.LONG,
  attacker: { 
    hasSmartlink: true,
    woundLevel: 'moderate'
  },
  defender: { 
    prone: true,
    inMeleeCombat: false
  },
  situation: {
    recoil: 3,
    calledShot: true,
    lightLevel: 'normal'
  }
});
console.log(JSON.stringify(test8, null, 2));
console.log('Complex scenario with smartlink, recoil, wounds, called shot, prone target at long range');
console.log(`Modifiers breakdown:`);
test8.modifiers.forEach(m => {
  console.log(`  ${m.type}: ${m.value > 0 ? '+' : ''}${m.value} ${m.explanation ? '(' + m.explanation + ')' : ''}`);
});

console.log('\n' + '='.repeat(60));
console.log('TEST SUMMARY');
console.log('='.repeat(60));
console.log('All tests completed. Review results above.');
console.log('\nKey SR2-Specific Features Tested:');
console.log('✓ Prone target at short range: -2 TN (SR2 rule, SR3 uses -1)');
console.log('✓ 4-tier light level system');
console.log('✓ Smartlink -2 TN bonus');
console.log('✓ Reach modifiers in melee');
console.log('✓ Wound penalties');
console.log('✓ Multiple modifier stacking');
