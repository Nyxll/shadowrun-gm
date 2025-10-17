#!/usr/bin/env node

/**
 * Apply house rules schema to database
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
    console.log('Reading house_rules.sql schema...');
    const schemaPath = path.join(__dirname, '..', 'schema', 'house_rules.sql');
    const schema = fs.readFileSync(schemaPath, 'utf-8');

    console.log('Applying schema to database...');
    await pool.query(schema);

    console.log('✅ Schema applied successfully!');

    // Verify table creation
    const tableCheck = await pool.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
        AND table_name IN ('campaigns', 'house_rules', 'rule_application_log')
      ORDER BY table_name
    `);

    console.log(`✅ Created ${tableCheck.rows.length} tables:`);
    tableCheck.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });

    // Verify functions
    const functionCheck = await pool.query(`
      SELECT routine_name 
      FROM information_schema.routines 
      WHERE routine_schema = 'public' 
        AND routine_name IN (
          'get_active_house_rules',
          'apply_karma_house_rules',
          'get_attribute_limit',
          'log_rule_application'
        )
      ORDER BY routine_name
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
        AND table_name IN ('campaign_summary', 'rule_application_stats')
      ORDER BY table_name
    `);

    console.log(`✅ Created ${viewCheck.rows.length} views:`);
    viewCheck.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });

    console.log('\n🎉 House rules system ready!');
    console.log('\nNext steps:');
    console.log('1. Create campaigns with: INSERT INTO campaigns (name, gm_name) VALUES (...)');
    console.log('2. Add house rules with: INSERT INTO house_rules (campaign_id, rule_name, rule_type, rule_config) VALUES (...)');
    console.log('3. Use get_active_house_rules(campaign_id) to retrieve rules');
    console.log('4. Use apply_karma_house_rules(base_cost, campaign_id, cost_type) to apply multipliers');

  } catch (error) {
    console.error('❌ Error applying schema:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

applySchema().catch(console.error);
