#!/usr/bin/env node

/**
 * Check Characters - Compare database vs latest files
 */

import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = path.join(__dirname, '../shadowrun.db');
const CHARACTERS_DIR = 'G:/My Drive/SR-ai/teaching-ai/Characters';

console.log('🔍 Checking Characters Status\n');
console.log('='.repeat(60));

// Check database
console.log('\n📊 Characters in Database:');
console.log('-'.repeat(60));

try {
  const db = new Database(DB_PATH);
  const characters = db.prepare('SELECT id, name, street_name, metatype, archetype FROM characters ORDER BY id').all();
  
  if (characters.length === 0) {
    console.log('❌ No characters found in database');
  } else {
    characters.forEach(char => {
      console.log(`ID ${char.id}: ${char.name} "${char.street_name}" (${char.metatype} ${char.archetype || 'N/A'})`);
    });
  }
  
  console.log(`\nTotal: ${characters.length} characters`);
  db.close();
} catch (error) {
  console.error('❌ Error reading database:', error.message);
}

// Check character files
console.log('\n📁 Latest Character Files:');
console.log('-'.repeat(60));

if (!fs.existsSync(CHARACTERS_DIR)) {
  console.log(`❌ Directory not found: ${CHARACTERS_DIR}`);
} else {
  try {
    const files = fs.readdirSync(CHARACTERS_DIR)
      .filter(name => name.endsWith('.markdown'))
      .sort();
    
    console.log(`Found ${files.length} character files\n`);
    
    // Group by character (numbered prefix)
    const characterGroups = {};
    
    files.forEach(filename => {
      const match = filename.match(/^(\d+)-([^_]+)_Updated_Character_Sheet\s*\((\d+)\)\.markdown$/);
      if (match) {
        const [, number, name, version] = match;
        const key = `${number}-${name}`;
        
        if (!characterGroups[key]) {
          characterGroups[key] = {
            number,
            name,
            versions: []
          };
        }
        
        characterGroups[key].versions.push({
          version: parseInt(version),
          filename
        });
      }
    });
    
    // Find latest version of each character
    console.log('Latest versions:');
    Object.values(characterGroups).forEach(group => {
      const latest = group.versions.sort((a, b) => b.version - a.version)[0];
      console.log(`  ${group.number}. ${group.name}: Version ${latest.version}`);
      console.log(`     File: ${latest.filename}`);
      
      // Read and parse basic info
      const filePath = path.join(CHARACTERS_DIR, latest.filename);
      const content = fs.readFileSync(filePath, 'utf-8');
      
      const nameMatch = content.match(/[-*]\s*\*\*Name\*\*:\s*([^\n]+)/i);
      const streetMatch = content.match(/[-*]\s*\*\*Street Name\*\*:\s*([^\n]+)/i);
      const raceMatch = content.match(/[-*]\s*\*\*Race\*\*:\s*([^\n]+)/i);
      
      if (nameMatch) console.log(`     Name: ${nameMatch[1].trim()}`);
      if (streetMatch) console.log(`     Street Name: ${streetMatch[1].trim()}`);
      if (raceMatch) console.log(`     Race: ${raceMatch[1].trim()}`);
      console.log();
    });
    
    console.log(`\nTotal: ${Object.keys(characterGroups).length} unique characters`);
    
  } catch (error) {
    console.error('❌ Error reading character files:', error.message);
  }
}

console.log('\n' + '='.repeat(60));
console.log('\n💡 Recommendation:');
console.log('If characters are missing from database, we should import the latest versions.');
console.log('If characters exist but are outdated, we should update them.');
