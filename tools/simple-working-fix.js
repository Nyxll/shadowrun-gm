import fs from 'fs';

console.log('Simple working fix - add type casts to all arrays and objects\n');

const MAX_SIZE = 1000 * 1024;

console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');

let fixes = 0;

// Step 1: Fix all JSON arrays to proper PostgreSQL arrays for TEXT[] columns
console.log('🔧 Converting JSON arrays to PostgreSQL arrays...');
content = content.replace(/, '(\[[^\]]*\])'/g, (match, arr) => {
  try {
    const parsed = JSON.parse(arr);
    if (Array.isArray(parsed)) {
      fixes++;
      if (parsed.length === 0) {
        return `, ARRAY[]::text[]`;
      }
      const items = parsed.map(i => `'${String(i).replace(/'/g, "''")}'`).join(',');
      return `, ARRAY[${items}]::text[]`;
    }
  } catch (e) {}
  return match;
});

console.log(`   Fixed ${fixes} arrays\n`);

// Step 2: Add ::jsonb cast to all JSON objects
console.log('🔧 Adding ::jsonb casts to objects...');
let jsonbFixes = 0;
content = content.replace(/, '(\{[^}]*\})'/g, (match, obj) => {
  jsonbFixes++;
  return `, '${obj}'::jsonb`;
});

console.log(`   Fixed ${jsonbFixes} objects\n`);

// Step 3: Fix the specific case where levels should be JSONB not TEXT[]
// Powers table: game_effects is JSONB, levels is JSONB
console.log('🔧 Fixing powers.levels to be JSONB...');
let levelsFixes = 0;
content = content.replace(
  /(INSERT INTO powers[^;]+game_effects, '[^']*'::jsonb), ARRAY\[\]::text\[\]/g,
  (match, prefix) => {
    levelsFixes++;
    return `${prefix}, '[]'::jsonb`;
  }
);
content = content.replace(
  /(INSERT INTO powers[^;]+game_effects, '[^']*'::jsonb), ARRAY\[[^\]]+\]::text\[\]/g,
  (match, prefix) => {
    levelsFixes++;
    // Extract the array content and convert back to JSON
    const arrayMatch = match.match(/ARRAY\[([^\]]+)\]::text\[\]/);
    if (arrayMatch) {
      const items = arrayMatch[1].split(',').map(i => i.trim().replace(/^'|'$/g, ''));
      const jsonArray = JSON.stringify(items);
      return `${prefix}, '${jsonArray}'::jsonb`;
    }
    return match;
  }
);

console.log(`   Fixed ${levelsFixes} levels columns\n`);

const totalFixes = fixes + jsonbFixes + levelsFixes;
console.log(`✅ Total: ${totalFixes} fixes\n`);

fs.writeFileSync('supabase-data-fixed.sql', content, 'utf8');

// Reorganize and split
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

console.log('📦 Creating files...\n');

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;

for (const table of tableOrder) {
  for (const insert of tableData[table]) {
    const insertSize = Buffer.byteLength(insert + '\n', 'utf8');
    
    if (currentSize + insertSize > MAX_SIZE && currentChunk.length > 0) {
      fs.writeFileSync(`data-load-final-${chunkNumber}.sql`, currentChunk.join('\n\n'), 'utf8');
      console.log(`✅ data-load-final-${chunkNumber}.sql`);
      currentChunk = [];
      currentSize = 0;
      chunkNumber++;
    }
    
    currentChunk.push(insert);
    currentSize += insertSize;
  }
}

if (currentChunk.length > 0) {
  fs.writeFileSync(`data-load-final-${chunkNumber}.sql`, currentChunk.join('\n\n'), 'utf8');
  console.log(`✅ data-load-final-${chunkNumber}.sql`);
}

console.log(`\n✅ Done! Created ${chunkNumber} files`);
