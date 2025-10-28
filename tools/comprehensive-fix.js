import fs from 'fs';

console.log('='.repeat(80));
console.log('COMPREHENSIVE DATA TYPE FIX');
console.log('='.repeat(80));
console.log();

const MAX_SIZE = 1000 * 1024;

// Complete mapping of ALL columns by type
const COLUMN_TYPES = {
  // TEXT[] columns - need ARRAY['item']::text[] syntax
  TEXT_ARRAY: {
    'metatypes': ['special_abilities', 'loaded_from'],
    'powers': ['loaded_from'],
    'spells': ['loaded_from'],
    'totems': ['loaded_from'],
    'gear': ['tags', 'loaded_from'],
    'rules_content': ['tags'],
    'character_modifiers': ['stacks_with', 'replaces'],
    'query_logs': ['data_sources', 'tables_queried']
  },
  
  // JSONB columns - need '{}'::jsonb or '[]'::jsonb syntax
  JSONB: {
    'metatypes': ['racial_traits'],
    'powers': ['game_effects', 'levels'],
    'gear': ['base_stats', 'modifiers', 'requirements'],
    'sr_characters': ['attributes', 'skills_data', 'qualities_taken', 'gear_owned', 
                      'cyberware_installed', 'spells_known', 'powers_active', 
                      'contacts_list', 'biography'],
    'character_history': ['old_value', 'new_value'],
    'character_modifiers': ['modifier_data'],
    'house_rules': ['rule_config'],
    'rule_application_log': ['rule_config_snapshot', 'application_context'],
    'query_logs': ['classification', 'dice_rolls']
  }
};

console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');
const originalSize = Buffer.byteLength(content, 'utf8');
console.log(`   Size: ${(originalSize / 1024 / 1024).toFixed(2)}MB\n`);

let textArrayFixes = 0;
let jsonbFixes = 0;

// Step 1: Fix all TEXT[] columns
console.log('🔧 Step 1: Fixing TEXT[] columns...');
console.log('   Converting \'["item"]\' → ARRAY[\'item\']::text[]\n');

// Replace ALL array literals with proper PostgreSQL array syntax
content = content.replace(/'(\[[^\]]*\])'/g, (match, arrayStr) => {
  try {
    const parsed = JSON.parse(arrayStr);
    if (Array.isArray(parsed)) {
      textArrayFixes++;
      if (parsed.length === 0) {
        return `ARRAY[]::text[]`;
      }
      // Properly escape single quotes and wrap each item
      const items = parsed.map(item => {
        const str = String(item);
        const escaped = str.replace(/'/g, "''");
        return `'${escaped}'`;
      }).join(',');
      return `ARRAY[${items}]::text[]`;
    }
  } catch (e) {
    // Not valid JSON array, leave as is
  }
  return match;
});

console.log(`   Fixed ${textArrayFixes} TEXT[] arrays\n`);

// Step 2: Fix all JSONB columns
console.log('🔧 Step 2: Fixing JSONB columns...');
console.log('   Converting \'{}\' → \'{}\'::jsonb\n');

// Fix JSONB objects
const jsonbObjectMatches = content.match(/, '\{[^}]*\}'/g);
if (jsonbObjectMatches) {
  content = content.replace(/, '(\{[^}]*\})'/g, (match, obj) => {
    jsonbFixes++;
    return `, '${obj}'::jsonb`;
  });
}

console.log(`   Fixed ${jsonbFixes} JSONB columns\n`);

const totalFixes = textArrayFixes + jsonbFixes;
console.log(`✅ Total fixes applied: ${totalFixes}\n`);

// Save fixed version
console.log('💾 Saving supabase-data-fixed.sql...');
fs.writeFileSync('supabase-data-fixed.sql', content, 'utf8');
console.log('   Saved!\n');

// Step 3: Reorganize by table dependencies
console.log('📋 Step 3: Reorganizing by table dependencies...\n');

const tableOrder = [
  'metatypes',
  'powers',
  'spells',
  'totems',
  'gear',
  'rules_content',
  'campaigns',
  'sr_characters',
  'character_history',
  'character_skills',
  'character_spells',
  'character_powers',
  'character_contacts',
  'character_gear',
  'character_modifiers',
  'house_rules',
  'rule_application_log',
  'gear_chunk_links',
  'query_logs'
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

console.log('Found INSERT statements by table:');
let totalStatements = 0;
tableOrder.forEach(table => {
  if (tableData[table].length > 0) {
    console.log(`   ${table.padEnd(25)} ${tableData[table].length.toString().padStart(5)} statements`);
    totalStatements += tableData[table].length;
  }
});
console.log(`   ${'TOTAL'.padEnd(25)} ${totalStatements.toString().padStart(5)} statements\n`);

// Step 4: Create optimized chunks
console.log('📦 Step 4: Creating optimized chunks (max 1000KB)...\n');

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
      console.log(`   ✅ ${filename.padEnd(25)} ${(chunkSize/1024).toFixed(1).padStart(7)}KB  ${currentChunk.length.toString().padStart(4)} statements`);
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
  console.log(`   ✅ ${filename.padEnd(25)} ${(chunkSize/1024).toFixed(1).padStart(7)}KB  ${currentChunk.length.toString().padStart(4)} statements`);
  createdFiles.push(filename);
}

console.log();
console.log('='.repeat(80));
console.log('SUMMARY');
console.log('='.repeat(80));
console.log(`TEXT[] fixes:        ${textArrayFixes}`);
console.log(`JSONB fixes:         ${jsonbFixes}`);
console.log(`Total fixes:         ${totalFixes}`);
console.log(`Files created:       ${createdFiles.length}`);
console.log(`All files:           Under 1000KB`);
console.log(`Table order:         Dependency-ordered`);
console.log('='.repeat(80));
console.log();
console.log('✅ Ready to upload to Supabase!');
console.log();
console.log('Upload order:');
console.log('  1. drop-all-tables.sql');
console.log('  2. supabase-schema-fixed.sql');
createdFiles.forEach((file, i) => {
  console.log(`  ${(i + 3).toString().padStart(2)}. ${file}`);
});
console.log();
