#!/usr/bin/env node
/**
 * PHASE 1 - STEP 1.2: Category Detector Tests
 * 
 * Tests for the CategoryDetector class
 */

import { CategoryDetector } from './category-detector.js';

const detector = new CategoryDetector();

console.log('='.repeat(80));
console.log('CATEGORY DETECTOR TESTS');
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

// Test 1: Detect armor category
test('Detects armor category header', () => {
  const line = '0-8|Clothing and Armor|7|Concealability|Ballistic|Impact|Weight|Availability|$Cost|Street Index';
  const result = detector.detectCategory(line);
  
  assert(result !== null, 'Should detect category');
  assertEquals(result.id, 8, 'Category ID should be 8');
  assertEquals(result.name, 'Clothing and Armor', 'Category name should match');
  assertEquals(result.fieldCount, 7, 'Field count should be 7');
  assertEquals(result.fields.length, 7, 'Should have 7 fields');
  assertEquals(result.fields[0], 'Concealability', 'First field should be Concealability');
});

// Test 2: Detect ammunition category
test('Detects ammunition category header', () => {
  const line = '0-5|Ammunition|6|Concealability|Damage|Weight|Availability|$Cost|Street Index';
  const result = detector.detectCategory(line);
  
  assert(result !== null, 'Should detect category');
  assertEquals(result.id, 5, 'Category ID should be 5');
  assertEquals(result.name, 'Ammunition', 'Category name should match');
  assertEquals(result.fieldCount, 6, 'Field count should be 6');
});

// Test 3: Detect explosives category
test('Detects explosives category header', () => {
  const line = '0-7|Explosives|6|Concealability|Rating|Weight|Availability|$Cost|Street Index';
  const result = detector.detectCategory(line);
  
  assert(result !== null, 'Should detect category');
  assertEquals(result.id, 7, 'Category ID should be 7');
  assertEquals(result.name, 'Explosives', 'Category name should match');
});

// Test 4: Non-category line returns null
test('Returns null for non-category lines', () => {
  const line = '3-* Ares Predator II';
  const result = detector.detectCategory(line);
  
  assertEquals(result, null, 'Should return null for non-category line');
});

// Test 5: Empty line returns null
test('Returns null for empty lines', () => {
  const result = detector.detectCategory('');
  assertEquals(result, null, 'Should return null for empty line');
});

// Test 6: Build schema for armor
test('Builds schema for armor category', () => {
  const category = {
    id: 8,
    name: 'Clothing and Armor',
    fieldCount: 7,
    fields: ['Concealability', 'Ballistic', 'Impact', 'Weight', 'Availability', '$Cost', 'Street Index']
  };
  
  const schema = detector.buildSchema(category);
  
  assertEquals(schema.table, 'gear', 'Table should be gear');
  assertEquals(schema.category, 'armor', 'Category should be armor');
  assertEquals(schema.categoryId, 8, 'Category ID should be 8');
});

// Test 7: Build schema for ammunition
test('Builds schema for ammunition category', () => {
  const category = {
    id: 5,
    name: 'Ammunition',
    fieldCount: 6,
    fields: ['Concealability', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']
  };
  
  const schema = detector.buildSchema(category);
  
  assertEquals(schema.category, 'ammunition', 'Category should be ammunition');
});

// Test 8: Normalize category name
test('Normalizes category names correctly', () => {
  assertEquals(detector.normalizeCategoryName('Clothing and Armor'), 'clothing_and_armor');
  assertEquals(detector.normalizeCategoryName('S+S Vision Enhancers'), 's_s_vision_enhancers');
  assertEquals(detector.normalizeCategoryName('Bow and crossbow'), 'bow_and_crossbow');
});

// Test 9: Normalize field name
test('Normalizes field names correctly', () => {
  assertEquals(detector.normalizeFieldName('$Cost'), 'cost');
  assertEquals(detector.normalizeFieldName('Street Index'), 'street_index');
  assertEquals(detector.normalizeFieldName('Str.Min.'), 'str_min');
});

// Test 10: Infer field types
test('Infers field types correctly', () => {
  assertEquals(detector.inferFieldType('$Cost'), 'cost');
  assertEquals(detector.inferFieldType('Availability'), 'availability');
  assertEquals(detector.inferFieldType('Weight'), 'number');
  assertEquals(detector.inferFieldType('Damage'), 'damage');
  assertEquals(detector.inferFieldType('Rating'), 'number');
  assertEquals(detector.inferFieldType('Concealability'), 'number');
  assertEquals(detector.inferFieldType('Street Index'), 'number');
  assertEquals(detector.inferFieldType('Name'), 'string');
});

// Test 11: Get categories to import (all)
test('Gets all categories to import', () => {
  const categories = detector.getCategoriesToImport();
  
  assert(categories.length === 23, 'Should have 23 categories');
  assert(categories.includes(8), 'Should include armor (8)');
  assert(categories.includes(5), 'Should include ammunition (5)');
});

// Test 12: Get categories to import (skip some)
test('Gets categories to import with skip list', () => {
  const categories = detector.getCategoriesToImport({ skip: [1, 2, 3] });
  
  assert(!categories.includes(1), 'Should not include category 1');
  assert(!categories.includes(2), 'Should not include category 2');
  assert(!categories.includes(3), 'Should not include category 3');
  assert(categories.includes(8), 'Should include armor (8)');
});

// Test 13: Get categories to import (only specific)
test('Gets only specific categories to import', () => {
  const categories = detector.getCategoriesToImport({ only: [5, 7, 8] });
  
  assertDeepEquals(categories, [5, 7, 8], 'Should only include specified categories');
});

// Test 14: Build generic schema
test('Builds generic schema for unknown category', () => {
  const category = {
    id: 99,
    name: 'Unknown Category',
    fieldCount: 3,
    fields: ['Field1', 'Field2', 'Field3']
  };
  
  const schema = detector.buildGenericSchema(category);
  
  assertEquals(schema.table, 'gear', 'Table should be gear');
  assertEquals(schema.category, 'unknown_category', 'Category should be normalized');
  assert(schema.fieldMappings !== undefined, 'Should have field mappings');
});

// Test 15: All 23 categories have mappings
test('All 23 categories have mappings', () => {
  const mappings = detector.buildCategoryMappings();
  const categoryIds = Object.keys(mappings).map(id => parseInt(id));
  
  assertEquals(categoryIds.length, 23, 'Should have 23 category mappings');
  
  for (let i = 1; i <= 23; i++) {
    assert(categoryIds.includes(i), `Should have mapping for category ${i}`);
  }
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
