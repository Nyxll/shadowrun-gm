import fs from 'fs';

console.log('Fixing JSON array syntax in SQL files...\n');

let totalFixed = 0;

for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (!fs.existsSync(filename)) continue;
  
  let content = fs.readFileSync(filename, 'utf8');
  let fixed = 0;
  
  // Fix single-quoted JSON arrays to use double quotes
  // Pattern: '['something']'::jsonb should be '["something"]'::jsonb
  const before = content;
  content = content.replace(/'(\[.*?\])'/g, (match, arrayContent) => {
    // Convert single quotes inside array to double quotes
    const fixed = arrayContent.replace(/'/g, '"');
    return `'${fixed}'`;
  });
  
  if (content !== before) {
    fs.writeFileSync(filename, content, 'utf8');
    fixed = (before.match(/'(\[.*?\])'/g) || []).length;
    console.log(`✅ Fixed ${fixed} JSON arrays in ${filename}`);
    totalFixed += fixed;
  }
}

console.log(`\n📊 Total JSON arrays fixed: ${totalFixed}`);
