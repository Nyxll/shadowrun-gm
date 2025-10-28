import fs from 'fs';

console.log('Fixing supabase-data.sql and creating optimized chunks...\n');

const MAX_SIZE = 1000 * 1024; // 1000KB

// Read the original file
console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');
const originalSize = Buffer.byteLength(content, 'utf8');
console.log(`   Original size: ${(originalSize / 1024 / 1024).toFixed(2)}MB\n`);

let fixCount = 0;

// Fix 1: JSONB columns - convert '{"key":"value"}' to '{"key":"value"}'::jsonb
console.log('🔧 Fix 1: JSONB type casting...');
const jsonbColumns = ['game_effects', 'activation_requirements', 'drain_modifiers', 'target_modifiers', 'duration_modifiers', 'range_modifiers'];
jsonbColumns.forEach(col => {
  const regex = new RegExp(`${col}, '(\\{[^']*\\})'`, 'g');
  const before = content;
  content = content.replace(regex, (match, json) => {
    fixCount++;
    return `${col}, '${json}'::jsonb`;
  });
});
console.log(`   Applied ${fixCount} fixes\n`);

// Fix 2: JSON array syntax for JSONB columns - '["item"]' to '["item"]'::jsonb
console.log('🔧 Fix 2: JSON array syntax for JSONB...');
const beforeFix2 = fixCount;
content = content.replace(/'(\[(?:[^\[\]']|'[^']*')*\])'/g, (match, arrayStr) => {
  try {
    JSON.parse(arrayStr);
    fixCount++;
    return `'${arrayStr}'::jsonb`;
  } catch (e) {
    return match;
  }
});
console.log(`   Applied ${fixCount - beforeFix2} fixes\n`);

// Fix 3: TEXT[] columns - convert '["item"]' to ARRAY['item']::text[]
console.log('🔧 Fix 3: TEXT[] array syntax...');
const beforeFix3 = fixCount;
const textArrayColumns = ['tables_queried', 'data_sources'];
textArrayColumns.forEach(col => {
  const regex = new RegExp(`${col}, '(\\[[^\\]]+\\])'`, 'g');
  content = content.replace(regex, (match, arrayStr) => {
    try {
      const parsed = JSON.parse(arrayStr);
      if (Array.isArray(parsed)) {
        fixCount++;
        const items = parsed.map(item => `'${item}'`).join(',');
        return `${col}, ARRAY[${items}]::text[]`;
      }
    } catch (e) {}
    return match;
  });
});
console.log(`   Applied ${fixCount - beforeFix3} fixes\n`);

// Fix 4: PostgreSQL array quotes - ARRAY['item'] format
console.log('🔧 Fix 4: PostgreSQL array quote syntax...');
const beforeFix4 = fixCount;
content = content.replace(/ARRAY\[([^\]]+)\]/g, (match, items) => {
  const fixed = items.replace(/"([^"]+)"/g, "'$1'");
  if (fixed !== items) fixCount++;
  return `ARRAY[${fixed}]`;
});
console.log(`   Applied ${fixCount - beforeFix4} fixes\n`);

// Save fixed version
console.log('💾 Saving fixed version...');
fs.writeFileSync('supabase-data-fixed.sql', content, 'utf8');
console.log(`   Saved as supabase-data-fixed.sql\n`);

console.log(`✅ Total fixes applied: ${fixCount}\n`);

// Now split into optimized chunks
console.log('📦 Splitting into optimized chunks (max 1000KB each)...\n');

const lines = content.split('\n');
let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;
const createdFiles = [];

for (const line of lines) {
  const lineSize = Buffer.byteLength(line + '\n', 'utf8');
  
  // If adding this line would exceed max size, save current chunk
  if (currentSize + lineSize > MAX_SIZE && currentChunk.length > 0) {
    const outputFilename = `data-load-${chunkNumber}.sql`;
    const chunkContent = currentChunk.join('\n');
    fs.writeFileSync(outputFilename, chunkContent, 'utf8');
    
    const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
    console.log(`✅ Created ${outputFilename}`);
    console.log(`   Size: ${(chunkSize / 1024).toFixed(1)}KB`);
    console.log(`   Lines: ${currentChunk.length}\n`);
    createdFiles.push(outputFilename);
    
    currentChunk = [];
    currentSize = 0;
    chunkNumber++;
  }
  
  currentChunk.push(line);
  currentSize += lineSize;
}

// Save remaining chunk
if (currentChunk.length > 0) {
  const outputFilename = `data-load-${chunkNumber}.sql`;
  const chunkContent = currentChunk.join('\n');
  fs.writeFileSync(outputFilename, chunkContent, 'utf8');
  
  const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
  console.log(`✅ Created ${outputFilename}`);
  console.log(`   Size: ${(chunkSize / 1024).toFixed(1)}KB`);
  console.log(`   Lines: ${currentChunk.length}\n`);
  createdFiles.push(outputFilename);
}

console.log(`\n📊 Summary:`);
console.log(`   Total fixes: ${fixCount}`);
console.log(`   Created ${createdFiles.length} optimized data load files`);
console.log(`   All files are under 1000KB`);
console.log(`\n📋 Upload order:`);
createdFiles.forEach((file, index) => {
  console.log(`   ${index + 1}. ${file}`);
});
