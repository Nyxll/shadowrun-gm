#!/usr/bin/env node

/**
 * Chunked Roleplay Log Parser
 * Processes large log files in manageable chunks with progress tracking
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const LOGS_DIR = 'G:/My Drive/SR-ai/teaching-ai/Logs';
const OUTPUT_DIR = path.join(__dirname, '../parsed-roleplay-data');
const LOG_FILE = path.join(OUTPUT_DIR, 'processing.log');
const CHUNK_SIZE = 50000; // Process 50KB chunks at a time

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

function showProgress(current, total, label = '') {
  const percentage = Math.floor((current / total) * 100);
  const barLength = 40;
  const filled = Math.floor((current / total) * barLength);
  const bar = '█'.repeat(filled) + '░'.repeat(barLength - filled);
  
  const message = `${label} [${bar}] ${percentage}% (${current}/${total})`;
  process.stdout.write(`\r${message}`);
  
  if (current === total) {
    process.stdout.write('\n');
  }
}

function detectResponseType(text) {
  const lower = text.toLowerCase();
  
  if (lower.includes('says') || lower.includes('asks') || lower.includes('tells')) {
    return 'npc_dialogue';
  }
  if (lower.includes('you see') || lower.includes('the room') || lower.includes('the street')) {
    return 'scene_description';
  }
  if (lower.includes('roll') || lower.includes('test') || lower.includes('target number')) {
    return 'mechanics';
  }
  if (lower.includes('suddenly') || lower.includes('without warning') || lower.includes('just then')) {
    return 'dramatic_moment';
  }
  
  return 'narrative';
}

function assessQuality(text) {
  let score = 0;
  
  // Positive indicators
  if (text.match(/\*[^*]+\*/)) score += 2; // Has emphasis/actions
  if (text.match(/[.!?]{2,}/)) score += 1; // Has dramatic punctuation
  if (text.match(/\b(vivid|dark|gleaming|shadow|neon|chrome)\b/i)) score += 1; // Atmospheric words
  if (text.length > 200) score += 1; // Detailed
  if (text.match(/"[^"]+"/)) score += 1; // Has dialogue
  
  // Negative indicators
  if (text.match(/\b(um|uh|hmm)\b/i)) score -= 1; // Hesitation
  if (text.match(/\b(error|mistake|sorry)\b/i)) score -= 1; // Errors
  
  if (score >= 4) return 'excellent';
  if (score >= 2) return 'good';
  if (score >= 0) return 'adequate';
  return 'poor';
}

function extractTeachingContent(chunk) {
  const content = [];
  
  // These logs are teaching sessions, not narratives
  // Look for rules explanations, examples, and structured teaching
  
  // Split by "Show thinking" or major breaks
  const sections = chunk.split(/(?:Show thinking|^[A-Z][^:]+:)/m);
  
  sections.forEach(section => {
    const trimmed = section.trim();
    if (trimmed.length < 50) return;
    
    // Look for teaching patterns
    const isTeaching = 
      trimmed.match(/(?:explain|example|rule|mechanic|how to|target number|dice pool)/i) ||
      trimmed.match(/\d+d\d+/) || // Dice notation
      trimmed.match(/Phase \d+:/) || // Structured teaching
      trimmed.match(/Step \d+:/) ||
      trimmed.length > 200; // Detailed content
    
    if (isTeaching) {
      content.push({
        text: trimmed,
        type: detectContentType(trimmed),
        wordCount: trimmed.split(/\s+/).length,
        hasExample: trimmed.includes('Example') || trimmed.includes('example'),
        hasDiceNotation: /\d+d\d+/.test(trimmed),
        hasRuleReference: /(?:SR2|Second Edition|p\.\s*\d+|page \d+)/i.test(trimmed)
      });
    }
  });
  
  return content;
}

function detectContentType(text) {
  const lower = text.toLowerCase();
  
  if (lower.includes('character sheet') || lower.includes('attributes') || lower.includes('skills')) {
    return 'character_mechanics';
  }
  if (lower.includes('dice') || lower.includes('roll') || lower.includes('target number')) {
    return 'dice_mechanics';
  }
  if (lower.includes('combat') || lower.includes('initiative') || lower.includes('damage')) {
    return 'combat_rules';
  }
  if (lower.includes('magic') || lower.includes('spell') || lower.includes('drain')) {
    return 'magic_rules';
  }
  if (lower.includes('matrix') || lower.includes('decker') || lower.includes('cyberdeck')) {
    return 'matrix_rules';
  }
  if (lower.includes('phase') || lower.includes('step') || lower.includes('teach')) {
    return 'teaching_structure';
  }
  
  return 'general_rules';
}

function processLogFileInChunks(filePath) {
  try {
    const filename = path.basename(filePath);
    const stats = fs.statSync(filePath);
    const fileSize = stats.size;
    
    log(`\n📖 Processing: ${filename}`);
    log(`   File size: ${(fileSize / 1024).toFixed(2)} KB`);
    
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Calculate number of chunks
    const numChunks = Math.ceil(content.length / CHUNK_SIZE);
    log(`   Processing in ${numChunks} chunks of ~${(CHUNK_SIZE / 1024).toFixed(0)}KB`);
    
    const allNarratives = [];
    let processedChars = 0;
    
    // Process in chunks
    for (let i = 0; i < numChunks; i++) {
      const start = i * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, content.length);
      
      // Extend to next paragraph boundary to avoid cutting mid-paragraph
      let chunkEnd = end;
      if (chunkEnd < content.length) {
        const nextBreak = content.indexOf('\n\n', end);
        if (nextBreak !== -1 && nextBreak - end < 1000) {
          chunkEnd = nextBreak;
        }
      }
      
      const chunk = content.substring(start, chunkEnd);
      const teachings = extractTeachingContent(chunk);
      allNarratives.push(...teachings);
      
      processedChars = chunkEnd;
      showProgress(i + 1, numChunks, '   Progress');
    }
    
    const withExamples = allNarratives.filter(n => n.hasExample);
    const withDice = allNarratives.filter(n => n.hasDiceNotation);
    const withRefs = allNarratives.filter(n => n.hasRuleReference);
    
    log(`   ✓ Found ${allNarratives.length} teaching segments`);
    log(`     With examples: ${withExamples.length}`);
    log(`     With dice notation: ${withDice.length}`);
    log(`     With rule references: ${withRefs.length}`);
    
    return {
      filename,
      path: filePath,
      fileSize,
      teachingContent: allNarratives,
      stats: {
        totalSegments: allNarratives.length,
        withExamples: allNarratives.filter(n => n.hasExample).length,
        withDice: allNarratives.filter(n => n.hasDiceNotation).length,
        withRefs: allNarratives.filter(n => n.hasRuleReference).length,
        byType: {
          npc_dialogue: allNarratives.filter(n => n.type === 'npc_dialogue').length,
          scene_description: allNarratives.filter(n => n.type === 'scene_description').length,
          dramatic_moment: allNarratives.filter(n => n.type === 'dramatic_moment').length,
          mechanics: allNarratives.filter(n => n.type === 'mechanics').length,
          narrative: allNarratives.filter(n => n.type === 'narrative').length
        }
      }
    };
  } catch (error) {
    log(`   ERROR: ${error.message}`);
    return null;
  }
}

async function processRoleplayLogs() {
  log('🎭 Chunked Roleplay Log Parser Starting...\n');
  
  try {
    log(`Checking directory: ${LOGS_DIR}`);
    
    if (!fs.existsSync(LOGS_DIR)) {
      log(`ERROR: Directory not found: ${LOGS_DIR}`);
      return;
    }
    
    const allFiles = fs.readdirSync(LOGS_DIR);
    log(`Found ${allFiles.length} total files`);
    
    const logFiles = allFiles
      .filter(name => name.endsWith('.log'))
      .map(name => path.join(LOGS_DIR, name));
    
    log(`Found ${logFiles.length} .log files to process\n`);
    
    const results = {
      logs: [],
      summary: {
        totalLogs: logFiles.length,
        totalSegments: 0,
        withExamples: 0,
        withDice: 0,
        withRefs: 0,
        totalFileSize: 0
      }
    };
    
    // Process each log file
    for (let i = 0; i < logFiles.length; i++) {
      const logPath = logFiles[i];
      
      log(`\n[${ i + 1}/${logFiles.length}] Processing log file...`);
      
      const parsed = processLogFileInChunks(logPath);
      if (parsed) {
        results.logs.push(parsed);
        
        results.summary.totalSegments += parsed.stats.totalSegments;
        results.summary.withExamples += parsed.stats.withExamples;
        results.summary.withDice += parsed.stats.withDice;
        results.summary.withRefs += parsed.stats.withRefs;
        results.summary.totalFileSize += parsed.fileSize;
      }
    }
    
    // Save full results
    const outputPath = path.join(OUTPUT_DIR, 'roleplay-logs-parsed.json');
    fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
    log(`\n✓ Saved full results to: ${outputPath}`);
    
    // Create training examples (teaching content with examples/references)
    const trainingExamples = {
      allTeachings: [],
      characterMechanics: [],
      diceMechanics: [],
      combatRules: [],
      magicRules: [],
      matrixRules: []
    };
    
    results.logs.forEach(logData => {
      logData.teachingContent
        .filter(t => t.hasExample || t.hasDiceNotation || t.hasRuleReference)
        .forEach(teaching => {
          const example = {
            text: teaching.text,
            type: teaching.type,
            source: logData.filename,
            wordCount: teaching.wordCount,
            hasExample: teaching.hasExample,
            hasDiceNotation: teaching.hasDiceNotation,
            hasRuleReference: teaching.hasRuleReference
          };
          
          trainingExamples.allTeachings.push(example);
          
          if (teaching.type === 'character_mechanics') {
            trainingExamples.characterMechanics.push(example);
          } else if (teaching.type === 'dice_mechanics') {
            trainingExamples.diceMechanics.push(example);
          } else if (teaching.type === 'combat_rules') {
            trainingExamples.combatRules.push(example);
          } else if (teaching.type === 'magic_rules') {
            trainingExamples.magicRules.push(example);
          } else if (teaching.type === 'matrix_rules') {
            trainingExamples.matrixRules.push(example);
          }
        });
    });
    
    const trainingPath = path.join(OUTPUT_DIR, 'training-examples.json');
    fs.writeFileSync(trainingPath, JSON.stringify(trainingExamples, null, 2));
    log(`✓ Saved training examples to: ${trainingPath}`);
    
    // Create summary
    const summaryPath = path.join(OUTPUT_DIR, 'summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(results.summary, null, 2));
    log(`✓ Saved summary to: ${summaryPath}`);
    
    log('\n' + '='.repeat(60));
    log('✅ Processing Complete!');
    log(`   Total logs: ${results.summary.totalLogs}`);
    log(`   Total file size: ${(results.summary.totalFileSize / 1024).toFixed(2)} KB`);
    log(`   Total teaching segments: ${results.summary.totalSegments}`);
    log(`   With examples: ${results.summary.withExamples}`);
    log(`   With dice notation: ${results.summary.withDice}`);
    log(`   With rule references: ${results.summary.withRefs}`);
    log('\n📁 Training Examples (Quality Content):');
    log(`   Total: ${trainingExamples.allTeachings.length}`);
    log(`   Character Mechanics: ${trainingExamples.characterMechanics.length}`);
    log(`   Dice Mechanics: ${trainingExamples.diceMechanics.length}`);
    log(`   Combat Rules: ${trainingExamples.combatRules.length}`);
    log(`   Magic Rules: ${trainingExamples.magicRules.length}`);
    log(`   Matrix Rules: ${trainingExamples.matrixRules.length}`);
    log('\n📁 Output files:');
    log(`   ${outputPath}`);
    log(`   ${trainingPath}`);
    log(`   ${summaryPath}`);
    log(`   ${LOG_FILE}`);
    
  } catch (error) {
    log(`FATAL ERROR: ${error.message}`);
    log(error.stack);
    throw error;
  }
}

processRoleplayLogs().catch(error => {
  log(`Unhandled error: ${error.message}`);
  process.exit(1);
});
