#!/usr/bin/env node

/**
 * Fix array and JSON literals in SQL files for PostgreSQL compatibility
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

console.log(`Found ${files.length} SQL files to fix\n`);

let totalFixed = 0;

files.forEach((file, index) => {
  const filePath = path.join(projectRoot, file);
  let content = fs.readFileSync(filePath, 'utf8');
  let fixed = false;
  
  // Fix ALL array literals: '["item"]' -> ARRAY['item']::text[]
  // This regex finds quoted arrays and converts them
  const arrayRegex = /'(\[(?:[^\]]*)\])'/g;
  if (arrayRegex.test(content)) {
    content = content.replace(/'(\[(?:[^\]]*)\])'/g, (match, arrayContent) => {
      if (arrayContent === '[]') {
        return 'ARRAY[]::text[]';
      }
      // Parse the JSON array and convert to PostgreSQL array syntax
      try {
        const items = JSON.parse(arrayContent);
        const pgArray = items.map(item => `'${item.replace(/'/g, "''")}'`).join(',');
        return `ARRAY[${pgArray}]::text[]`;
      } catch (e) {
        console.error(`Error parsing array in ${file}: ${arrayContent}`);
        return match;
      }
    });
    fixed = true;
  }
  
  // Fix timestamps with extra quotes: '"2025-10-15T08:08:34.847Z"' -> '2025-10-15T08:08:34.847Z'
  content = content.replace(/'"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)"'/g, "'$1'");
  
  if (fixed) {
    fs.writeFileSync(filePath, content);
    console.log(`✅ Fixed ${file}`);
    totalFixed++;
  } else {
    console.log(`⏭️  Skipped ${file} (no arrays to fix)`);
  }
});

console.log(`\n🎉 Fixed ${totalFixed} files!`);
