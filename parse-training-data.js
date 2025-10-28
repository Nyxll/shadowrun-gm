/**
 * Training Data Parser
 * 
 * Parses gm-train.txt to extract real player queries and categorize them
 * for training the intent classification system.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read the training file
const trainingFile = path.join(__dirname, 'train', 'gm-train.txt');
const content = fs.readFileSync(trainingFile, 'utf-8');

// Intent mapping from training categories to our system
const intentMapping = {
  'GEAR_LOOKUP': 'GEAR_LOOKUP',
  'GEAR_COMPARISON': 'GEAR_COMPARISON',
  'RULES_QUESTION': 'RULES_QUESTION',
  'LORE_QUESTION': 'LORE_QUESTION',
  'ROLEPLAY_ACTION': 'ROLEPLAY_ACTION',
  'CHARACTER_ACTION': 'ROLEPLAY_ACTION', // Map to ROLEPLAY_ACTION
  'COMBAT_ACTION': 'COMBAT_ACTION',
  'MIXED_QUERY': 'MIXED_QUERY',
  'SPELL_LOOKUP': 'SPELL_LOOKUP',
  'POWER_LOOKUP': 'POWER_LOOKUP',
  'TOTEM_LOOKUP': 'TOTEM_LOOKUP'
};

// Extract queries from markdown tables
function extractFromTables(text) {
  const queries = [];
  
  // Match table rows with | Statement/Action | Category |
  const tableRowRegex = /\|\s*"?([^|]+?)"?\s*\|\s*\*\*([A-Z_]+(?:\s*\/\s*\*\*[A-Z_]+\*\*)*)\*\*\s*(?:\([^)]*\))?\s*\|/g;
  
  let match;
  while ((match = tableRowRegex.exec(text)) !== null) {
    const query = match[1].trim();
    const categories = match[2];
    
    // Handle multiple categories (e.g., "GEAR_LOOKUP / **RULES_QUESTION**")
    const categoryList = categories.split(/\s*\/\s*\*\*|\*\*\s*\/\s*/).map(c => c.replace(/\*\*/g, '').trim());
    
    // Use the first category as primary
    const primaryCategory = categoryList[0];
    
    if (intentMapping[primaryCategory]) {
      queries.push({
        query: cleanQuery(query),
        intent: intentMapping[primaryCategory],
        originalCategory: primaryCategory,
        multiCategory: categoryList.length > 1
      });
    }
  }
  
  return queries;
}

// Extract queries from bullet lists
function extractFromBullets(text) {
  const queries = [];
  
  // Match bullet points with category annotations
  const bulletRegex = /-\s+"([^"]+)"\s*\(([^)]+)\)/g;
  
  let match;
  while ((match = bulletRegex.exec(text)) !== null) {
    const query = match[1].trim();
    const annotation = match[2];
    
    // Try to extract category from annotation
    const categoryMatch = annotation.match(/\*\*([A-Z_]+)\*\*/);
    if (categoryMatch) {
      const category = categoryMatch[1];
      if (intentMapping[category]) {
        queries.push({
          query: cleanQuery(query),
          intent: intentMapping[category],
          originalCategory: category,
          multiCategory: false
        });
      }
    }
  }
  
  return queries;
}

// Clean up query text
function cleanQuery(query) {
  return query
    .replace(/\[.*?\]/g, '') // Remove [bracketed text]
    .replace(/\*\*/g, '') // Remove markdown bold
    .replace(/\s+/g, ' ') // Normalize whitespace
    .replace(/^["']|["']$/g, '') // Remove surrounding quotes
    .trim();
}

// Parse the training data
console.log('Parsing training data from gm-train.txt...\n');

const tableQueries = extractFromTables(content);
const bulletQueries = extractFromBullets(content);
const allQueries = [...tableQueries, ...bulletQueries];

// Remove duplicates
const uniqueQueries = [];
const seen = new Set();

for (const item of allQueries) {
  const key = `${item.query}|${item.intent}`;
  if (!seen.has(key) && item.query.length > 5) { // Filter out very short queries
    seen.add(key);
    uniqueQueries.push(item);
  }
}

// Group by intent
const byIntent = {};
for (const item of uniqueQueries) {
  if (!byIntent[item.intent]) {
    byIntent[item.intent] = [];
  }
  byIntent[item.intent].push(item.query);
}

// Display statistics
console.log('=== TRAINING DATA STATISTICS ===\n');
console.log(`Total unique queries extracted: ${uniqueQueries.length}\n`);

for (const [intent, queries] of Object.entries(byIntent).sort((a, b) => b[1].length - a[1].length)) {
  console.log(`${intent}: ${queries.length} examples`);
}

// Generate training examples for embedding similarity
console.log('\n=== GENERATING TRAINING EXAMPLES ===\n');

const trainingExamples = {};

for (const [intent, queries] of Object.entries(byIntent)) {
  // Take up to 15 best examples per intent
  trainingExamples[intent] = queries.slice(0, 15);
}

// Save to JSON file
const outputPath = path.join(__dirname, 'train', 'parsed-training-data.json');
fs.writeFileSync(outputPath, JSON.stringify({
  metadata: {
    totalQueries: uniqueQueries.length,
    generatedAt: new Date().toISOString(),
    source: 'gm-train.txt'
  },
  byIntent: trainingExamples,
  allQueries: uniqueQueries
}, null, 2));

console.log(`\nTraining data saved to: ${outputPath}`);

// Display sample queries for each intent
console.log('\n=== SAMPLE QUERIES BY INTENT ===\n');

for (const [intent, queries] of Object.entries(trainingExamples)) {
  console.log(`\n${intent} (${queries.length} examples):`);
  queries.slice(0, 5).forEach((q, i) => {
    console.log(`  ${i + 1}. "${q}"`);
  });
  if (queries.length > 5) {
    console.log(`  ... and ${queries.length - 5} more`);
  }
}

console.log('\n=== DONE ===\n');
