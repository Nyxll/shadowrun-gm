#!/usr/bin/env node

/**
 * Roleplay Log Parser
 * Extracts excellent GM responses, player interactions, and learning patterns
 * from historical gameplay logs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const LOGS_DIR = 'G:/My Drive/SR-ai/teaching-ai/Logs';
const OUTPUT_DIR = path.join(__dirname, '../parsed-roleplay-data');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Parse a log file and extract roleplay examples
 */
function parseLogFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const filename = path.basename(filePath);
    
    return {
      filename,
      path: filePath,
      conversations: extractConversations(content),
      gmResponses: extractGMResponses(content),
      playerActions: extractPlayerActions(content),
      diceRolls: extractDiceRolls(content),
      rulesDiscussions: extractRulesDiscussions(content),
      narrativeExcellence: extractNarrativeExcellence(content),
      frustrationPoints: extractFrustrationPoints(content),
      successPoints: extractSuccessPoints(content)
    };
  } catch (error) {
    console.error(`Error parsing ${filePath}:`, error.message);
    return null;
  }
}

/**
 * Extract conversation turns (user/assistant pairs)
 */
function extractConversations(content) {
  const conversations = [];
  
  // Split by common conversation markers
  const turns = content.split(/\n\n+/);
  let currentConversation = null;
  
  turns.forEach(turn => {
    const trimmed = turn.trim();
    if (!trimmed) return;
    
    // Detect if this is a user message or assistant response
    const isUserMessage = 
      trimmed.match(/^(User|Player|You):/i) ||
      trimmed.match(/^[A-Z][a-z]+\s+(says|asks|does):/i) ||
      !trimmed.match(/^(GM|Gamemaster|Assistant|Show thinking):/i);
    
    if (isUserMessage) {
      if (currentConversation) {
        conversations.push(currentConversation);
      }
      currentConversation = {
        user: trimmed,
        assistant: null,
        context: []
      };
    } else if (currentConversation) {
      currentConversation.assistant = trimmed;
    }
  });
  
  if (currentConversation && currentConversation.assistant) {
    conversations.push(currentConversation);
  }
  
  return conversations;
}

/**
 * Extract GM responses that demonstrate good roleplay
 */
function extractGMResponses(content) {
  const responses = [];
  
  // Look for narrative descriptions, NPC dialogue, scene setting
  const patterns = [
    // Scene descriptions
    /(?:GM|Gamemaster):\s*([^]*?)(?=\n\n|User:|Player:|$)/gi,
    // NPC dialogue with emotion/action
    /\*\*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\*\*\s+([^.!?]+[.!?])\s*\*([^*]+)\*/g,
    // Atmospheric descriptions
    /The\s+(?:air|room|street|night|shadows?|atmosphere)[^.!?]+[.!?]/gi
  ];
  
  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const text = match[1] || match[0];
      if (text.length > 50 && text.length < 1000) {
        responses.push({
          text: text.trim(),
          type: detectResponseType(text),
          quality: assessQuality(text)
        });
      }
    }
  });
  
  return responses;
}

/**
 * Detect type of GM response
 */
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

/**
 * Assess quality of response (simple heuristic)
 */
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

/**
 * Extract player actions
 */
function extractPlayerActions(content) {
  const actions = [];
  const lines = content.split('\n');
  
  lines.forEach(line => {
    // Look for "I do X" or "Character does X" patterns
    const actionMatch = line.match(/(?:I|[A-Z][a-z]+)\s+(attempt|try|want|cast|shoot|hack|sneak|investigate|search|ask|tell)/i);
    if (actionMatch) {
      actions.push({
        text: line.trim(),
        actionType: actionMatch[1].toLowerCase()
      });
    }
  });
  
  return actions;
}

/**
 * Extract dice roll discussions
 */
function extractDiceRolls(content) {
  const rolls = [];
  
  // Look for dice roll patterns
  const patterns = [
    /roll\s+(\d+d\d+(?:[+\-]\d+)?)/gi,
    /target\s+number\s+(\d+)/gi,
    /(\d+)\s+successes?/gi,
    /initiative\s+(\d+)/gi
  ];
  
  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      rolls.push({
        context: getContext(content, match.index, 100),
        roll: match[0],
        value: match[1]
      });
    }
  });
  
  return rolls;
}

/**
 * Extract rules discussions
 */
function extractRulesDiscussions(content) {
  const discussions = [];
  
  // Look for rules explanations
  const ruleKeywords = [
    'rule', 'mechanic', 'target number', 'modifier', 'dice pool',
    'combat pool', 'karma pool', 'initiative', 'damage code',
    'staging', 'essence', 'drain'
  ];
  
  const lines = content.split('\n');
  let currentDiscussion = [];
  
  lines.forEach(line => {
    const hasRuleKeyword = ruleKeywords.some(keyword => 
      line.toLowerCase().includes(keyword)
    );
    
    if (hasRuleKeyword) {
      currentDiscussion.push(line);
    } else if (currentDiscussion.length > 0) {
      if (currentDiscussion.length >= 2) {
        discussions.push({
          text: currentDiscussion.join('\n'),
          keywords: extractKeywords(currentDiscussion.join(' '), ruleKeywords)
        });
      }
      currentDiscussion = [];
    }
  });
  
  return discussions;
}

/**
 * Extract narrative excellence examples
 */
function extractNarrativeExcellence(content) {
  const examples = [];
  
  // Look for particularly good narrative passages
  const sections = content.split(/\n\n+/);
  
  sections.forEach(section => {
    if (section.length < 100 || section.length > 2000) return;
    
    const quality = assessQuality(section);
    if (quality === 'excellent' || quality === 'good') {
      examples.push({
        text: section.trim(),
        quality,
        type: detectResponseType(section),
        wordCount: section.split(/\s+/).length
      });
    }
  });
  
  return examples;
}

/**
 * Extract frustration points (where user had issues)
 */
function extractFrustrationPoints(content) {
  const frustrations = [];
  
  const frustrationIndicators = [
    /no,?\s+(?:that's|thats)\s+(?:not|wrong)/gi,
    /(?:confused|confusing|unclear|doesn't make sense)/gi,
    /(?:forgot|remember|already told you)/gi,
    /(?:wrong|incorrect|mistake)/gi,
    /why\s+(?:did|would)\s+you/gi
  ];
  
  frustrationIndicators.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      frustrations.push({
        text: getContext(content, match.index, 200),
        indicator: match[0],
        category: categorizeFrustration(match[0])
      });
    }
  });
  
  return frustrations;
}

/**
 * Extract success points (where things went well)
 */
function extractSuccessPoints(content) {
  const successes = [];
  
  const successIndicators = [
    /(?:perfect|excellent|great|awesome|love it)/gi,
    /(?:exactly|precisely|that's right)/gi,
    /(?:good|nice|well done)/gi,
    /(?:yes!|yeah!|brilliant)/gi
  ];
  
  successIndicators.forEach(pattern => {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      successes.push({
        text: getContext(content, match.index, 200),
        indicator: match[0]
      });
    }
  });
  
  return successes;
}

/**
 * Get context around a position in text
 */
function getContext(text, position, radius) {
  const start = Math.max(0, position - radius);
  const end = Math.min(text.length, position + radius);
  return text.substring(start, end).trim();
}

/**
 * Extract keywords from text
 */
function extractKeywords(text, keywords) {
  return keywords.filter(keyword => 
    text.toLowerCase().includes(keyword.toLowerCase())
  );
}

/**
 * Categorize frustration
 */
function categorizeFrustration(indicator) {
  const lower = indicator.toLowerCase();
  
  if (lower.includes('forgot') || lower.includes('remember')) {
    return 'memory_issue';
  }
  if (lower.includes('wrong') || lower.includes('incorrect')) {
    return 'rules_error';
  }
  if (lower.includes('confused') || lower.includes('unclear')) {
    return 'clarity_issue';
  }
  
  return 'general';
}

/**
 * Main processing function
 */
async function processRoleplayLogs() {
  console.log('🎭 Scanning roleplay logs directory...\n');
  
  if (!fs.existsSync(LOGS_DIR)) {
    console.error(`❌ Directory not found: ${LOGS_DIR}`);
    return;
  }
  
  const logFiles = fs.readdirSync(LOGS_DIR)
    .filter(name => name.endsWith('.log'))
    .map(name => path.join(LOGS_DIR, name));
  
  console.log(`Found ${logFiles.length} log files\n`);
  
  const results = {
    logs: [],
    summary: {
      totalLogs: logFiles.length,
      totalConversations: 0,
      totalGMResponses: 0,
      excellentNarratives: 0,
      frustrationPoints: 0,
      successPoints: 0,
      diceRolls: 0,
      rulesDiscussions: 0
    }
  };
  
  for (const logPath of logFiles) {
    console.log(`📖 Processing: ${path.basename(logPath)}`);
    
    const parsed = parseLogFile(logPath);
    if (parsed) {
      results.logs.push(parsed);
      
      // Update summary
      results.summary.totalConversations += parsed.conversations.length;
      results.summary.totalGMResponses += parsed.gmResponses.length;
      results.summary.excellentNarratives += parsed.narrativeExcellence.filter(n => n.quality === 'excellent').length;
      results.summary.frustrationPoints += parsed.frustrationPoints.length;
      results.summary.successPoints += parsed.successPoints.length;
      results.summary.diceRolls += parsed.diceRolls.length;
      results.summary.rulesDiscussions += parsed.rulesDiscussions.length;
      
      console.log(`   Conversations: ${parsed.conversations.length}`);
      console.log(`   GM Responses: ${parsed.gmResponses.length}`);
      console.log(`   Excellent Narratives: ${parsed.narrativeExcellence.filter(n => n.quality === 'excellent').length}`);
      console.log(`   Frustrations: ${parsed.frustrationPoints.length}`);
      console.log(`   Successes: ${parsed.successPoints.length}\n`);
    }
  }
  
  // Save results
  const outputPath = path.join(OUTPUT_DIR, 'roleplay-logs-parsed.json');
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  
  // Save training examples (excellent narratives only)
  const trainingExamples = {
    narratives: [],
    npcDialogue: [],
    sceneDescriptions: []
  };
  
  results.logs.forEach(log => {
    log.narrativeExcellence
      .filter(n => n.quality === 'excellent')
      .forEach(narrative => {
        trainingExamples.narratives.push({
          text: narrative.text,
          type: narrative.type,
          source: log.filename
        });
        
        if (narrative.type === 'npc_dialogue') {
          trainingExamples.npcDialogue.push(narrative);
        } else if (narrative.type === 'scene_description') {
          trainingExamples.sceneDescriptions.push(narrative);
        }
      });
  });
  
  const trainingPath = path.join(OUTPUT_DIR, 'training-examples.json');
  fs.writeFileSync(trainingPath, JSON.stringify(trainingExamples, null, 2));
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 Summary:');
  console.log(`   Total logs: ${results.summary.totalLogs}`);
  console.log(`   Total conversations: ${results.summary.totalConversations}`);
  console.log(`   GM responses: ${results.summary.totalGMResponses}`);
  console.log(`   Excellent narratives: ${results.summary.excellentNarratives}`);
  console.log(`   Frustration points: ${results.summary.frustrationPoints}`);
  console.log(`   Success points: ${results.summary.successPoints}`);
  console.log(`   Dice rolls: ${results.summary.diceRolls}`);
  console.log(`   Rules discussions: ${results.summary.rulesDiscussions}`);
  console.log('\n📁 Output saved to:');
  console.log(`   ${outputPath}`);
  console.log(`   ${trainingPath}`);
  
  return results;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  processRoleplayLogs().catch(console.error);
}

export { processRoleplayLogs, parseLogFile };
