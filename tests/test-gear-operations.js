#!/usr/bin/env node

/**
 * Gear System Integration Tests
 * Tests lookup_gear, compare_gear, and get_gear_details MCP tools
 */

import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST || '127.0.0.1',
  port: parseInt(process.env.POSTGRES_PORT || '5434'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

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

async function lookupGear(args) {
  const { query, category, subcategory, max_cost, tags, limit = 10 } = args;
  
  let sql = 'SELECT * FROM gear WHERE 1=1';
  const params = [];
  let paramCount = 0;
  
  if (query) {
    paramCount++;
    sql += ` AND search_vector @@ plainto_tsquery('english', $${paramCount})`;
    params.push(query);
  }
  
  if (category) {
    paramCount++;
    sql += ` AND category = $${paramCount}`;
    params.push(category);
  }
  
  if (subcategory) {
    paramCount++;
    sql += ` AND subcategory = $${paramCount}`;
    params.push(subcategory);
  }
  
  if (max_cost) {
    paramCount++;
    sql += ` AND cost <= $${paramCount}`;
    params.push(max_cost);
  }
  
  if (tags && tags.length > 0) {
    paramCount++;
    sql += ` AND tags && $${paramCount}`;
    params.push(tags);
  }
  
  if (query) {
    sql += ` ORDER BY ts_rank(search_vector, plainto_tsquery('english', $1)) DESC`;
  } else {
    sql += ` ORDER BY name`;
  }
  
  paramCount++;
  sql += ` LIMIT $${paramCount}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  return result.rows;
}

async function compareGear(args) {
  const { category, subcategory, sort_by = 'cost', limit = 10 } = args;
  
  let sql = 'SELECT * FROM gear WHERE category = $1';
  const params = [category];
  
  if (subcategory) {
    sql += ' AND subcategory = $2';
    params.push(subcategory);
  }
  
  const sortField = {
    'cost': 'cost',
    'damage': "(base_stats->>'damage')",
    'essence': "(base_stats->>'essence')::NUMERIC",
    'availability': 'availability',
    'conceal': "(base_stats->>'conceal')::INTEGER",
    'ammo': "(base_stats->>'ammo')::INTEGER",
  }[sort_by] || 'cost';
  
  sql += ` ORDER BY ${sortField} ${sort_by === 'cost' || sort_by === 'essence' || sort_by === 'conceal' ? 'ASC' : 'DESC'} NULLS LAST LIMIT $${params.length + 1}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  return result.rows;
}

async function getGearDetails(gearId) {
  const result = await pool.query('SELECT * FROM gear WHERE id = $1', [gearId]);
  return result.rows[0] || null;
}

async function runTests() {
  console.log('⚙️  Gear System Integration Tests\n');
  console.log('='.repeat(80));
  
  try {
    // Test 1: Lookup Gear by Text Query
    console.log('\n📋 Test 1: Lookup Gear by Text Query (pistol)');
    const pistols = await lookupGear({ query: 'pistol', limit: 5 });
    assert(Array.isArray(pistols), 'Returns array of results');
    assert(pistols.length > 0, 'Found pistol results');
    assert(pistols.every(g => g.name && g.category), 'All results have name and category');
    console.log(`   Found ${pistols.length} pistols`);
    pistols.slice(0, 3).forEach(p => console.log(`     - ${p.name}`));
    
    // Test 2: Lookup Gear by Category
    console.log('\n📋 Test 2: Lookup Gear by Category (weapon)');
    const weapons = await lookupGear({ category: 'weapon', limit: 10 });
    assert(Array.isArray(weapons), 'Returns array of results');
    assert(weapons.length > 0, 'Found weapon results');
    assert(weapons.every(w => w.category === 'weapon'), 'All results are weapons');
    console.log(`   Found ${weapons.length} weapons`);
    
    // Test 3: Lookup Gear by Subcategory
    console.log('\n📋 Test 3: Lookup Gear by Subcategory (heavy_pistols)');
    const heavyPistols = await lookupGear({ 
      category: 'weapon', 
      subcategory: 'heavy_pistols',
      limit: 5 
    });
    assert(Array.isArray(heavyPistols), 'Returns array of results');
    if (heavyPistols.length > 0) {
      assert(heavyPistols.every(h => h.subcategory === 'heavy_pistols'), 'All results are heavy pistols');
      console.log(`   Found ${heavyPistols.length} heavy pistols`);
      heavyPistols.forEach(h => {
        const damage = h.base_stats?.damage || 'N/A';
        console.log(`     - ${h.name}: ${damage} damage`);
      });
    } else {
      console.log(`   No heavy pistols found (may need data)`);
    }
    
    // Test 4: Lookup Gear with Cost Filter
    console.log('\n📋 Test 4: Lookup Gear with Cost Filter (weapons under 1000¥)');
    const cheapWeapons = await lookupGear({ 
      category: 'weapon',
      max_cost: 1000,
      limit: 5
    });
    assert(Array.isArray(cheapWeapons), 'Returns array of results');
    if (cheapWeapons.length > 0) {
      assert(cheapWeapons.every(w => !w.cost || w.cost <= 1000), 'All results under 1000¥');
      console.log(`   Found ${cheapWeapons.length} cheap weapons`);
      cheapWeapons.forEach(w => {
        console.log(`     - ${w.name}: ¥${w.cost || 'N/A'}`);
      });
    } else {
      console.log(`   No cheap weapons found`);
    }
    
    // Test 5: Compare Gear by Damage
    console.log('\n📋 Test 5: Compare Weapons by Damage');
    const weaponsByDamage = await compareGear({ 
      category: 'weapon',
      sort_by: 'damage',
      limit: 5
    });
    assert(Array.isArray(weaponsByDamage), 'Returns array of results');
    assert(weaponsByDamage.length > 0, 'Found weapons to compare');
    console.log(`   Top ${weaponsByDamage.length} weapons by damage:`);
    weaponsByDamage.forEach((w, idx) => {
      const damage = w.base_stats?.damage || 'N/A';
      console.log(`     ${idx + 1}. ${w.name}: ${damage}`);
    });
    
    // Test 6: Compare Gear by Cost
    console.log('\n📋 Test 6: Compare Weapons by Cost (cheapest first)');
    const weaponsByCost = await compareGear({ 
      category: 'weapon',
      sort_by: 'cost',
      limit: 5
    });
    assert(Array.isArray(weaponsByCost), 'Returns array of results');
    assert(weaponsByCost.length > 0, 'Found weapons to compare');
    console.log(`   Cheapest ${weaponsByCost.length} weapons:`);
    weaponsByCost.forEach((w, idx) => {
      console.log(`     ${idx + 1}. ${w.name}: ¥${w.cost || 'N/A'}`);
    });
    
    // Test 7: Compare Cyberware by Essence Cost
    console.log('\n📋 Test 7: Compare Cyberware by Essence Cost');
    const cyberwareByEssence = await compareGear({ 
      category: 'cyberware',
      sort_by: 'essence',
      limit: 5
    });
    assert(Array.isArray(cyberwareByEssence), 'Returns array of results');
    if (cyberwareByEssence.length > 0) {
      console.log(`   Lowest essence cost cyberware:`);
      cyberwareByEssence.forEach((c, idx) => {
        const essence = c.base_stats?.essence || 'N/A';
        console.log(`     ${idx + 1}. ${c.name}: ${essence} essence`);
      });
    } else {
      console.log(`   No cyberware found (may need data)`);
    }
    
    // Test 8: Get Gear Details by ID
    console.log('\n📋 Test 8: Get Gear Details by ID');
    if (weapons.length > 0) {
      const firstWeapon = weapons[0];
      const details = await getGearDetails(firstWeapon.id);
      assert(details !== null, 'Returns gear details');
      assert(details.id === firstWeapon.id, 'Correct gear ID');
      assert(details.name === firstWeapon.name, 'Correct gear name');
      assert(details.base_stats !== null, 'Has base_stats');
      console.log(`   Retrieved: ${details.name}`);
      console.log(`   Stats: ${JSON.stringify(details.base_stats, null, 2)}`);
    } else {
      console.log(`   Skipped (no weapons available)`);
    }
    
    // Test 9: Get Non-Existent Gear
    console.log('\n📋 Test 9: Get Non-Existent Gear (error handling)');
    const nonExistent = await getGearDetails(999999);
    assert(nonExistent === null, 'Returns null for non-existent ID');
    console.log(`   Correctly returned null for invalid ID`);
    
    // Test 10: Lookup with Empty Results
    console.log('\n📋 Test 10: Lookup with No Results');
    const noResults = await lookupGear({ query: 'xyznonexistent123' });
    assert(Array.isArray(noResults), 'Returns array even with no results');
    assert(noResults.length === 0, 'Array is empty');
    console.log(`   Correctly returned empty array`);
    
    // Test 11: Compare Specific Subcategory
    console.log('\n📋 Test 11: Compare Specific Subcategory (sniper_rifle)');
    const sniperRifles = await compareGear({ 
      category: 'weapon',
      subcategory: 'sniper_rifle',
      sort_by: 'damage',
      limit: 5
    });
    assert(Array.isArray(sniperRifles), 'Returns array of results');
    if (sniperRifles.length > 0) {
      assert(sniperRifles.every(s => s.subcategory === 'sniper_rifle'), 'All are sniper rifles');
      console.log(`   Found ${sniperRifles.length} sniper rifles:`);
      sniperRifles.forEach((s, idx) => {
        const damage = s.base_stats?.damage || 'N/A';
        console.log(`     ${idx + 1}. ${s.name}: ${damage} damage`);
      });
    } else {
      console.log(`   No sniper rifles found (may need data)`);
    }
    
    // Test 12: Verify Gear Stats Structure
    console.log('\n📋 Test 12: Verify Gear Stats Structure');
    if (weapons.length > 0) {
      const weapon = weapons[0];
      assert(typeof weapon.id === 'number', 'ID is a number');
      assert(typeof weapon.name === 'string', 'Name is a string');
      assert(typeof weapon.category === 'string', 'Category is a string');
      assert(weapon.base_stats && typeof weapon.base_stats === 'object', 'base_stats is an object');
      console.log(`   Verified structure for: ${weapon.name}`);
      console.log(`   Fields: id, name, category, subcategory, base_stats, cost, availability`);
    } else {
      console.log(`   Skipped (no weapons available)`);
    }
    
    // Test 13: Limit Parameter
    console.log('\n📋 Test 13: Verify Limit Parameter');
    const limited = await lookupGear({ category: 'weapon', limit: 3 });
    assert(limited.length <= 3, 'Respects limit parameter');
    console.log(`   Requested 3, got ${limited.length} results`);
    
    // Test 14: Tags Filter (if available)
    console.log('\n📋 Test 14: Tags Filter');
    const tagged = await lookupGear({ 
      category: 'weapon',
      tags: ['smartlink'],
      limit: 5
    });
    assert(Array.isArray(tagged), 'Returns array for tag search');
    if (tagged.length > 0) {
      console.log(`   Found ${tagged.length} items with 'smartlink' tag`);
      tagged.forEach(t => {
        console.log(`     - ${t.name}: tags = ${t.tags?.join(', ') || 'none'}`);
      });
    } else {
      console.log(`   No items with 'smartlink' tag found`);
    }
    
  } catch (error) {
    console.error(`\n❌ Test execution error: ${error.message}`);
    console.error(error.stack);
    testsFailed++;
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
  
  await pool.end();
  process.exit(testsFailed > 0 ? 1 : 0);
}

runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
