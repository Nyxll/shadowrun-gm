#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const inputFile = path.join(__dirname, '..', 'supabase-data.sql');
const content = fs.readFileSync(inputFile, 'utf8');

// Split by INSERT statements
const statements = [];
let current = '';
let inStatement = false;

content.split('\n').forEach(line => {
  const trimmed = line.trim();
  
  if (trimmed.startsWith('INSERT INTO')) {
    if (current) {
      statements.push(current);
    }
    current = line + '\n';
    inStatement = true;
  } else if (inStatement) {
    current += line + '\n';
    if (trimmed.endsWith(';')) {
      statements.push(current);
      current = '';
      inStatement = false;
    }
  } else if (trimmed && !trimmed.startsWith('--')) {
    current += line + '\n';
  }
});

if (current) {
  statements.push(current);
}

console.log(`Total statements: ${statements.length}`);

// Split into chunks of 50 statements each
const chunkSize = 50;
const chunks = [];

for (let i = 0; i < statements.length; i += chunkSize) {
  chunks.push(statements.slice(i, i + chunkSize));
}

console.log(`Creating ${chunks.length} files...`);

chunks.forEach((chunk, index) => {
  const filename = path.join(__dirname, '..', `supabase-data-part${index + 1}.sql`);
  fs.writeFileSync(filename, chunk.join('\n'));
  console.log(`✅ Created part ${index + 1}: ${chunk.length} statements`);
});

console.log(`\n🎉 Split complete! Upload files in order: part1, part2, etc.`);
