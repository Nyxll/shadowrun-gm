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

// Missing TacComm and other items identified by verify-gear-import.js
const missingItems = [
  {
    name: 'Secured Short-Haul Link',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      range: 'short',
      security: 'secured'
    },
    cost: 500,
    availability: '4/48hrs',
    description: 'Secured short-range communication link for tactical communications',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Secured Long-Haul Link',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      range: 'long',
      security: 'secured'
    },
    cost: 1000,
    availability: '6/48hrs',
    description: 'Secured long-range communication link for tactical communications',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Secured Uplink',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      range: 'satellite',
      security: 'secured'
    },
    cost: 2000,
    availability: '8/72hrs',
    description: 'Secured satellite uplink for tactical communications',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Unsecured Short-Haul Link',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      range: 'short',
      security: 'unsecured'
    },
    cost: 250,
    availability: '2/24hrs',
    description: 'Unsecured short-range communication link',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Unsecured Long-Haul Link',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      range: 'long',
      security: 'unsecured'
    },
    cost: 500,
    availability: '4/24hrs',
    description: 'Unsecured long-range communication link',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Unsecured Uplink',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      range: 'satellite',
      security: 'unsecured'
    },
    cost: 1000,
    availability: '6/48hrs',
    description: 'Unsecured satellite uplink',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Laser Link (TacComm)',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      type: 'laser',
      range: 'line_of_sight'
    },
    cost: 750,
    availability: '5/48hrs',
    description: 'Laser-based tactical communication link',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Master Unit (TacComm)',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      type: 'master_unit',
      capacity: 'multiple_channels'
    },
    cost: 3000,
    availability: '8/72hrs',
    description: 'Master control unit for tactical communication network',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Microwave Link (TacComm)',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      type: 'microwave',
      range: 'medium'
    },
    cost: 600,
    availability: '5/48hrs',
    description: 'Microwave-based tactical communication link',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Personal Comm Unit (TacComm)',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      type: 'personal',
      portability: 'portable'
    },
    cost: 400,
    availability: '4/24hrs',
    description: 'Personal tactical communication unit',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Portable Master Unit (TacComm)',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      type: 'portable_master',
      portability: 'portable'
    },
    cost: 2000,
    availability: '7/48hrs',
    description: 'Portable master control unit for tactical communications',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Satellite Uplink (TacComm)',
    category: 'electronics',
    subcategory: 'communications',
    base_stats: {
      type: 'satellite',
      range: 'global'
    },
    cost: 5000,
    availability: '10/7days',
    description: 'Satellite uplink for global tactical communications',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Radio Jammer',
    category: 'electronics',
    subcategory: 'countermeasures',
    base_stats: {
      type: 'jammer',
      range: 'area_effect'
    },
    cost: 1500,
    availability: '8/72hrs',
    description: 'Radio frequency jammer for disrupting communications',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  },
  {
    name: 'Dikote TM (100 cm^3)',
    category: 'weapon_modification',
    subcategory: 'blade_treatment',
    base_stats: {
      volume: '100cm3',
      effect: 'blade_hardening'
    },
    cost: 200,
    availability: '6/48hrs',
    description: 'Dikote blade treatment for weapon hardening (100 cubic centimeters)',
    source_file: 'manual_addition',
    loaded_from: ['manual_taccomm_fix']
  }
];

async function addMissingItems() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('  ADDING MISSING TACCOMM ITEMS');
  console.log('═══════════════════════════════════════════════════════════\n');
  
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    let added = 0;
    let skipped = 0;
    
    for (const item of missingItems) {
      // Check if item already exists
      const existing = await client.query(
        'SELECT id FROM gear WHERE name = $1',
        [item.name]
      );
      
      if (existing.rows.length > 0) {
        console.log(`⏭️  Skipped: ${item.name} (already exists)`);
        skipped++;
        continue;
      }
      
      // Insert item
      await client.query(`
        INSERT INTO gear (
          name, category, subcategory, base_stats, cost, availability,
          description, source_file, loaded_from, data_quality,
          search_vector
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, 8,
          to_tsvector('english', $1 || ' ' || COALESCE($7, ''))
        )
      `, [
        item.name,
        item.category,
        item.subcategory,
        JSON.stringify(item.base_stats),
        item.cost,
        item.availability,
        item.description,
        item.source_file,
        item.loaded_from
      ]);
      
      console.log(`✅ Added: ${item.name}`);
      added++;
    }
    
    await client.query('COMMIT');
    
    console.log('\n═══════════════════════════════════════════════════════════');
    console.log('  SUMMARY');
    console.log('═══════════════════════════════════════════════════════════\n');
    console.log(`✅ Added: ${added} items`);
    console.log(`⏭️  Skipped: ${skipped} items (already existed)`);
    console.log(`📊 Total processed: ${missingItems.length} items\n`);
    
    // Verify final count
    const result = await pool.query('SELECT COUNT(*) as total FROM gear');
    console.log(`📈 New total items in database: ${result.rows[0].total}\n`);
    
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ Error adding items:', error.message);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

addMissingItems().catch(console.error);
