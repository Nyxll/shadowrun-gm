/**
 * Simple Database Connection Test
 * Tests if PostgreSQL is responding
 */

import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'shadowrun_gm',
  password: process.env.DB_PASSWORD || 'postgres',
  port: process.env.DB_PORT || 5432,
  connectionTimeoutMillis: 5000, // 5 second timeout
});

async function testConnection() {
  console.log('Testing database connection...\n');
  console.log('Connection details:');
  console.log(`  Host: ${process.env.DB_HOST || 'localhost'}`);
  console.log(`  Port: ${process.env.DB_PORT || 5432}`);
  console.log(`  Database: ${process.env.DB_NAME || 'shadowrun_gm'}`);
  console.log(`  User: ${process.env.DB_USER || 'postgres'}\n`);
  
  let client;
  try {
    console.log('Attempting to connect...');
    client = await pool.connect();
    console.log('✓ Connected successfully!\n');
    
    console.log('Testing query execution...');
    const result = await client.query('SELECT version()');
    console.log('✓ Query executed successfully!\n');
    
    console.log('PostgreSQL Version:');
    console.log(`  ${result.rows[0].version}\n`);
    
    console.log('✓ Database is responding normally');
    
  } catch (err) {
    console.error('✗ Connection failed:', err.message);
    
    if (err.code === 'ECONNREFUSED') {
      console.error('\nPossible causes:');
      console.error('  1. PostgreSQL is not running');
      console.error('  2. PostgreSQL is not listening on the specified port');
      console.error('  3. Firewall is blocking the connection');
    } else if (err.code === 'ETIMEDOUT') {
      console.error('\nConnection timed out - PostgreSQL may be hung or overloaded');
    } else if (err.message.includes('password')) {
      console.error('\nAuthentication failed - check username/password');
    }
    
    throw err;
  } finally {
    if (client) {
      client.release();
    }
  }
}

testConnection()
  .then(() => {
    pool.end();
    process.exit(0);
  })
  .catch((err) => {
    pool.end();
    process.exit(1);
  });
