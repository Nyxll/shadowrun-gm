#!/usr/bin/env node

/**
 * Batch xAI Export Processor
 * Processes xAI exports in configurable batches with progress tracking
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const XAI_EXPORT_DIR = 'D:/projects/xAI/prod-mc-asset-server';
const OUTPUT_DIR = path.join(__dirname, '../parsed-xai-data');
const BATCH_SIZE = 50; // Process 50 at a time
const PROGRESS_FILE = path.join(OUTPUT_DIR, 'progress.json');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Simple progress bar
 */
function showProgress(current, total, label = '') {
  const percentage = Math.floor((current / total) * 100);
  const barLength = 40;
  const filled = Math.floor((current / total) * barLength);
  const bar = '█'.repeat(filled) + '░'.repeat(barLength - filled);
  
  process.stdout.write(`\r${label} [${bar}] ${percentage}% (${current}/${total})`);
  
  if (current === total) {
    process.stdout.write('\n');
  }
}

/**
 * Detect content type
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
 * Extract metadata
 */
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

/**
 * Check if content is binary
 */
function isBinaryContent(buffer) {
  // Check first 512 bytes for null bytes or high percentage of non-text chars
  const sample = buffer.slice(0, Math.min(512, buffer.length));
  let nonTextChars = 0;
  
  for (let i = 0; i < sample.length; i++) {
    const byte = sample[i];
    // Null byte = definitely binary
    if (byte === 0) return true;
    // Count non-printable, non-whitespace chars
    if (byte < 32 && byte !== 9 && byte !== 10 && byte !== 13) {
      nonTextChars++;
    }
  }
  
  // If >30% non-text chars, probably binary
  return (nonTextChars / sample.length) > 0.3;
}

/**
 * Check if content is a generic prompt (not valuable)
 */
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
  
  // If content is short and starts with generic phrase, skip it
  if (content.length < 500) {
    for (const phrase of genericPhrases) {
      if (lower.startsWith(phrase) || lower.includes(phrase)) {
        return true;
      }
    }
  }
  
  return false;
}

/**
 * Parse a single content file
 */
function parseContentFile(uuid, contentPath) {
  try {
    // Read as buffer first to check if binary
    const buffer = fs.readFileSync(contentPath);
    
    // Skip binary files
    if (isBinaryContent(buffer)) {
      return {
        uuid,
        type: 'binary_skipped',
        skip: true
      };
    }
    
    // Convert to string
    const content = buffer.toString('utf-8');
    
    // Skip generic prompts
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
      content // Keep full content for now
    };
  } catch (error) {
    return {
      uuid,
      type: 'error',
      error: error.message
    };
  }
}

/**
 * Load or create progress tracking
 */
function loadProgress() {
  if (fs.existsSync(PROGRESS_FILE)) {
    return JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf-8'));
  }
  return {
    processedUUIDs: [],
    lastBatch: 0,
    completed: false
  };
}

/**
 * Save progress
 */
function saveProgress(progress) {
  fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

/**
 * Main batch processing function
 */
async function processBatch(startBatch = 0) {
  console.log('🔄 xAI Batch Processor\n');
  
  // Get all UUID folders
  const entries = fs.readdirSync(XAI_EXPORT_DIR);
  const allFolders = entries.filter(name => {
    const fullPath = path.join(XAI_EXPORT_DIR, name);
    return fs.statSync(fullPath).isDirectory();
  });
  
  // Filter to only folders with content
  const folders = allFolders.filter(uuid => {
    const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
    return fs.existsSync(contentPath);
  });
  
  console.log(`Found ${folders.length} folders with content\n`);
  
  // Load progress
  const progress = loadProgress();
  const processedSet = new Set(progress.processedUUIDs);
  
  // Filter out already processed
  const remaining = folders.filter(uuid => !processedSet.has(uuid));
  
  if (remaining.length === 0) {
    console.log('✅ All folders already processed!');
    return;
  }
  
  console.log(`Processing ${remaining.length} remaining folders in batches of ${BATCH_SIZE}\n`);
  
  const results = {
    byType: {},
    items: [],
    errors: []
  };
  
  // Load existing results if any
  const resultsPath = path.join(OUTPUT_DIR, 'xai-parsed-all.json');
  if (fs.existsSync(resultsPath)) {
    const existing = JSON.parse(fs.readFileSync(resultsPath, 'utf-8'));
    results.items = existing.items || [];
    results.byType = existing.byType || {};
  }
  
  // Process in batches
  const totalBatches = Math.ceil(remaining.length / BATCH_SIZE);
  
  for (let batchNum = startBatch; batchNum < totalBatches; batchNum++) {
    const start = batchNum * BATCH_SIZE;
    const end = Math.min(start + BATCH_SIZE, remaining.length);
    const batch = remaining.slice(start, end);
    
    console.log(`\nBatch ${batchNum + 1}/${totalBatches}:`);
    
    for (let i = 0; i < batch.length; i++) {
      const uuid = batch[i];
      const contentPath = path.join(XAI_EXPORT_DIR, uuid, 'content');
      
      showProgress(i + 1, batch.length, 'Processing');
      
      const parsed = parseContentFile(uuid, contentPath);
      
      // Skip binary and generic prompts
      if (!parsed.skip) {
        results.items.push(parsed);
      }
      
      // Update type counts
      const type = parsed.type;
      results.byType[type] = (results.byType[type] || 0) + 1;
      
      if (type === 'error') {
        results.errors.push({ uuid, error: parsed.error });
      }
      
      // Track progress
      progress.processedUUIDs.push(uuid);
    }
    
    // Save after each batch
    progress.lastBatch = batchNum;
    saveProgress(progress);
    
    fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
    
    console.log(`✓ Batch ${batchNum + 1} saved`);
  }
  
  // Mark as completed
  progress.completed = true;
  saveProgress(progress);
  
  // Create summary
  const summary = {
    totalProcessed: results.items.length,
    byType: results.byType,
    errors: results.errors.length,
    characters: results.items
      .filter(item => item.type === 'character_sheet')
      .map(item => ({
        name: item.metadata.characterName,
        streetName: item.metadata.streetName,
        race: item.metadata.race,
        uuid: item.uuid
      }))
  };
  
  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'xai-summary.json'),
    JSON.stringify(summary, null, 2)
  );
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Processing Complete!');
  console.log(`   Total items: ${results.items.length}`);
  console.log(`   Characters: ${summary.characters.length}`);
  console.log(`   Errors: ${results.errors.length}`);
  console.log('\n📁 Output files:');
  console.log(`   ${resultsPath}`);
  console.log(`   ${path.join(OUTPUT_DIR, 'xai-summary.json')}`);
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const startBatch = parseInt(process.argv[2]) || 0;
  processBatch(startBatch).catch(console.error);
}

export { processBatch };
