import fs from 'fs';

console.log('Finding files with malformed array literals...\n');

const files = fs.readdirSync('.').filter(f => 
  (f.startsWith('supabase-data-part') || f.startsWith('supabase-data-ordered-part')) && 
  f.endsWith('.sql')
);

files.forEach(f => {
  const content = fs.readFileSync(f, 'utf8');
  
  // Look for the pattern from the error: '["structured"]'
  if (content.includes('"[\\"structured\\"]"') || 
      content.includes('\'["structured"]\'') ||
      content.includes('\'["gear"]\'')) {
    console.log(`Found in: ${f}`);
    
    // Show a sample
    const lines = content.split('\n');
    const badLine = lines.find(l => 
      l.includes('"[\\"structured\\"]"') || 
      l.includes('\'["structured"]\'') ||
      l.includes('\'["gear"]\'')
    );
    if (badLine) {
      console.log(`  Sample: ${badLine.substring(0, 200)}...\n`);
    }
  }
});
