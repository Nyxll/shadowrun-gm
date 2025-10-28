import fs from 'fs';
import path from 'path';

// Get all SQL files matching the pattern
const files = [];
for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (fs.existsSync(filename)) {
    files.push(filename);
  }
}

console.log(`Found ${files.length} SQL files to process`);

let totalReplacements = 0;

files.forEach(file => {
  console.log(`Processing ${file}...`);
  let content = fs.readFileSync(file, 'utf8');
  let fileReplacements = 0;
  
  // Replace ARRAY[]::text[]::jsonb with '[]'::jsonb
  const beforeCount = (content.match(/ARRAY\[\]::text\[\]::jsonb/g) || []).length;
  content = content.replace(/ARRAY\[\]::text\[\]::jsonb/g, "'[]'::jsonb");
  fileReplacements += beforeCount;
  
  // Replace ARRAY[]::text[] with '[]'::jsonb when used in jsonb columns
  // This handles cases where ::jsonb might be missing
  const beforeCount2 = (content.match(/ARRAY\[\]::text\[\]/g) || []).length;
  content = content.replace(/ARRAY\[\]::text\[\]/g, "'[]'::jsonb");
  fileReplacements += beforeCount2;
  
  if (fileReplacements > 0) {
    fs.writeFileSync(file, content, 'utf8');
    console.log(`  ✓ Fixed ${fileReplacements} occurrences in ${file}`);
    totalReplacements += fileReplacements;
  } else {
    console.log(`  - No changes needed in ${file}`);
  }
});

console.log(`\nTotal replacements: ${totalReplacements}`);
console.log('Done!');
