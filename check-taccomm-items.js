#!/usr/bin/env node

import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;
const pool = new Pool({
  host: process.env.POSTGRES_HOST,
  port: process.env.POSTGRES_PORT,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB
});

const itemsToCheck = [
  'Secured Short-Haul Link',
  'Secured Long-Haul Link',
  'Secured Uplink',
  'Unsecured Short-Haul Link',
  'Unsecured Long-Haul Link',
  'Unsecured Uplink',
  'Laser Link (TacComm)',
  'Master Unit (TacComm)',
  'Microwave Link (TacComm)',
  'Personal Comm Unit (TacComm)',
  'Portable Master Unit (TacComm)',
  'Satellite Uplink (TacComm)',
  'Radio Jammer',
  'Dikote TM (100 cm^3)'
];

async function checkItems() {
  console.log('Checking TacComm items in database...\n');
  
  let found = 0;
  let missing = 0;
  
  for (const itemName of itemsToCheck) {
    const result = await pool.query(
      'SELECT id, name, category, subcategory FROM gear WHERE name = $1',
      [itemName]
    );
    
    if (result.rows.length > 0) {
      const item = result.rows[0];
      console.log(`✅ ${item.name}`);
      console.log(`   ID: ${item.id}, Category: ${item.category}, Subcategory: ${item.subcategory}`);
      found++;
    } else {
      console.log(`❌ ${itemName} - NOT FOUND`);
      missing++;
    }
  }
  
  console.log(`\n═══════════════════════════════════════`);
  console.log(`Found: ${found}/${itemsToCheck.length}`);
  console.log(`Missing: ${missing}/${itemsToCheck.length}`);
  
  await pool.end();
}

checkItems().catch(console.error);
