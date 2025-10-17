#!/usr/bin/env node

/**
 * Apply query logs schema to database
 */

import pg from 'pg';
import dotenv from 'dotenv';
import fs from 'fs';
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

async function applySchema() {
  try {
    console.log('Connecting to database...');
    
    // Read schema file
    const schemaPath = path.join(__dirname, '..', 'schema', 'query_logs.sql');
    const schema = fs.readFileSync(schemaPath, 'utf8');
    
    console.log('Applying query logs schema...');
    
    // First, drop the table if it exists
    console.log('Dropping existing table...');
    await pool.query('DROP TABLE IF EXISTS query_logs CASCADE');
    
    // Split into individual statements and execute separately
    const statements = schema
      .split(';')
      .map(s => s.trim())
      .filter(s => s.length > 0 && !s.startsWith('--') && !s.includes('DROP TABLE'));
    
    for (const statement of statements) {
      if (statement.trim()) {
        await pool.query(statement);
      }
    }
    
    console.log('✅ Query logs schema applied successfully!');
    
    // Verify table was created
    const result = await pool.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'query_logs'
      ORDER BY ordinal_position
    `);
    
    console.log('\nTable structure:');
    result.rows.forEach(row => {
      console.log(`  - ${row.column_name}: ${row.data_type}`);
    });
    
    // Check views
    const views = await pool.query(`
      SELECT table_name 
      FROM information_schema.views 
      WHERE table_name IN ('query_analytics', 'common_queries', 'problematic_queries')
    `);
    
    console.log('\nViews created:');
    views.rows.forEach(row => {
      console.log(`  - ${row.table_name}`);
    });
    
  } catch (error) {
    console.error('Error applying schema:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

applySchema();
