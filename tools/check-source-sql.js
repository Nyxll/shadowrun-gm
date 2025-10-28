import fs from 'fs';

const content = fs.readFileSync('supabase-data.sql', 'utf8');
const lines = content.split('\n');

let count = 0;
for (let i = 0; i < lines.length && count < 10; i++) {
  if (lines[i].includes('ARRAY[]::text[]')) {
    console.log(`Line ${i + 1}: ${lines[i].substring(0, 200)}...`);
    count++;
  }
}

console.log(`\nTotal occurrences: ${content.match(/ARRAY\[\]::text\[\]/g)?.length || 0}`);
