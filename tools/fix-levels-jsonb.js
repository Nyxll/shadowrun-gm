import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read the SQL file
const sqlFilePath = path.join(__dirname, '..', 'supabase-data-fixed.sql');
let sqlContent = fs.readFileSync(sqlFilePath, 'utf8');

console.log('Fixing levels column type mismatch...');
console.log('Original file size:', sqlContent.length, 'bytes');

// Count occurrences before fix
const beforeCount = (sqlContent.match(/ARRAY\[\]::text\[\]/g) || []).length;
console.log('Found', beforeCount, 'instances of ARRAY[]::text[]');

// Replace ARRAY[]::text[] with '[]'::jsonb
sqlContent = sqlContent.replace(/ARRAY\[\]::text\[\]/g, "'[]'::jsonb");

// Count occurrences after fix
const afterCount = (sqlContent.match(/ARRAY\[\]::text\[\]/g) || []).length;
console.log('Remaining instances of ARRAY[]::text[]:', afterCount);

// Count new jsonb arrays
const jsonbCount = (sqlContent.match(/'?\[\]'?::jsonb/g) || []).length;
console.log('Total instances of []::jsonb:', jsonbCount);

// Write the fixed content back
fs.writeFileSync(sqlFilePath, sqlContent, 'utf8');

console.log('\n✓ Fixed! Updated file saved to:', sqlFilePath);
console.log('File size after fix:', sqlContent.length, 'bytes');
