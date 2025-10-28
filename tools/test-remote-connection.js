import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Client } = pg;

const connectionString = process.env.DATABASE_URL;

console.log('Testing connection to remote Supabase...\n');
console.log(`Connection string: ${connectionString.replace(/:[^:@]+@/, ':****@')}\n`);

const client = new Client({
  connectionString,
  ssl: {
    rejectUnauthorized: false
  }
});

async function testConnection() {
  try {
    console.log('🔌 Connecting...');
    await client.connect();
    console.log('✅ Connected successfully!\n');
    
    // Test query
    console.log('🔍 Running test query...');
    const result = await client.query('SELECT version()');
    console.log('✅ Query successful!');
    console.log(`   PostgreSQL version: ${result.rows[0].version}\n`);
    
    // Check if tables exist
    console.log('📋 Checking for existing tables...');
    const tables = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    
    if (tables.rows.length > 0) {
      console.log(`✅ Found ${tables.rows.length} tables:`);
      tables.rows.forEach(row => {
        console.log(`   - ${row.table_name}`);
      });
    } else {
      console.log('⚠️  No tables found in public schema');
    }
    
    console.log('\n✅ Connection test successful!');
    
  } catch (error) {
    console.error('❌ Connection test failed:');
    console.error(`   ${error.message}`);
    if (error.code) {
      console.error(`   Error code: ${error.code}`);
    }
  } finally {
    await client.end();
    console.log('\n🔌 Disconnected');
  }
}

testConnection();
