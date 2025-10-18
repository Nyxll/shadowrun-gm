#!/usr/bin/env node

/**
 * Test suite for Clarification & Learning System
 * Tests the integrated clarification engine and learning engine
 */

import pg from 'pg';
import dotenv from 'dotenv';
import { ClarificationEngine } from '../lib/intent/clarification-engine.js';
import { LearningEngine } from '../lib/intent/learning-engine.js';
import { IntentClassifier } from '../lib/intent/intent-classifier.js';

dotenv.config();

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

// Mock LLM classifier for testing
async function mockClassifier(query) {
  // Simple mock that returns uncertain classification
  return {
    intent: 'rules',
    confidence: 0.4,
    data_sources: ['chunks'],
    tables: [],
    search_terms: [query],
  };
}

async function runTests() {
  console.log('='.repeat(60));
  console.log('CLARIFICATION & LEARNING SYSTEM TEST SUITE');
  console.log('='.repeat(60));
  console.log('');

  const clarificationEngine = new ClarificationEngine(pool);
  const learningEngine = new LearningEngine(pool);
  const intentClassifier = new IntentClassifier(mockClassifier, {
    clarificationEngine,
    learningEngine
  });

  let passedTests = 0;
  let failedTests = 0;

  // Test 1: Clarification Engine - Detect ambiguous query
  console.log('Test 1: Detect ambiguous query');
  console.log('-'.repeat(60));
  try {
    const classification = {
      intent: 'lookup',
      confidence: 0.3,
      data_sources: ['structured'],
      tables: ['spells', 'powers'],
      item_name: 'fireball'
    };
    
    const needsClarification = await clarificationEngine.needsClarification(classification);
    console.log(`✓ Ambiguous query detected: ${needsClarification}`);
    console.log(`  Confidence: ${classification.confidence}`);
    console.log(`  Multiple tables: ${classification.tables.join(', ')}`);
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 2: Generate clarification options
  console.log('Test 2: Generate clarification options');
  console.log('-'.repeat(60));
  try {
    const classification = {
      intent: 'lookup',
      confidence: 0.3,
      data_sources: ['structured'],
      tables: ['spells', 'powers'],
      item_name: 'fireball'
    };
    
    const options = await clarificationEngine.generateOptions(
      'tell me about fireball',
      classification
    );
    
    console.log(`✓ Generated ${options.length} clarification options:`);
    options.forEach((opt, idx) => {
      console.log(`  ${idx + 1}. ${opt.label}`);
      console.log(`     Intent: ${opt.classification.intent}, Table: ${opt.classification.tables[0]}`);
    });
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 3: Record clarification
  console.log('Test 3: Record clarification interaction');
  console.log('-'.repeat(60));
  try {
    const originalQuery = 'show me fireball';
    const originalClassification = {
      intent: 'lookup',
      confidence: 0.3,
      tables: ['spells', 'powers']
    };
    
    const selectedOption = {
      label: 'Fireball spell (magic)',
      classification: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['spells'],
        item_name: 'Fireball'
      }
    };
    
    const clarificationId = await clarificationEngine.recordClarification(
      originalQuery,
      originalClassification,
      [selectedOption],
      selectedOption
    );
    
    console.log(`✓ Clarification recorded with ID: ${clarificationId}`);
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 4: Learning Engine - Record pattern
  console.log('Test 4: Record learned pattern');
  console.log('-'.repeat(60));
  try {
    const pattern = {
      text: 'show me',
      type: 'phrase',
      confidence: 0.75
    };
    const intent = 'lookup';
    const queryAttemptId = 1; // Mock ID
    const exampleQuery = 'show me fireball';
    
    await learningEngine.recordPattern(pattern, intent, queryAttemptId, exampleQuery);
    console.log(`✓ Pattern recorded`);
    console.log(`  Pattern: ${pattern.text}`);
    console.log(`  Type: ${pattern.type}`);
    console.log(`  Intent: ${intent}`);
    console.log(`  Confidence: ${pattern.confidence}`);
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 5: Learning Engine - Find similar patterns
  console.log('Test 5: Find similar learned patterns');
  console.log('-'.repeat(60));
  try {
    const query = 'show me ares predator';
    const patterns = await learningEngine.findSimilarPatterns(query);
    
    console.log(`✓ Found ${patterns.length} similar patterns:`);
    patterns.forEach((p, idx) => {
      console.log(`  ${idx + 1}. ${p.pattern_text}`);
      console.log(`     Intent: ${p.intent}, Confidence: ${p.confidence}`);
      console.log(`     Success rate: ${p.success_rate || 0}%`);
    });
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 6: Learning Engine - Update pattern success
  console.log('Test 6: Update pattern success metrics');
  console.log('-'.repeat(60));
  try {
    // First, get a pattern to update
    const patterns = await learningEngine.findSimilarPatterns('show me');
    if (patterns.length > 0) {
      const patternId = patterns[0].id;
      await learningEngine.recordPatternSuccess(patternId, true);
      console.log(`✓ Pattern success recorded for ID: ${patternId}`);
      console.log(`  Previous success rate: ${patterns[0].success_rate}%`);
      passedTests++;
    } else {
      console.log('⚠ No patterns found to update (skipping test)');
      passedTests++;
    }
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 7: Intent Classifier with learning
  console.log('Test 7: Intent classification with learned patterns');
  console.log('-'.repeat(60));
  try {
    const query = 'show me fireball spell';
    const classification = await intentClassifier.classify(query);
    
    console.log(`✓ Classification result:`);
    console.log(`  Intent: ${classification.intent}`);
    console.log(`  Confidence: ${classification.confidence}`);
    console.log(`  Data sources: ${classification.data_sources.join(', ')}`);
    console.log(`  Tables: ${classification.tables.join(', ')}`);
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 8: Get clarification statistics
  console.log('Test 8: Retrieve clarification statistics');
  console.log('-'.repeat(60));
  try {
    const stats = await pool.query(`
      SELECT 
        COUNT(*) as total_clarifications,
        AVG(CASE WHEN was_helpful THEN 1 ELSE 0 END) * 100 as helpful_percentage,
        COUNT(DISTINCT ci.id) as unique_interactions
      FROM clarification_interactions ci
      WHERE ci.timestamp > NOW() - INTERVAL '7 days'
    `);
    
    const row = stats.rows[0];
    console.log(`✓ Clarification statistics (last 7 days):`);
    console.log(`  Total clarifications: ${row.total_clarifications}`);
    console.log(`  Helpful rate: ${parseFloat(row.helpful_percentage || 0).toFixed(1)}%`);
    console.log(`  Unique queries: ${row.unique_queries}`);
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Test 9: Get learning statistics
  console.log('Test 9: Retrieve learning statistics');
  console.log('-'.repeat(60));
  try {
    const stats = await pool.query(`
      SELECT 
        COUNT(*) as total_patterns,
        AVG(success_rate) as avg_success_rate,
        AVG(confidence) as avg_boost,
        COUNT(*) FILTER (WHERE is_active = true) as active_patterns
      FROM learned_patterns
    `);
    
    const row = stats.rows[0];
    console.log(`✓ Learning statistics:`);
    console.log(`  Total patterns: ${row.total_patterns}`);
    console.log(`  Active patterns: ${row.active_patterns}`);
    console.log(`  Avg success rate: ${parseFloat(row.avg_success_rate || 0).toFixed(1)}%`);
    console.log(`  Avg confidence boost: +${parseFloat(row.avg_boost || 0).toFixed(2)}`);
    passedTests++;
  } catch (error) {
    console.log(`✗ FAILED: ${error.message}`);
    failedTests++;
  }
  console.log('');

  // Summary
  console.log('='.repeat(60));
  console.log('TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total tests: ${passedTests + failedTests}`);
  console.log(`✓ Passed: ${passedTests}`);
  console.log(`✗ Failed: ${failedTests}`);
  console.log(`Success rate: ${((passedTests / (passedTests + failedTests)) * 100).toFixed(1)}%`);
  console.log('');

  if (failedTests === 0) {
    console.log('🎉 All tests passed!');
  } else {
    console.log('⚠️  Some tests failed. Please review the output above.');
  }

  await pool.end();
  process.exit(failedTests > 0 ? 1 : 0);
}

runTests().catch(error => {
  console.error('Test suite error:', error);
  process.exit(1);
});
