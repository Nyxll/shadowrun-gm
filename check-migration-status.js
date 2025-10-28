/**
 * Check Migration Status
 * Verifies if migration 005 has been applied
 */

import 'dotenv/config';
import pkg from 'pg';
const { Pool } = pkg;

// Database configuration
const pool = new Pool({
  user: process.env.POSTGRES_USER || process.env.DB_USER || 'postgres',
  host: process.env.POSTGRES_HOST || process.env.DB_HOST || 'localhost',
  database: process.env.POSTGRES_DB || process.env.DB_NAME || 'postgres',
  password: process.env.POSTGRES_PASSWORD || process.env.DB_PASSWORD || 'postgres',
  port: process.env.POSTGRES_PORT || process.env.DB_PORT || 5432,
});

async function checkStatus() {
  const client = await pool.connect();
  
  try {
    console.log('Checking migration status...\n');
    
    // Check if new columns exist
    const columnsResult = await client.query(`
      SELECT column_name, data_type, is_nullable
      FROM information_schema.columns 
      WHERE table_name = 'query_logs' 
        AND column_name IN ('is_training_data', 'expected_intent', 'gm_response', 'dice_rolls', 'is_correct', 'confidence', 'classification_method', 'training_source')
      ORDER BY column_name
    `);
    
    console.log('=== MIGRATION COLUMNS STATUS ===');
    if (columnsResult.rows.length === 0) {
      console.log('❌ Migration NOT applied - no new columns found');
    } else {
      console.log(`✓ Found ${columnsResult.rows.length}/8 expected columns:\n`);
      columnsResult.rows.forEach(row => {
        console.log(`  ✓ ${row.column_name.padEnd(25)} ${row.data_type.padEnd(20)} ${row.is_nullable === 'YES' ? 'NULL' : 'NOT NULL'}`);
      });
      
      if (columnsResult.rows.length < 8) {
        console.log('\n⚠️  WARNING: Migration partially applied - some columns missing');
      }
    }
    
    // Check if views exist
    const viewsResult = await client.query(`
      SELECT table_name 
      FROM information_schema.views 
      WHERE table_schema = 'public' 
        AND table_name LIKE 'training%'
      ORDER BY table_name
    `);
    
    console.log('\n=== TRAINING VIEWS STATUS ===');
    if (viewsResult.rows.length === 0) {
      console.log('❌ No training views found');
    } else {
      console.log(`✓ Found ${viewsResult.rows.length}/4 expected views:\n`);
      viewsResult.rows.forEach(row => {
        console.log(`  ✓ ${row.table_name}`);
      });
    }
    
    // Check if trigger exists
    const triggerResult = await client.query(`
      SELECT trigger_name 
      FROM information_schema.triggers 
      WHERE event_object_table = 'query_logs' 
        AND trigger_name = 'set_is_correct_trigger'
    `);
    
    console.log('\n=== TRIGGER STATUS ===');
    if (triggerResult.rows.length === 0) {
      console.log('❌ Trigger not found');
    } else {
      console.log('✓ set_is_correct_trigger exists');
    }
    
    // Check for training data
    const dataResult = await client.query(`
      SELECT 
        COUNT(*) as total_queries,
        COUNT(CASE WHEN is_training_data = TRUE THEN 1 END) as training_queries,
        COUNT(CASE WHEN is_training_data = TRUE AND gm_response IS NOT NULL THEN 1 END) as processed_queries
      FROM query_logs
    `);
    
    console.log('\n=== DATA STATUS ===');
    if (dataResult.rows.length > 0) {
      const data = dataResult.rows[0];
      console.log(`Total queries in database: ${data.total_queries}`);
      console.log(`Training queries imported: ${data.training_queries}`);
      console.log(`Training queries processed: ${data.processed_queries}`);
      
      if (data.training_queries > 0) {
        const percentProcessed = ((data.processed_queries / data.training_queries) * 100).toFixed(1);
        console.log(`Processing progress: ${percentProcessed}%`);
      }
    }
    
    // Overall status
    console.log('\n=== OVERALL STATUS ===');
    const migrationComplete = columnsResult.rows.length === 8 && viewsResult.rows.length === 4 && triggerResult.rows.length === 1;
    
    if (migrationComplete) {
      console.log('✓ Migration 005 is COMPLETE');
      console.log('\nNext steps:');
      console.log('  1. Run: node import-training-data.js (if not done)');
      console.log('  2. Run: node training-processor.js (to process queries)');
    } else {
      console.log('❌ Migration 005 is INCOMPLETE or NOT RUN');
      console.log('\nTo apply migration:');
      console.log('  Option 1: psql -U postgres -d shadowrun_gm -f migrations/005_enhance_query_logs_for_training.sql');
      console.log('  Option 2: node run-migration.js');
    }
    
  } catch (err) {
    console.error('Error checking status:', err.message);
    throw err;
  } finally {
    client.release();
  }
}

// Run check
checkStatus()
  .then(() => {
    pool.end();
    process.exit(0);
  })
  .catch((err) => {
    console.error('\nCheck failed:', err.message);
    pool.end();
    process.exit(1);
  });
