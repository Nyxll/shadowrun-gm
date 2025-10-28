#!/usr/bin/env node

/**
 * xAI Export Sample Parser
 * Parses first 10 UUID folders to test parsing logic
 * This is Chunk 2 - Sample Analysis
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const XAI_EXPORT_DIR = 'D:/projects/xAI/prod-mc-asset-server';
const OUTPUT_DIR = path.join(__dirname, '../parsed-xai-data');
const SAMPLE_SIZE = 10;

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Detect what type of content this is
 */
function detectContentType(content) {
  const lower = content.toLowerCase();
  
  if (lower.includes('character sheet') || lower.includes('## basic information')) {
    return 'character_sheet';
  }
  if (lower.includes('campaign') || lower.includes('plot') || lower.includes('adventure')) {
    return 'campaign_data';
  }
  if (lower.includes('session') || lower.includes('run log') || lower.includes('karma award')) {
    return 'session_log';
  }
  if (lower.includes('npc') || lower.includes('contact')) {
    return 'npc_data';
  }
  if (lower.includes('location') || lower.includes('facility') || lower.includes('layout')) {
    return 'location_data';
  }
  
  return 'unknown';
}

/**
 * Extract metadata from content
 */
function extractMetadata(content, type) {
  const metadata = {
    type,
    created: new Date().toISOString(),
    contentLength: content.length,
    lineCount: content.split('\n').length
  };
  
  // Extract character name if it's a character sheet
  if (type === 'character_sheet') {
    const nameMatch = content.match(/(?:Name|Character):\s*\*\*([^*]+)\*\*/i) ||
                     content.match(/^#\s+([^\n]+)\s+Character Sheet/im);
    if (nameMatch) {
      metadata.characterName = nameMatch[1].trim();
    }
    
    const streetNameMatch = content.match(/Street Name:\s*\*\*([^*]+)\*\*/i);
    if (streetNameMatch) {
      metadata.streetName = streetNameMatch[1].trim();
    }
    
    const raceMatch = content.match(/Race:\s*\*\*([^*]+)\*\*/i);
    if (raceMatch) {
      metadata.race = raceMatch[1].trim();
    }
  }
  
  // Extract first heading for all types
  const headingMatch = content.match(/^#\s+(.+)$/m);
  if (headingMatch) {
    metadata.title = headingMatch[1].trim();
  }
  
  return metadata;
}

/**
 * Parse character sheet into structured data
 */
function parseCharacterSheet(content) {
  const character = {
    basicInfo: {},
    attributes: {},
    skills: [],
    spells: [],
    gear: [],
    notes: []
  };
  
  // Extract basic info
  const basicInfoSection = content.match(/## Basic Information([\s\S]*?)(?=##|$)/i);
  if (basicInfoSection) {
    const lines = basicInfoSection[1].split('\n');
    lines.forEach(line => {
      const match = line.match(/[-*]\s*\*\*([^*]+)\*\*:\s*(.+)/);
      if (match) {
        const key = match[1].toLowerCase().replace(/\s+/g, '_');
        character.basicInfo[key] = match[2].trim();
      }
    });
  }
  
  // Extract attributes
  const attributesSection = content.match(/## Attributes([\s\S]*?)(?=##|$)/i);
  if (attributesSection) {
    const lines = attributesSection[1].split('\n');
    lines.forEach(line => {
      const match = line.match(/[-*]\s*\*\*([^*]+)\*\*:\s*(\d+)/);
      if (match) {
        const attr = match[1].toLowerCase();
        character.attributes[attr] = parseInt(match[2]);
      }
    });
  }
  
  // Extract skills
  const skillsSection = content.match(/## Skills([\s\S]*?)(?=##|$)/i);
  if (skillsSection) {
    const lines = skillsSection[1].split('\n');
    lines.forEach(line => {
      const match = line.match(/[-*]\s*([^:]+):\s*(\d+)(?:\s*\(([^)]+)\s*(\d+)\))?/);
      if (match) {
        character.skills.push({
          name: match[1].trim(),
          rating: parseInt(match[2]),
          specialization: match[3] || null,
          specializationRating: match[4] ? parseInt(match[4]) : null
        });
      }
    });
  }
  
  // Extract spells
  const spellsSection = content.match(/## Spells([\s\S]*?)(?=##|$)/i);
  if (spellsSection) {
    const lines = spellsSection[1].split('\n');
    lines.forEach(line => {
      const match = line.match(/[-*]\s*([^0-9]+)\s+(\d+)\s*\(([^)]+)\)/);
      if (match) {
        character.spells.push({
          name: match[1].trim(),
          force: parseInt(match[2]),
          type: match[3].trim()
        });
      }
    });
  }
  
  return character;
}

/**
 * Parse a single content file
 */
function parseContentFile(filePath, uuid) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Detect content type based on patterns
    const contentType = detectContentType(content);
    
    // Get preview (first 500 chars)
    const preview = content.substring(0, 500) + (content.length > 500 ? '...' : '');
    
    const result = {
      uuid,
      type: contentType,
      metadata: extractMetadata(content, contentType),
      preview,
      fullContent: content
    };
    
    // Parse character sheets fully
    if (contentType === 'character_sheet') {
      result.parsed = parseCharacterSheet(content);
    }
    
    return result;
  } catch (error) {
    console.error(`❌ Error parsing ${filePath}:`, error.message);
    return {
      uuid,
      type: 'error',
      error: error.message
    };
  }
}

/**
 * Main sample parsing function
 */
async function sampleParseXAIExports() {
  console.log('🔬 xAI Export Sample Parser');
  console.log('='.repeat(60));
  console.log(`Parsing first ${SAMPLE_SIZE} items from: ${XAI_EXPORT_DIR}\n`);
  
  if (!fs.existsSync(XAI_EXPORT_DIR)) {
    console.error(`❌ Directory not found: ${XAI_EXPORT_DIR}`);
    return;
  }
  
  // Load discovery results if available
  const discoveryPath = path.join(OUTPUT_DIR, 'xai-discovery.json');
  let folders = [];
  
  if (fs.existsSync(discoveryPath)) {
    console.log('📋 Loading discovery results...');
    const discovery = JSON.parse(fs.readFileSync(discoveryPath, 'utf-8'));
    folders = discovery.folders.filter(f => f.hasContent).slice(0, SAMPLE_SIZE);
    console.log(`   Found ${discovery.summary.foldersWithContent} folders with content`);
    console.log(`   Sampling first ${folders.length}\n`);
  } else {
    console.log('⚠️  No discovery results found. Scanning directory...');
    const entries = fs.readdirSync(XAI_EXPORT_DIR);
    for (const entry of entries) {
      const fullPath = path.join(XAI_EXPORT_DIR, entry);
      const stats = fs.statSync(fullPath);
      if (stats.isDirectory()) {
        const contentPath = path.join(fullPath, 'content');
        if (fs.existsSync(contentPath)) {
          folders.push({ uuid: entry, hasContent: true });
          if (folders.length >= SAMPLE_SIZE) break;
        }
      }
    }
    console.log(`   Found ${folders.length} folders to sample\n`);
  }
  
  const results = {
    timestamp: new Date().toISOString(),
    sampleSize: folders.length,
    items: [],
    summary: {
      byType: {},
      totalCharacters: 0,
      totalErrors: 0
    }
  };
  
  console.log('🔍 Parsing samples...\n');
  
  for (let i = 0; i < folders.length; i++) {
    const folder = folders[i];
    const contentPath = path.join(XAI_EXPORT_DIR, folder.uuid, 'content');
    
    console.log(`[${i + 1}/${folders.length}] Processing ${folder.uuid.substring(0, 8)}...`);
    
    const parsed = parseContentFile(contentPath, folder.uuid);
    results.items.push(parsed);
    
    // Update summary
    const type = parsed.type;
    results.summary.byType[type] = (results.summary.byType[type] || 0) + 1;
    
    if (type === 'character_sheet') {
      results.summary.totalCharacters++;
      const charName = parsed.metadata.characterName || 'Unknown';
      console.log(`   ✅ Character: ${charName}`);
    } else if (type === 'error') {
      results.summary.totalErrors++;
      console.log(`   ❌ Error: ${parsed.error}`);
    } else {
      console.log(`   📄 Type: ${type}`);
    }
  }
  
  // Display summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 Sample Analysis Summary:');
  console.log('─'.repeat(60));
  console.log(`Total items sampled: ${results.sampleSize}`);
  console.log(`\nContent Types:`);
  Object.entries(results.summary.byType).forEach(([type, count]) => {
    const percentage = ((count / results.sampleSize) * 100).toFixed(1);
    console.log(`  ${type.padEnd(20)}: ${count.toString().padStart(3)} (${percentage}%)`);
  });
  
  if (results.summary.totalCharacters > 0) {
    console.log(`\n✨ Characters Found:`);
    results.items
      .filter(item => item.type === 'character_sheet')
      .forEach((item, i) => {
        const name = item.metadata.characterName || 'Unknown';
        const race = item.metadata.race || 'Unknown';
        console.log(`  ${i + 1}. ${name} (${race})`);
      });
  }
  
  // Save results
  const outputPath = path.join(OUTPUT_DIR, 'xai-sample-parsed.json');
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  
  // Save a human-readable summary
  const summaryPath = path.join(OUTPUT_DIR, 'xai-sample-summary.txt');
  const summaryText = `xAI Export Sample Analysis
${'='.repeat(60)}
Timestamp: ${results.timestamp}
Sample Size: ${results.sampleSize}

Content Type Distribution:
${Object.entries(results.summary.byType)
  .map(([type, count]) => `  ${type}: ${count}`)
  .join('\n')}

${results.summary.totalCharacters > 0 ? `
Characters Found (${results.summary.totalCharacters}):
${results.items
  .filter(item => item.type === 'character_sheet')
  .map((item, i) => {
    const name = item.metadata.characterName || 'Unknown';
    const race = item.metadata.race || 'Unknown';
    return `  ${i + 1}. ${name} (${race})`;
  })
  .join('\n')}
` : ''}

Files saved:
  - ${outputPath}
  - ${summaryPath}
`;
  
  fs.writeFileSync(summaryPath, summaryText);
  
  console.log('\n💾 Results saved to:');
  console.log(`   ${outputPath}`);
  console.log(`   ${summaryPath}`);
  
  console.log('\n✅ Sample parsing complete!');
  console.log('\n💡 Next steps:');
  console.log('   - Review the sample results');
  console.log('   - If parsing looks good, proceed to batch processing');
  console.log('   - Run: node tools/batch-parse-xai.js');
  
  return results;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  sampleParseXAIExports().catch(console.error);
}

export { sampleParseXAIExports };
