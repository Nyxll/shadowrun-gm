import fs from 'fs';

console.log('Fixing data by column positions...\n');

const MAX_SIZE = 1000 * 1024;

console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');

let fixCount = 0;

// Fix metatypes: special_abilities is position 17 (TEXT[]), racial_traits is position 18 (JSONB)
console.log('🔧 Fixing metatypes...');
content = content.replace(
  /(INSERT INTO metatypes \([^)]+\) VALUES \([^,]+(?:,[^,]+){16}), '(\[\])', '(\{\})'/g,
  (match, prefix, arr, obj) => {
    fixCount += 2;
    return `${prefix}, ARRAY[]::text[], '{}'::jsonb`;
  }
);

// Fix powers: levels is JSONB
console.log('🔧 Fixing powers...');
content = content.replace(
  /(INSERT INTO powers \([^)]+\) VALUES \([^)]+), '(\[\])'/g,
  (match, prefix, arr) => {
    fixCount++;
    return `${prefix}, '[]'::jsonb`;
  }
);

// Fix gear: tags is TEXT[], base_stats/modifiers/requirements are JSONB
console.log('🔧 Fixing gear...');
content = content.replace(
  /(INSERT INTO gear \([^)]+\) VALUES \([^,]+(?:,[^,]+){5}), '(\{[^}]*\})', '(\{[^}]*\})', '(\{[^}]*\})', '(\{[^}]*\})'/g,
  (match, prefix, stats, mods, reqs, tags) => {
    fixCount += 4;
    return `${prefix}, '${stats}'::jsonb, '${mods}'::jsonb, '${reqs}'::jsonb, '${tags}'::jsonb`;
  }
);

// Fix query_logs: data_sources and tables_queried are TEXT[]
console.log('🔧 Fixing query_logs...');
content = content.replace(
  /(data_sources|tables_queried), '(\[[^\]]*\])'/g,
  (match, col, arr) => {
    try {
      const parsed = JSON.parse(arr);
      if (Array.isArray(parsed) && parsed.length === 0) {
        fixCount++;
        return `${col}, ARRAY[]::text[]`;
      } else if (Array.isArray(parsed)) {
        fixCount++;
        const items = parsed.map(item => `'${item.replace(/'/g, "''")}'`).join(',');
        return `${col}, ARRAY[${items}]::text[]`;
      }
    } catch (e) {}
    return match;
  }
);

// Fix all remaining '[]' to ARRAY[]::text[] and '{}' to '{}'::jsonb
console.log('🔧 Fixing remaining arrays and objects...');
content = content.replace(/, '\[\]'/g, () => {
  fixCount++;
  return `, ARRAY[]::text[]`;
});

content = content.replace(/, '\{\}'/g, () => {
  fixCount++;
  return `, '{}'::jsonb`;
});

console.log(`✅ Applied ${fixCount} fixes\n`);

// Save and split
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

let currentChunk = [];
let currentSize = 0;
let chunkNumber = 1;

for (const table of tableOrder) {
  for (const insert of tableData[table]) {
    const insertSize = Buffer.byteLength(insert + '\n', 'utf8');
    
    if (currentSize + insertSize > MAX_SIZE && currentChunk.length > 0) {
      fs.writeFileSync(`data-load-final-${chunkNumber}.sql`, currentChunk.join('\n\n'), 'utf8');
      console.log(`✅ Created data-load-final-${chunkNumber}.sql (${(currentSize/1024).toFixed(1)}KB)`);
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
  console.log(`✅ Created data-load-final-${chunkNumber}.sql (${(currentSize/1024).toFixed(1)}KB)`);
}

console.log(`\n📊 Total: ${fixCount} fixes, ${chunkNumber} files created`);
