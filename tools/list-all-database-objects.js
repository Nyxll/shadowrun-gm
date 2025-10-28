import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function listAllObjects() {
  try {
    console.log('📋 Listing all database objects...\n');
    
    // This won't work via REST API - we need to provide a manual list
    console.log('⚠️  Cannot query system tables via REST API');
    console.log('Please run this SQL in Supabase SQL Editor to see all objects:\n');
    
    const sql = `
-- List all tables
SELECT 'TABLE' as type, table_name as name
FROM information_schema.tables 
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
UNION ALL
-- List all views
SELECT 'VIEW' as type, table_name as name
FROM information_schema.views
WHERE table_schema = 'public'
UNION ALL
-- List all sequences
SELECT 'SEQUENCE' as type, sequence_name as name
FROM information_schema.sequences
WHERE sequence_schema = 'public'
UNION ALL
-- List all functions
SELECT 'FUNCTION' as type, routine_name as name
FROM information_schema.routines
WHERE routine_schema = 'public'
UNION ALL
-- List all triggers
SELECT 'TRIGGER' as type, trigger_name as name
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY type, name;
`;
    
    console.log(sql);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

listAllObjects();
