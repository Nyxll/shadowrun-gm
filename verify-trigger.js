import 'dotenv/config';
import pg from 'pg';

const { Pool } = pg;

const pool = new Pool({
  user: process.env.POSTGRES_USER || 'postgres',
  host: process.env.POSTGRES_HOST || 'localhost',
  database: process.env.POSTGRES_DB || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'postgres',
  port: process.env.POSTGRES_PORT || 5432,
});

async function verifyTrigger() {
  const client = await pool.connect();
  
  try {
    console.log('Checking for trigger...\n');
    
    const result = await client.query(`
      SELECT 
        tgname as trigger_name,
        tgrelid::regclass as table_name,
        tgenabled as enabled,
        pg_get_triggerdef(oid) as definition
      FROM pg_trigger
      WHERE tgname = 'trigger_update_query_correctness'
        AND tgrelid = 'query_logs'::regclass
    `);
    
    if (result.rows.length > 0) {
      console.log('✓ Trigger found!\n');
      console.log('Details:');
      console.log(result.rows[0]);
    } else {
      console.log('❌ Trigger not found');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    client.release();
    await pool.end();
  }
}

verifyTrigger();
