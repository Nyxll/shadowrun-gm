/**
 * Import Training Data
 * 
 * Imports the 173 parsed training queries from gm-train.txt
 * into the query_logs table for training and validation.
 */

import 'dotenv/config';
import pkg from 'pg';
const { Pool } = pkg;
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Database configuration
const pool = new Pool({
  user: process.env.POSTGRES_USER || process.env.DB_USER || 'postgres',
  host: process.env.POSTGRES_HOST || process.env.DB_HOST || 'localhost',
  database: process.env.POSTGRES_DB || process.env.DB_NAME || 'postgres',
  password: process.env.POSTGRES_PASSWORD || process.env.DB_PASSWORD || 'postgres',
  port: process.env.POSTGRES_PORT || process.env.DB_PORT || 5432,
});

async function importTrainingData() {
  const client = await pool.connect();
  
  try {
    console.log('Loading training data from parsed-training-data.json...\n');
    
    // Load the parsed training data
    const trainingDataPath = path.join(__dirname, 'train', 'parsed-training-data.json');
    const trainingData = JSON.parse(fs.readFileSync(trainingDataPath, 'utf-8'));
    
    console.log(`Found ${trainingData.metadata.totalQueries} training queries\n`);
    
    // Begin transaction
    await client.query('BEGIN');
    
    // Prepare insert statement
    const insertQuery = `
      INSERT INTO query_logs (
        query_text,
        expected_intent,
        is_training_data,
        training_source,
        timestamp
      ) VALUES ($1, $2, TRUE, $3, NOW())
      ON CONFLICT DO NOTHING
      RETURNING id
    `;
    
    let imported = 0;
    let skipped = 0;
    const intentCounts = {};
    
    // Import each query
    for (const query of trainingData.allQueries) {
      try {
        const result = await client.query(insertQuery, [
          query.query,
          query.intent,
          'gm-train.txt'
        ]);
        
        if (result.rowCount > 0) {
          imported++;
          intentCounts[query.intent] = (intentCounts[query.intent] || 0) + 1;
        } else {
          skipped++;
        }
      } catch (err) {
        console.error(`Error importing query: ${query.query.substring(0, 50)}...`);
        console.error(err.message);
        skipped++;
      }
    }
    
    // Commit transaction
    await client.query('COMMIT');
    
    console.log('=== IMPORT COMPLETE ===\n');
    console.log(`Successfully imported: ${imported} queries`);
    console.log(`Skipped (duplicates): ${skipped} queries\n`);
    
    console.log('Intent Distribution:');
    Object.entries(intentCounts)
      .sort((a, b) => b[1] - a[1])
      .forEach(([intent, count]) => {
        const pct = ((count / imported) * 100).toFixed(1);
        console.log(`  ${intent.padEnd(20)} ${count.toString().padStart(3)} (${pct}%)`);
      });
    
    // Show training progress
    console.log('\n=== TRAINING PROGRESS ===\n');
    const progressResult = await client.query('SELECT * FROM training_progress');
    console.table(progressResult.rows);
    
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('Error importing training data:', err);
    throw err;
  } finally {
    client.release();
  }
}

// Run import
importTrainingData()
  .then(() => {
    console.log('\nImport completed successfully!');
    pool.end();
    process.exit(0);
  })
  .catch((err) => {
    console.error('\nImport failed:', err);
    pool.end();
    process.exit(1);
  });
