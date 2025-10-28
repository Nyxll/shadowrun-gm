import fs from 'fs';

console.log('Merging files 55-86 into larger chunks (under 1MB each)...\n');

const MAX_SIZE = 1000 * 1024; // 1MB in bytes
const startFile = 55;
const endFile = 86;

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;
const mergedFiles = [];

for (let i = startFile; i <= endFile; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  
  if (!fs.existsSync(filename)) {
    console.log(`⚠️  File ${filename} not found, skipping...`);
    continue;
  }
  
  const content = fs.readFileSync(filename, 'utf8');
  const fileSize = Buffer.byteLength(content, 'utf8');
  
  // If adding this file would exceed max size, save current chunk
  if (currentSize + fileSize > MAX_SIZE && currentChunk.length > 0) {
    const mergedFilename = `supabase-data-merged-${startFile}-${endFile}-chunk${chunkNumber}.sql`;
    const mergedContent = currentChunk.join('\n\n');
    fs.writeFileSync(mergedFilename, mergedContent, 'utf8');
    
    const mergedSize = Buffer.byteLength(mergedContent, 'utf8');
    console.log(`✅ Created ${mergedFilename} (${(mergedSize / 1024).toFixed(1)}KB, ${currentChunk.length} files)`);
    mergedFiles.push(mergedFilename);
    
    currentChunk = [];
    currentSize = 0;
    chunkNumber++;
  }
  
  currentChunk.push(content);
  currentSize += fileSize;
  console.log(`   Added part${i} (${(fileSize / 1024).toFixed(1)}KB) - Total: ${(currentSize / 1024).toFixed(1)}KB`);
}

// Save remaining chunk
if (currentChunk.length > 0) {
  const mergedFilename = `supabase-data-merged-${startFile}-${endFile}-chunk${chunkNumber}.sql`;
  const mergedContent = currentChunk.join('\n\n');
  fs.writeFileSync(mergedFilename, mergedContent, 'utf8');
  
  const mergedSize = Buffer.byteLength(mergedContent, 'utf8');
  console.log(`✅ Created ${mergedFilename} (${(mergedSize / 1024).toFixed(1)}KB, ${currentChunk.length} files)`);
  mergedFiles.push(mergedFilename);
}

console.log(`\n📦 Created ${mergedFiles.length} merged files:`);
mergedFiles.forEach(f => console.log(`   - ${f}`));
console.log(`\n💡 You can now upload these merged files instead of parts 55-86`);
