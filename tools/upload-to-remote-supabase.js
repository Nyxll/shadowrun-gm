import pg from 'pg';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const { Client } = pg;

// Use the remote DATABASE_URL from .env
const connectionString = process.env.DATABASE_URL;

console.log('Connecting to remote Supabase...\n');

const client = new Client({
  connectionString,
  ssl: {
    rejectUnauthorized: false
  }
});

async function uploadFile(filename) {
  if (!fs.existsSync(filename)) {
    console.log(`⚠️  ${filename} not found, skipping...`);
    return false;
  }

  console.log(`📤 Uploading ${filename}...`);
  const sql = fs.readFileSync(filename, 'utf8');
  
  try {
    await client.query(sql);
    console.log(`✅ Successfully uploaded ${filename}\n`);
    return true;
  } catch (error) {
    console.error(`❌ Error uploading ${filename}:`);
    console.error(`   ${error.message}\n`);
    return false;
  }
}

async function main() {
  try {
    await client.connect();
    console.log('✅ Connected to remote Supabase!\n');
    
    // Upload files in order
    const filesToUpload = [
      // Parts 1-38
      ...Array.from({ length: 38 }, (_, i) => `supabase-data-ordered-part${i + 1}.sql`),
      // Merged file for 39-54
      'supabase-data-merged-39-54-chunk1.sql',
      // Merged file for 55-86
      'supabase-data-merged-55-86-chunk1.sql',
      // Parts 87-91
      ...Array.from({ length: 5 }, (_, i) => `supabase-data-ordered-part${i + 87}.sql`)
    ];
    
    let successCount = 0;
    let failCount = 0;
    
    for (const file of filesToUpload) {
      const success = await uploadFile(file);
      if (success) {
        successCount++;
      } else {
        failCount++;
      }
    }
    
    console.log('\n📊 Upload Summary:');
    console.log(`   ✅ Successful: ${successCount}`);
    console.log(`   ❌ Failed: ${failCount}`);
    
  } catch (error) {
    console.error('❌ Connection error:', error.message);
  } finally {
    await client.end();
    console.log('\n🔌 Disconnected from database');
  }
}

main();
