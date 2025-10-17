#!/usr/bin/env node

/**
 * Apply character_modifiers schema to database
 */

import pg from 'pg';
import { config } from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

config({ path: path.join(__dirname, '..', '.env') });

const { Pool } = pg;

const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
});

async function applySchema() {
  try {
    console.log('Reading character_modifiers.sql schema...');
    const schemaPath = path.join(__dirname, '..', 'schema', 'character_modifiers.sql');
    const schema = fs.readFileSync(schemaPath, 'utf-8');

    console.log('Applying schema to database...');
    await pool.query(schema);

    console.log('✅ Schema applied successfully!');

    // Verify table creation
    const tableCheck = await pool.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
        AND table_name = 'character_modifiers'
    `);

    if (tableCheck.rows.length > 0) {
      console.log('✅ character_modifiers table created');
    }

    // Verify functions
    const functionCheck = await pool.query(`
      SELECT routine_name 
      FROM information_schema.routines 
      WHERE routine_schema = 'public' 
        AND routine_name IN (
          'get_active_modifiers',
          'calculate_modifier_total',
          'get_augmented_attribute',
          'calculate_combat_pool',
          'calculate_spell_pool',
          'calculate_initiative'
        )
    `);

    console.log(`✅ Created ${functionCheck.rows.length} helper functions:`);
    functionCheck.rows.forEach(row => {
      console.log(`   - ${row.routine_name}`);
    });

    // Verify views
    const viewCheck = await pool.query(`
      SELECT table_name 
      FROM information_schema.views 
      WHERE table_schema = 'public' 
        AND table_name IN ('character_augmented_stats', 'active_modifiers_summary')
    `);

    console.log(`✅ Created ${viewCheck.rows.length} views:`);
    viewCheck.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });

    console.log('\n🎉 Character modifiers system ready!');

  } catch (error) {
    console.error('❌ Error applying schema:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

applySchema().catch(console.error);
