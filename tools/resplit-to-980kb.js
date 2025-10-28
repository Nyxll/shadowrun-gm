import fs from 'fs';

console.log('Resplitting files to be under 980KB...\n');

const MAX_SIZE = 980 * 1024; // 980KB

// Read the fixed data
const content = fs.readFileSync('supabase-data-fixed.sql', 'utf8');

// Reorganize by table order
const tableOrder = [
  'metatypes', 'powers', 'spells', 'totems', 'gear', 'rules_content',
  'campaigns', 'sr_characters', 'character_history', 'character_skills',
  'character_spells', 'character_powers', 'character_contacts', 'character_gear',
  'character_modifiers', 'house_rules', 'rule_application_log',
  'gear_chunk_links', 'query_logs'
];

const tableData = {};
tableOrder.forEach(t => tableData[t] = []);

const lines = content.split('\n');
let currentInsert = '';

for (const line of lines) {
  if (line.trim().startsWith('INSERT INTO')) {
    if (currentInsert) {
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

console.log('Creating files under 980KB...\n');

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;

for (const table of tableOrder) {
  for (const insert of tableData[table]) {
    const insertSize = Buffer.byteLength(insert + '\n', 'utf8');
    
    if (currentSize + insertSize > MAX_SIZE && currentChunk.length > 0) {
      const filename = `data-load-final-${chunkNumber}.sql`;
      const chunkContent = currentChunk.join('\n\n');
      fs.writeFileSync(filename, chunkContent, 'utf8');
      const actualSize = Buffer.byteLength(chunkContent, 'utf8');
      console.log(`✅ ${filename.padEnd(30)} ${(actualSize/1024).toFixed(1).padStart(7)}KB`);
      currentChunk = [];
      currentSize = 0;
      chunkNumber++;
    }
    
    currentChunk.push(insert);
    currentSize += insertSize;
  }
}

if (currentChunk.length > 0) {
  const filename = `data-load-final-${chunkNumber}.sql`;
  const chunkContent = currentChunk.join('\n\n');
  fs.writeFileSync(filename, chunkContent, 'utf8');
  const actualSize = Buffer.byteLength(chunkContent, 'utf8');
  console.log(`✅ ${filename.padEnd(30)} ${(actualSize/1024).toFixed(1).padStart(7)}KB`);
}

console.log(`\n✅ Created ${chunkNumber} files, all under 980KB`);
