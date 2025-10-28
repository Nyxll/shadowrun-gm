import fs from 'fs';

// All JSONB columns from the schema
const jsonbColumns = {
  metatypes: ['racial_traits'],
  powers: ['game_effects', 'levels'],
  gear: ['base_stats', 'modifiers', 'requirements'],
  sr_characters: ['attributes', 'skills_data', 'qualities_taken', 'gear_owned', 
                  'cyberware_installed', 'spells_known', 'powers_active', 
                  'contacts_list', 'biography'],
  character_modifiers: ['modifier_data'],
  house_rules: ['rule_config'],
  rule_application_log: ['rule_config_snapshot', 'application_context'],
  query_logs: ['classification', 'dice_rolls']
};

console.log('Checking all SQL files for JSONB field issues...\n');

// Check all ordered files
let totalIssues = 0;
let filesWithIssues = 0;

for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (!fs.existsSync(filename)) continue;
  
  const content = fs.readFileSync(filename, 'utf8');
  const lines = content.split('\n');
  
  let fileIssues = 0;
  
  lines.forEach((line, lineNum) => {
    // Check for ARRAY[]::text[] patterns (should be '[]'::jsonb)
    if (line.includes('ARRAY[]::text[]')) {
      console.log(`❌ ${filename}:${lineNum + 1} - Found ARRAY[]::text[]`);
      fileIssues++;
    }
    
    // Check for empty object patterns that might be wrong
    if (line.includes("'{}'::text[]")) {
      console.log(`❌ ${filename}:${lineNum + 1} - Found '{}'::text[] (should be '{}'::jsonb or '{}')`);
      fileIssues++;
    }
  });
  
  if (fileIssues > 0) {
    filesWithIssues++;
    totalIssues += fileIssues;
  }
}

console.log(`\n📊 Summary:`);
console.log(`Files checked: 91`);
console.log(`Files with issues: ${filesWithIssues}`);
console.log(`Total issues found: ${totalIssues}`);

if (totalIssues === 0) {
  console.log('\n✅ All files look good!');
} else {
  console.log('\n⚠️  Issues found that need fixing');
}
