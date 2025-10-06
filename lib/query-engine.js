/**
 * Query Engine for Shadowrun GM RAG Database
 * Provides reusable query functions with logging and clarifications support
 */

import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

// Database connection pool
const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

/**
 * Log a query to the database
 */
async function logQuery(queryText, queryType, categoryFilter, resultsCount, executionTimeMs, searchRankScores = null) {
  try {
    await pool.query(`
      INSERT INTO query_logs (query_text, query_type, category_filter, results_count, execution_time_ms, search_rank_scores)
      VALUES ($1, $2, $3, $4, $5, $6)
    `, [queryText, queryType, categoryFilter, resultsCount, executionTimeMs, searchRankScores ? JSON.stringify(searchRankScores) : null]);
  } catch (error) {
    console.error('Failed to log query:', error.message);
  }
}

/**
 * Log clarification usage
 */
async function logClarificationUsage(clarificationId, ruleId, queryContext) {
  try {
    await pool.query(`
      INSERT INTO clarification_usage_logs (clarification_id, rule_id, query_context)
      VALUES ($1, $2, $3)
    `, [clarificationId, ruleId, queryContext]);
  } catch (error) {
    console.error('Failed to log clarification usage:', error.message);
  }
}

/**
 * Get clarifications for a rule
 */
async function getClarificationsForRule(ruleId) {
  const result = await pool.query(`
    SELECT id, clarification_type, title, content, source, source_reference, priority
    FROM rule_clarifications
    WHERE rule_id = $1 AND is_active = true
    ORDER BY priority DESC
  `, [ruleId]);
  
  return result.rows;
}

/**
 * Get general clarifications matching keywords
 */
async function getGeneralClarifications(keywords, limit = 3) {
  const result = await pool.query(`
    SELECT id, clarification_type, title, content, source, source_reference, priority
    FROM rule_clarifications
    WHERE rule_id IS NULL 
      AND is_active = true
      AND to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
    ORDER BY priority DESC, ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) DESC
    LIMIT $2
  `, [keywords, limit]);
  
  return result.rows;
}

/**
 * Simple text search query
 */
export async function simpleQuery(queryText, category = null, limit = 5) {
  const startTime = Date.now();
  
  let query = `
    SELECT 
      id,
      title, 
      content, 
      category, 
      subcategory, 
      tags,
      ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) as rank
    FROM rules_content
    WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
  `;
  
  const params = [queryText];
  
  if (category) {
    query += ` AND category = $2`;
    params.push(category);
    query += ` ORDER BY rank DESC LIMIT $3`;
    params.push(limit);
  } else {
    query += ` ORDER BY rank DESC LIMIT $2`;
    params.push(limit);
  }
  
  const result = await pool.query(query, params);
  const executionTime = Date.now() - startTime;
  
  // Get clarifications for each result
  const resultsWithClarifications = await Promise.all(
    result.rows.map(async (row) => {
      const clarifications = await getClarificationsForRule(row.id);
      return { ...row, clarifications };
    })
  );
  
  // Log the query
  await logQuery(queryText, 'simple', category, result.rows.length, executionTime, 
    result.rows.map(r => ({ title: r.title, rank: r.rank })));
  
  return {
    results: resultsWithClarifications,
    executionTime,
    count: result.rows.length
  };
}

/**
 * Multi-topic query - searches for multiple related topics
 */
export async function multiTopicQuery(topics, limit = 3) {
  const startTime = Date.now();
  const allResults = [];
  
  for (const topic of topics) {
    const result = await pool.query(`
      SELECT 
        id,
        title, 
        content, 
        category, 
        subcategory, 
        tags,
        ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) as rank
      FROM rules_content
      WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
      ORDER BY rank DESC
      LIMIT $2
    `, [topic, limit]);
    
    if (result.rows.length > 0) {
      // Get clarifications for each result
      const resultsWithClarifications = await Promise.all(
        result.rows.map(async (row) => {
          const clarifications = await getClarificationsForRule(row.id);
          return { ...row, clarifications, topic };
        })
      );
      
      allResults.push({
        topic,
        results: resultsWithClarifications
      });
    }
  }
  
  const executionTime = Date.now() - startTime;
  
  // Log the query
  await logQuery(topics.join(', '), 'multi-topic', null, allResults.length, executionTime);
  
  return {
    results: allResults,
    executionTime,
    topicCount: allResults.length
  };
}

/**
 * Advanced query with clarifications
 */
export async function advancedQuery(queryText, options = {}) {
  const {
    category = null,
    includeGeneralClarifications = true,
    limit = 5
  } = options;
  
  const startTime = Date.now();
  
  // Get base results
  const baseResults = await simpleQuery(queryText, category, limit);
  
  // Get general clarifications if requested
  let generalClarifications = [];
  if (includeGeneralClarifications) {
    generalClarifications = await getGeneralClarifications(queryText, 3);
  }
  
  const executionTime = Date.now() - startTime;
  
  // Log the query
  await logQuery(queryText, 'advanced', category, baseResults.count, executionTime);
  
  return {
    ...baseResults,
    generalClarifications,
    executionTime
  };
}

/**
 * Get all categories
 */
export async function getCategories() {
  const result = await pool.query(`
    SELECT category, COUNT(*) as count
    FROM rules_content
    GROUP BY category
    ORDER BY count DESC
  `);
  
  return result.rows;
}

/**
 * Get subcategories for a category
 */
export async function getSubcategories(category) {
  const result = await pool.query(`
    SELECT subcategory, COUNT(*) as count
    FROM rules_content
    WHERE category = $1 AND subcategory IS NOT NULL
    GROUP BY subcategory
    ORDER BY count DESC
  `, [category]);
  
  return result.rows;
}

/**
 * Close the database connection pool
 */
export async function closePool() {
  await pool.end();
}

export default {
  simpleQuery,
  multiTopicQuery,
  advancedQuery,
  getCategories,
  getSubcategories,
  getClarificationsForRule,
  getGeneralClarifications,
  logClarificationUsage,
  closePool
};
