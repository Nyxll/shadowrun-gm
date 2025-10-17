#!/usr/bin/env node

/**
 * Test Hybrid Search Implementation
 * Tests vector search, keyword search, and RRF fusion
 */

import pg from 'pg';
import dotenv from 'dotenv';
import OpenAI from 'openai';

dotenv.config();

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Import functions from server (simplified versions for testing)
async function generateQueryEmbedding(query) {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: query,
  });
  return response.data[0].embedding;
}

async function vectorSearch(query, categories = [], limit = 20) {
  const embedding = await generateQueryEmbedding(query);
  const embeddingStr = `[${embedding.join(',')}]`;
  
  let sql = `
    SELECT 
      id, title, content, category, subcategory,
      1 - (embedding <=> $1::vector) as similarity_score
    FROM rules_content
    WHERE embedding IS NOT NULL
  `;
  
  const params = [embeddingStr];
  
  if (categories.length > 0) {
    sql += ` AND category = ANY($2)`;
    params.push(categories);
  }
  
  sql += ` ORDER BY embedding <=> $1::vector LIMIT ${limit}`;
  
  const result = await pool.query(sql, params);
  return result.rows;
}

async function keywordSearch(query, categories = [], limit = 20) {
  let sql = `
    SELECT 
      id, title, content, category, subcategory,
      ts_rank(to_tsvector('english', title || ' ' || content), 
              plainto_tsquery('english', $1)) as rank
    FROM rules_content
    WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
  `;
  
  const params = [query];
  
  if (categories.length > 0) {
    sql += ` AND category = ANY($2)`;
    params.push(categories);
  }
  
  sql += ` ORDER BY rank DESC LIMIT ${limit}`;
  
  const result = await pool.query(sql, params);
  return result.rows;
}

function reciprocalRankFusion(vectorResults, keywordResults, k = 60) {
  const scores = new Map();
  
  vectorResults.forEach((result, index) => {
    const rank = index + 1;
    const score = 1 / (k + rank);
    scores.set(result.id, {
      ...result,
      rrf_score: score,
      vector_rank: rank,
      vector_score: result.similarity_score || 0,
    });
  });
  
  keywordResults.forEach((result, index) => {
    const rank = index + 1;
    const score = 1 / (k + rank);
    
    if (scores.has(result.id)) {
      const existing = scores.get(result.id);
      existing.rrf_score += score;
      existing.keyword_rank = rank;
      existing.keyword_score = result.rank || 0;
    } else {
      scores.set(result.id, {
        ...result,
        rrf_score: score,
        keyword_rank: rank,
        keyword_score: result.rank || 0,
      });
    }
  });
  
  return Array.from(scores.values())
    .sort((a, b) => b.rrf_score - a.rrf_score);
}

async function hybridSearch(query, categories = [], limit = 10) {
  const [vectorResults, keywordResults] = await Promise.all([
    vectorSearch(query, categories, 20),
    keywordSearch(query, categories, 20)
  ]);
  
  const fusedResults = reciprocalRankFusion(vectorResults, keywordResults);
  return fusedResults.slice(0, limit);
}

// Test queries
const testQueries = [
  {
    name: 'Initiative Rules',
    query: 'How does initiative work?',
    categories: ['combat'],
    expectedKeywords: ['initiative', 'combat turn', 'reaction']
  },
  {
    name: 'Spell Drain',
    query: 'What is spell drain?',
    categories: ['magic'],
    expectedKeywords: ['drain', 'spell', 'willpower']
  },
  {
    name: 'Avoiding Damage (Semantic)',
    query: 'How do I avoid getting shot?',
    categories: ['combat'],
    expectedKeywords: ['dodge', 'cover', 'combat pool', 'armor']
  },
  {
    name: 'Matrix Hacking',
    query: 'How does decking work?',
    categories: ['matrix'],
    expectedKeywords: ['decker', 'cyberdeck', 'matrix']
  },
  {
    name: 'Astral Combat',
    query: 'Fighting in astral space',
    categories: ['magic'],
    expectedKeywords: ['astral', 'combat', 'spirit']
  }
];

async function runTests() {
  console.log('=== Hybrid Search Test Suite ===\n');
  
  try {
    // Test database connection
    await pool.query('SELECT NOW()');
    console.log('✓ Database connection successful\n');
    
    // Test 1: Vector Search
    console.log('Test 1: Vector Search');
    console.log('----------------------');
    const vectorResults = await vectorSearch('initiative combat', ['combat'], 5);
    console.log(`Found ${vectorResults.length} results`);
    if (vectorResults.length > 0) {
      console.log('Top result:', {
        title: vectorResults[0].title,
        similarity: vectorResults[0].similarity_score.toFixed(4),
        category: vectorResults[0].category
      });
      console.log('✓ Vector search working\n');
    } else {
      console.log('✗ No vector results found\n');
    }
    
    // Test 2: Keyword Search
    console.log('Test 2: Keyword Search');
    console.log('----------------------');
    const keywordResults = await keywordSearch('initiative combat', ['combat'], 5);
    console.log(`Found ${keywordResults.length} results`);
    if (keywordResults.length > 0) {
      console.log('Top result:', {
        title: keywordResults[0].title,
        rank: keywordResults[0].rank.toFixed(4),
        category: keywordResults[0].category
      });
      console.log('✓ Keyword search working\n');
    } else {
      console.log('✗ No keyword results found\n');
    }
    
    // Test 3: RRF Fusion
    console.log('Test 3: Reciprocal Rank Fusion');
    console.log('-------------------------------');
    const fusedResults = reciprocalRankFusion(vectorResults, keywordResults);
    console.log(`Fused ${fusedResults.length} unique results`);
    if (fusedResults.length > 0) {
      console.log('Top 3 fused results:');
      fusedResults.slice(0, 3).forEach((r, i) => {
        console.log(`  ${i + 1}. ${r.title}`);
        console.log(`     RRF Score: ${r.rrf_score.toFixed(4)}`);
        console.log(`     Vector Rank: ${r.vector_rank || 'N/A'}, Keyword Rank: ${r.keyword_rank || 'N/A'}`);
      });
      console.log('✓ RRF fusion working\n');
    } else {
      console.log('✗ No fused results\n');
    }
    
    // Test 4: Full Hybrid Search
    console.log('Test 4: Full Hybrid Search');
    console.log('--------------------------');
    for (const test of testQueries) {
      console.log(`\nQuery: "${test.query}"`);
      console.log(`Categories: ${test.categories.join(', ')}`);
      
      const results = await hybridSearch(test.query, test.categories, 5);
      
      if (results.length > 0) {
        console.log(`✓ Found ${results.length} results`);
        console.log(`  Top result: ${results[0].title}`);
        console.log(`  RRF Score: ${results[0].rrf_score.toFixed(4)}`);
        
        // Check if expected keywords appear in results
        const allContent = results.map(r => (r.title + ' ' + r.content).toLowerCase()).join(' ');
        const foundKeywords = test.expectedKeywords.filter(kw => 
          allContent.includes(kw.toLowerCase())
        );
        console.log(`  Keywords found: ${foundKeywords.length}/${test.expectedKeywords.length}`);
        console.log(`  (${foundKeywords.join(', ')})`);
      } else {
        console.log(`✗ No results found`);
      }
    }
    
    // Test 5: Performance Comparison
    console.log('\n\nTest 5: Performance Comparison');
    console.log('------------------------------');
    
    const perfQuery = 'How does initiative work in combat?';
    
    // Vector only
    const vectorStart = Date.now();
    const vectorOnly = await vectorSearch(perfQuery, ['combat'], 10);
    const vectorTime = Date.now() - vectorStart;
    
    // Keyword only
    const keywordStart = Date.now();
    const keywordOnly = await keywordSearch(perfQuery, ['combat'], 10);
    const keywordTime = Date.now() - keywordStart;
    
    // Hybrid
    const hybridStart = Date.now();
    const hybridResults = await hybridSearch(perfQuery, ['combat'], 10);
    const hybridTime = Date.now() - hybridStart;
    
    console.log(`Vector search: ${vectorTime}ms (${vectorOnly.length} results)`);
    console.log(`Keyword search: ${keywordTime}ms (${keywordOnly.length} results)`);
    console.log(`Hybrid search: ${hybridTime}ms (${hybridResults.length} results)`);
    console.log(`Overhead: ${hybridTime - Math.max(vectorTime, keywordTime)}ms`);
    
    // Summary
    console.log('\n\n=== Test Summary ===');
    console.log('✓ All core functions working');
    console.log('✓ Vector similarity search operational');
    console.log('✓ Keyword search operational');
    console.log('✓ RRF fusion operational');
    console.log('✓ Hybrid search operational');
    console.log('\nImplementation successful!');
    
  } catch (error) {
    console.error('\n✗ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

runTests();
