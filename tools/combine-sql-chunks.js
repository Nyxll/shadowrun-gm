#!/usr/bin/env node

/**
 * Combine the 91 ordered SQL files into 10 larger chunks
 * Each chunk will be small enough for the SQL Editor but reduce manual work
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.join(__dirname, '..');

// Find all ordered SQL files
const files = fs.readdirSync(projectRoot)
  .filter(f => f.startsWith('supabase-data-ordered-part') && f.endsWith('.sql'))
  .sort((a, b) => {
    const numA = parseInt(a.match(/part(\d+)/)[1]);
    const numB = parseInt(b.match(/part(\d+)/)[1]);
    return numA - numB;
  });

console.log(`Found ${files.length} SQL files`);

// Combine into 10 chunks (about 9 files each)
const chunksCount = 10;
const filesPerChunk = Math.ceil(files.length / chunksCount);

console.log(`Creating ${chunksCount} combined files (${filesPerChunk} parts each)...\n`);

for (let i = 0; i < chunksCount; i++) {
  const startIdx = i * filesPerChunk;
  const endIdx = Math.min(startIdx + filesPerChunk, files.length);
  const chunkFiles = files.slice(startIdx, endIdx);
  
  let combined = `-- Combined SQL Chunk ${i + 1} of ${chunksCount}\n`;
  combined += `-- Contains parts ${startIdx + 1} to ${endIdx}\n`;
  combined += `-- ========================================\n\n`;
  
  chunkFiles.forEach((file, idx) => {
    const filePath = path.join(projectRoot, file);
    const content = fs.readFileSync(filePath, 'utf8');
    combined += `-- File: ${file}\n`;
    combined += content;
    combined += '\n\n';
  });
  
  const outputFile = path.join(projectRoot, `supabase-upload-chunk${i + 1}.sql`);
  fs.writeFileSync(outputFile, combined);
  
  console.log(`✅ Created chunk ${i + 1}: supabase-upload-chunk${i + 1}.sql (${chunkFiles.length} files)`);
}

console.log(`\n🎉 Done! Now you only need to upload 10 files instead of 91!`);
console.log(`\nUpload these files in order in the Supabase SQL Editor:`);
for (let i = 1; i <= chunksCount; i++) {
  console.log(`  ${i}. supabase-upload-chunk${i}.sql`);
}
