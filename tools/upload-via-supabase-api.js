import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('Connecting to Supabase via REST API...\n');
console.log(`URL: ${supabaseUrl}\n`);

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  try {
    console.log('🔍 Testing connection...');
    
    // Try to query a table to test connection
    const { data, error } = await supabase
      .from('metatypes')
      .select('count')
      .limit(1);
    
    if (error) {
      console.error('❌ Connection test failed:');
      console.error(`   ${error.message}`);
      return false;
    }
    
    console.log('✅ Connection successful!\n');
    
    // List all tables
    console.log('📋 Checking available tables...');
    const tables = ['metatypes', 'powers', 'spells', 'totems', 'gear', 'rules_content', 'query_logs'];
    
    for (const table of tables) {
      const { count, error } = await supabase
        .from(table)
        .select('*', { count: 'exact', head: true });
      
      if (!error) {
        console.log(`   ✅ ${table}: ${count} rows`);
      } else {
        console.log(`   ⚠️  ${table}: ${error.message}`);
      }
    }
    
    return true;
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    return false;
  }
}

testConnection();
