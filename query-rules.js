#!/usr/bin/env node

import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST,
  port: process.env.POSTGRES_PORT,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB,
});

async function queryRules() {
  try {
    // Query for full auto, darkness, thermographic, smartlink, and range rules
    const queries = [
      'full auto burst fire automatic',
      'darkness visibility light thermographic',
      'smartlink targeting',
      'range distance medium long'
    ];
    
    console.log('Searching for rules about: Full Auto + Darkness + Thermographic + Smartlink + Range\n');
    console.log('='.repeat(80));
    
    for (const query of queries) {
      const result = await pool.query(`
        SELECT title, content, category, subcategory, tags
        FROM rules_content
        WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
        ORDER BY ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) DESC
        LIMIT 3
      `, [query]);
      
      if (result.rows.length > 0) {
        console.log(`\n## Results for: "${query}"\n`);
        result.rows.forEach((row, i) => {
          console.log(`### ${i + 1}. ${row.title}`);
          console.log(`**Category:** ${row.category}${row.subcategory ? ' > ' + row.subcategory : ''}`);
          if (row.tags && row.tags.length > 0) {
            console.log(`**Tags:** ${row.tags.join(', ')}`);
          }
          console.log(`\n${row.content}\n`);
          console.log('-'.repeat(80));
        });
      }
    }
    
    await pool.end();
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

queryRules();
