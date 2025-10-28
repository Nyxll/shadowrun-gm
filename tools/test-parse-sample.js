#!/usr/bin/env node

/**
 * Test Parser - Small Sample
 * Tests parsing on a small sample before processing everything
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test with small samples
const XAI_EXPORT_DIR = 'D:/projects/xAI/prod-mc-asset-server';
const LOGS_DIR = 'G:/My Drive/SR-ai/teaching-ai/Logs';
const OUTPUT_DIR = path.join(__dirname, '../test-parsed-sample');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

console.log('🧪 Testing Parsers with Small Sample\n');
console.log('='.repeat(60));

// Test 1: Check if directories exist
console.log('\n📁 Test 1: Directory Access');
console.log('-'.repeat(60));

const xaiExists = fs.existsSync(XAI_EXPORT_DIR);
const logsExists = fs.existsSync(LOGS_DIR);

console.log(`xAI Export Dir: ${xaiExists ? '✅ Found' : '❌ Not Found'}`);
console.log(`  Path: ${XAI_EXPORT_DIR}`);

console.log(`Logs Dir: ${logsExists ? '✅ Found' : '❌ Not Found'}`);
console.log(`  Path: ${LOGS_DIR}`);

if (!xaiExists && !logsExists) {
  console.log('\n❌ Neither directory found. Please verify paths.');
  process.exit(1);
}

// Test 2: Sample xAI exports (first 3 folders)
if (xaiExists) {
  console.log('\n📦 Test 2: xAI Export Sample (First 3 Folders)');
  console.log('-'.repeat(60));
  
  try {
    const folders = fs.readdirSync(XAI_EXPORT_DIR)
      .filter(name => {
        const fullPath = path.join(XAI_EXPORT_DIR, name);
        return fs.statSync(fullPath).isDirectory();
      })
      .slice(0, 3); // Only first 3
    
    console.log(`Found ${folders.length} sample folders to test\n`);
    
    const results = [];
    
    for (const uuid of folders) {
      const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
      
      if (fs.existsSync(contentPath)) {
        const content = fs.readFileSync(contentPath, 'utf-8');
        const preview = content.substring(0, 200).replace(/\n/g, ' ');
        
        console.log(`UUID: ${uuid}`);
        console.log(`  Size: ${content.length} bytes`);
        console.log(`  Preview: ${preview}...`);
        
        // Detect type
        const lower = content.toLowerCase();
        let type = 'unknown';
        if (lower.includes('character sheet')) type = 'character_sheet';
        else if (lower.includes('campaign')) type = 'campaign';
        else if (lower.includes('session')) type = 'session_log';
        
        console.log(`  Type: ${type}\n`);
        
        results.push({
          uuid,
          type,
          size: content.length,
          preview: preview
        });
      } else {
        console.log(`UUID: ${uuid}`);
        console.log(`  ❌ No 'content' file found\n`);
      }
    }
    
    // Save sample results
    const samplePath = path.join(OUTPUT_DIR, 'xai-sample.json');
    fs.writeFileSync(samplePath, JSON.stringify(results, null, 2));
    console.log(`✅ Sample saved to: ${samplePath}`);
    
  } catch (error) {
    console.error(`❌ Error reading xAI exports:`, error.message);
  }
}

// Test 3: Sample log files (first 2 files)
if (logsExists) {
  console.log('\n📝 Test 3: Roleplay Log Sample (First 2 Files)');
  console.log('-'.repeat(60));
  
  try {
    const logFiles = fs.readdirSync(LOGS_DIR)
      .filter(name => name.endsWith('.log'))
      .slice(0, 2); // Only first 2
    
    console.log(`Found ${logFiles.length} sample log files to test\n`);
    
    const results = [];
    
    for (const filename of logFiles) {
      const filePath = path.join(LOGS_DIR, filename);
      const content = fs.readFileSync(filePath, 'utf-8');
      const lines = content.split('\n').length;
      const preview = content.substring(0, 200).replace(/\n/g, ' ');
      
      console.log(`File: ${filename}`);
      console.log(`  Size: ${content.length} bytes`);
      console.log(`  Lines: ${lines}`);
      console.log(`  Preview: ${preview}...`);
      
      // Count some patterns
      const conversations = (content.match(/\n\n+/g) || []).length;
      const diceRolls = (content.match(/roll\s+\d+d\d+/gi) || []).length;
      const gmResponses = (content.match(/GM:|Gamemaster:/gi) || []).length;
      
      console.log(`  Conversations: ~${conversations}`);
      console.log(`  Dice Rolls: ${diceRolls}`);
      console.log(`  GM Responses: ${gmResponses}\n`);
      
      results.push({
        filename,
        size: content.length,
        lines,
        conversations,
        diceRolls,
        gmResponses,
        preview
      });
    }
    
    // Save sample results
    const samplePath = path.join(OUTPUT_DIR, 'logs-sample.json');
    fs.writeFileSync(samplePath, JSON.stringify(results, null, 2));
    console.log(`✅ Sample saved to: ${samplePath}`);
    
  } catch (error) {
    console.error(`❌ Error reading log files:`, error.message);
  }
}

// Test 4: Parse one complete character sheet
if (xaiExists) {
  console.log('\n🧑 Test 4: Parse Complete Character Sheet');
  console.log('-'.repeat(60));
  
  try {
    const folders = fs.readdirSync(XAI_EXPORT_DIR)
      .filter(name => {
        const fullPath = path.join(XAI_EXPORT_DIR, name);
        return fs.statSync(fullPath).isDirectory();
      });
    
    // Find a character sheet
    let characterSheet = null;
    let characterUuid = null;
    
    for (const uuid of folders) {
      const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
      if (fs.existsSync(contentPath)) {
        const content = fs.readFileSync(contentPath, 'utf-8');
        if (content.toLowerCase().includes('character sheet')) {
          characterSheet = content;
          characterUuid = uuid;
          break;
        }
      }
    }
    
    if (characterSheet) {
      console.log(`Found character sheet in: ${characterUuid}\n`);
      
      // Extract basic info
      const nameMatch = characterSheet.match(/Name:\s*\*\*([^*]+)\*\*/i);
      const raceMatch = characterSheet.match(/Race:\s*\*\*([^*]+)\*\*/i);
      const streetNameMatch = characterSheet.match(/Street Name:\s*\*\*([^*]+)\*\*/i);
      
      console.log('Extracted Data:');
      console.log(`  Name: ${nameMatch ? nameMatch[1] : 'Not found'}`);
      console.log(`  Street Name: ${streetNameMatch ? streetNameMatch[1] : 'Not found'}`);
      console.log(`  Race: ${raceMatch ? raceMatch[1] : 'Not found'}`);
      
      // Extract attributes
      const attributesSection = characterSheet.match(/## Attributes([\s\S]*?)(?=##|$)/i);
      if (attributesSection) {
        console.log('\n  Attributes:');
        const attrLines = attributesSection[1].split('\n');
        attrLines.forEach(line => {
          const match = line.match(/[-*]\s*\*\*([^*]+)\*\*:\s*(\d+)/);
          if (match) {
            console.log(`    ${match[1]}: ${match[2]}`);
          }
        });
      }
      
      // Extract skills
      const skillsSection = characterSheet.match(/## Skills([\s\S]*?)(?=##|$)/i);
      if (skillsSection) {
        console.log('\n  Skills (first 5):');
        const skillLines = skillsSection[1].split('\n').slice(0, 7);
        skillLines.forEach(line => {
          const match = line.match(/[-*]\s*([^:]+):\s*(\d+)/);
          if (match) {
            console.log(`    ${match[1].trim()}: ${match[2]}`);
          }
        });
      }
      
      const parsed = {
        uuid: characterUuid,
        name: nameMatch ? nameMatch[1] : null,
        streetName: streetNameMatch ? streetNameMatch[1] : null,
        race: raceMatch ? raceMatch[1] : null,
        hasAttributes: !!attributesSection,
        hasSkills: !!skillsSection
      };
      
      const parsedPath = path.join(OUTPUT_DIR, 'character-parsed.json');
      fs.writeFileSync(parsedPath, JSON.stringify(parsed, null, 2));
      console.log(`\n✅ Parsed character saved to: ${parsedPath}`);
      
    } else {
      console.log('❌ No character sheet found in sample');
    }
    
  } catch (error) {
    console.error(`❌ Error parsing character:`, error.message);
  }
}

console.log('\n' + '='.repeat(60));
console.log('✅ Sample Testing Complete!');
console.log(`\nResults saved to: ${OUTPUT_DIR}`);
console.log('\nNext steps:');
console.log('1. Review the sample output files');
console.log('2. If everything looks good, run the full parsers');
console.log('3. node tools/parse-xai-exports.js');
console.log('4. node tools/parse-roleplay-logs.js');
