import fs from 'fs';

console.log('Fixing PostgreSQL array string quotes...\n');

let totalFixed = 0;

// Fix all ordered files
for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (!fs.existsSync(filename)) continue;
  
  let content = fs.readFileSync(filename, 'utf8');
  const before = content;
  
  // Fix ARRAY["string"] to ARRAY['string']
  // This regex finds ARRAY[...] and replaces double quotes with single quotes inside
  content = content.replace(/ARRAY\[([^\]]+)\]::text\[\]/g, (match, items) => {
    // Replace double quotes with single quotes for string literals
    const fixed = items.replace(/"/g, "'");
    return `ARRAY[${fixed}]::text[]`;
  });
  
  if (content !== before) {
    fs.writeFileSync(filename, content, 'utf8');
    const count = (before.match(/ARRAY\[([^\]]+)\]::text\[\]/g) || []).length;
    console.log(`✅ Fixed ${count} arrays in ${filename}`);
    totalFixed += count;
  }
}

// Fix merged files
const mergedFiles = [
  'supabase-data-merged-39-54-chunk1.sql',
  'supabase-data-merged-55-86-chunk1.sql'
];

mergedFiles.forEach(filename => {
  if (!fs.existsSync(filename)) return;
  
  let content = fs.readFileSync(filename, 'utf8');
  const before = content;
  
  content = content.replace(/ARRAY\[([^\]]+)\]::text\[\]/g, (match, items) => {
    const fixed = items.replace(/"/g, "'");
    return `ARRAY[${fixed}]::text[]`;
  });
  
  if (content !== before) {
    fs.writeFileSync(filename, content, 'utf8');
    const count = (before.match(/ARRAY\[([^\]]+)\]::text\[\]/g) || []).length;
    console.log(`✅ Fixed ${count} arrays in ${filename}`);
    totalFixed += count;
  }
});

console.log(`\n📊 Total arrays fixed: ${totalFixed}`);
