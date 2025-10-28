/**
 * Run Migration 005
 * Executes the query_logs enhancement migration
 * 
 * NOTE: This script splits the SQL file into individual statements
 * to avoid hanging issues with multi-statement execution.
 * 
 * Alternative: Use psql directly for more reliable execution:
 *   psql -U postgres -d shadowrun_gm -f migrations/005_enhance_query_logs_for_training.sql
 */

import pkg from 'pg';
const { Pool } = pkg;
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Database configuration
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'shadowrun_gm',
  password: process.env.DB_PASSWORD || 'postgres',
  port: process.env.DB_PORT || 5432,
});

/**
 * Split SQL file into individual statements
 * Handles multi-line statements and comments
 */
function splitSQLStatements(sql) {
  const statements = [];
  let currentStatement = '';
  let inFunction = false;
  let dollarQuoteTag = null;
  
  const lines = sql.split('\n');
  
  for (let line of lines) {
    const trimmedLine = line.trim();
    
    // Skip empty lines and comments
    if (!trimmedLine || trimmedLine.startsWith('--')) {
      continue;
    }
    
    // Track if we're inside a function definition ($$...$$)
    const dollarMatches = trimmedLine.match(/\$\$/g);
    if (dollarMatches) {
      for (let match of dollarMatches) {
        if (dollarQuoteTag === null) {
          dollarQuoteTag = match;
          inFunction = true;
        } else {
          dollarQuoteTag = null;
          inFunction = false;
        }
      }
    }
    
    currentStatement += line + '\n';
    
    // If we hit a semicolon and we're not in a function, that's the end of a statement
    if (trimmedLine.endsWith(';') && !inFunction) {
      statements.push(currentStatement.trim());
      currentStatement = '';
    }
  }
  
  // Add any remaining statement
  if (currentStatement.trim()) {
    statements.push(currentStatement.trim());
  }
  
  return statements.filter(s => s.length > 0);
}

async function runMigration() {
  const client = await pool.connect();
  
  try {
    console.log('Running migration 005_enhance_query_logs_for_training.sql...\n');
    
    // Read migration file
    const migrationPath = path.join(__dirname, 'migrations', '005_enhance_query_logs_for_training.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf-8');
    
    // Split into individual statements
    const statements = splitSQLStatements(migrationSQL);
    console.log(`Found ${statements.length} SQL statements to execute\n`);
    
    // Execute each statement in a transaction
    await client.query('BEGIN');
    
    let executedCount = 0;
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      
      // Show progress for major operations
      if (statement.includes('ALTER TABLE')) {
        console.log(`[${i + 1}/${statements.length}] Altering table...`);
      } else if (statement.includes('CREATE FUNCTION')) {
        console.log(`[${i + 1}/${statements.length}] Creating function...`);
      } else if (statement.includes('CREATE TRIGGER')) {
        console.log(`[${i + 1}/${statements.length}] Creating trigger...`);
      } else if (statement.includes('CREATE INDEX')) {
        console.log(`[${i + 1}/${statements.length}] Creating index...`);
      } else if (statement.includes('CREATE OR REPLACE VIEW')) {
        console.log(`[${i + 1}/${statements.length}] Creating view...`);
      } else if (statement.includes('DROP TRIGGER')) {
        console.log(`[${i + 1}/${statements.length}] Dropping old trigger...`);
      } else if (statement.includes('COMMENT')) {
        // Skip logging comments to reduce noise
      } else {
        console.log(`[${i + 1}/${statements.length}] Executing statement...`);
      }
      
      try {
        await client.query(statement);
        executedCount++;
      } catch (err) {
        // Some statements might fail if already applied (e.g., ADD COLUMN IF NOT EXISTS)
        // We'll continue but log the error
        if (!err.message.includes('already exists') && !err.message.includes('does not exist')) {
          console.warn(`  ⚠️  Warning: ${err.message}`);
        }
      }
    }
    
    await client.query('COMMIT');
    console.log(`\n✓ Successfully executed ${executedCount}/${statements.length} statements\n`);
    
    // Verify new columns exist
    const result = await client.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'query_logs' 
        AND column_name IN ('is_training_data', 'expected_intent', 'gm_response', 'dice_rolls', 'is_correct', 'confidence', 'classification_method', 'training_source')
      ORDER BY column_name
    `);
    
    console.log('New columns added to query_logs:');
    result.rows.forEach(row => {
      console.log(`  ✓ ${row.column_name} (${row.data_type})`);
    });
    
    // Verify views exist
    const viewsResult = await client.query(`
      SELECT table_name 
      FROM information_schema.views 
      WHERE table_schema = 'public' 
        AND table_name LIKE 'training%'
      ORDER BY table_name
    `);
    
    console.log('\nViews created:');
    viewsResult.rows.forEach(row => {
      console.log(`  ✓ ${row.table_name}`);
    });
    
    // Verify trigger exists
    const triggerResult = await client.query(`
      SELECT trigger_name 
      FROM information_schema.triggers 
      WHERE event_object_table = 'query_logs' 
        AND trigger_name = 'trigger_update_query_correctness'
    `);
    
    console.log('\nTrigger created:');
    if (triggerResult.rows.length > 0) {
      console.log(`  ✓ trigger_update_query_correctness`);
    } else {
      console.log(`  ⚠️  Warning: trigger not found`);
    }
    
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('\n✗ Migration failed:', err.message);
    console.error('\nTip: You can also run the migration directly with psql:');
    console.error('  psql -U postgres -d shadowrun_gm -f migrations/005_enhance_query_logs_for_training.sql');
    throw err;
  } finally {
    client.release();
  }
}

// Run migration
runMigration()
  .then(() => {
    console.log('\n✓ Migration complete!');
    console.log('\nNext steps:');
    console.log('  1. node import-training-data.js  (import training queries)');
    console.log('  2. node training-processor.js    (process and respond to queries)');
    pool.end();
    process.exit(0);
  })
  .catch((err) => {
    console.error('\n✗ Migration failed:', err.message);
    pool.end();
    process.exit(1);
  });
