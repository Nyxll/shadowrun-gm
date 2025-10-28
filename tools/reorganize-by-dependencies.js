import fs from 'fs';

console.log('Reorganizing data files by table dependencies...\n');

const MAX_SIZE = 1000 * 1024; // 1000KB

// Read the fixed data file
console.log('📖 Reading supabase-data-fixed.sql...');
const content = fs.readFileSync('supabase-data-fixed.sql', 'utf8');

// Define table dependency order (parent tables first)
const tableOrder = [
  'metatypes',
  'powers',
  'spells',
  'totems',
  'gear',
  'rules_content',
  'sr_characters',        // Must come before character_history
  'character_history',
  'character_skills',
  'character_gear',
  'character_spells',
  'character_contacts',
  'query_logs'
];

console.log('📋 Extracting INSERT statements by table...\n');

// Extract INSERT statements for each table
const tableData = {};
tableOrder.forEach(table => {
  tableData[table] = [];
});

const lines = content.split('\n');
let currentInsert = '';

for (const line of lines) {
  if (line.trim().startsWith('INSERT INTO')) {
    // Save previous insert if exists
    if (currentInsert) {
      // Find which table this insert belongs to
      for (const table of tableOrder) {
        if (currentInsert.includes(`INSERT INTO ${table}`)) {
          tableData[table].push(currentInsert);
          break;
        }
      }
    }
    currentInsert = line;
  } else if (currentInsert) {
    currentInsert += '\n' + line;
    if (line.trim().endsWith(';')) {
      // End of INSERT statement
      for (const table of tableOrder) {
        if (currentInsert.includes(`INSERT INTO ${table}`)) {
          tableData[table].push(currentInsert);
          break;
        }
      }
      currentInsert = '';
    }
  }
}

// Report what we found
console.log('Found INSERT statements:');
tableOrder.forEach(table => {
  if (tableData[table].length > 0) {
    console.log(`   ${table}: ${tableData[table].length} statements`);
  }
});

// Now create chunks respecting table order
console.log('\n📦 Creating ordered chunks (max 1000KB each)...\n');

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;
const createdFiles = [];

for (const table of tableOrder) {
  const inserts = tableData[table];
  
  for (const insert of inserts) {
    const insertSize = Buffer.byteLength(insert + '\n', 'utf8');
    
    // If adding this insert would exceed max size, save current chunk
    if (currentSize + insertSize > MAX_SIZE && currentChunk.length > 0) {
      const outputFilename = `data-load-ordered-${chunkNumber}.sql`;
      const chunkContent = currentChunk.join('\n\n');
      fs.writeFileSync(outputFilename, chunkContent, 'utf8');
      
      const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
      console.log(`✅ Created ${outputFilename}`);
      console.log(`   Size: ${(chunkSize / 1024).toFixed(1)}KB`);
      console.log(`   Statements: ${currentChunk.length}\n`);
      createdFiles.push(outputFilename);
      
      currentChunk = [];
      currentSize = 0;
      chunkNumber++;
    }
    
    currentChunk.push(insert);
    currentSize += insertSize;
  }
}

// Save remaining chunk
if (currentChunk.length > 0) {
  const outputFilename = `data-load-ordered-${chunkNumber}.sql`;
  const chunkContent = currentChunk.join('\n\n');
  fs.writeFileSync(outputFilename, chunkContent, 'utf8');
  
  const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
  console.log(`✅ Created ${outputFilename}`);
  console.log(`   Size: ${(chunkSize / 1024).toFixed(1)}KB`);
  console.log(`   Statements: ${currentChunk.length}\n`);
  createdFiles.push(outputFilename);
}

console.log(`\n📊 Summary:`);
console.log(`   Created ${createdFiles.length} dependency-ordered data load files`);
console.log(`   All files are under 1000KB`);
console.log(`   Tables are loaded in correct dependency order`);
console.log(`\n📋 Upload order:`);
createdFiles.forEach((file, index) => {
  console.log(`   ${index + 1}. ${file}`);
});
