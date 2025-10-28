import fs from 'fs';

console.log('Creating optimized data load files (max 1000KB each)...\n');

const MAX_SIZE = 1000 * 1024; // 1000KB in bytes
const allFiles = [];

// Collect all ordered files
for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (fs.existsSync(filename)) {
    allFiles.push(filename);
  }
}

console.log(`Found ${allFiles.length} files to merge\n`);

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;
const createdFiles = [];

for (const filename of allFiles) {
  const content = fs.readFileSync(filename, 'utf8');
  const fileSize = Buffer.byteLength(content, 'utf8');
  
  // If adding this file would exceed max size, save current chunk
  if (currentSize + fileSize > MAX_SIZE && currentChunk.length > 0) {
    const outputFilename = `data-load-${chunkNumber}.sql`;
    const mergedContent = currentChunk.join('\n\n');
    fs.writeFileSync(outputFilename, mergedContent, 'utf8');
    
    const mergedSize = Buffer.byteLength(mergedContent, 'utf8');
    console.log(`✅ Created ${outputFilename}`);
    console.log(`   Size: ${(mergedSize / 1024).toFixed(1)}KB`);
    console.log(`   Files: ${currentChunk.length}\n`);
    createdFiles.push(outputFilename);
    
    currentChunk = [];
    currentSize = 0;
    chunkNumber++;
  }
  
  currentChunk.push(content);
  currentSize += fileSize;
}

// Save remaining chunk
if (currentChunk.length > 0) {
  const outputFilename = `data-load-${chunkNumber}.sql`;
  const mergedContent = currentChunk.join('\n\n');
  fs.writeFileSync(outputFilename, mergedContent, 'utf8');
  
  const mergedSize = Buffer.byteLength(mergedContent, 'utf8');
  console.log(`✅ Created ${outputFilename}`);
  console.log(`   Size: ${(mergedSize / 1024).toFixed(1)}KB`);
  console.log(`   Files: ${currentChunk.length}\n`);
  createdFiles.push(outputFilename);
}

console.log(`\n📦 Summary:`);
console.log(`   Created ${createdFiles.length} optimized data load files`);
console.log(`   All files are under 1000KB`);
console.log(`\n📋 Upload order:`);
createdFiles.forEach((file, index) => {
  console.log(`   ${index + 1}. ${file}`);
});
