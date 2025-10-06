#!/usr/bin/env node

/**
 * Test the enhanced query engine
 */

import queryEngine from './lib/query-engine.js';

async function testQueries() {
  console.log('Testing Enhanced Query Engine\n');
  console.log('='.repeat(80));
  
  try {
    // Test 1: Simple query
    console.log('\n## Test 1: Simple Query - "heavy pistol full auto"\n');
    const result1 = await queryEngine.advancedQuery('heavy pistol full auto', {
      includeGeneralClarifications: true,
      limit: 3
    });
    
    console.log(`Found ${result1.count} rules`);
    console.log(`General clarifications: ${result1.generalClarifications.length}`);
    
    if (result1.generalClarifications.length > 0) {
      console.log('\nClarifications found:');
      result1.generalClarifications.forEach(c => {
        console.log(`  - [${c.clarification_type}] ${c.title}`);
      });
    }
    
    // Test 2: Multi-topic query
    console.log('\n## Test 2: Multi-Topic Query\n');
    const result2 = await queryEngine.multiTopicQuery([
      'full auto burst fire',
      'darkness thermographic',
      'smartlink'
    ], 2);
    
    console.log(`Found ${result2.topicCount} topics with results`);
    result2.results.forEach(topic => {
      console.log(`  - ${topic.topic}: ${topic.results.length} results`);
    });
    
    // Test 3: Get categories
    console.log('\n## Test 3: Categories\n');
    const categories = await queryEngine.getCategories();
    console.log('Categories:');
    categories.forEach(cat => {
      console.log(`  - ${cat.category}: ${cat.count} rules`);
    });
    
    // Test 4: Get clarifications
    console.log('\n## Test 4: Search Clarifications - "smartlink"\n');
    const clarifications = await queryEngine.getGeneralClarifications('smartlink', 5);
    console.log(`Found ${clarifications.length} clarifications`);
    clarifications.forEach(c => {
      console.log(`  - [${c.clarification_type}] ${c.title}`);
    });
    
    console.log('\n' + '='.repeat(80));
    console.log('✓ All tests completed successfully!');
    
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    await queryEngine.closePool();
  }
}

testQueries();
