import fs from 'fs';

console.log('Creating FINAL PROPER FIX based on exact column positions...\n');

const MAX_SIZE = 1000 * 1024;

console.log('📖 Reading supabase-data.sql...');
let content = fs.readFileSync('supabase-data.sql', 'utf8');

let fixes = 0;

// Process line by line to handle each INSERT correctly
const lines = content.split('\n');
const fixedLines = [];

for (let line of lines) {
  if (line.includes('INSERT INTO metatypes')) {
    // Position 17: special_abilities (TEXT[])
    // Position 18: racial_traits (JSONB)
    line = line.replace(
      /(VALUES \([^,]+(?:,[^,]+){16}), '(\[[^\]]*\])', '(\{[^}]*\})'/,
      (match, prefix, arr, obj) => {
        fixes += 2;
        // Convert array to ARRAY syntax
        let arrayVal = 'ARRAY[]::text[]';
        try {
          const parsed = JSON.parse(arr);
          if (parsed.length > 0) {
            const items = parsed.map(i => `'${String(i).replace(/'/g, "''")}'`).join(',');
            arrayVal = `ARRAY[${items}]::text[]`;
          }
        } catch (e) {}
        return `${prefix}, ${arrayVal}, '${obj}'::jsonb`;
      }
    );
  } else if (line.includes('INSERT INTO powers')) {
    // Position 7: game_effects (JSONB)
    // Position 8: levels (JSONB)
    line = line.replace(
      /(VALUES \([^,]+(?:,[^,]+){6}), '(\{[^}]*\})', '(\[[^\]]*\])'/,
      (match, prefix, obj, arr) => {
        fixes += 2;
        return `${prefix}, '${obj}'::jsonb, '${arr}'::jsonb`;
      }
    );
  } else if (line.includes('INSERT INTO gear')) {
    // Positions: base_stats, modifiers, requirements (all JSONB), tags (TEXT[])
    line = line.replace(
      /(VALUES \([^,]+(?:,[^,]+){5}), '(\{[^}]*\})', '(\{[^}]*\})', '(\{[^}]*\})', '(\{[^}]*\})'/,
      (match, prefix, stats, mods, reqs, tags) => {
        fixes += 4;
        return `${prefix}, '${stats}'::jsonb, '${mods}'::jsonb, '${reqs}'::jsonb, '${tags}'::jsonb`;
      }
    );
  } else if (line.includes('INSERT INTO query_logs')) {
    // Fix data_sources and tables_queried (TEXT[])
    line = line.replace(
      /(data_sources|tables_queried), '(\[[^\]]*\])'/g,
      (match, col, arr) => {
        fixes++;
        let arrayVal = 'ARRAY[]::text[]';
        try {
          const parsed = JSON.parse(arr);
          if (parsed.length > 0) {
            const items = parsed.map(i => `'${String(i).replace(/'/g, "''")}'`).join(',');
            arrayVal = `ARRAY[${items}]::text[]`;
          }
        } catch (e) {}
        return `${col}, ${arrayVal}`;
      }
    );
    // Fix classification and dice_rolls (JSONB)
    line = line.replace(
      /(classification|dice_rolls), '(\{[^}]*\}|(\[[^\]]*\]))'/g,
      (match, col, val) => {
        fixes++;
        return `${col}, '${val}'::jsonb`;
      }
    );
  }
  
  // Fix any remaining loaded_from TEXT[] columns
  if (line.includes('loaded_from')) {
    line = line.replace(
      /loaded_from, '(\[[^\]]*\])'/g,
      (match, arr) => {
        fixes++;
        let arrayVal = 'ARRAY[]::text[]';
        try {
          const parsed = JSON.parse(arr);
          if (parsed.length > 0) {
            const items = parsed.map(i => `'${String(i).replace(/'/g, "''")}'`).join(',');
            arrayVal = `ARRAY[${items}]::text[]`;
          }
        } catch (e) {}
        return `loaded_from, ${arrayVal}`;
      }
    );
  }
  
  fixedLines.push(line);
}

content = fixedLines.join('\n');

console.log(`✅ Applied ${fixes} fixes\n`);

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

const contentLines = content.split('\n');
let currentInsert = '';

for (const line of contentLines) {
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
      console.log(`✅ data-load-final-${chunkNumber}.sql (${(currentSize/1024).toFixed(1)}KB)`);
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
  console.log(`✅ data-load-final-${chunkNumber}.sql (${(currentSize/1024).toFixed(1)}KB)`);
}

console.log(`\n✅ Created ${chunkNumber} files with ${fixes} fixes`);
