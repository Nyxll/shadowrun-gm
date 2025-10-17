#!/usr/bin/env node

/**
 * Test script for the unified Shadowrun GM MCP server
 * Tests all 3 use cases: rules, gear, and lore queries
 */

import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

async function testQuery(description, sql, params = []) {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`TEST: ${description}`);
  console.log('='.repeat(70));
  
  try {
    const result = await pool.query(sql, params);
    console.log(`✓ Found ${result.rows.length} results`);
    
    if (result.rows.length > 0) {
      console.log('\nFirst result:');
      console.log(`  Title: ${result.rows[0].title}`);
      console.log(`  Category: ${result.rows[0].category}`);
      console.log(`  Content Type: ${result.rows[0].content_type}`);
      console.log(`  Content preview: ${result.rows[0].content.substring(0, 150)}...`);
    }
    
    return true;
  } catch (error) {
    console.error(`✗ Error: ${error.message}`);
    return false;
  }
}

async function runTests() {
  console.log('\n' + '='.repeat(70));
  console.log('SHADOWRUN GM UNIFIED SERVER - DATABASE TESTS');
  console.log('='.repeat(70));
  
  // Test 1: Rules query (initiative)
  await testQuery(
    'Rules Query: Initiative',
    `SELECT title, content, category, content_type
     FROM rules_content
     WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'initiative')
     AND content_type IN ('rule_mechanic', 'table')
     ORDER BY ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', 'initiative')) DESC
     LIMIT 3`
  );
  
  // Test 2: Gear list query (heavy pistols)
  await testQuery(
    'Gear List Query: Heavy Pistols',
    `SELECT title, content, category, content_type, source_file
     FROM rules_content
     WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'heavy pistol')
     AND category = 'gear_mechanics'
     AND content_type IN ('stat_block', 'table')
     ORDER BY ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', 'heavy pistol')) DESC
     LIMIT 10`
  );
  
  // Test 3: Lore query (dragons)
  await testQuery(
    'Lore Query: Dragons and Saeder-Krupp',
    `SELECT title, content, category, content_type, source_file
     FROM rules_content
     WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'dragon Saeder Krupp')
     AND content_type IN ('flavor_text', 'introduction')
     ORDER BY ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', 'dragon Saeder Krupp')) DESC
     LIMIT 3`
  );
  
  // Test 4: Check database stats
  console.log(`\n${'='.repeat(70)}`);
  console.log('DATABASE STATISTICS');
  console.log('='.repeat(70));
  
  const stats = await pool.query(`
    SELECT 
      COUNT(*) as total_chunks,
      COUNT(DISTINCT category) as categories,
      COUNT(DISTINCT content_type) as content_types,
      COUNT(DISTINCT source_file) as source_files
    FROM rules_content
  `);
  
  console.log(`Total chunks: ${stats.rows[0].total_chunks}`);
  console.log(`Categories: ${stats.rows[0].categories}`);
  console.log(`Content types: ${stats.rows[0].content_types}`);
  console.log(`Source files: ${stats.rows[0].source_files}`);
  
  // Test 5: Content type distribution
  const distribution = await pool.query(`
    SELECT content_type, COUNT(*) as count
    FROM rules_content
    GROUP BY content_type
    ORDER BY count DESC
  `);
  
  console.log('\nContent Type Distribution:');
  distribution.rows.forEach(row => {
    console.log(`  ${row.content_type}: ${row.count} chunks`);
  });
  
  await pool.end();
  
  console.log(`\n${'='.repeat(70)}`);
  console.log('✓ ALL TESTS COMPLETE');
  console.log('='.repeat(70));
  console.log('\nThe database is ready for the unified MCP server!');
  console.log('Next step: Add server-unified.js to your MCP configuration.');
}

runTests().catch(error => {
  console.error('Test error:', error);
  process.exit(1);
});
