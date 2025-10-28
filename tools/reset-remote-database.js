import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('⚠️  WARNING: This will DROP all tables and recreate them!\n');

const supabase = createClient(supabaseUrl, supabaseKey);

async function resetDatabase() {
  try {
    console.log('🗑️  Dropping all tables...\n');
    
    const tables = ['query_logs', 'rules_content', 'gear', 'totems', 'spells', 'powers', 'metatypes'];
    
    for (const table of tables) {
      console.log(`   Deleting all rows from ${table}...`);
      const { error } = await supabase
        .from(table)
        .delete()
        .neq('id', 0); // Delete all rows
      
      if (error) {
        console.log(`   ⚠️  ${table}: ${error.message}`);
      } else {
        console.log(`   ✅ ${table} cleared`);
      }
    }
    
    console.log('\n✅ All tables cleared!');
    console.log('\n📝 Note: Tables still exist but are empty.');
    console.log('   To recreate schema, use Supabase SQL Editor with supabase-schema-fixed.sql');
    console.log('   Or if you want to drop tables completely, you need to use SQL Editor with:');
    console.log('   DROP TABLE IF EXISTS query_logs, rules_content, gear, totems, spells, powers, metatypes CASCADE;');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

console.log('This script will clear all data from your tables.');
console.log('Press Ctrl+C to cancel, or wait 5 seconds to continue...\n');

setTimeout(() => {
  resetDatabase();
}, 5000);
