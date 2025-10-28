import fs from 'fs';

console.log('Fixing text[] columns that were incorrectly converted to jsonb...\n');

// Columns that should be text[] not jsonb
const textArrayColumns = {
  metatypes: ['special_abilities', 'loaded_from'],
  powers: ['loaded_from'],
  spells: ['loaded_from'],
  totems: ['loaded_from'],
  gear: ['tags', 'loaded_from'],
  rules_content: ['tags'],
  query_logs: ['data_sources', 'tables_queried']
};

let totalFixed = 0;

for (let i = 1; i <= 91; i++) {
  const filename = `supabase-data-ordered-part${i}.sql`;
  if (!fs.existsSync(filename)) continue;
  
  let content = fs.readFileSync(filename, 'utf8');
  let fileFixed = 0;
  
  // Fix '[]'::jsonb back to ARRAY[]::text[] for text[] columns
  // Also fix '["something"]'::jsonb to ARRAY['something']::text[]
  
  const lines = content.split('\n');
  const fixedLines = lines.map(line => {
    if (!line.includes('INSERT INTO')) return line;
    
    let fixedLine = line;
    
    // For gear table tags column: '[]'::jsonb -> ARRAY[]::text[]
    if (line.includes('INSERT INTO gear')) {
      // Replace empty arrays
      fixedLine = fixedLine.replace(/, '(\[\])'::jsonb,/g, ', ARRAY[]::text[],');
      // Replace arrays with values like '["tag1","tag2"]'::jsonb
      fixedLine = fixedLine.replace(/, '(\[.*?\])'::jsonb,/g, (match, arrayContent) => {
        // Convert JSON array to PostgreSQL array
        const items = arrayContent.match(/"([^"]+)"/g);
        if (items) {
          const pgArray = items.map(item => item).join(',');
          return `, ARRAY[${pgArray}]::text[],`;
        }
        return ', ARRAY[]::text[],';
      });
    }
    
    // For loaded_from columns in various tables
    if (line.includes('loaded_from')) {
      // Find and replace loaded_from values
      fixedLine = fixedLine.replace(/loaded_from, ([^,]+), ([^,]+), ([^,]+)\) VALUES \(([^)]+), '(\[.*?\])'::jsonb,/g, 
        (match, col1, col2, col3, values, arrayContent) => {
          const items = arrayContent.match(/"([^"]+)"/g);
          if (items) {
            const pgArray = items.map(item => item).join(',');
            return `loaded_from, ${col1}, ${col2}, ${col3}) VALUES (${values}, ARRAY[${pgArray}]::text[],`;
          }
          return `loaded_from, ${col1}, ${col2}, ${col3}) VALUES (${values}, ARRAY[]::text[],`;
        });
    }
    
    if (fixedLine !== line) fileFixed++;
    return fixedLine;
  });
  
  if (fileFixed > 0) {
    fs.writeFileSync(filename, fixedLines.join('\n'), 'utf8');
    console.log(`✅ Fixed ${fileFixed} text[] columns in ${filename}`);
    totalFixed += fileFixed;
  }
}

// Also fix the merged file
const mergedFile = 'supabase-data-merged-39-54-chunk1.sql';
if (fs.existsSync(mergedFile)) {
  let content = fs.readFileSync(mergedFile, 'utf8');
  let fileFixed = 0;
  
  const lines = content.split('\n');
  const fixedLines = lines.map(line => {
    if (!line.includes('INSERT INTO')) return line;
    
    let fixedLine = line;
    
    if (line.includes('INSERT INTO gear')) {
      fixedLine = fixedLine.replace(/, '(\[\])'::jsonb,/g, ', ARRAY[]::text[],');
      fixedLine = fixedLine.replace(/, '(\[.*?\])'::jsonb,/g, (match, arrayContent) => {
        const items = arrayContent.match(/"([^"]+)"/g);
        if (items) {
          const pgArray = items.map(item => item).join(',');
          return `, ARRAY[${pgArray}]::text[],`;
        }
        return ', ARRAY[]::text[],';
      });
    }
    
    if (line.includes('loaded_from')) {
      fixedLine = fixedLine.replace(/loaded_from, ([^,]+), ([^,]+), ([^,]+)\) VALUES \(([^)]+), '(\[.*?\])'::jsonb,/g, 
        (match, col1, col2, col3, values, arrayContent) => {
          const items = arrayContent.match(/"([^"]+)"/g);
          if (items) {
            const pgArray = items.map(item => item).join(',');
            return `loaded_from, ${col1}, ${col2}, ${col3}) VALUES (${values}, ARRAY[${pgArray}]::text[],`;
          }
          return `loaded_from, ${col1}, ${col2}, ${col3}) VALUES (${values}, ARRAY[]::text[],`;
        });
    }
    
    if (fixedLine !== line) fileFixed++;
    return fixedLine;
  });
  
  if (fileFixed > 0) {
    fs.writeFileSync(mergedFile, fixedLines.join('\n'), 'utf8');
    console.log(`✅ Fixed ${fileFixed} text[] columns in ${mergedFile}`);
    totalFixed += fileFixed;
  }
}

console.log(`\n📊 Total text[] columns fixed: ${totalFixed}`);
