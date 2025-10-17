#!/usr/bin/env node

/**
 * View query analytics from the logs
 */

import pg from 'pg';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '..', '.env') });

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

async function viewAnalytics() {
  try {
    console.log('='.repeat(80));
    console.log('SHADOWRUN GM QUERY ANALYTICS');
    console.log('='.repeat(80));
    console.log('');
    
    // Total queries
    const total = await pool.query('SELECT COUNT(*) as count FROM query_logs');
    console.log(`📊 Total Queries: ${total.rows[0].count}`);
    console.log('');
    
    // Recent queries
    console.log('📝 Recent Queries (Last 10):');
    console.log('-'.repeat(80));
    const recent = await pool.query(`
      SELECT 
        timestamp,
        query_text,
        intent,
        result_count,
        execution_time_ms,
        error_message
      FROM query_logs
      ORDER BY timestamp DESC
      LIMIT 10
    `);
    
    recent.rows.forEach((row, idx) => {
      const time = new Date(row.timestamp).toLocaleString();
      const status = row.error_message ? '❌ ERROR' : '✅ OK';
      console.log(`${idx + 1}. [${time}] ${status}`);
      console.log(`   Query: "${row.query_text}"`);
      console.log(`   Intent: ${row.intent || 'unknown'} | Results: ${row.result_count || 0} | Time: ${row.execution_time_ms}ms`);
      if (row.error_message) {
        console.log(`   Error: ${row.error_message}`);
      }
      console.log('');
    });
    
    // Query by intent
    console.log('📈 Queries by Intent:');
    console.log('-'.repeat(80));
    const byIntent = await pool.query(`
      SELECT 
        intent,
        COUNT(*) as count,
        AVG(execution_time_ms)::INTEGER as avg_time,
        AVG(result_count)::INTEGER as avg_results
      FROM query_logs
      WHERE intent IS NOT NULL
      GROUP BY intent
      ORDER BY count DESC
    `);
    
    byIntent.rows.forEach(row => {
      console.log(`  ${row.intent}: ${row.count} queries (avg ${row.avg_time}ms, ${row.avg_results} results)`);
    });
    console.log('');
    
    // Most common queries
    console.log('🔥 Most Common Queries:');
    console.log('-'.repeat(80));
    const common = await pool.query(`
      SELECT 
        query_text,
        COUNT(*) as frequency,
        intent
      FROM query_logs
      GROUP BY query_text, intent
      HAVING COUNT(*) > 1
      ORDER BY frequency DESC
      LIMIT 5
    `);
    
    if (common.rows.length > 0) {
      common.rows.forEach((row, idx) => {
        console.log(`  ${idx + 1}. "${row.query_text}" (${row.frequency}x, intent: ${row.intent})`);
      });
    } else {
      console.log('  No repeated queries yet');
    }
    console.log('');
    
    // Errors
    const errors = await pool.query(`
      SELECT COUNT(*) as count FROM query_logs WHERE error_message IS NOT NULL
    `);
    
    if (errors.rows[0].count > 0) {
      console.log('⚠️  Errors:');
      console.log('-'.repeat(80));
      const errorList = await pool.query(`
        SELECT 
          timestamp,
          query_text,
          error_message
        FROM query_logs
        WHERE error_message IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 5
      `);
      
      errorList.rows.forEach((row, idx) => {
        const time = new Date(row.timestamp).toLocaleString();
        console.log(`  ${idx + 1}. [${time}] "${row.query_text}"`);
        console.log(`     Error: ${row.error_message}`);
      });
      console.log('');
    }
    
    console.log('='.repeat(80));
    console.log('💡 Tip: Query logs help tune the AI classification system');
    console.log('   Review problematic queries to improve routing accuracy');
    console.log('='.repeat(80));
    
  } catch (error) {
    console.error('Error viewing analytics:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

viewAnalytics();
