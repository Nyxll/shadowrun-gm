#!/usr/bin/env node

/**
 * xAI Export Parser
 * Parses character sheets and campaign data from xAI export folders
 * Each UUID folder contains a 'content' file with markdown-formatted data
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const XAI_EXPORT_DIR = 'D:/projects/xAI/prod-mc-asset-server';
const OUTPUT_DIR = path.join(__dirname, '../parsed-xai-data');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Parse a single content file
 */
function parseContentFile(filePath, uuid) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Detect content type based on patterns
    const contentType = detectContentType(content);
    
    return {
      uuid,
      type: contentType,
      content,
      metadata: extractMetadata(content, contentType),
      parsed: parseByType(content, contentType)
    };
  } catch (error) {
    console.error(`Error parsing ${filePath}:`, error.message);
    return null;
  }
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
    created: new Date().toISOString()
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
  
  return metadata;
}

/**
 * Parse content based on type
 */
function parseByType(content, type) {
  switch (type) {
    case 'character_sheet':
      return parseCharacterSheet(content);
    case 'campaign_data':
      return parseCampaignData(content);
    case 'session_log':
      return parseSessionLog(content);
    default:
      return { raw: content };
  }
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
 * Parse campaign data
 */
function parseCampaignData(content) {
  return {
    sections: extractSections(content),
    plotPoints: extractPlotPoints(content),
    npcs: extractNPCMentions(content)
  };
}

/**
 * Parse session log
 */
function parseSessionLog(content) {
  return {
    sections: extractSections(content),
    karmaAwards: extractKarmaAwards(content),
    events: extractEvents(content)
  };
}

/**
 * Extract markdown sections
 */
function extractSections(content) {
  const sections = [];
  const lines = content.split('\n');
  let currentSection = null;
  
  lines.forEach(line => {
    const headerMatch = line.match(/^(#{1,6})\s+(.+)/);
    if (headerMatch) {
      if (currentSection) {
        sections.push(currentSection);
      }
      currentSection = {
        level: headerMatch[1].length,
        title: headerMatch[2].trim(),
        content: []
      };
    } else if (currentSection && line.trim()) {
      currentSection.content.push(line);
    }
  });
  
  if (currentSection) {
    sections.push(currentSection);
  }
  
  return sections;
}

/**
 * Extract plot points
 */
function extractPlotPoints(content) {
  const plotPoints = [];
  const lines = content.split('\n');
  
  lines.forEach(line => {
    if (line.match(/[-*]\s*\*\*Plot/i) || line.match(/[-*]\s*\*\*Objective/i)) {
      plotPoints.push(line.replace(/[-*]\s*\*\*[^*]+\*\*:\s*/, '').trim());
    }
  });
  
  return plotPoints;
}

/**
 * Extract NPC mentions
 */
function extractNPCMentions(content) {
  const npcs = new Set();
  
  // Look for common NPC patterns
  const patterns = [
    /\*\*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\*\*\s+(?:says|asks|tells|responds)/g,
    /NPC:\s*\*\*([^*]+)\*\*/g,
    /Contact:\s*\*\*([^*]+)\*\*/g
  ];
  
  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      npcs.add(match[1].trim());
    }
  });
  
  return Array.from(npcs);
}

/**
 * Extract karma awards
 */
function extractKarmaAwards(content) {
  const awards = [];
  const lines = content.split('\n');
  
  lines.forEach(line => {
    const match = line.match(/[-*]\s*([^:]+):\s*(\d+)\s*karma/i);
    if (match) {
      awards.push({
        reason: match[1].trim(),
        amount: parseInt(match[2])
      });
    }
  });
  
  return awards;
}

/**
 * Extract events
 */
function extractEvents(content) {
  const events = [];
  const lines = content.split('\n');
  
  lines.forEach(line => {
    if (line.match(/^[-*]\s+[A-Z]/)) {
      events.push(line.replace(/^[-*]\s+/, '').trim());
    }
  });
  
  return events;
}

/**
 * Main processing function
 */
async function processXAIExports() {
  console.log('🔍 Scanning xAI export directory...\n');
  
  if (!fs.existsSync(XAI_EXPORT_DIR)) {
    console.error(`❌ Directory not found: ${XAI_EXPORT_DIR}`);
    return;
  }
  
  const uuidFolders = fs.readdirSync(XAI_EXPORT_DIR)
    .filter(name => {
      const fullPath = path.join(XAI_EXPORT_DIR, name);
      return fs.statSync(fullPath).isDirectory();
    });
  
  console.log(`Found ${uuidFolders.length} UUID folders\n`);
  
  const results = {
    characterSheets: [],
    campaignData: [],
    sessionLogs: [],
    npcData: [],
    locationData: [],
    unknown: [],
    errors: []
  };
  
  let processed = 0;
  
  for (const uuid of uuidFolders) {
    const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
    
    if (fs.existsSync(contentPath)) {
      const parsed = parseContentFile(contentPath, uuid);
      
      if (parsed) {
        processed++;
        
        // Categorize by type
        switch (parsed.type) {
          case 'character_sheet':
            results.characterSheets.push(parsed);
            console.log(`✅ Character: ${parsed.metadata.characterName || 'Unknown'} (${uuid})`);
            break;
          case 'campaign_data':
            results.campaignData.push(parsed);
            console.log(`📚 Campaign data (${uuid})`);
            break;
          case 'session_log':
            results.sessionLogs.push(parsed);
            console.log(`📝 Session log (${uuid})`);
            break;
          case 'npc_data':
            results.npcData.push(parsed);
            console.log(`👤 NPC data (${uuid})`);
            break;
          case 'location_data':
            results.locationData.push(parsed);
            console.log(`🏢 Location data (${uuid})`);
            break;
          default:
            results.unknown.push(parsed);
            console.log(`❓ Unknown type (${uuid})`);
        }
      }
    }
  }
  
  // Save results
  const outputPath = path.join(OUTPUT_DIR, 'xai-exports-parsed.json');
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  
  // Save summary
  const summary = {
    totalFolders: uuidFolders.length,
    processed,
    characterSheets: results.characterSheets.length,
    campaignData: results.campaignData.length,
    sessionLogs: results.sessionLogs.length,
    npcData: results.npcData.length,
    locationData: results.locationData.length,
    unknown: results.unknown.length,
    characters: results.characterSheets.map(c => ({
      name: c.metadata.characterName,
      streetName: c.metadata.streetName,
      race: c.metadata.race,
      uuid: c.uuid
    }))
  };
  
  const summaryPath = path.join(OUTPUT_DIR, 'xai-exports-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 Summary:');
  console.log(`   Total folders: ${summary.totalFolders}`);
  console.log(`   Processed: ${summary.processed}`);
  console.log(`   Character sheets: ${summary.characterSheets}`);
  console.log(`   Campaign data: ${summary.campaignData}`);
  console.log(`   Session logs: ${summary.sessionLogs}`);
  console.log(`   NPC data: ${summary.npcData}`);
  console.log(`   Location data: ${summary.locationData}`);
  console.log(`   Unknown: ${summary.unknown}`);
  console.log('\n📁 Output saved to:');
  console.log(`   ${outputPath}`);
  console.log(`   ${summaryPath}`);
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  processXAIExports().catch(console.error);
}

export { processXAIExports, parseContentFile };
