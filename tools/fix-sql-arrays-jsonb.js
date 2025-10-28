#!/usr/bin/env node

/**
 * Fix array and JSONB literals in SQL files for PostgreSQL compatibility
 * Converts ARRAY[]::text[] to '[]'::jsonb for JSONB columns
 * Converts ARRAY[]::text[] to ARRAY[]::text[] for text[] columns (no change needed)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.join(__dirname, '..');

// Map of table columns that should be JSONB (not text[])
const jsonbColumns = {
  'metatypes': ['racial_traits'],
  'powers': ['game_effects', 'levels'],
  'qualities': ['modifiers', 'requirements'],
  'gear': ['base_stats'],
  'characters': ['attributes', 'skills_data', 'qualities_taken', 'gear_owned', 
                 'cyberware_installed', 'spells_known', 'powers_active', 
                 'contacts_list', 'biography'],
  'character_history': ['old_value', 'new_value'],
  'active_modifiers': ['modifier_data'],
  'modifier_rules': ['rule_config'],
  'modifier_applications': ['rule_config_snapshot', 'application_context'],
  'training_data': ['classification', 'dice_rolls']
};

// Find all ordered SQL files
const files = fs.readdirSync(projectRoot)
  .filter(f => f.startsWith('supabase-data-ordered-part') && f.endsWith('.sql'))
  .sort((a, b) => {
    const numA = parseInt(a.match(/part(\d+)/)[1]);
    const numB = parseInt(b.match(/part(\d+)/)[1]);
    return numA - numB;
  });

console.log(`Found ${files.length} SQL files to fix\n`);

let totalFixed = 0;

files.forEach((file, index) => {
  const filePath = path.join(projectRoot, file);
  let content = fs.readFileSync(filePath, 'utf8');
  let hasChanges = false;
  
  // For each table with JSONB columns
  for (const [tableName, columns] of Object.entries(jsonbColumns)) {
    // Create regex to match INSERT statements for this table
    const tableRegex = new RegExp(`INSERT INTO ${tableName} \\([^)]+\\) VALUES \\([^;]+\\);`, 'g');
    const matches = content.match(tableRegex);
    
    if (matches) {
      matches.forEach(match => {
        let fixedMatch = match;
        
        // Replace ARRAY[]::text[] with '[]'::jsonb
        // Replace ARRAY[...]::text[] with '[...]'::jsonb (convert to JSON array)
        fixedMatch = fixedMatch.replace(/ARRAY\[\]::text\[\]/g, "'[]'::jsonb");
        
        // Handle non-empty arrays - convert ARRAY['item1','item2']::text[] to '["item1","item2"]'::jsonb
        fixedMatch = fixedMatch.replace(/ARRAY\[([^\]]+)\]::text\[\]/g, (match, items) => {
          // Split items and convert to JSON array format
          const itemList = items.split(',').map(item => item.trim());
          const jsonArray = '[' + itemList.join(',') + ']';
          return `'${jsonArray}'::jsonb`;
        });
        
        if (fixedMatch !== match) {
          content = content.replace(match, fixedMatch);
          hasChanges = true;
        }
      });
    }
  }
  
  if (hasChanges) {
    fs.writeFileSync(filePath, content);
    console.log(`✅ Fixed ${file}`);
    totalFixed++;
  } else {
    console.log(`⏭️  Skipped ${file} (no changes needed)`);
  }
});

console.log(`\n🎉 Fixed ${totalFixed} files!`);
