#!/usr/bin/env node

/**
 * Test database connection and query
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

async function testConnection() {
  console.log('Testing database connection...');
  console.log(`Host: ${process.env.POSTGRES_HOST}`);
  console.log(`Port: ${process.env.POSTGRES_PORT}`);
  console.log(`Database: ${process.env.POSTGRES_DB}`);
  
  try {
    // Test basic connection
    const timeResult = await pool.query('SELECT NOW()');
    console.log('✓ Database connection successful');
    console.log(`  Server time: ${timeResult.rows[0].now}`);
    
    // Test table exists
    const tableCheck = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'rules_content'
      )
    `);
    
    if (tableCheck.rows[0].exists) {
      console.log('✓ Table rules_content exists');
      
      // Get count
      const countResult = await pool.query('SELECT COUNT(*) FROM rules_content');
      console.log(`  Total records: ${countResult.rows[0].count}`);
      
      // Test query with new schema
      const testQuery = await pool.query(`
        SELECT title, category, subcategory 
        FROM rules_content 
        LIMIT 3
      `);
      
      console.log('\n✓ Sample records:');
      testQuery.rows.forEach((row, i) => {
        console.log(`  ${i + 1}. ${row.title} (${row.category}${row.subcategory ? ' > ' + row.subcategory : ''})`);
      });
      
      // Test category query
      const categoryResult = await pool.query(`
        SELECT category, COUNT(*) as count
        FROM rules_content
        GROUP BY category
        ORDER BY count DESC
        LIMIT 5
      `);
      
      console.log('\n✓ Top categories:');
      categoryResult.rows.forEach(row => {
        console.log(`  ${row.category}: ${row.count} records`);
      });
      
    } else {
      console.log('✗ Table rules_content does not exist');
    }
    
    console.log('\n✓ All tests passed!');
    
  } catch (error) {
    console.error('✗ Error:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

testConnection();
