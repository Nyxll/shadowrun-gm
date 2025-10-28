#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const inputFile = path.join(__dirname, '..', 'supabase-data.sql');
const content = fs.readFileSync(inputFile, 'utf8');

// Define table dependency order (parent tables first)
const tableOrder = [
  'metatypes',
  'powers',
  'spells',
  'totems',
  'rules_content',
  'gear',
  'gear_chunk_links',
  'campaigns',
  'sr_characters',
  'character_skills',
  'character_spells',
  'character_powers',
  'character_contacts',
  'character_gear',
  'character_history',
  'character_modifiers',
  'house_rules',
  'rule_application_log',
  'query_logs'
];

// Parse all INSERT statements
const statementsByTable = {};

let current = '';
let currentTable = '';
let inStatement = false;

content.split('\n').forEach(line => {
  const trimmed = line.trim();
  
  if (trimmed.startsWith('INSERT INTO')) {
    if (current && currentTable) {
      if (!statementsByTable[currentTable]) {
        statementsByTable[currentTable] = [];
      }
      statementsByTable[currentTable].push(current);
    }
    
    // Extract table name
    const match = trimmed.match(/INSERT INTO\s+(\w+)/i);
    currentTable = match ? match[1] : '';
    current = line + '\n';
    inStatement = true;
  } else if (inStatement) {
    current += line + '\n';
    if (trimmed.endsWith(';')) {
      if (currentTable) {
        if (!statementsByTable[currentTable]) {
          statementsByTable[currentTable] = [];
        }
        statementsByTable[currentTable].push(current);
      }
      current = '';
      currentTable = '';
      inStatement = false;
    }
  }
});

// Add any remaining statement
if (current && currentTable) {
  if (!statementsByTable[currentTable]) {
    statementsByTable[currentTable] = [];
  }
  statementsByTable[currentTable].push(current);
}

console.log('\n📊 Statements by table:');
Object.keys(statementsByTable).forEach(table => {
  console.log(`  ${table}: ${statementsByTable[table].length} statements`);
});

// Combine statements in dependency order
const orderedStatements = [];

tableOrder.forEach(table => {
  if (statementsByTable[table]) {
    console.log(`\n✅ Adding ${statementsByTable[table].length} statements from ${table}`);
    orderedStatements.push(...statementsByTable[table]);
  }
});

// Add any tables not in our order list
Object.keys(statementsByTable).forEach(table => {
  if (!tableOrder.includes(table)) {
    console.log(`\n⚠️  Adding ${statementsByTable[table].length} statements from unlisted table: ${table}`);
    orderedStatements.push(...statementsByTable[table]);
  }
});

console.log(`\n📝 Total ordered statements: ${orderedStatements.length}`);

// Split into chunks of 50
const chunkSize = 50;
const chunks = [];

for (let i = 0; i < orderedStatements.length; i += chunkSize) {
  chunks.push(orderedStatements.slice(i, i + chunkSize));
}

console.log(`\n📦 Creating ${chunks.length} files...\n`);

chunks.forEach((chunk, index) => {
  const filename = path.join(__dirname, '..', `supabase-data-ordered-part${index + 1}.sql`);
  fs.writeFileSync(filename, chunk.join('\n'));
  console.log(`✅ Created ordered part ${index + 1}: ${chunk.length} statements`);
});

console.log(`\n🎉 Split complete! Files are in correct dependency order.`);
console.log(`Upload files in order: ordered-part1, ordered-part2, etc.`);
