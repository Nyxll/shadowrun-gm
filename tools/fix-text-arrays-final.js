import fs from 'fs';

console.log('Fixing TEXT[] arrays with proper PostgreSQL syntax...\n');

const MAX_SIZE = 1000 * 1024;

console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');

let fixCount = 0;

// Fix all '["item1","item2"]' patterns to ARRAY['item1','item2']::text[]
console.log('🔧 Fixing TEXT[] arrays with values...');
content = content.replace(/'(\[[^\]]+\])'/g, (match, arrayStr) => {
  try {
    const parsed = JSON.parse(arrayStr);
    if (Array.isArray(parsed)) {
      fixCount++;
      if (parsed.length === 0) {
        return `ARRAY[]::text[]`;
      }
      // Escape single quotes in items and wrap in single quotes
      const items = parsed.map(item => {
        const escaped = String(item).replace(/'/g, "''");
        return `'${escaped}'`;
      }).join(',');
      return `ARRAY[${items}]::text[]`;
    }
  } catch (e) {
    // Not valid JSON, leave as is
  }
  return match;
});

console.log(`   Fixed ${fixCount} TEXT[] arrays\n`);

// Fix empty arrays and objects
console.log('🔧 Fixing empty arrays and objects...');
let emptyFixes = 0;

content = content.replace(/, '\[\]'/g, () => {
  emptyFixes++;
  return `, ARRAY[]::text[]`;
});

content = content.replace(/, '\{\}'/g, () => {
  emptyFixes++;
  return `, '{}'::jsonb`;
});

console.log(`   Fixed ${emptyFixes} empty arrays/objects\n`);

const totalFixes = fixCount + emptyFixes;
console.log(`✅ Total fixes: ${totalFixes}\n`);

// Save fixed version
fs.writeFileSync('supabase-data-fixed.sql', content, 'utf8');
console.log('💾 Saved supabase-data-fixed.sql\n');

// Reorganize by table dependencies and split
console.log('📋 Reorganizing by table dependencies...\n');

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

console.log('Found INSERT statements:');
let totalStatements = 0;
tableOrder.forEach(table => {
  if (tableData[table].length > 0) {
    console.log(`   ${table}: ${tableData[table].length} statements`);
    totalStatements += tableData[table].length;
  }
});
console.log(`   Total: ${totalStatements} statements\n`);

// Create chunks
console.log('📦 Creating optimized chunks...\n');

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;
const createdFiles = [];

for (const table of tableOrder) {
  for (const insert of tableData[table]) {
    const insertSize = Buffer.byteLength(insert + '\n', 'utf8');
    
    if (currentSize + insertSize > MAX_SIZE && currentChunk.length > 0) {
      const filename = `data-load-final-${chunkNumber}.sql`;
      const chunkContent = currentChunk.join('\n\n');
      fs.writeFileSync(filename, chunkContent, 'utf8');
      const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
      console.log(`✅ ${filename} (${(chunkSize/1024).toFixed(1)}KB, ${currentChunk.length} statements)`);
      createdFiles.push(filename);
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
  const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
  console.log(`✅ ${filename} (${(chunkSize/1024).toFixed(1)}KB, ${currentChunk.length} statements)`);
  createdFiles.push(filename);
}

console.log(`\n📊 Summary:`);
console.log(`   Total fixes: ${totalFixes}`);
console.log(`   Files created: ${createdFiles.length}`);
console.log(`   All files under 1000KB`);
console.log(`   Tables in dependency order`);
