import fs from 'fs';

console.log('Fixing query_logs table array columns...\n');

let totalFixed = 0;

// Fix all ordered files
for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (!fs.existsSync(filename)) continue;
  
  let content = fs.readFileSync(filename, 'utf8');
  const before = content;
  
  // Fix query_logs INSERT statements
  // Pattern: '["value"]' should be ARRAY['value']::text[]
  content = content.replace(/INSERT INTO query_logs \([^)]+\) VALUES \(([^;]+)\);/g, (match, values) => {
    // Split by commas but be careful with nested structures
    let fixedValues = values;
    
    // Fix data_sources and tables_queried which are text[] columns
    // They appear as '"[\"structured\"]"' and need to be ARRAY['structured']::text[]
    
    // Pattern 1: '"[\"value\"]"' -> ARRAY['value']::text[]
    fixedValues = fixedValues.replace(/'"(\[\\?"[^"]+\\?"\])"'/g, (m, arrayStr) => {
      // Remove escape characters and parse
      const cleaned = arrayStr.replace(/\\/g, '');
      try {
        const parsed = JSON.parse(cleaned);
        if (Array.isArray(parsed)) {
          const items = parsed.map(item => `'${item}'`).join(',');
          return `ARRAY[${items}]::text[]`;
        }
      } catch (e) {
        // If parsing fails, return original
      }
      return m;
    });
    
    // Pattern 2: '["value"]' -> ARRAY['value']::text[]
    fixedValues = fixedValues.replace(/'(\["[^"]+"\])'/g, (m, arrayStr) => {
      try {
        const parsed = JSON.parse(arrayStr);
        if (Array.isArray(parsed)) {
          const items = parsed.map(item => `'${item}'`).join(',');
          return `ARRAY[${items}]::text[]`;
        }
      } catch (e) {
        // If parsing fails, return original
      }
      return m;
    });
    
    return `INSERT INTO query_logs (${match.match(/INSERT INTO query_logs \(([^)]+)\)/)[1]}) VALUES (${fixedValues});`;
  });
  
  if (content !== before) {
    fs.writeFileSync(filename, content, 'utf8');
    const count = (before.match(/INSERT INTO query_logs/g) || []).length;
    console.log(`✅ Fixed ${count} query_logs entries in ${filename}`);
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
  
  content = content.replace(/INSERT INTO query_logs \([^)]+\) VALUES \(([^;]+)\);/g, (match, values) => {
    let fixedValues = values;
    
    fixedValues = fixedValues.replace(/'"(\[\\?"[^"]+\\?"\])"'/g, (m, arrayStr) => {
      const cleaned = arrayStr.replace(/\\/g, '');
      try {
        const parsed = JSON.parse(cleaned);
        if (Array.isArray(parsed)) {
          const items = parsed.map(item => `'${item}'`).join(',');
          return `ARRAY[${items}]::text[]`;
        }
      } catch (e) {}
      return m;
    });
    
    fixedValues = fixedValues.replace(/'(\["[^"]+"\])'/g, (m, arrayStr) => {
      try {
        const parsed = JSON.parse(arrayStr);
        if (Array.isArray(parsed)) {
          const items = parsed.map(item => `'${item}'`).join(',');
          return `ARRAY[${items}]::text[]`;
        }
      } catch (e) {}
      return m;
    });
    
    return `INSERT INTO query_logs (${match.match(/INSERT INTO query_logs \(([^)]+)\)/)[1]}) VALUES (${fixedValues});`;
  });
  
  if (content !== before) {
    fs.writeFileSync(filename, content, 'utf8');
    const count = (before.match(/INSERT INTO query_logs/g) || []).length;
    console.log(`✅ Fixed ${count} query_logs entries in ${filename}`);
    totalFixed += count;
  }
});

console.log(`\n📊 Total query_logs entries fixed: ${totalFixed}`);
