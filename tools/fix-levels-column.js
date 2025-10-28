import fs from 'fs';

console.log('Fixing powers.levels column to be JSONB instead of TEXT[]\n');

let totalFixes = 0;

for (let i = 1; i <= 40; i++) {
  const filename = `data-load-final-${i}.sql`;
  if (!fs.existsSync(filename)) continue;
  
  let content = fs.readFileSync(filename, 'utf8');
  let fixes = 0;
  
  // Fix: game_effects, ARRAY[]::text[] → game_effects, '[]'::jsonb
  content = content.replace(
    /(INSERT INTO powers[^;]+), ARRAY\[\]::text\[\]/gs,
    (match, prefix) => {
      if (match.includes('game_effects')) {
        fixes++;
        return `${prefix}, '[]'::jsonb`;
      }
      return match;
    }
  );
  
  // Fix: game_effects, ARRAY[...]::text[] → game_effects, '[...]'::jsonb
  content = content.replace(
    /(INSERT INTO powers[^;]+game_effects[^,]+), ARRAY\[([^\]]+)\]::text\[\]/gs,
    (match, prefix, items) => {
      fixes++;
      // Convert ARRAY['item1','item2'] back to JSON array
      const itemList = items.split(',').map(i => {
        const trimmed = i.trim();
        // Remove quotes and unescape
        return trimmed.replace(/^'|'$/g, '').replace(/''/g, "'");
      });
      const jsonArray = JSON.stringify(itemList);
      return `${prefix}, '${jsonArray}'::jsonb`;
    }
  );
  
  if (fixes > 0) {
    fs.writeFileSync(filename, content, 'utf8');
    console.log(`✅ ${filename}: Fixed ${fixes} levels columns`);
    totalFixes += fixes;
  }
}

console.log(`\n✅ Total: Fixed ${totalFixes} levels columns across all files`);
