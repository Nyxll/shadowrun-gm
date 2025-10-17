#!/usr/bin/env node
/**
 * PHASE 1 - STEP 1.5: Universal Parser Tests
 * 
 * Tests for the GearDatParser class
 */

import { GearDatParser } from './gear-dat-parser.js';
import fs from 'fs';

console.log('='.repeat(80));
console.log('GEAR.DAT PARSER TESTS');
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

// Mock database config (won't actually connect in tests)
const mockDbConfig = {
  host: 'localhost',
  port: 5432,
  user: 'test',
  password: 'test',
  database: 'test'
};

// Test 1: Parser instantiation
test('Creates parser instance', () => {
  const parser = new GearDatParser(mockDbConfig);
  assert(parser.detector, 'Should have detector');
  assert(parser.parser, 'Should have parser');
  assert(parser.importer, 'Should have importer');
});

// Test 2: Parse file structure
test('Parses file structure correctly', () => {
  const parser = new GearDatParser(mockDbConfig);
  
  const lines = [
    '0-8|Clothing and Armor|7|Concealability|Ballistic|Impact|Weight|Availability|$Cost|Street Index',
    '1-Armor',
    '3-* Ordinary Clothing              8|-|-|-|1|Always|50|.8|',
    '3-* Fine Clothing                  8|-|-|-|1|Always|500|1|',
    '0-3|Firearms|10|Concealability|Damage|Weight|Availability|$Cost|Street Index|Ammunition|Mode|Recoil|Str.Min.',
    '1-Pistols',
    '2-Heavy Pistols',
    '3-* Ares Predator II               3|9M|2.5|5/12hrs|450|1.2|15(c)|SA|2|-|'
  ];
  
  const structure = parser.parseFileStructure(lines);
  
  assertEquals(structure.categories.length, 2, 'Should find 2 categories');
  assertEquals(structure.categories[0].id, 8, 'First category ID should be 8');
  assertEquals(structure.categories[0].name, 'Clothing and Armor', 'First category name');
  assertEquals(structure.categories[0].items.length, 2, 'First category should have 2 items');
  assertEquals(structure.categories[1].id, 3, 'Second category ID should be 3');
  assertEquals(structure.categories[1].items.length, 1, 'Second category should have 1 item');
});

// Test 3: Handles empty lines
test('Handles empty lines correctly', () => {
  const parser = new GearDatParser(mockDbConfig);
  
  const lines = [
    '0-8|Clothing and Armor|7|Concealability|Ballistic|Impact|Weight|Availability|$Cost|Street Index',
    '',
    '1-Armor',
    '',
    '3-* Ordinary Clothing              8|-|-|-|1|Always|50|.8|',
    ''
  ];
  
  const structure = parser.parseFileStructure(lines);
  
  assertEquals(structure.categories.length, 1, 'Should find 1 category');
  assertEquals(structure.categories[0].items.length, 1, 'Should have 1 item');
});

// Test 4: Handles multiple categories
test('Handles multiple categories in sequence', () => {
  const parser = new GearDatParser(mockDbConfig);
  
  const lines = [
    '0-8|Clothing and Armor|7|...',
    '3-* Item 1                         8|...',
    '0-3|Firearms|10|...',
    '3-* Item 2                         3|...',
    '0-5|Ammunition|6|...',
    '3-* Item 3                         5|...'
  ];
  
  const structure = parser.parseFileStructure(lines);
  
  assertEquals(structure.categories.length, 3, 'Should find 3 categories');
  assertEquals(structure.categories[0].id, 8);
  assertEquals(structure.categories[1].id, 3);
  assertEquals(structure.categories[2].id, 5);
});

// Test 5: Ignores non-item lines
test('Ignores section headers and other non-item lines', () => {
  const parser = new GearDatParser(mockDbConfig);
  
  const lines = [
    '0-8|Clothing and Armor|7|...',
    '1-Armor',
    '2-Light Armor',
    '3-* Armor Jacket                   8|5|3|3|2|2/48hrs|600|1|',
    '2-Heavy Armor',
    '3-* Full Body Armor                8|8|6|10|4|8/10days|8000|2|'
  ];
  
  const structure = parser.parseFileStructure(lines);
  
  assertEquals(structure.categories.length, 1);
  assertEquals(structure.categories[0].items.length, 2, 'Should only count item lines');
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
