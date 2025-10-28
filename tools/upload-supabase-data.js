#!/usr/bin/env node

/**
 * Upload Supabase Data Incrementally
 * 
 * This script reads the supabase-data.sql file and uploads all the
 * Shadowrun data to Supabase in manageable batches.
 */

import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase configuration
const supabaseUrl = 'https://bxjguoeuqeucfrwabmga.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4amd1b2V1cWV1Y2Zyd2FibWdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3OTk3ODYsImV4cCI6MjA3NjM3NTc4Nn0.qmtttCNM5yIHgN9mgD1zcQRQbSU8hI32BW5kBO_n6io';

const supabase = createClient(supabaseUrl, supabaseKey);

// Colors for console output
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

function parseInsertStatements(sqlContent) {
  const statements = [];
  const lines = sqlContent.split('\n');
  let currentStatement = '';
  let inStatement = false;
  let tableName = '';
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    // Skip comments and empty lines
    if (!trimmed || trimmed.startsWith('--')) {
      continue;
    }
    
    // Start of INSERT statement
    if (trimmed.toUpperCase().startsWith('INSERT INTO')) {
      inStatement = true;
      currentStatement = line + '\n';
      
      // Extract table name
      const match = trimmed.match(/INSERT INTO\s+(\w+)/i);
      if (match) {
        tableName = match[1];
      }
      continue;
    }
    
    if (inStatement) {
      currentStatement += line + '\n';
      
      // End of statement
      if (trimmed.endsWith(';')) {
        statements.push({
          table: tableName,
          sql: currentStatement.trim()
        });
        currentStatement = '';
        inStatement = false;
        tableName = '';
      }
    }
  }
  
  return statements;
}

function parseInsertData(insertSQL) {
  // Extract table name
  const tableMatch = insertSQL.match(/INSERT INTO\s+(\w+)/i);
  if (!tableMatch) return null;
  
  const tableName = tableMatch[1];
  
  // Extract column names
  const columnsMatch = insertSQL.match(/\(([^)]+)\)\s+VALUES/i);
  if (!columnsMatch) return null;
  
  const columns = columnsMatch[1].split(',').map(c => c.trim());
  
  // Extract values - this is complex due to nested parentheses and quotes
  const valuesSection = insertSQL.substring(insertSQL.toUpperCase().indexOf('VALUES') + 6);
  const rows = [];
  
  let currentRow = '';
  let parenDepth = 0;
  let inString = false;
  let stringChar = '';
  
  for (let i = 0; i < valuesSection.length; i++) {
    const char = valuesSection[i];
    const prevChar = i > 0 ? valuesSection[i - 1] : '';
    
    // Track string boundaries
    if ((char === "'" || char === '"') && prevChar !== '\\') {
      if (!inString) {
        inString = true;
        stringChar = char;
      } else if (char === stringChar) {
        inString = false;
      }
    }
    
    // Track parentheses depth (only when not in string)
    if (!inString) {
      if (char === '(') parenDepth++;
      if (char === ')') parenDepth--;
      
      // End of a row
      if (parenDepth === 0 && currentRow && (char === ',' || char === ';')) {
        rows.push(currentRow.trim());
        currentRow = '';
        continue;
      }
    }
    
    if (parenDepth > 0) {
      currentRow += char;
    }
  }
  
  // Add last row if exists
  if (currentRow.trim()) {
    rows.push(currentRow.trim());
  }
  
  return {
    table: tableName,
    columns,
    rows
  };
}

async function uploadData() {
  log('\n🚀 Starting Supabase Data Upload', 'bright');
  log('=' .repeat(60), 'gray');
  
  // Read the data file
  const dataPath = path.join(__dirname, '..', 'supabase-data.sql');
  
  if (!fs.existsSync(dataPath)) {
    log('❌ Data file not found: ' + dataPath, 'red');
    process.exit(1);
  }
  
  log(`📄 Reading data from: ${dataPath}`, 'cyan');
  const sqlContent = fs.readFileSync(dataPath, 'utf8');
  
  log('📝 Parsing INSERT statements...', 'cyan');
  const statements = parseInsertStatements(sqlContent);
  
  log(`\n✅ Found ${statements.length} INSERT statements\n`, 'green');
  
  // Group by table
  const tableGroups = {};
  statements.forEach(stmt => {
    if (!tableGroups[stmt.table]) {
      tableGroups[stmt.table] = [];
    }
    tableGroups[stmt.table].push(stmt.sql);
  });
  
  log('📊 Data breakdown by table:', 'cyan');
  Object.keys(tableGroups).forEach(table => {
    log(`  - ${table}: ${tableGroups[table].length} INSERT statements`, 'gray');
  });
  log('');
  
  let totalSuccess = 0;
  let totalErrors = 0;
  const errors = [];
  
  // Process each table
  for (const [tableName, inserts] of Object.entries(tableGroups)) {
    log(`\n📦 Processing table: ${tableName}`, 'bright');
    log('-'.repeat(60), 'gray');
    
    let tableSuccess = 0;
    let tableErrors = 0;
    
    for (let i = 0; i < inserts.length; i++) {
      const insertSQL = inserts[i];
      const num = i + 1;
      
      process.stdout.write(`  [${num}/${inserts.length}] Inserting data... `);
      
      try {
        // Use Supabase's REST API to execute raw SQL
        const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify({ query: insertSQL })
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || `HTTP ${response.status}`);
        }
        
        log('✅', 'green');
        tableSuccess++;
        totalSuccess++;
        
      } catch (error) {
        // Check if it's a duplicate key error (which we can skip)
        if (error.message && (error.message.includes('duplicate') || error.message.includes('already exists'))) {
          log('⏭️  (duplicate)', 'yellow');
        } else {
          log('❌', 'red');
          tableErrors++;
          totalErrors++;
          errors.push({
            table: tableName,
            statement: num,
            error: error.message,
            sql: insertSQL.substring(0, 200) + '...'
          });
        }
      }
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    log(`  Table summary: ${tableSuccess} success, ${tableErrors} errors`, tableErrors > 0 ? 'yellow' : 'green');
  }
  
  // Final Summary
  log('\n' + '='.repeat(60), 'gray');
  log('📊 Upload Summary:', 'bright');
  log(`  ✅ Successful inserts: ${totalSuccess}`, 'green');
  log(`  ❌ Failed inserts: ${totalErrors}`, totalErrors > 0 ? 'red' : 'green');
  
  if (errors.length > 0) {
    log('\n⚠️  Errors encountered:', 'yellow');
    errors.slice(0, 10).forEach(err => {
      log(`\n  Table: ${err.table}, Statement #${err.statement}`, 'red');
      log(`  Error: ${err.error}`, 'gray');
    });
    
    if (errors.length > 10) {
      log(`\n  ... and ${errors.length - 10} more errors`, 'gray');
    }
    
    // Write full error log
    const errorLogPath = path.join(__dirname, '..', 'data-upload-errors.log');
    const errorLog = errors.map(err => 
      `Table: ${err.table}\nStatement: ${err.statement}\nError: ${err.error}\nSQL: ${err.sql}\n${'='.repeat(80)}\n`
    ).join('\n');
    
    fs.writeFileSync(errorLogPath, errorLog);
    log(`\n📝 Full error log written to: ${errorLogPath}`, 'yellow');
  }
  
  log('\n🎉 Data upload complete!', 'bright');
}

// Run the upload
uploadData().catch(error => {
  log(`\n❌ Fatal error: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});
