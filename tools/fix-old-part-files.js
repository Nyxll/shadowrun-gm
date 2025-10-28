import fs from 'fs';

console.log('Fixing old supabase-data-part*.sql files...\n');

const files = ['supabase-data-part50.sql', 'supabase-data-part51.sql', 'supabase-data-part55.sql'];

files.forEach(filename => {
  if (!fs.existsSync(filename)) {
    console.log(`⚠️  ${filename} not found, skipping...`);
    return;
  }
  
  let content = fs.readFileSync(filename, 'utf8');
  const before = content;
  
  // Fix '["value"]' to ARRAY['value']::text[] for text[] columns
  content = content.replace(/'(\["[^"]+"\])'/g, (match, arrayStr) => {
    try {
      const parsed = JSON.parse(arrayStr);
      if (Array.isArray(parsed)) {
        const items = parsed.map(item => `'${item}'`).join(',');
        return `ARRAY[${items}]::text[]`;
      }
    } catch (e) {
      console.log(`  Warning: Could not parse ${arrayStr}`);
    }
    return match;
  });
  
  if (content !== before) {
    fs.writeFileSync(filename, content, 'utf8');
    console.log(`✅ Fixed ${filename}`);
  } else {
    console.log(`  No changes needed for ${filename}`);
  }
});

console.log('\n⚠️  IMPORTANT: You should be uploading supabase-data-ORDERED-part*.sql files, not supabase-data-part*.sql files!');
console.log('The ordered files are the correct ones with all fixes applied.');
