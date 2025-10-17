#!/usr/bin/env node
/**
 * PHASE 1 - STEP 1.3: Field Parser Tests
 * 
 * Tests for the FieldParser class
 */

import { FieldParser } from './field-parser.js';
import { CategoryDetector } from './category-detector.js';

const parser = new FieldParser();
const detector = new CategoryDetector();

console.log('='.repeat(80));
console.log('FIELD PARSER TESTS');
console.log('='.repeat(80));
console.log();

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
    passed++;
  } catch (error) {
    console.log(`✗ ${name}`);
    console.log(`  Error: ${error.message}`);
    failed++;
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

function assertEquals(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${expected}, got ${actual}`);
  }
}

function assertDeepEquals(actual, expected, message) {
  const actualStr = JSON.stringify(actual);
  const expectedStr = JSON.stringify(expected);
  if (actualStr !== expectedStr) {
    throw new Error(message || `Expected ${expectedStr}, got ${actualStr}`);
  }
}

// Test 1: Detect item lines
test('Detects item lines correctly', () => {
  assert(parser.isItemLine('3-* Ares Predator II 3|4|10|SA/BF|9M|2.5|5/12hrs|450|1.2|'));
  assert(parser.isItemLine('3-* Ordinary Clothing 8|-|-|-|1|Always|50|.8|'));
  assert(!parser.isItemLine('0-8|Clothing and Armor|7|...'));
  assert(!parser.isItemLine('1-Armor'));
  assert(!parser.isItemLine(''));
});

// Test 2: Parse armor item
test('Parses armor item correctly', () => {
  const line = '3-* Ordinary Clothing              8|-|-|-|1|Always|50|.8|';
  const schema = detector.buildSchema({
    id: 8,
    name: 'Clothing and Armor',
    fieldCount: 7,
    fields: ['Concealability', 'Ballistic', 'Impact', 'Weight', 'Availability', '$Cost', 'Street Index']
  });
  
  const item = parser.parseItem(line, schema);
  
  assertEquals(item.name, 'Ordinary Clothing');
  assertEquals(item.category_id, 8);
  assertEquals(item.concealability, null); // "-" becomes null
  assertEquals(item.ballistic, null);
  assertEquals(item.impact, null);
  assertEquals(item.weight, 1); // Weight is "1", not null
  assertEquals(item.cost, 50);
  assertEquals(item.street_index, 0.8);
});

// Test 3: Parse ammunition item
test('Parses ammunition item correctly', () => {
  const line = '3-* #000 Triplex Rounds (HP only)  5|9|(see rules)|.5|4/60hrs|50|1.25|';
  const schema = detector.buildSchema({
    id: 5,
    name: 'Ammunition',
    fieldCount: 6,
    fields: ['Concealability', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']
  });
  
  const item = parser.parseItem(line, schema);
  
  assertEquals(item.name, '#000 Triplex Rounds (HP only)');
  assertEquals(item.category_id, 5);
  assertEquals(item.concealability, 9);
  assertEquals(item.damage, '(see rules)');
  assertEquals(item.weight, 0.5);
  assertEquals(item.cost, 50);
});

// Test 4: Parse explosive item
test('Parses explosive item correctly', () => {
  // Based on actual GEAR.DAT format for explosives
  const line = '3-* Concussion Grenade             7|5|6|.25|5/4days|30|';
  const schema = detector.buildSchema({
    id: 7,
    name: 'Explosives',
    fieldCount: 6,
    fields: ['Concealability', 'Rating', 'Weight', 'Availability', '$Cost', 'Street Index']
  });
  
  const item = parser.parseItem(line, schema);
  
  assertEquals(item.name, 'Concussion Grenade');
  assertEquals(item.concealability, 5);
  assertEquals(item.rating, 6); // Rating is a number
  assertEquals(item.weight, 0.25); // Weight is a number
});

// Test 5: Parse cost field
test('Parses cost field correctly', () => {
  assertEquals(parser.parseField('450', 'cost'), 450);
  assertEquals(parser.parseField('1,500', 'cost'), 1500);
  assertEquals(parser.parseField('Always', 'cost'), 'Always');
  assertEquals(parser.parseField('Varies', 'cost'), 'Varies');
});

// Test 6: Parse availability field
test('Parses availability field correctly', () => {
  const avail1 = parser.parseField('5/12hrs', 'availability');
  assertDeepEquals(avail1, { rating: 5, time: '12hrs' });
  
  const avail2 = parser.parseField('Always', 'availability');
  assertDeepEquals(avail2, { rating: 0, time: 'always' });
  
  const avail3 = parser.parseField('4/3days', 'availability');
  assertDeepEquals(avail3, { rating: 4, time: '3days' });
});

// Test 7: Parse damage field
test('Parses damage field correctly', () => {
  const dmg1 = parser.parseField('9M', 'damage');
  assertDeepEquals(dmg1, { power: '9', type: 'M' });
  
  const dmg2 = parser.parseField('10S', 'damage');
  assertDeepEquals(dmg2, { power: '10', type: 'S' });
  
  const dmg3 = parser.parseField('(STR+2)M', 'damage');
  assertDeepEquals(dmg3, { power: '(STR+2)', type: 'M' });
  
  const dmg4 = parser.parseField('(see rules)', 'damage');
  assertEquals(dmg4, '(see rules)');
});

// Test 8: Parse number field
test('Parses number field correctly', () => {
  assertEquals(parser.parseField('5', 'number'), 5);
  assertEquals(parser.parseField('2.5', 'number'), 2.5);
  assertEquals(parser.parseField('0.8', 'number'), 0.8);
  assertEquals(parser.parseField('-', 'number'), null);
});

// Test 9: Parse mode field
test('Parses mode field correctly', () => {
  assertDeepEquals(parser.parseField('SA', 'mode'), ['SA']);
  assertDeepEquals(parser.parseField('SA/BF', 'mode'), ['SA', 'BF']);
  assertDeepEquals(parser.parseField('SS/SA/BF', 'mode'), ['SS', 'SA', 'BF']);
});

// Test 10: Parse ammunition field
test('Parses ammunition field correctly', () => {
  const ammo1 = parser.parseField('10(c)', 'ammunition');
  assertDeepEquals(ammo1, { capacity: 10, type: 'c' });
  
  const ammo2 = parser.parseField('30(c)', 'ammunition');
  assertDeepEquals(ammo2, { capacity: 30, type: 'c' });
  
  assertEquals(parser.parseField('belt', 'ammunition'), 'belt');
  assertEquals(parser.parseField('Varies', 'ammunition'), 'Varies');
});

// Test 11: Validate item with all required fields
test('Validates item with all required fields', () => {
  const item = {
    name: 'Test Item',
    category_id: 8,
    concealability: 5
  };
  
  const validation = parser.validateItem(item, null);
  assert(validation.valid, 'Should be valid');
  assertEquals(validation.errors.length, 0);
});

// Test 12: Validate item missing name
test('Validates item missing name', () => {
  const item = {
    name: '',
    category_id: 8
  };
  
  const validation = parser.validateItem(item, null);
  assert(!validation.valid, 'Should be invalid');
  assert(validation.errors.length > 0, 'Should have errors');
});

// Test 13: Validate item missing category ID
test('Validates item missing category ID', () => {
  const item = {
    name: 'Test Item'
  };
  
  const validation = parser.validateItem(item, null);
  assert(!validation.valid, 'Should be invalid');
  assert(validation.errors.length > 0, 'Should have errors');
});

// Test 14: Parse multiple items
test('Parses multiple items from lines', () => {
  const lines = [
    '3-* Ordinary Clothing              8|-|-|-|1|Always|50|.8|',
    '3-* Fine Clothing                  8|-|-|-|1|Always|500|1|',
    '3-* Tres Chic Clothing             8|-|-|-|1|Always|1000|1|',
    '1-Armor', // Not an item line
    '3-* Armor Jacket                   8|5|3|3|2|2/48hrs|600|1|'
  ];
  
  const schema = detector.buildSchema({
    id: 8,
    name: 'Clothing and Armor',
    fieldCount: 7,
    fields: ['Concealability', 'Ballistic', 'Impact', 'Weight', 'Availability', '$Cost', 'Street Index']
  });
  
  const result = parser.parseItems(lines, schema);
  
  assertEquals(result.items.length, 4, 'Should parse 4 items');
  assertEquals(result.stats.total, 4, 'Should count 4 item lines');
  assertEquals(result.stats.parsed, 4, 'Should successfully parse 4');
  assertEquals(result.stats.failed, 0, 'Should have 0 failures');
});

// Test 15: Handle parse errors gracefully
test('Handles parse errors gracefully', () => {
  const lines = [
    '3-* Valid Item 8|5|3|3|2|2/48hrs|600|1|',
    '3-* Invalid Item', // Missing pipe separator
    '3-* Another Valid Item 8|5|3|3|2|2/48hrs|600|1|'
  ];
  
  const schema = detector.buildSchema({
    id: 8,
    name: 'Clothing and Armor',
    fieldCount: 7,
    fields: ['Concealability', 'Ballistic', 'Impact', 'Weight', 'Availability', '$Cost', 'Street Index']
  });
  
  const result = parser.parseItems(lines, schema);
  
  assertEquals(result.items.length, 2, 'Should parse 2 valid items');
  assertEquals(result.parseErrors.length, 1, 'Should have 1 parse error');
  assertEquals(result.stats.failed, 1, 'Should count 1 failure');
});

// Test 16: Normalize field names
test('Normalizes field names correctly', () => {
  assertEquals(parser.normalizeFieldName('$Cost'), 'cost');
  assertEquals(parser.normalizeFieldName('Street Index'), 'street_index');
  assertEquals(parser.normalizeFieldName('Str.Min.'), 'str_min');
  assertEquals(parser.normalizeFieldName('Concealability'), 'concealability');
});

// Test 17: Infer field types
test('Infers field types correctly', () => {
  assertEquals(parser.inferFieldType('$Cost'), 'cost');
  assertEquals(parser.inferFieldType('Availability'), 'availability');
  assertEquals(parser.inferFieldType('Damage'), 'damage');
  assertEquals(parser.inferFieldType('Mode'), 'mode');
  assertEquals(parser.inferFieldType('Ammunition'), 'ammunition');
  assertEquals(parser.inferFieldType('Weight'), 'number');
  assertEquals(parser.inferFieldType('Ballistic'), 'number');
  assertEquals(parser.inferFieldType('Name'), 'string');
});

// Test 18: Parse item without schema
test('Parses item without schema', () => {
  const line = '3-* Test Item 99|value1|value2|value3|';
  const item = parser.parseItem(line, null);
  
  assertEquals(item.name, 'Test Item');
  assertEquals(item.category_id, 99);
  assertEquals(item.field_0, 'value1');
  assertEquals(item.field_1, 'value2');
  assertEquals(item.field_2, 'value3');
});

// Test 19: Handle null/empty values
test('Handles null/empty values correctly', () => {
  assertEquals(parser.parseField('', 'string'), null);
  assertEquals(parser.parseField('-', 'number'), null);
  assertEquals(parser.parseField('N/A', 'cost'), null);
});

// Test 20: Parse real armor data
test('Parses real armor data from GEAR.DAT', () => {
  const lines = [
    '3-* Ordinary Clothing              8|-|-|-|1|Always|50|.8|',
    '3-* Fine Clothing                  8|-|-|-|1|Always|500|1|',
    '3-* Tres Chic Clothing             8|-|-|-|1|Always|1000|1|'
  ];
  
  const schema = detector.buildSchema({
    id: 8,
    name: 'Clothing and Armor',
    fieldCount: 7,
    fields: ['Concealability', 'Ballistic', 'Impact', 'Weight', 'Availability', '$Cost', 'Street Index']
  });
  
  const result = parser.parseItems(lines, schema);
  
  assertEquals(result.items.length, 3);
  assertEquals(result.items[0].name, 'Ordinary Clothing');
  assertEquals(result.items[1].name, 'Fine Clothing');
  assertEquals(result.items[2].name, 'Tres Chic Clothing');
  
  // Check costs
  assertEquals(result.items[0].cost, 50);
  assertEquals(result.items[1].cost, 500);
  assertEquals(result.items[2].cost, 1000);
});

// Summary
console.log();
console.log('='.repeat(80));
console.log('TEST SUMMARY');
console.log('='.repeat(80));
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total:  ${passed + failed}`);
console.log();

if (failed === 0) {
  console.log('✓ ALL TESTS PASSED!');
  process.exit(0);
} else {
  console.log('✗ SOME TESTS FAILED');
  process.exit(1);
}
