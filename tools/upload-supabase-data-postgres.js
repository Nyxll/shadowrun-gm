#!/usr/bin/env node

/**
 * Upload Supabase Data via Direct Postgres Connection
 * 
 * This script uses a direct Postgres connection to execute the SQL file.
 */

import pg from 'pg';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase Postgres connection
// Try different connection formats
const connectionString = 'postgresql://postgres.bxjguoeuqeucfrwabmga:h0WNNseI2Xbm6ZRU1BRtQQJZlIqrIq@aws-0-us-east-1.pooler.supabase.com:6543/postgres';

// Colors
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function uploadData() {
  log('\n🚀 Starting Supabase Data Upload via Postgres', 'bright');
  log('=' .repeat(60), 'gray');
  
  // Read the data file
  const dataPath = path.join(__dirname, '..', 'supabase-data.sql');
  
  if (!fs.existsSync(dataPath)) {
    log('❌ Data file not found: ' + dataPath, 'red');
    process.exit(1);
  }
  
  log(`📄 Reading SQL file...`, 'cyan');
  const sqlContent = fs.readFileSync(dataPath, 'utf8');
  
  // Create Postgres client
  const client = new pg.Client({ connectionString });
  
  try {
    log('🔌 Connecting to Supabase Postgres...', 'cyan');
    await client.connect();
    log('✅ Connected successfully!', 'green');
    
    // Split into individual statements
    log('\n📝 Parsing SQL statements...', 'cyan');
    const statements = sqlContent
      .split('\n')
      .filter(line => line.trim() && !line.trim().startsWith('--'))
      .join('\n')
      .split(';')
      .map(s => s.trim())
      .filter(s => s.length > 0);
    
    log(`✅ Found ${statements.length} SQL statements\n`, 'green');
    
    let successCount = 0;
    let errorCount = 0;
    const errors = [];
    
    // Execute each statement
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      const num = i + 1;
      
      // Extract table name for display
      let tableName = 'unknown';
      const match = statement.match(/INSERT INTO\s+(\w+)/i);
      if (match) tableName = match[1];
      
      process.stdout.write(`[${num}/${statements.length}] ${tableName}... `);
      
      try {
        await client.query(statement + ';');
        log('✅', 'green');
        successCount++;
      } catch (error) {
        // Check if it's a duplicate error
        if (error.message.includes('duplicate') || error.message.includes('already exists')) {
          log('⏭️  (duplicate)', 'yellow');
        } else {
          log('❌', 'red');
          errorCount++;
          errors.push({
            statement: num,
            table: tableName,
            error: error.message,
            sql: statement.substring(0, 100) + '...'
          });
        }
      }
    }
    
    // Summary
    log('\n' + '='.repeat(60), 'gray');
    log('📊 Upload Summary:', 'bright');
    log(`  ✅ Successful: ${successCount}`, 'green');
    log(`  ❌ Errors: ${errorCount}`, errorCount > 0 ? 'red' : 'green');
    
    if (errors.length > 0) {
      log('\n⚠️  Errors encountered:', 'yellow');
      errors.slice(0, 5).forEach(err => {
        log(`\n  Statement #${err.statement} (${err.table})`, 'red');
        log(`  Error: ${err.error}`, 'gray');
      });
      
      if (errors.length > 5) {
        log(`\n  ... and ${errors.length - 5} more errors`, 'gray');
      }
      
      // Write error log
      const errorLogPath = path.join(__dirname, '..', 'postgres-upload-errors.log');
      const errorLog = errors.map(err => 
        `Statement: ${err.statement}\nTable: ${err.table}\nError: ${err.error}\nSQL: ${err.sql}\n${'='.repeat(80)}\n`
      ).join('\n');
      
      fs.writeFileSync(errorLogPath, errorLog);
      log(`\n📝 Full error log: ${errorLogPath}`, 'yellow');
    }
    
    log('\n🎉 Data upload complete!', 'bright');
    
  } catch (error) {
    log(`\n❌ Fatal error: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  } finally {
    await client.end();
    log('🔌 Connection closed', 'gray');
  }
}

uploadData();
