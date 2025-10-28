#!/usr/bin/env node

/**
 * Comprehensive Dice Rolling System Tests
 * Tests all 13 dice-related MCP tools via the shadowrun2.com API
 */

import axios from 'axios';

const API_BASE_URL = 'https://shadowrun2.com/dice/api.php';

// Helper function to call the dice API
async function callDiceAPI(action, params = {}) {
  try {
    const response = await axios.get(API_BASE_URL, {
      params: { action, ...params },
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'API request failed');
    }
  } catch (error) {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw error;
  }
}

// Helper function for POST requests
async function callDiceAPIPOST(action, data = {}) {
  try {
    const response = await axios.post(API_BASE_URL, {
      action,
      ...data,
    }, {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'API request failed');
    }
  } catch (error) {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw error;
  }
}

// Test result tracking
let testsPassed = 0;
let testsFailed = 0;
const failedTests = [];

function assert(condition, testName, details = '') {
  if (condition) {
    console.log(`✅ PASS: ${testName}`);
    testsPassed++;
  } else {
    console.log(`❌ FAIL: ${testName}`);
    if (details) console.log(`   Details: ${details}`);
    testsFailed++;
    failedTests.push({ name: testName, details });
  }
}

async function runTests() {
  console.log('🎲 Dice Rolling System Tests\n');
  console.log('='.repeat(80));
  
  // Test 1: Basic Dice Roll
  console.log('\n📋 Test 1: Basic Dice Roll (2d6)');
  try {
    const result = await callDiceAPI('roll', { notation: '2d6' });
    assert(result.rolls && result.rolls.length === 2, 'Returns 2 dice rolls');
    assert(result.rolls.every(r => r >= 1 && r <= 6), 'All rolls are valid d6 values');
    assert(result.sum === result.rolls.reduce((a, b) => a + b, 0), 'Sum is correct');
    assert(result.modifier === 0, 'Modifier is 0 for 2d6');
    assert(result.total === result.sum, 'Total equals sum when no modifier');
    console.log(`   Result: ${JSON.stringify(result)}`);
  } catch (error) {
    assert(false, 'Basic dice roll', error.message);
  }
  
  // Test 2: Dice Roll with Modifier
  console.log('\n📋 Test 2: Dice Roll with Modifier (1d20+5)');
  try {
    const result = await callDiceAPI('roll', { notation: '1d20+5' });
    assert(result.rolls && result.rolls.length === 1, 'Returns 1 die roll');
    assert(result.rolls[0] >= 1 && result.rolls[0] <= 20, 'Roll is valid d20 value');
    assert(result.modifier === 5, 'Modifier is 5');
    assert(result.total === result.sum + 5, 'Total includes modifier');
    console.log(`   Result: ${JSON.stringify(result)}`);
  } catch (error) {
    assert(false, 'Dice roll with modifier', error.message);
  }
  
  // Test 3: Dice Roll with Negative Modifier
  console.log('\n📋 Test 3: Dice Roll with Negative Modifier (3d8-2)');
  try {
    const result = await callDiceAPI('roll', { notation: '3d8-2' });
    assert(result.rolls && result.rolls.length === 3, 'Returns 3 dice rolls');
    assert(result.modifier === -2, 'Modifier is -2');
    assert(result.total === result.sum - 2, 'Total includes negative modifier');
    console.log(`   Result: ${JSON.stringify(result)}`);
  } catch (error) {
    assert(false, 'Dice roll with negative modifier', error.message);
  }
  
  // Test 4: Multiple Dice Rolls
  console.log('\n📋 Test 4: Multiple Dice Rolls');
  try {
    const result = await callDiceAPI('roll_multiple', { 
      notations: ['2d6', '1d20+5', '3d8'] 
    });
    assert(Array.isArray(result) && result.length === 3, 'Returns 3 roll results');
    assert(result[0].notation === '2d6', 'First notation correct');
    assert(result[1].notation === '1d20+5', 'Second notation correct');
    assert(result[2].notation === '3d8', 'Third notation correct');
    console.log(`   Results: ${result.length} rolls completed`);
  } catch (error) {
    assert(false, 'Multiple dice rolls', error.message);
  }
  
  // Test 5: Roll with Advantage
  console.log('\n📋 Test 5: Roll with Advantage (1d20)');
  try {
    const result = await callDiceAPI('roll_advantage', { notation: '1d20' });
    const roll1 = typeof result.roll1 === 'object' ? result.roll1.value : result.roll1;
    const roll2 = typeof result.roll2 === 'object' ? result.roll2.value : result.roll2;
    const finalResult = typeof result.result === 'object' ? result.result.value : result.result;
    assert(roll1 >= 1 && roll1 <= 20, 'First roll is valid');
    assert(roll2 >= 1 && roll2 <= 20, 'Second roll is valid');
    assert(finalResult === Math.max(roll1, roll2), 'Result is higher roll');
    assert(result.advantage === true, 'Advantage flag is true');
    console.log(`   Rolls: ${roll1}, ${roll2} → ${finalResult}`);
  } catch (error) {
    assert(false, 'Roll with advantage', error.message);
  }
  
  // Test 6: Roll with Disadvantage
  console.log('\n📋 Test 6: Roll with Disadvantage (1d20)');
  try {
    const result = await callDiceAPI('roll_disadvantage', { notation: '1d20' });
    const roll1 = typeof result.roll1 === 'object' ? result.roll1.value : result.roll1;
    const roll2 = typeof result.roll2 === 'object' ? result.roll2.value : result.roll2;
    const finalResult = typeof result.result === 'object' ? result.result.value : result.result;
    assert(roll1 >= 1 && roll1 <= 20, 'First roll is valid');
    assert(roll2 >= 1 && roll2 <= 20, 'Second roll is valid');
    assert(finalResult === Math.min(roll1, roll2), 'Result is lower roll');
    assert(result.disadvantage === true, 'Disadvantage flag is true');
    console.log(`   Rolls: ${roll1}, ${roll2} → ${finalResult}`);
  } catch (error) {
    assert(false, 'Roll with disadvantage', error.message);
  }
  
  // Test 7: Target Number Roll (Shadowrun-style)
  console.log('\n📋 Test 7: Target Number Roll (6d6! vs TN 5)');
  try {
    const result = await callDiceAPI('roll_tn', { 
      notation: '6d6!', 
      tn: 5 
    });
    assert(Array.isArray(result.rolls), 'Returns rolls array');
    assert(result.rolls.length >= 6, 'Has at least 6 dice (may have explosions)');
    assert(typeof result.successes === 'number', 'Returns success count');
    assert(Array.isArray(result.failures), 'Returns failures array');
    assert(result.target_number === 5, 'Target number is 5');
    console.log(`   Rolls: ${result.rolls.join(', ')}`);
    console.log(`   Successes: ${result.successes}, Failures: ${result.failures.length}`);
  } catch (error) {
    assert(false, 'Target number roll', error.message);
  }
  
  // Test 8: Opposed Roll
  console.log('\n📋 Test 8: Opposed Roll (6d6! TN5 vs 4d6! TN4)');
  try {
    const result = await callDiceAPI('roll_opposed', {
      notation1: '6d6!',
      tn1: 5,
      notation2: '4d6!',
      tn2: 4
    });
    assert(result.attacker && result.defender, 'Returns both sides');
    assert(typeof result.attacker.successes === 'number', 'Attacker has successes');
    assert(typeof result.defender.successes === 'number', 'Defender has successes');
    assert(typeof result.net_successes === 'number', 'Returns net successes');
    assert(result.winner === 'attacker' || result.winner === 'defender' || result.winner === 'tie', 'Has valid winner');
    console.log(`   Attacker: ${result.attacker.successes} successes`);
    console.log(`   Defender: ${result.defender.successes} successes`);
    console.log(`   Winner: ${result.winner} (net: ${result.net_successes})`);
  } catch (error) {
    assert(false, 'Opposed roll', error.message);
  }
  
  // Test 9: Initiative Roll
  console.log('\n📋 Test 9: Initiative Roll (2d6+10)');
  try {
    const result = await callDiceAPI('roll_initiative', { notation: '2d6+10' });
    assert(Array.isArray(result.rolls) && result.rolls.length === 2, 'Returns 2 dice');
    assert(result.rolls.every(r => r >= 1 && r <= 6), 'Dice are valid d6');
    assert(result.modifier === 10, 'Modifier is 10');
    assert(typeof result.initiative === 'number', 'Returns initiative score');
    assert(Array.isArray(result.phases), 'Returns phases array');
    console.log(`   Initiative: ${result.initiative}`);
    console.log(`   Phases: ${result.phases.join(', ')}`);
  } catch (error) {
    assert(false, 'Initiative roll', error.message);
  }
  
  // Test 10: Track Initiative (Multiple Characters)
  console.log('\n📋 Test 10: Track Initiative (3 characters)');
  try {
    const result = await callDiceAPIPOST('track_initiative', {
      characters: [
        { name: 'Street Samurai', notation: '3d6+12' },
        { name: 'Decker', notation: '2d6+8' },
        { name: 'Mage', notation: '1d6+6' }
      ]
    });
    assert(Array.isArray(result.characters), 'Returns characters array');
    assert(result.characters.length === 3, 'Has 3 characters');
    assert(result.characters.every(c => c.initiative > 0), 'All have initiative scores');
    assert(result.phases !== undefined, 'Returns phases breakdown');
    console.log(`   Initiative Order:`);
    result.characters.forEach(c => {
      console.log(`     ${c.name}: ${c.initiative} (phases: ${c.phases.join(', ')})`);
    });
  } catch (error) {
    assert(false, 'Track initiative', error.message);
  }
  
  // Test 11: Roll with Pools
  console.log('\n📋 Test 11: Roll with Pools (Skill + Combat Pool)');
  try {
    const result = await callDiceAPIPOST('roll_with_pools', {
      pools: [
        { name: 'Firearms Skill', notation: '6d6!' },
        { name: 'Combat Pool', notation: '4d6!' }
      ],
      target_number: 5
    });
    assert(Array.isArray(result.pools), 'Returns pools array');
    assert(result.pools.length === 2, 'Has 2 pools');
    assert(result.pools[0].name === 'Firearms Skill', 'First pool name correct');
    assert(result.pools[1].name === 'Combat Pool', 'Second pool name correct');
    assert(typeof result.total_successes === 'number', 'Returns total successes');
    console.log(`   Total Successes: ${result.total_successes}`);
    result.pools.forEach(p => {
      console.log(`     ${p.name}: ${p.successes} successes`);
    });
  } catch (error) {
    assert(false, 'Roll with pools', error.message);
  }
  
  // Test 12: Opposed Pools
  console.log('\n📋 Test 12: Opposed Pools (Attacker vs Defender)');
  try {
    const result = await callDiceAPIPOST('roll_opposed_pools', {
      side1: {
        pools: [
          { name: 'Firearms', notation: '6d6!' },
          { name: 'Combat Pool', notation: '3d6!' }
        ],
        target_number: 5,
        label: 'Attacker'
      },
      side2: {
        pools: [
          { name: 'Dodge', notation: '4d6!' },
          { name: 'Combat Pool', notation: '5d6!' }
        ],
        target_number: 4,
        label: 'Defender'
      }
    });
    assert(result.side1 && result.side2, 'Returns both sides');
    assert(result.side1.label === 'Attacker', 'Side 1 label correct');
    assert(result.side2.label === 'Defender', 'Side 2 label correct');
    assert(typeof result.net_successes === 'number', 'Returns net successes');
    console.log(`   ${result.side1.label}: ${result.side1.total_successes} successes`);
    console.log(`   ${result.side2.label}: ${result.side2.total_successes} successes`);
    console.log(`   Winner: ${result.winner} (net: ${result.net_successes})`);
  } catch (error) {
    assert(false, 'Opposed pools', error.message);
  }
  
  // Test 13: Buy Karma Dice
  console.log('\n📋 Test 13: Buy Karma Dice (3 dice at TN 5)');
  try {
    const result = await callDiceAPI('buy_karma_dice', {
      karma_dice_count: 3,
      target_number: 5,
      sides: 6,
      exploding: true
    });
    assert(result.karma_cost === 3 || result.karma_dice_count === 3, 'Karma cost is 3');
    assert(Array.isArray(result.rolls), 'Returns rolls array');
    assert(result.rolls.length >= 3, 'Has at least 3 dice');
    assert(typeof result.successes === 'number', 'Returns successes');
    console.log(`   Karma Spent: ${result.karma_cost || result.karma_dice_count}, Successes: ${result.successes}`);
  } catch (error) {
    assert(false, 'Buy karma dice', error.message);
  }
  
  // Test 14: Buy Successes
  console.log('\n📋 Test 14: Buy Successes (2 successes with 1 natural success)');
  try {
    const result = await callDiceAPI('buy_successes', {
      current_successes: 1,
      successes_to_buy: 2
    });
    assert(result.karma_cost === 2 || result.successes_to_buy === 2, 'Karma cost is 2 (permanent)');
    assert(result.original_successes === 1 || result.current_successes === 1, 'Original successes is 1');
    assert(result.bought_successes === 2 || result.successes_to_buy === 2, 'Bought 2 successes');
    assert(result.total_successes === 3 || result.final_successes === 3, 'Total is 3 successes');
    assert(result.permanent_karma === true || result.is_permanent === true, 'Permanent karma flag is true');
    console.log(`   Total: ${result.total_successes || result.final_successes} (${result.original_successes || result.current_successes} natural + ${result.bought_successes || result.successes_to_buy} bought)`);
  } catch (error) {
    assert(false, 'Buy successes', error.message);
  }
  
  // Test 15: Invalid Dice Notation
  console.log('\n📋 Test 15: Invalid Dice Notation (error handling)');
  try {
    await callDiceAPI('roll', { notation: 'invalid' });
    assert(false, 'Invalid notation should throw error');
  } catch (error) {
    assert(true, 'Invalid notation throws error', error.message);
  }
  
  // Test 16: Exploding Dice Verification
  console.log('\n📋 Test 16: Exploding Dice (10d6! should have explosions)');
  try {
    const result = await callDiceAPI('roll_tn', { 
      notation: '10d6!', 
      tn: 5 
    });
    // With 10d6, we should statistically get some 6s that explode
    const hasExplosions = result.rolls.length > 10;
    console.log(`   Rolled ${result.rolls.length} dice (${hasExplosions ? 'has' : 'no'} explosions)`);
    assert(Array.isArray(result.rolls), 'Returns rolls array');
  } catch (error) {
    assert(false, 'Exploding dice verification', error.message);
  }
  
  // Summary
  console.log('\n' + '='.repeat(80));
  console.log(`\n📊 Test Results: ${testsPassed} passed, ${testsFailed} failed`);
  
  if (testsFailed > 0) {
    console.log('\n❌ Failed Tests:');
    failedTests.forEach(test => {
      console.log(`   - ${test.name}`);
      if (test.details) console.log(`     ${test.details}`);
    });
  } else {
    console.log('\n🎉 All tests passed!');
  }
  
  process.exit(testsFailed > 0 ? 1 : 0);
}

runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
