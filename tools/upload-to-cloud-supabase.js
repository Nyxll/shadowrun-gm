#!/usr/bin/env node

/**
 * Upload data to Cloud Supabase using the Supabase JS client
 * This script reads the ordered SQL files and uploads them via the API
 */

import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Supabase connection from .env
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase credentials in .env file');
  console.error('Required: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

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

async function uploadSQLFile(filePath, fileNum, totalFiles) {
  log(`\n[${fileNum}/${totalFiles}] Processing ${path.basename(filePath)}...`, 'cyan');
  
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Use Supabase RPC to execute raw SQL
  const { data, error } = await supabase.rpc('exec_sql', {
    sql_query: content
  });
  
  if (error) {
    log(`❌ Error: ${error.message}`, 'red');
    return { success: false, error };
  }
  
  log(`✅ Successfully uploaded`, 'green');
  return { success: true };
}

async function main() {
  log('\n🚀 Starting Cloud Supabase Data Upload', 'bright');
  log('=' .repeat(60), 'gray');
  log(`URL: ${supabaseUrl}`, 'gray');
  
  // Find all ordered SQL files
  const projectRoot = path.join(__dirname, '..');
  const files = fs.readdirSync(projectRoot)
    .filter(f => f.startsWith('supabase-data-ordered-part') && f.endsWith('.sql'))
    .sort((a, b) => {
      const numA = parseInt(a.match(/part(\d+)/)[1]);
      const numB = parseInt(b.match(/part(\d+)/)[1]);
      return numA - numB;
    });
  
  if (files.length === 0) {
    log('❌ No ordered SQL files found!', 'red');
    log('Run: node tools/split-sql-ordered.js first', 'yellow');
    process.exit(1);
  }
  
  log(`\n📦 Found ${files.length} SQL files to upload\n`, 'green');
  
  let successCount = 0;
  let errorCount = 0;
  const errors = [];
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const filePath = path.join(projectRoot, file);
    
    const result = await uploadSQLFile(filePath, i + 1, files.length);
    
    if (result.success) {
      successCount++;
    } else {
      errorCount++;
      errors.push({ file, error: result.error });
    }
    
    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  // Summary
  log('\n' + '='.repeat(60), 'gray');
  log('📊 Upload Summary:', 'bright');
  log(`  ✅ Successful: ${successCount}`, 'green');
  log(`  ❌ Errors: ${errorCount}`, errorCount > 0 ? 'red' : 'green');
  
  if (errors.length > 0) {
    log('\n⚠️  Files with errors:', 'yellow');
    errors.forEach(({ file, error }) => {
      log(`  ${file}: ${error.message}`, 'red');
    });
  }
  
  log('\n🎉 Upload process complete!', 'bright');
}

main().catch(error => {
  log(`\n❌ Fatal error: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});
