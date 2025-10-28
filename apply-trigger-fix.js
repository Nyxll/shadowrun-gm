import 'dotenv/config';
import pg from 'pg';
import fs from 'fs';

const { Pool } = pg;

const pool = new Pool({
  user: process.env.POSTGRES_USER || process.env.DB_USER || 'postgres',
  host: process.env.POSTGRES_HOST || process.env.DB_HOST || 'localhost',
  database: process.env.POSTGRES_DB || process.env.DB_NAME || 'postgres',
  password: process.env.POSTGRES_PASSWORD || process.env.DB_PASSWORD || 'postgres',
  port: process.env.POSTGRES_PORT || process.env.DB_PORT || 5432,
});

async function applyTriggerFix() {
  const client = await pool.connect();
  
  try {
    console.log('Applying trigger fix...\n');
    
    // Read the SQL file
    const sql = fs.readFileSync('fix-training-trigger.sql', 'utf8');
    
    // Execute the SQL
    const result = await client.query(sql);
    
    console.log('✓ Trigger fix applied successfully\n');
    
    // Show verification result
    if (result.rows && result.rows.length > 0) {
      console.log('Trigger verification:');
      console.log(result.rows[0]);
    }
    
  } catch (error) {
    console.error('Error applying trigger fix:', error.message);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

applyTriggerFix().catch(console.error);
