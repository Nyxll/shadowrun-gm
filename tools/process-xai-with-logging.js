#!/usr/bin/env node

/**
 * Batch xAI Export Processor with File Logging
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const XAI_EXPORT_DIR = 'D:/projects/xAI/prod-mc-asset-server';
const OUTPUT_DIR = path.join(__dirname, '../parsed-xai-data');
const BATCH_SIZE = 50;
const PROGRESS_FILE = path.join(OUTPUT_DIR, 'progress.json');
const LOG_FILE = path.join(OUTPUT_DIR, 'processing.log');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Clear log file
fs.writeFileSync(LOG_FILE, '');

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_FILE, logMessage);
  console.log(message);
}

function isBinaryContent(buffer) {
  const sample = buffer.slice(0, Math.min(512, buffer.length));
  let nonTextChars = 0;
  
  for (let i = 0; i < sample.length; i++) {
    const byte = sample[i];
    if (byte === 0) return true;
    if (byte < 32 && byte !== 9 && byte !== 10 && byte !== 13) {
      nonTextChars++;
    }
  }
  
  return (nonTextChars / sample.length) > 0.3;
}

function isGenericPrompt(content) {
  const lower = content.toLowerCase();
  const genericPhrases = [
    'help me rewrite',
    'can you help',
    'please help',
    'i need help',
    'how do i',
    'what is the best way',
    'summarize this',
    'translate this',
    'fix this',
    'improve this'
  ];
  
  if (content.length < 500) {
    for (const phrase of genericPhrases) {
      if (lower.startsWith(phrase) || lower.includes(phrase)) {
        return true;
      }
    }
  }
  
  return false;
}

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

function extractMetadata(content, type) {
  const metadata = { type };
  
  if (type === 'character_sheet') {
    const nameMatch = content.match(/(?:Name|Character):\s*\*\*([^*]+)\*\*/i) ||
                     content.match(/^#\s+([^\n]+)\s+Character Sheet/im);
    if (nameMatch) metadata.characterName = nameMatch[1].trim();
    
    const streetNameMatch = content.match(/Street Name:\s*\*\*([^*]+)\*\*/i);
    if (streetNameMatch) metadata.streetName = streetNameMatch[1].trim();
    
    const raceMatch = content.match(/Race:\s*\*\*([^*]+)\*\*/i);
    if (raceMatch) metadata.race = raceMatch[1].trim();
  }
  
  const headingMatch = content.match(/^#\s+(.+)$/m);
  if (headingMatch) metadata.title = headingMatch[1].trim();
  
  return metadata;
}

function parseContentFile(uuid, contentPath) {
  try {
    const buffer = fs.readFileSync(contentPath);
    
    if (isBinaryContent(buffer)) {
      return {
        uuid,
        type: 'binary_skipped',
        skip: true
      };
    }
    
    const content = buffer.toString('utf-8');
    
    if (isGenericPrompt(content)) {
      return {
        uuid,
        type: 'generic_prompt_skipped',
        skip: true
      };
    }
    
    const contentType = detectContentType(content);
    
    return {
      uuid,
      type: contentType,
      metadata: extractMetadata(content, contentType),
      contentLength: content.length,
      content
    };
  } catch (error) {
    return {
      uuid,
      type: 'error',
      error: error.message
    };
  }
}

async function processBatch() {
  log('🔄 xAI Batch Processor Starting...\n');
  
  try {
    log(`Reading directory: ${XAI_EXPORT_DIR}`);
    const entries = fs.readdirSync(XAI_EXPORT_DIR);
    log(`Found ${entries.length} total entries`);
    
    const allFolders = entries.filter(name => {
      const fullPath = path.join(XAI_EXPORT_DIR, name);
      return fs.statSync(fullPath).isDirectory();
    });
    log(`Found ${allFolders.length} folders`);
    
    const folders = allFolders.filter(uuid => {
      const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
      return fs.existsSync(contentPath);
    });
    
    log(`Found ${folders.length} folders with content files\n`);
    
    const results = {
      byType: {},
      items: [],
      errors: []
    };
    
    const totalBatches = Math.ceil(folders.length / BATCH_SIZE);
    log(`Processing in ${totalBatches} batches of ${BATCH_SIZE}\n`);
    
    for (let batchNum = 0; batchNum < totalBatches; batchNum++) {
      const start = batchNum * BATCH_SIZE;
      const end = Math.min(start + BATCH_SIZE, folders.length);
      const batch = folders.slice(start, end);
      
      log(`\nBatch ${batchNum + 1}/${totalBatches}: Processing ${batch.length} items...`);
      
      for (let i = 0; i < batch.length; i++) {
        const uuid = batch[i];
        const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
        
        const parsed = parseContentFile(uuid, contentPath);
        
        if (!parsed.skip) {
          results.items.push(parsed);
        }
        
        const type = parsed.type;
        results.byType[type] = (results.byType[type] || 0) + 1;
        
        if (type === 'error') {
          results.errors.push({ uuid, error: parsed.error });
          log(`  ERROR in ${uuid}: ${parsed.error}`);
        }
        
        // Log progress every 10 items
        if ((i + 1) % 10 === 0) {
          log(`  Progress: ${i + 1}/${batch.length}`);
        }
      }
      
      log(`✓ Batch ${batchNum + 1} complete`);
      
      // Save after each batch
      const resultsPath = path.join(OUTPUT_DIR, 'xai-parsed-all.json');
      fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
      log(`  Saved to ${resultsPath}`);
    }
    
    // Create summary
    const summary = {
      totalProcessed: results.items.length,
      totalScanned: folders.length,
      byType: results.byType,
      errors: results.errors.length,
      characters: results.items
        .filter(item => item.type === 'character_sheet')
        .map(item => ({
          name: item.metadata?.characterName,
          streetName: item.metadata?.streetName,
          race: item.metadata?.race,
          uuid: item.uuid
        }))
    };
    
    const summaryPath = path.join(OUTPUT_DIR, 'xai-summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
    
    log('\n' + '='.repeat(60));
    log('✅ Processing Complete!');
    log(`   Total scanned: ${folders.length}`);
    log(`   Total kept: ${results.items.length}`);
    log(`   Characters: ${summary.characters.length}`);
    log(`   Binary skipped: ${results.byType.binary_skipped || 0}`);
    log(`   Generic prompts skipped: ${results.byType.generic_prompt_skipped || 0}`);
    log(`   Errors: ${results.errors.length}`);
    log('\n📁 Output files:');
    log(`   ${path.join(OUTPUT_DIR, 'xai-parsed-all.json')}`);
    log(`   ${summaryPath}`);
    log(`   ${LOG_FILE}`);
    
  } catch (error) {
    log(`FATAL ERROR: ${error.message}`);
    log(error.stack);
    throw error;
  }
}

processBatch().catch(error => {
  log(`Unhandled error: ${error.message}`);
  process.exit(1);
});
