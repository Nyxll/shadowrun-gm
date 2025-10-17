#!/usr/bin/env node

/**
 * Apply Character System Schema
 * Creates all character-related tables in the database
 */

import pg from 'pg';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const { Pool } = pg;

// Use hardcoded values from MCP config since .env loading is problematic
const pool = new Pool({
  host: process.env.POSTGRES_HOST || '127.0.0.1',
  port: parseInt(process.env.POSTGRES_PORT || '5434'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'daf562f1a5bccb27ff6a7de5c0b5Wq',
  database: process.env.POSTGRES_DB || 'postgres',
});

async function applySchema() {
  console.log('Applying character system schema...\n');

  try {
    // Read the schema file
    const schemaPath = path.join(__dirname, '..', 'schema', 'character_system.sql');
    const schema = fs.readFileSync(schemaPath, 'utf8');

    // Execute the schema
    await pool.query(schema);

    console.log('✓ Character system schema applied successfully!');
    console.log('\nTables created:');
    console.log('  - campaigns');
    console.log('  - metatypes');
    console.log('  - sr_characters');
    console.log('  - character_skills');
    console.log('  - character_spells');
    console.log('  - character_powers');
    console.log('  - character_gear');
    console.log('  - character_contacts');
    console.log('  - character_history');
    console.log('  - character_modifiers');

    // Insert default metatypes
    console.log('\nInserting default metatypes...');
    await pool.query(`
      INSERT INTO metatypes (name, body_range, quickness_range, strength_range, charisma_range, intelligence_range, willpower_range, reaction_range, essence_range, magic_range)
      VALUES 
        ('human', ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[0, 6]),
        ('elf', ARRAY[1, 6], ARRAY[1, 7], ARRAY[1, 6], ARRAY[1, 8], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[0, 6]),
        ('dwarf', ARRAY[1, 7], ARRAY[1, 6], ARRAY[1, 7], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 7], ARRAY[1, 6], ARRAY[1, 6], ARRAY[0, 6]),
        ('ork', ARRAY[1, 8], ARRAY[1, 6], ARRAY[1, 8], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[0, 6]),
        ('troll', ARRAY[1, 9], ARRAY[1, 6], ARRAY[1, 9], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[1, 6], ARRAY[0, 6])
      ON CONFLICT (name) DO NOTHING
    `);

    console.log('✓ Default metatypes inserted!');
    console.log('\nSchema application complete!');
  } catch (error) {
    console.error('Error applying schema:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

applySchema();
