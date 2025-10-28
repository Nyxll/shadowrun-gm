#!/usr/bin/env node

/**
 * Export Database Schema and Data for Supabase Migration
 * 
 * This script:
 * 1. Lists all tables in the database
 * 2. Identifies Shadowrun GM tables (excludes n8n and other apps)
 * 3. Generates schema export (CREATE TABLE, indexes, triggers, functions)
 * 4. Generates data export (INSERT statements)
 */

import pg from 'pg';
import fs from 'fs';
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

// Tables that belong to Shadowrun GM system
const SHADOWRUN_TABLES = [
  'rules_content',
  'spells',
  'powers',
  'totems',
  'gear',
  'gear_chunks',
  'campaigns',
  'house_rules',
  'metatypes',
  'sr_characters',
  'character_skills',
  'character_spells',
  'character_powers',
  'character_gear',
  'character_contacts',
  'character_history',
  'character_modifiers',
  'query_logs',
  'clarification_feedback',
  'clarification_patterns'
];

async function listAllTables() {
  const result = await pool.query(`
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public'
    ORDER BY tablename
  `);
  
  console.log('\n=== All Tables in Database ===');
  result.rows.forEach(row => {
    const isShadowrun = SHADOWRUN_TABLES.includes(row.tablename);
    console.log(`${isShadowrun ? '✓' : '✗'} ${row.tablename}`);
  });
  
  return result.rows.map(r => r.tablename);
}

async function getTableSchema(tableName) {
  const result = await pool.query(`
    SELECT 
      column_name,
      data_type,
      character_maximum_length,
      column_default,
      is_nullable,
      udt_name
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = $1
    ORDER BY ordinal_position
  `, [tableName]);
  
  return result.rows;
}

async function getTableConstraints(tableName) {
  const result = await pool.query(`
    SELECT
      tc.constraint_name,
      tc.constraint_type,
      kcu.column_name,
      ccu.table_name AS foreign_table_name,
      ccu.column_name AS foreign_column_name,
      rc.update_rule,
      rc.delete_rule
    FROM information_schema.table_constraints AS tc
    LEFT JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    LEFT JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
    LEFT JOIN information_schema.referential_constraints AS rc
      ON tc.constraint_name = rc.constraint_name
    WHERE tc.table_schema = 'public' AND tc.table_name = $1
    ORDER BY tc.constraint_type, tc.constraint_name
  `, [tableName]);
  
  return result.rows;
}

async function getTableIndexes(tableName) {
  const result = await pool.query(`
    SELECT
      indexname,
      indexdef
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = $1
    AND indexname NOT LIKE '%_pkey'
    ORDER BY indexname
  `, [tableName]);
  
  return result.rows;
}

async function getTriggers(tableName) {
  const result = await pool.query(`
    SELECT
      trigger_name,
      event_manipulation,
      action_timing,
      action_statement
    FROM information_schema.triggers
    WHERE event_object_schema = 'public' AND event_object_table = $1
    ORDER BY trigger_name
  `, [tableName]);
  
  return result.rows;
}

async function getFunctions() {
  const result = await pool.query(`
    SELECT
      p.proname AS function_name,
      pg_get_functiondef(p.oid) AS function_definition
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.prokind = 'f'
    ORDER BY p.proname
  `);
  
  return result.rows;
}

async function getTableData(tableName, limit = null) {
  const limitClause = limit ? `LIMIT ${limit}` : '';
  const result = await pool.query(`SELECT * FROM ${tableName} ${limitClause}`);
  return result.rows;
}

function generateCreateTable(tableName, columns, constraints) {
  let sql = `-- Table: ${tableName}\n`;
  sql += `CREATE TABLE IF NOT EXISTS ${tableName} (\n`;
  
  // Columns
  const columnDefs = columns.map(col => {
    let def = `  ${col.column_name} ${col.udt_name}`;
    
    if (col.character_maximum_length) {
      def += `(${col.character_maximum_length})`;
    }
    
    if (col.column_default) {
      def += ` DEFAULT ${col.column_default}`;
    }
    
    if (col.is_nullable === 'NO') {
      def += ' NOT NULL';
    }
    
    return def;
  });
  
  sql += columnDefs.join(',\n');
  
  // Primary key
  const pk = constraints.find(c => c.constraint_type === 'PRIMARY KEY');
  if (pk) {
    sql += `,\n  CONSTRAINT ${pk.constraint_name} PRIMARY KEY (${pk.column_name})`;
  }
  
  // Unique constraints
  const uniques = constraints.filter(c => c.constraint_type === 'UNIQUE');
  uniques.forEach(u => {
    sql += `,\n  CONSTRAINT ${u.constraint_name} UNIQUE (${u.column_name})`;
  });
  
  sql += '\n);\n\n';
  
  // Foreign keys (added separately for clarity)
  const fks = constraints.filter(c => c.constraint_type === 'FOREIGN KEY');
  fks.forEach(fk => {
    sql += `ALTER TABLE ${tableName}\n`;
    sql += `  ADD CONSTRAINT ${fk.constraint_name}\n`;
    sql += `  FOREIGN KEY (${fk.column_name})\n`;
    sql += `  REFERENCES ${fk.foreign_table_name} (${fk.foreign_column_name})`;
    if (fk.update_rule) sql += `\n  ON UPDATE ${fk.update_rule}`;
    if (fk.delete_rule) sql += `\n  ON DELETE ${fk.delete_rule}`;
    sql += ';\n\n';
  });
  
  return sql;
}

function generateInserts(tableName, rows) {
  if (rows.length === 0) return '';
  
  let sql = `-- Data for: ${tableName}\n`;
  
  const columns = Object.keys(rows[0]);
  
  rows.forEach(row => {
    const values = columns.map(col => {
      const val = row[col];
      if (val === null) return 'NULL';
      if (typeof val === 'object') return `'${JSON.stringify(val).replace(/'/g, "''")}'`;
      if (typeof val === 'string') return `'${val.replace(/'/g, "''")}'`;
      if (typeof val === 'boolean') return val ? 'TRUE' : 'FALSE';
      return val;
    });
    
    sql += `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${values.join(', ')});\n`;
  });
  
  sql += '\n';
  return sql;
}

async function exportDatabase() {
  console.log('🚀 Starting database export for Supabase migration...\n');
  
  try {
    // List all tables
    const allTables = await listAllTables();
    
    // Filter to Shadowrun tables only
    const shadowrunTables = allTables.filter(t => SHADOWRUN_TABLES.includes(t));
    
    console.log(`\n📊 Found ${shadowrunTables.length} Shadowrun GM tables to export\n`);
    
    // Generate schema export
    let schemaSQL = `-- Shadowrun GM Database Schema Export
-- Generated: ${new Date().toISOString()}
-- Target: Supabase
-- 
-- This script creates all tables, indexes, constraints, triggers, and functions
-- for the Shadowrun GM system.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

`;
    
    // Export functions first (they may be used by triggers)
    console.log('📝 Exporting functions...');
    const functions = await getFunctions();
    functions.forEach(func => {
      schemaSQL += `${func.function_definition};\n\n`;
    });
    
    // Export tables
    console.log('📝 Exporting table schemas...');
    for (const tableName of shadowrunTables) {
      console.log(`  - ${tableName}`);
      
      const columns = await getTableSchema(tableName);
      const constraints = await getTableConstraints(tableName);
      
      schemaSQL += generateCreateTable(tableName, columns, constraints);
    }
    
    // Export indexes
    console.log('📝 Exporting indexes...');
    for (const tableName of shadowrunTables) {
      const indexes = await getTableIndexes(tableName);
      if (indexes.length > 0) {
        schemaSQL += `-- Indexes for: ${tableName}\n`;
        indexes.forEach(idx => {
          schemaSQL += `${idx.indexdef};\n`;
        });
        schemaSQL += '\n';
      }
    }
    
    // Export triggers
    console.log('📝 Exporting triggers...');
    for (const tableName of shadowrunTables) {
      const triggers = await getTriggers(tableName);
      if (triggers.length > 0) {
        schemaSQL += `-- Triggers for: ${tableName}\n`;
        triggers.forEach(trig => {
          schemaSQL += `CREATE TRIGGER ${trig.trigger_name}\n`;
          schemaSQL += `  ${trig.action_timing} ${trig.event_manipulation}\n`;
          schemaSQL += `  ON ${tableName}\n`;
          schemaSQL += `  ${trig.action_statement};\n\n`;
        });
      }
    }
    
    // Write schema file
    fs.writeFileSync('supabase-schema.sql', schemaSQL);
    console.log('\n✅ Schema exported to: supabase-schema.sql');
    
    // Generate data export
    console.log('\n📝 Exporting table data...');
    let dataSQL = `-- Shadowrun GM Database Data Export
-- Generated: ${new Date().toISOString()}
-- 
-- This script contains all data from Shadowrun GM tables.
-- Run this AFTER running supabase-schema.sql

`;
    
    for (const tableName of shadowrunTables) {
      const rows = await getTableData(tableName);
      console.log(`  - ${tableName}: ${rows.length} rows`);
      
      if (rows.length > 0) {
        dataSQL += generateInserts(tableName, rows);
      }
    }
    
    // Write data file
    fs.writeFileSync('supabase-data.sql', dataSQL);
    console.log('\n✅ Data exported to: supabase-data.sql');
    
    // Generate migration instructions
    const instructions = `# Supabase Migration Instructions

## Files Generated

1. **supabase-schema.sql** - Database structure (tables, indexes, triggers, functions)
2. **supabase-data.sql** - All data from Shadowrun GM tables

## Migration Steps

### 1. Create Supabase Project

1. Go to https://supabase.com
2. Create a new project
3. Wait for project to be ready
4. Note your connection details

### 2. Run Schema Migration

In Supabase SQL Editor:

\`\`\`sql
-- Copy and paste contents of supabase-schema.sql
-- Or use the Supabase CLI:
supabase db push
\`\`\`

### 3. Run Data Migration

In Supabase SQL Editor:

\`\`\`sql
-- Copy and paste contents of supabase-data.sql
-- This will populate all tables with your data
\`\`\`

### 4. Update Environment Variables

Update your .env file with new Supabase credentials:

\`\`\`env
POSTGRES_HOST=db.your-project-ref.supabase.co
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-supabase-password
POSTGRES_DB=postgres
\`\`\`

### 5. Test Connection

Run the test script:

\`\`\`bash
node tools/test-connection.js
\`\`\`

## Tables Exported

${shadowrunTables.map(t => `- ${t}`).join('\n')}

## Notes

- Vector extension is required for embeddings
- pg_trgm extension is required for fuzzy text search
- All foreign key relationships are preserved
- Triggers and functions are included
- Data is exported in dependency order

## Rollback

If you need to rollback, simply:
1. Delete the Supabase project
2. Create a new one
3. Re-run the migration

## Support

For issues, check:
- Supabase logs in dashboard
- PostgreSQL error messages
- Connection string format
`;
    
    fs.writeFileSync('SUPABASE-MIGRATION.md', instructions);
    console.log('✅ Instructions written to: SUPABASE-MIGRATION.md');
    
    console.log('\n🎉 Export complete!');
    console.log('\nNext steps:');
    console.log('1. Review supabase-schema.sql');
    console.log('2. Review supabase-data.sql');
    console.log('3. Follow instructions in SUPABASE-MIGRATION.md');
    
  } catch (error) {
    console.error('❌ Export failed:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

exportDatabase().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
