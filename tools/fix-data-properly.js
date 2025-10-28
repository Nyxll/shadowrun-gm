import fs from 'fs';

console.log('Fixing supabase-data.sql with correct type handling...\n');

const MAX_SIZE = 1000 * 1024; // 1000KB

// Read the original file
console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');
const originalSize = Buffer.byteLength(content, 'utf8');
console.log(`   Original size: ${(originalSize / 1024 / 1024).toFixed(2)}MB\n`);

let fixCount = 0;

// Define which columns are JSONB vs TEXT[]
const jsonbColumns = {
  'metatypes': ['racial_traits'],
  'powers': ['game_effects', 'levels'],
  'spells': [],
  'totems': [],
  'gear': ['base_stats', 'modifiers', 'requirements'],
  'rules_content': [],
  'sr_characters': ['attributes', 'skills_data', 'qualities_taken', 'gear_owned', 'cyberware_installed', 'spells_known', 'powers_active', 'contacts_list', 'biography'],
  'character_history': ['old_value', 'new_value'],
  'character_modifiers': ['modifier_data'],
  'house_rules': ['rule_config'],
  'rule_application_log': ['rule_config_snapshot', 'application_context'],
  'query_logs': ['classification', 'dice_rolls']
};

const textArrayColumns = {
  'metatypes': ['special_abilities', 'loaded_from'],
  'powers': ['loaded_from'],
  'spells': ['loaded_from'],
  'totems': ['loaded_from'],
  'gear': ['tags', 'loaded_from'],
  'rules_content': ['tags'],
  'character_modifiers': ['stacks_with', 'replaces'],
  'query_logs': ['data_sources', 'tables_queried']
};

console.log('🔧 Fixing JSONB columns...');
let jsonbFixes = 0;

// Fix JSONB columns - add ::jsonb cast
Object.entries(jsonbColumns).forEach(([table, columns]) => {
  columns.forEach(col => {
    // Match: column_name, '{...}' or column_name, '[...]'
    const regex1 = new RegExp(`(${col}), '(\\{[^']*\\})'`, 'g');
    const regex2 = new RegExp(`(${col}), '(\\[[^']*\\])'`, 'g');
    
    content = content.replace(regex1, (match, colName, json) => {
      jsonbFixes++;
      return `${colName}, '${json}'::jsonb`;
    });
    
    content = content.replace(regex2, (match, colName, json) => {
      jsonbFixes++;
      return `${colName}, '${json}'::jsonb`;
    });
  });
});

console.log(`   Applied ${jsonbFixes} JSONB fixes\n`);

console.log('🔧 Fixing TEXT[] columns...');
let textArrayFixes = 0;

// Fix TEXT[] columns - convert '["item"]' to ARRAY['item']::text[]
Object.entries(textArrayColumns).forEach(([table, columns]) => {
  columns.forEach(col => {
    const regex = new RegExp(`(${col}), '(\\[[^\\]]*\\])'`, 'g');
    
    content = content.replace(regex, (match, colName, arrayStr) => {
      try {
        const parsed = JSON.parse(arrayStr);
        if (Array.isArray(parsed)) {
          textArrayFixes++;
          if (parsed.length === 0) {
            return `${colName}, ARRAY[]::text[]`;
          }
          const items = parsed.map(item => `'${item.replace(/'/g, "''")}'`).join(',');
          return `${colName}, ARRAY[${items}]::text[]`;
        }
      } catch (e) {
        console.log(`  Warning: Could not parse ${arrayStr} for ${col}`);
      }
      return match;
    });
  });
});

console.log(`   Applied ${textArrayFixes} TEXT[] fixes\n`);

fixCount = jsonbFixes + textArrayFixes;

// Save fixed version
console.log('💾 Saving fixed version...');
fs.writeFileSync('supabase-data-fixed.sql', content, 'utf8');
console.log(`   Saved as supabase-data-fixed.sql\n`);

console.log(`✅ Total fixes applied: ${fixCount}\n`);

// Now reorganize by table dependencies and split
console.log('📋 Reorganizing by table dependencies...\n');

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

// Extract INSERT statements for each table
const tableData = {};
tableOrder.forEach(table => {
  tableData[table] = [];
});

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
tableOrder.forEach(table => {
  if (tableData[table].length > 0) {
    console.log(`   ${table}: ${tableData[table].length} statements`);
  }
});

// Create chunks respecting table order
console.log('\n📦 Creating ordered chunks (max 1000KB each)...\n');

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;
const createdFiles = [];

for (const table of tableOrder) {
  const inserts = tableData[table];
  
  for (const insert of inserts) {
    const insertSize = Buffer.byteLength(insert + '\n', 'utf8');
    
    if (currentSize + insertSize > MAX_SIZE && currentChunk.length > 0) {
      const outputFilename = `data-load-final-${chunkNumber}.sql`;
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

if (currentChunk.length > 0) {
  const outputFilename = `data-load-final-${chunkNumber}.sql`;
  const chunkContent = currentChunk.join('\n\n');
  fs.writeFileSync(outputFilename, chunkContent, 'utf8');
  
  const chunkSize = Buffer.byteLength(chunkContent, 'utf8');
  console.log(`✅ Created ${outputFilename}`);
  console.log(`   Size: ${(chunkSize / 1024).toFixed(1)}KB`);
  console.log(`   Statements: ${currentChunk.length}\n`);
  createdFiles.push(outputFilename);
}

console.log(`\n📊 Summary:`);
console.log(`   JSONB fixes: ${jsonbFixes}`);
console.log(`   TEXT[] fixes: ${textArrayFixes}`);
console.log(`   Total fixes: ${fixCount}`);
console.log(`   Created ${createdFiles.length} properly typed data load files`);
console.log(`   All files under 1000KB`);
console.log(`   Tables in correct dependency order`);
console.log(`\n📋 Upload order:`);
createdFiles.forEach((file, index) => {
  console.log(`   ${index + 1}. ${file}`);
});
