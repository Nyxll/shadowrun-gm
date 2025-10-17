/**
 * Test suite for DAT Parser
 */

import { DATParser } from '../dat-parser.js';

function assert(condition, message) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

function testBasicParsing() {
  console.log('\n=== Test: Basic Line Parsing ===');
  
  const parser = new DATParser();
  
  // Test category header
  const header = parser.parseLine('1-Firearms');
  assert(header.type === 'category_header', 'Should parse category header');
  assert(header.level === 1, 'Should have correct level');
  assert(header.name === 'Firearms', 'Should have correct name');
  assert(header.normalized === 'firearms', 'Should normalize category');
  
  console.log('✓ Category header parsing works');
}

function testHeavyPistolParsing() {
  console.log('\n=== Test: Heavy Pistol Parsing ===');
  
  const parser = new DATParser();
  
  // Set up context
  parser.parseLine('1-Firearms');
  parser.parseLine('2-Pistols');
  parser.parseLine('3-');
  parser.parseLine('4-Heavy pistols');
  
  // Parse Ares Predator
  const line = '5-* Ares Predator                  3|5|15(c)|SA|9M|2.25|3/24hrs|450|.5|None|';
  const result = parser.parseLine(line);
  
  assert(result.type === 'gear_item', 'Should be gear item');
  assert(result.name === 'Ares Predator', 'Should have correct name');
  assert(result.category === 'firearms', 'Should have correct category');
  assert(result.subcategory === 'pistols', 'Should have correct subcategory');
  assert(result.gear_type === 'heavy_pistols', 'Should have correct gear type');
  assert(result.stats.damage === '9M', 'Should parse damage');
  assert(result.stats.conceal === 3, 'Should parse conceal');
  assert(result.stats.ammo === 5, 'Should parse ammo');
  assert(result.stats.mode === 'SA', 'Should parse mode');
  assert(result.stats.cost === 2.25, 'Should parse cost');
  assert(result.hierarchical_path === 'Firearms → Pistols →  → Heavy pistols', 'Should build path');
  assert(result.tags.includes('firearms'), 'Should have firearms tag');
  assert(result.tags.includes('pistols'), 'Should have pistols tag');
  assert(result.tags.includes('heavy_pistols'), 'Should have heavy_pistols tag');
  assert(result.tags.includes('weapon'), 'Should have weapon tag');
  
  console.log('✓ Heavy pistol parsing works');
  console.log(`  Name: ${result.name}`);
  console.log(`  Damage: ${result.stats.damage}`);
  console.log(`  Conceal: ${result.stats.conceal}`);
  console.log(`  Path: ${result.hierarchical_path}`);
  console.log(`  Tags: ${result.tags.join(', ')}`);
}

function testSniperRifleParsing() {
  console.log('\n=== Test: Sniper Rifle Parsing ===');
  
  const parser = new DATParser();
  
  // Set up context
  parser.parseLine('1-Firearms');
  parser.parseLine('2-Rifles');
  parser.parseLine('3-');
  parser.parseLine('4-Sniper rifles');
  
  // Parse a sniper rifle (example stats)
  const line = '5-* Remington 950                  6|5|18|SS|10S|2.5|8/48hrs|2000|2|Scope|';
  const result = parser.parseLine(line);
  
  assert(result.type === 'gear_item', 'Should be gear item');
  assert(result.name === 'Remington 950', 'Should have correct name');
  assert(result.category === 'firearms', 'Should have correct category');
  assert(result.gear_type === 'sniper_rifles', 'Should have correct gear type');
  assert(result.stats.damage === '10S', 'Should parse damage');
  assert(result.stats.conceal === 6, 'Should parse conceal');
  
  console.log('✓ Sniper rifle parsing works');
  console.log(`  Name: ${result.name}`);
  console.log(`  Damage: ${result.stats.damage}`);
  console.log(`  Conceal: ${result.stats.conceal}`);
}

function testArmorParsing() {
  console.log('\n=== Test: Armor Parsing ===');
  
  const parser = new DATParser();
  
  // Set up context
  parser.parseLine('1-Armor');
  parser.parseLine('2-Body Armor');
  parser.parseLine('3-');
  parser.parseLine('4-Light armor');
  
  // Parse armor (Ballistic|Impact|Conceal|Cost|Avail|Street Index|Weight)
  const line = '5-* Lined Coat                     3|2|10|0.5|Always|100|2|';
  const result = parser.parseLine(line);
  
  assert(result.type === 'gear_item', 'Should be gear item');
  assert(result.name === 'Lined Coat', 'Should have correct name');
  assert(result.category === 'armor', 'Should have correct category');
  assert(result.stats.ballistic === 3, 'Should parse ballistic');
  assert(result.stats.impact === 2, 'Should parse impact');
  assert(result.stats.conceal === 10, 'Should parse conceal');
  assert(result.stats.cost === 0.5, 'Should parse cost');
  
  console.log('✓ Armor parsing works');
  console.log(`  Name: ${result.name}`);
  console.log(`  Ballistic: ${result.stats.ballistic}`);
  console.log(`  Impact: ${result.stats.impact}`);
}

function testCyberwareParsing() {
  console.log('\n=== Test: Cyberware Parsing ===');
  
  const parser = new DATParser();
  
  // Set up context
  parser.parseLine('1-Cyberware');
  parser.parseLine('2-Bodyware');
  parser.parseLine('3-');
  parser.parseLine('4-Cyberlimbs');
  
  // Parse cyberware (Essence|Cost|Avail|Street Index|Legality)
  const line = '5-* Cyberarm                       0.5|15|4/48hrs|1.5|Legal|';
  const result = parser.parseLine(line);
  
  assert(result.type === 'gear_item', 'Should be gear item');
  assert(result.name === 'Cyberarm', 'Should have correct name');
  assert(result.category === 'cyberware', 'Should have correct category');
  assert(result.stats.essence === 0.5, 'Should parse essence');
  assert(result.stats.cost === 15, 'Should parse cost');
  
  console.log('✓ Cyberware parsing works');
  console.log(`  Name: ${result.name}`);
  console.log(`  Essence: ${result.stats.essence}`);
  console.log(`  Cost: ${result.stats.cost}`);
}

function testContextTracking() {
  console.log('\n=== Test: Context Tracking ===');
  
  const parser = new DATParser();
  
  // Parse hierarchical structure
  parser.parseLine('1-Firearms');
  assert(parser.currentContext.level1 === 'Firearms', 'Level 1 should be set');
  assert(parser.currentContext.level2 === null, 'Level 2 should be null');
  
  parser.parseLine('2-Pistols');
  assert(parser.currentContext.level1 === 'Firearms', 'Level 1 should persist');
  assert(parser.currentContext.level2 === 'Pistols', 'Level 2 should be set');
  
  parser.parseLine('4-Heavy pistols');
  assert(parser.currentContext.level1 === 'Firearms', 'Level 1 should persist');
  assert(parser.currentContext.level2 === 'Pistols', 'Level 2 should persist');
  assert(parser.currentContext.level4 === 'Heavy pistols', 'Level 4 should be set');
  
  // Change to different subcategory
  parser.parseLine('2-Rifles');
  assert(parser.currentContext.level1 === 'Firearms', 'Level 1 should persist');
  assert(parser.currentContext.level2 === 'Rifles', 'Level 2 should change');
  assert(parser.currentContext.level4 === null, 'Level 4 should be cleared');
  
  console.log('✓ Context tracking works correctly');
}

function testSearchableText() {
  console.log('\n=== Test: Searchable Text Generation ===');
  
  const parser = new DATParser();
  
  parser.parseLine('1-Firearms');
  parser.parseLine('2-Pistols');
  parser.parseLine('4-Heavy pistols');
  
  const line = '5-* Ares Predator                  3|5|15(c)|SA|9M|2.25|3/24hrs|450|.5|None|';
  const result = parser.parseLine(line);
  
  assert(result.searchable_text.includes('Ares Predator'), 'Should include name');
  assert(result.searchable_text.includes('Firearms'), 'Should include category');
  assert(result.searchable_text.includes('Pistols'), 'Should include subcategory');
  assert(result.searchable_text.includes('Heavy pistols'), 'Should include gear type');
  assert(result.searchable_text.includes('damage 9M'), 'Should include damage');
  assert(result.searchable_text.includes('mode SA'), 'Should include mode');
  assert(result.searchable_text.includes('conceal 3'), 'Should include conceal');
  
  console.log('✓ Searchable text generation works');
  console.log(`  Text: ${result.searchable_text}`);
}

function testMultipleItems() {
  console.log('\n=== Test: Multiple Items ===');
  
  const parser = new DATParser();
  
  parser.parseLine('1-Firearms');
  parser.parseLine('2-Pistols');
  parser.parseLine('4-Heavy pistols');
  
  const items = [
    '5-* Ares Predator                  3|5|15(c)|SA|9M|2.25|3/24hrs|450|.5|None|',
    '5-* Colt Manhunter                 3|5|16(c)|SA|9M|2.5|4/24hrs|425|1|Laser Sight|',
    '5-* Ruger Super Warhawk            3|6|16(c)|SS|10M|2.5|4/24hrs|350|1|None|'
  ];
  
  const results = items.map(line => parser.parseLine(line));
  
  assert(results.length === 3, 'Should parse all items');
  assert(results[0].name === 'Ares Predator', 'First item correct');
  assert(results[1].name === 'Colt Manhunter', 'Second item correct');
  assert(results[2].name === 'Ruger Super Warhawk', 'Third item correct');
  
  // All should have same category/subcategory/gear_type
  results.forEach(result => {
    assert(result.category === 'firearms', 'All should be firearms');
    assert(result.subcategory === 'pistols', 'All should be pistols');
    assert(result.gear_type === 'heavy_pistols', 'All should be heavy pistols');
  });
  
  console.log('✓ Multiple items parsing works');
  console.log(`  Parsed ${results.length} items successfully`);
}

function testDamageComparison() {
  console.log('\n=== Test: Damage Comparison ===');
  
  const parser = new DATParser();
  
  // Heavy pistol
  parser.parseLine('1-Firearms');
  parser.parseLine('2-Pistols');
  parser.parseLine('4-Heavy pistols');
  const heavyPistol = parser.parseLine('5-* Ares Predator                  3|5|15(c)|SA|9M|2.25|3/24hrs|450|.5|None|');
  
  // Sniper rifle
  parser.parseLine('2-Rifles');
  parser.parseLine('4-Sniper rifles');
  const sniperRifle = parser.parseLine('5-* Remington 950                  6|5|18|SS|10S|2.5|8/48hrs|2000|2|Scope|');
  
  console.log('✓ Damage comparison data:');
  console.log(`  Heavy Pistol (${heavyPistol.name}): ${heavyPistol.stats.damage}`);
  console.log(`  Sniper Rifle (${sniperRifle.name}): ${sniperRifle.stats.damage}`);
  console.log(`  Winner: Sniper rifle has higher damage (10S vs 9M)`);
}

// Run all tests
async function runAllTests() {
  console.log('╔════════════════════════════════════════╗');
  console.log('║   DAT Parser Test Suite                ║');
  console.log('╚════════════════════════════════════════╝');
  
  try {
    testBasicParsing();
    testHeavyPistolParsing();
    testSniperRifleParsing();
    testArmorParsing();
    testCyberwareParsing();
    testContextTracking();
    testSearchableText();
    testMultipleItems();
    testDamageComparison();
    
    console.log('\n╔════════════════════════════════════════╗');
    console.log('║   ✓ ALL TESTS PASSED                   ║');
    console.log('╚════════════════════════════════════════╝\n');
    
    return true;
  } catch (error) {
    console.error('\n╔════════════════════════════════════════╗');
    console.error('║   ✗ TEST FAILED                        ║');
    console.error('╚════════════════════════════════════════╝');
    console.error('\nError:', error.message);
    console.error(error.stack);
    return false;
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests().then(success => {
    process.exit(success ? 0 : 1);
  });
}

export { runAllTests };
