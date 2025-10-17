#!/usr/bin/env node

/**
 * Load Powers from CSV file into PostgreSQL database
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

function parseCSV(content) {
  const lines = content.split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  const powers = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const values = line.split(',').map(v => v.trim());
    if (values.length < 3) continue;

    const power = {
      page_reference: values[0],
      name: values[1],
      cost: parseFloat(values[2]) || 0,
      modifiers: values[3] || '',
    };

    powers.push(power);
  }

  return powers;
}

async function loadPowers() {
  try {
    console.log('Reading POWERS.csv...');
    const csvPath = 'G:\\My Drive\\SR-ai\\DataTables\\POWERS.csv';
    const content = fs.readFileSync(csvPath, 'utf-8');
    
    const powers = parseCSV(content);
    console.log(`Parsed ${powers.length} powers from CSV`);

    // Clear existing powers
    console.log('Clearing existing powers...');
    await pool.query('DELETE FROM powers');

    // Insert powers
    console.log('Inserting powers...');
    let inserted = 0;

    for (const power of powers) {
      // Determine power type (all are adept for now)
      const powerType = 'adept';
      
      // Build description from modifiers
      let description = `Adept power: ${power.name}`;
      if (power.modifiers) {
        description += `\n${power.modifiers}`;
      }

      try {
        await pool.query(`
          INSERT INTO powers (
            name,
            power_type,
            power_point_cost,
            description,
            page_reference
          ) VALUES ($1, $2, $3, $4, $5)
        `, [
          power.name,
          powerType,
          power.cost,
          description,
          power.page_reference
        ]);
        inserted++;
      } catch (error) {
        console.error(`Error inserting power ${power.name}:`, error.message);
      }
    }

    console.log(`\n✅ Successfully loaded ${inserted} powers`);

    // Show some stats
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total,
        MIN(power_point_cost) as min_cost,
        MAX(power_point_cost) as max_cost,
        AVG(power_point_cost) as avg_cost
      FROM powers
    `);

    console.log('\nPowers Statistics:');
    console.log(`Total: ${result.rows[0].total}`);
    console.log(`Cost Range: ${result.rows[0].min_cost} - ${result.rows[0].max_cost}`);
    console.log(`Average Cost: ${parseFloat(result.rows[0].avg_cost).toFixed(2)}`);

    // Show melee-focused powers
    const meleeResult = await pool.query(`
      SELECT name, power_point_cost, description
      FROM powers
      WHERE name ILIKE '%killing hands%'
         OR name ILIKE '%counterstrike%'
         OR name ILIKE '%smashing blow%'
         OR name ILIKE '%nerve strike%'
         OR name ILIKE '%distance strike%'
         OR name ILIKE '%improved armed combat%'
         OR name ILIKE '%improved unarmed combat%'
      ORDER BY name
    `);

    console.log('\n🥊 Melee-Focused Powers:');
    for (const power of meleeResult.rows) {
      console.log(`  - ${power.name} (${power.power_point_cost} points)`);
    }

  } catch (error) {
    console.error('Error loading powers:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

loadPowers().catch(console.error);
