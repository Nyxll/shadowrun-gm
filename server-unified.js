#!/usr/bin/env node

/**
 * Shadowrun GM MCP Server - Unified System
 * Provides comprehensive Shadowrun 2nd Edition support:
 * - AI-powered query system for rules, gear, and lore
 * - Complete dice rolling system via shadowrun2.com API
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import pg from 'pg';
import dotenv from 'dotenv';
import OpenAI from 'openai';
import axios from 'axios';
import { createCharacter, getCharacter, updateCharacter } from './character-functions.js';
import { IntentClassifier } from './lib/intent/intent-classifier.js';
import { ClarificationEngine } from './lib/intent/clarification-engine.js';
import { LearningEngine } from './lib/intent/learning-engine.js';

dotenv.config();

const API_BASE_URL = 'https://shadowrun2.com/dice/api.php';

// Helper function to call the dice API
async function callDiceAPI(action, params = {}) {
  try {
    const response = await axios.get(API_BASE_URL, {
      params: {
        action,
        ...params,
      },
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'API request failed');
    }
  } catch (error) {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw error;
  }
}

// Helper function to call the dice API with POST (for complex data)
async function callDiceAPIPOST(action, data = {}) {
  try {
    const response = await axios.post(API_BASE_URL, {
      action,
      ...data,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'API request failed');
    }
  } catch (error) {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw error;
  }
}

const { Pool } = pg;

// Database connection pool
const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// OpenAI client for query classification and gear parsing
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Initialize clarification and learning engines
const clarificationEngine = new ClarificationEngine(pool);
const learningEngine = new LearningEngine(pool);

// Initialize intent classifier with LLM fallback and clarification/learning support
const intentClassifier = new IntentClassifier(classifyQueryEnhanced, {
  clarificationEngine,
  learningEngine
});

// Create MCP server
const server = new Server(
  {
    name: 'shadowrun-gm-unified',
    version: '2.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Enhanced query classification with multi-source routing
 */
async function classifyQueryEnhanced(query) {
  const prompt = `You are a Shadowrun 2nd Edition expert. Analyze this query and determine the best data sources.

User Query: "${query}"

Classify the query intent and determine which data sources to use:

QUERY INTENTS:
- lookup: Get specific item stats (e.g., "What's the Fireball spell?", "Show me Ares Predator stats", "Tell me about Bear totem")
- list: Show all items of a type (e.g., "List combat spells", "Show all heavy pistols", "What adept powers are there?")
- compare: Rank/compare items (e.g., "Best heavy pistol?", "Compare shotguns by damage", "Rank manipulation spells by drain")
- rules: Explain mechanics (e.g., "How does initiative work?", "Explain spell drain", "How does astral combat work?")
- hybrid: Need both stats AND explanation (e.g., "Tell me about Fireball and how to use it", "Explain the Ares Predator")

DATA SOURCES:
- structured: Use database tables (spells, powers, totems, gear) for stats, lists, comparisons
- chunks: Use text chunks (rules_content) for explanations, mechanics, lore
- both: Use both sources for comprehensive answers

STRUCTURED TABLES & WHEN TO USE THEM:
- spells: Use for ANY query about specific spells, spell lists, or spell comparisons
  * Examples: "Fireball spell", "list manipulation spells", "combat spells", "what spells can I cast?"
  * Fields: name, category (Combat/Detection/Health/Illusion/Manipulation), spell_type, drain_code
  
- powers: Use for ANY query about adept powers, critter powers, or power lists
  * Examples: "adept powers", "what powers are there?", "improved reflexes", "critter abilities"
  * Fields: name, power_type (adept/critter), power_point_cost
  
- totems: Use for ANY query about totems, shamanic traditions, or totem spirits
  * Examples: "Bear totem", "what totems exist?", "shamanic totems", "totem advantages"
  * Fields: name, advantages, disadvantages
  
- gear: Use for weapons, armor, cyberware, vehicles, equipment
  * Examples: "Ares Predator", "heavy pistols", "best sniper rifle", "armor jacket"
  * Fields: name, category, subcategory, base_stats (damage/ammo/mode/essence/etc)

IMPORTANT CLASSIFICATION RULES:
1. If query mentions "spell", "magic", "mana", "drain" → likely spells table
2. If query mentions "power", "adept", "critter ability" → likely powers table
3. If query mentions "totem", "shaman", "spirit guide" → likely totems table
4. If query mentions weapon names, armor, cyberware, vehicles → likely gear table
5. If query asks "how does X work?" or "explain X" → use chunks for rules
6. If query asks for stats or lists → use structured tables
7. Spell categories: Combat, Detection, Health, Illusion, Manipulation
8. For "list all X" queries → intent is "list", use structured tables

EXAMPLES:
Query: "list all manipulation spells"
→ intent: "list", data_sources: ["structured"], tables: ["spells"], category_filter: "Manipulation"

Query: "what's the Fireball spell?"
→ intent: "lookup", data_sources: ["structured"], tables: ["spells"], item_name: "Fireball"

Query: "show me adept powers"
→ intent: "list", data_sources: ["structured"], tables: ["powers"]

Query: "tell me about Bear totem"
→ intent: "lookup", data_sources: ["structured"], tables: ["totems"], item_name: "Bear"

Query: "how does spell drain work?"
→ intent: "rules", data_sources: ["chunks"], chunk_categories: ["magic"]

Query: "best heavy pistol"
→ intent: "compare", data_sources: ["structured"], tables: ["gear"], category_filter: "weapon", sort_by: "damage"

Return ONLY valid JSON:
{
  "intent": "lookup|list|compare|rules|hybrid",
  "data_sources": ["structured", "chunks"] or ["structured"] or ["chunks"],
  "tables": ["spells", "powers", "totems", "gear"],
  "item_name": "specific item name if lookup",
  "item_type": "spell|power|totem|weapon|armor|cyberware",
  "category_filter": "Combat|Detection|etc for spells, weapon category for gear",
  "sort_by": "damage|cost|drain|etc for comparisons",
  "search_terms": ["keyword1", "keyword2"],
  "chunk_categories": ["magic", "combat", "etc"],
  "needs_explanation": true|false
}`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a query router. Return only valid JSON.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.2,
      max_tokens: 400,
    });

    const result = JSON.parse(response.choices[0].message.content.trim());
    console.error('Enhanced classification:', JSON.stringify(result, null, 2));
    return result;
  } catch (error) {
    console.error('Classification error:', error);
    // Fallback
    return {
      intent: 'rules',
      data_sources: ['chunks'],
      tables: [],
      search_terms: [query],
      chunk_categories: ['general'],
      needs_explanation: true,
    };
  }
}

/**
 * Extract gear stats from content using AI
 */
async function extractGearStats(content, gearType) {
  const prompt = `Extract gear statistics from this Shadowrun 2nd Edition text.

Text: ${content.substring(0, 1000)}

Extract these stats (use null if not found):
- name: weapon/item name
- damage: damage code (e.g., "9M", "12S", "6L")
- ammo: ammunition capacity (number)
- mode: fire mode (e.g., "SA", "SA/BF", "SA/BF/FA")
- reach: reach value for melee (number)
- conceal: concealability rating (number, lower is better)
- cost: price in nuyen (number)

Return ONLY valid JSON:
{
  "name": "string",
  "damage": "string",
  "ammo": number,
  "mode": "string",
  "reach": number,
  "conceal": number,
  "cost": number
}`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a Shadowrun gear stats extractor. Return only valid JSON.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.1,
      max_tokens: 200,
    });

    return JSON.parse(response.choices[0].message.content.trim());
  } catch (error) {
    console.error('Stats extraction error:', error);
    return null;
  }
}

/**
 * Rank gear items by specified criteria
 */
function rankGear(items, criteria) {
  const scoreFunctions = {
    damage: (stats) => {
      if (!stats.damage) return 0;
      const match = stats.damage.match(/(\d+)([MLSD])/);
      if (!match) return 0;
      const power = parseInt(match[1]);
      const type = { 'D': 4, 'M': 3, 'S': 2, 'L': 1 }[match[2]] || 0;
      return power * 10 + type;
    },
    reach: (stats) => stats.reach || 0,
    conceal: (stats) => stats.conceal ? (10 - stats.conceal) : 0, // Lower is better, so invert
    ammo: (stats) => stats.ammo || 0,
    mode: (stats) => {
      const modes = { 'SA/BF/FA': 3, 'SA/BF': 2, 'SA': 1 };
      return modes[stats.mode] || 0;
    },
    cost: (stats) => stats.cost ? (100000 - stats.cost) : 0, // Lower is better, so invert
  };

  const scoreFunc = scoreFunctions[criteria] || scoreFunctions.damage;

  return items
    .map(item => ({
      ...item,
      score: scoreFunc(item.stats),
    }))
    .sort((a, b) => b.score - a.score);
}

/**
 * Query spells table
 */
async function querySpells(classification, limit = 10) {
  const { item_name, category_filter, sort_by } = classification;
  
  let sql = 'SELECT * FROM spells WHERE 1=1';
  const params = [];
  let paramCount = 0;
  
  // Specific spell lookup
  if (item_name) {
    paramCount++;
    sql += ` AND LOWER(name) = LOWER($${paramCount})`;
    params.push(item_name);
  }
  
  // Category filter (Combat, Detection, Health, Illusion, Manipulation)
  if (category_filter) {
    paramCount++;
    sql += ` AND category = $${paramCount}`;
    params.push(category_filter);
  }
  
  // Sorting
  const sortField = sort_by === 'drain' ? 'drain_code' : 'name';
  sql += ` ORDER BY ${sortField}`;
  
  paramCount++;
  sql += ` LIMIT $${paramCount}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  return result.rows;
}

/**
 * Query powers table
 */
async function queryPowers(classification, limit = 10) {
  const { item_name, category_filter } = classification;
  
  let sql = 'SELECT * FROM powers WHERE 1=1';
  const params = [];
  let paramCount = 0;
  
  // Specific power lookup
  if (item_name) {
    paramCount++;
    sql += ` AND LOWER(name) = LOWER($${paramCount})`;
    params.push(item_name);
  }
  
  // Type filter (adept, critter)
  if (category_filter) {
    paramCount++;
    sql += ` AND power_type = $${paramCount}`;
    params.push(category_filter);
  }
  
  sql += ` ORDER BY name`;
  
  paramCount++;
  sql += ` LIMIT $${paramCount}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  return result.rows;
}

/**
 * Query totems table
 */
async function queryTotems(classification, limit = 10) {
  const { item_name } = classification;
  
  let sql = 'SELECT * FROM totems WHERE 1=1';
  const params = [];
  let paramCount = 0;
  
  // Specific totem lookup
  if (item_name) {
    paramCount++;
    sql += ` AND LOWER(name) = LOWER($${paramCount})`;
    params.push(item_name);
  }
  
  sql += ` ORDER BY name`;
  
  paramCount++;
  sql += ` LIMIT $${paramCount}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  return result.rows;
}

/**
 * Query gear table
 */
async function queryGear(classification, limit = 10) {
  const { item_name, category_filter, sort_by, search_terms } = classification;
  
  let sql = 'SELECT * FROM gear WHERE 1=1';
  const params = [];
  let paramCount = 0;
  
  // Specific item lookup by name
  if (item_name) {
    paramCount++;
    sql += ` AND LOWER(name) LIKE LOWER($${paramCount})`;
    params.push(`%${item_name}%`);
  }
  
  // Text search using search terms
  if (!item_name && search_terms && search_terms.length > 0) {
    paramCount++;
    sql += ` AND search_vector @@ plainto_tsquery('english', $${paramCount})`;
    params.push(search_terms.join(' '));
  }
  
  // Category filter (weapon, armor, cyberware, etc.)
  if (category_filter) {
    paramCount++;
    sql += ` AND (category = $${paramCount} OR subcategory = $${paramCount})`;
    params.push(category_filter);
  }
  
  // Sorting
  const sortField = {
    'cost': 'cost',
    'damage': "(base_stats->>'damage')",
    'essence': "(base_stats->>'essence')::NUMERIC",
    'conceal': "(base_stats->>'conceal')::INTEGER",
    'ammo': "(base_stats->>'ammo')::INTEGER",
  }[sort_by] || 'name';
  
  const sortDir = (sort_by === 'cost' || sort_by === 'essence' || sort_by === 'conceal') ? 'ASC' : 'DESC';
  sql += ` ORDER BY ${sortField} ${sortDir} NULLS LAST`;
  
  paramCount++;
  sql += ` LIMIT $${paramCount}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  return result.rows;
}

/**
 * Generate embedding for a query using OpenAI
 */
async function generateQueryEmbedding(query) {
  try {
    const response = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: query,
    });
    return response.data[0].embedding;
  } catch (error) {
    console.error('Embedding generation error:', error);
    throw new Error(`Failed to generate embedding: ${error.message}`);
  }
}

/**
 * Vector similarity search using pgvector
 */
async function vectorSearch(query, classification, limit = 20) {
  // Generate embedding for query
  const embedding = await generateQueryEmbedding(query);
  
  // Convert to pgvector format
  const embeddingStr = `[${embedding.join(',')}]`;
  
  let sql = `
    SELECT 
      id,
      title,
      content,
      category,
      subcategory,
      tags,
      content_type,
      source_file,
      1 - (embedding <=> $1::vector) as similarity_score
    FROM rules_content
    WHERE embedding IS NOT NULL
  `;
  
  const params = [embeddingStr];
  let paramCount = 1;
  
  // Add category filter if specified
  if (classification.categories && classification.categories.length > 0) {
    paramCount++;
    sql += ` AND category = ANY($${paramCount})`;
    params.push(classification.categories);
  }
  
  // Add content type filter if specified
  if (classification.content_types && classification.content_types.length > 0) {
    paramCount++;
    sql += ` AND content_type = ANY($${paramCount})`;
    params.push(classification.content_types);
  }
  
  // Order by similarity (higher = more similar)
  sql += ` ORDER BY embedding <=> $1::vector LIMIT ${limit}`;
  
  const result = await pool.query(sql, params);
  return result.rows;
}

/**
 * Keyword search using PostgreSQL full-text search
 */
async function keywordSearch(query, classification, limit = 20) {
  const { categories, content_types } = classification;
  
  let sql = `
    SELECT 
      id,
      title,
      content,
      category,
      subcategory,
      tags,
      content_type,
      source_file,
      ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) as rank
    FROM rules_content
    WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
  `;
  
  const params = [query];
  let paramCount = 1;
  
  if (categories && categories.length > 0) {
    paramCount++;
    sql += ` AND category = ANY($${paramCount})`;
    params.push(categories);
  }
  
  if (content_types && content_types.length > 0) {
    paramCount++;
    sql += ` AND content_type = ANY($${paramCount})`;
    params.push(content_types);
  }
  
  sql += ` ORDER BY rank DESC LIMIT ${limit}`;
  
  const result = await pool.query(sql, params);
  return result.rows;
}

/**
 * Reciprocal Rank Fusion - combines vector and keyword search results
 */
function reciprocalRankFusion(vectorResults, keywordResults, k = 60) {
  const scores = new Map();
  
  // Score vector results (rank 1 = highest score)
  vectorResults.forEach((result, index) => {
    const rank = index + 1;
    const score = 1 / (k + rank);
    scores.set(result.id, {
      ...result,
      rrf_score: score,
      vector_rank: rank,
      vector_score: result.similarity_score || 0,
    });
  });
  
  // Add keyword results (boost if already in vector results)
  keywordResults.forEach((result, index) => {
    const rank = index + 1;
    const score = 1 / (k + rank);
    
    if (scores.has(result.id)) {
      // Item in both results - add scores
      const existing = scores.get(result.id);
      existing.rrf_score += score;
      existing.keyword_rank = rank;
      existing.keyword_score = result.rank || 0;
    } else {
      // Only in keyword results
      scores.set(result.id, {
        ...result,
        rrf_score: score,
        keyword_rank: rank,
        keyword_score: result.rank || 0,
      });
    }
  });
  
  // Sort by combined RRF score
  return Array.from(scores.values())
    .sort((a, b) => b.rrf_score - a.rrf_score);
}

/**
 * Hybrid search combining vector similarity and keyword search
 */
async function hybridSearch(query, classification, limit = 10) {
  console.error('Starting hybrid search for:', query);
  
  try {
    // Run both searches in parallel
    const [vectorResults, keywordResults] = await Promise.all([
      vectorSearch(query, classification, 20),
      keywordSearch(query, classification, 20)
    ]);
    
    console.error('Vector results:', vectorResults.length);
    console.error('Keyword results:', keywordResults.length);
    
    // Fuse results using Reciprocal Rank Fusion
    const fusedResults = reciprocalRankFusion(vectorResults, keywordResults);
    
    console.error('Fused results:', fusedResults.length);
    if (fusedResults.length > 0) {
      console.error('Top 3 RRF scores:', fusedResults.slice(0, 3).map(r => ({
        title: r.title,
        rrf_score: r.rrf_score.toFixed(4),
        vector_rank: r.vector_rank || 'N/A',
        keyword_rank: r.keyword_rank || 'N/A'
      })));
    }
    
    // Return top N
    return fusedResults.slice(0, limit);
  } catch (error) {
    console.error('Hybrid search error:', error);
    // Fallback to keyword search only if vector search fails
    console.error('Falling back to keyword-only search');
    return await keywordSearch(query, classification, limit);
  }
}

/**
 * Legacy function - now redirects to hybrid search
 * @deprecated Use hybridSearch instead
 */
async function searchDatabase(classification, limit = 10) {
  const { keywords } = classification;
  const query = keywords ? keywords.join(' ') : '';
  return await hybridSearch(query, classification, limit);
}

/**
 * Format results based on query type
 */
async function formatResults(results, classification, rankingCriteria = null) {
  const { type, needs_ranking, gear_type } = classification;
  
  if (results.length === 0) {
    return 'No results found. Try rephrasing your query or using different keywords.';
  }
  
  switch (type) {
    case 'rules': {
      let output = `# Rules Query Results (${results.length} found)\n\n`;
      
      for (let i = 0; i < results.length; i++) {
        const r = results[i];
        output += `## ${i + 1}. ${r.title}\n`;
        output += `**Category:** ${r.category}`;
        if (r.subcategory) output += ` > ${r.subcategory}`;
        output += `\n**Type:** ${r.content_type}\n\n`;
        output += `${r.content}\n\n`;
        if (r.tags && r.tags.length > 0) {
          output += `*Tags: ${r.tags.join(', ')}*\n\n`;
        }
        output += '---\n\n';
      }
      
      return output;
    }
    
    case 'gear_list': {
      let output = `# Gear List: ${gear_type || 'Items'} (${results.length} found)\n\n`;
      
      // Extract stats for each item
      const itemsWithStats = await Promise.all(
        results.map(async (r) => ({
          ...r,
          stats: await extractGearStats(r.content, gear_type),
        }))
      );
      
      // Format as table
      output += '| Item | Damage | Ammo | Mode | Conceal | Source |\n';
      output += '|------|--------|------|------|---------|--------|\n';
      
      for (const item of itemsWithStats) {
        const s = item.stats || {};
        output += `| ${s.name || item.title} | ${s.damage || '-'} | ${s.ammo || '-'} | ${s.mode || '-'} | ${s.conceal || '-'} | ${item.source_file} |\n`;
      }
      
      output += '\n---\n\n';
      
      // Add detailed content for first few items
      output += '## Detailed Information\n\n';
      for (let i = 0; i < Math.min(3, results.length); i++) {
        output += `### ${results[i].title}\n${results[i].content}\n\n`;
      }
      
      return output;
    }
    
    case 'gear_compare': {
      if (needs_ranking && !rankingCriteria) {
        // Ask user for ranking criteria
        let output = `# Gear Comparison: ${gear_type || 'Items'}\n\n`;
        output += `Found ${results.length} items. How should I rank them?\n\n`;
        output += 'Please specify ranking criteria:\n';
        output += '- **damage** - Highest damage code\n';
        if (gear_type === 'melee') {
          output += '- **reach** - Longest reach\n';
        }
        output += '- **conceal** - Best concealability (lowest number)\n';
        output += '- **ammo** - Largest ammunition capacity\n';
        output += '- **mode** - Most fire modes (FA > BF > SA)\n';
        output += '- **cost** - Lowest price\n';
        output += '- **all** - Show all without ranking\n\n';
        output += 'Re-run the query with ranking_criteria parameter set to your choice.';
        return output;
      }
      
      // Extract stats and rank
      const itemsWithStats = await Promise.all(
        results.map(async (r) => ({
          ...r,
          stats: await extractGearStats(r.content, gear_type),
        }))
      );
      
      const ranked = rankGear(itemsWithStats, rankingCriteria || 'damage');
      
      let output = `# Gear Comparison: ${gear_type || 'Items'}\n`;
      output += `Ranked by: **${rankingCriteria || 'damage'}**\n\n`;
      
      // Show top recommendation
      if (ranked.length > 0) {
        const top = ranked[0];
        output += `## 🏆 Top Recommendation: ${top.stats?.name || top.title}\n\n`;
        output += `${top.content}\n\n`;
        output += '---\n\n';
      }
      
      // Show comparison table
      output += '## Full Comparison\n\n';
      output += '| Rank | Item | Damage | Ammo | Mode | Reach | Conceal | Score |\n';
      output += '|------|------|--------|------|------|-------|---------|-------|\n';
      
      for (let i = 0; i < ranked.length; i++) {
        const item = ranked[i];
        const s = item.stats || {};
        output += `| ${i + 1} | ${s.name || item.title} | ${s.damage || '-'} | ${s.ammo || '-'} | ${s.mode || '-'} | ${s.reach || '-'} | ${s.conceal || '-'} | ${item.score.toFixed(1)} |\n`;
      }
      
      return output;
    }
    
    case 'lore': {
      let output = `# Lore Query Results (${results.length} found)\n\n`;
      
      for (let i = 0; i < results.length; i++) {
        const r = results[i];
        output += `## ${r.title}\n\n`;
        output += `${r.content}\n\n`;
        output += `*Source: ${r.source_file}*\n\n`;
        output += '---\n\n';
      }
      
      return output;
    }
    
    default:
      return 'Unknown query type.';
  }
}

/**
 * Lookup gear from database with fuzzy matching
 */
async function lookupGear(args) {
  const { query, category, subcategory, max_cost, tags, limit = 10 } = args;
  
  let sql = 'SELECT * FROM gear WHERE 1=1';
  const params = [];
  let paramCount = 0;
  
  // Text search - use full-text search for better matching
  if (query) {
    paramCount++;
    sql += ` AND search_vector @@ plainto_tsquery('english', $${paramCount})`;
    params.push(query);
  }
  
  // Category filter
  if (category) {
    paramCount++;
    sql += ` AND category = $${paramCount}`;
    params.push(category);
  }
  
  // Subcategory filter with fuzzy matching
  if (subcategory) {
    // Normalize: remove trailing 's', replace spaces with underscores
    const normalized = subcategory.toLowerCase().replace(/s$/, '').replace(/\s+/g, '_');
    paramCount++;
    sql += ` AND (subcategory = $${paramCount} OR subcategory ILIKE $${paramCount + 1} OR subcategory ILIKE $${paramCount + 2})`;
    params.push(subcategory);
    paramCount++;
    params.push(`%${normalized}%`);
    paramCount++;
    // Also try with spaces replaced by underscores
    params.push(`%${subcategory.replace(/\s+/g, '_')}%`);
  }
  
  // Cost filter
  if (max_cost) {
    paramCount++;
    sql += ` AND cost <= $${paramCount}`;
    params.push(max_cost);
  }
  
  // Tags filter
  if (tags && tags.length > 0) {
    paramCount++;
    sql += ` AND tags && $${paramCount}`;
    params.push(tags);
  }
  
  // Order and limit
  if (query) {
    sql += ` ORDER BY ts_rank(search_vector, plainto_tsquery('english', $1)) DESC`;
  } else {
    sql += ` ORDER BY name`;
  }
  
  paramCount++;
  sql += ` LIMIT $${paramCount}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  
  if (result.rows.length === 0) {
    return 'No gear found matching your criteria.';
  }
  
  // Format results
  let output = `# Gear Search Results (${result.rows.length} found)\n\n`;
  
  for (const item of result.rows) {
    output += `## ${item.name}\n`;
    output += `**ID:** ${item.id} | **Category:** ${item.category}`;
    if (item.subcategory) output += ` > ${item.subcategory}`;
    output += `\n`;
    
    // Display key stats based on category
    if (item.category === 'weapon') {
      const stats = item.base_stats;
      output += `**Damage:** ${stats.damage || 'N/A'} | `;
      output += `**Conceal:** ${stats.conceal || 'N/A'} | `;
      output += `**Ammo:** ${stats.ammo || 'N/A'} | `;
      output += `**Mode:** ${stats.mode || 'N/A'}\n`;
    } else if (item.category === 'cyberware') {
      const stats = item.base_stats;
      output += `**Essence:** ${stats.essence || 'N/A'} | `;
      output += `**Index:** ${stats.index || 'N/A'}\n`;
    } else if (item.category === 'armor') {
      const stats = item.base_stats;
      output += `**Ballistic:** ${stats.ballistic || 'N/A'} | `;
      output += `**Impact:** ${stats.impact || 'N/A'} | `;
      output += `**Conceal:** ${stats.conceal || 'N/A'}\n`;
    }
    
    if (item.cost) output += `**Cost:** ¥${item.cost.toLocaleString()}\n`;
    if (item.availability) output += `**Availability:** ${item.availability}\n`;
    if (item.description) output += `\n${item.description}\n`;
    if (item.tags && item.tags.length > 0) {
      output += `\n*Tags: ${item.tags.join(', ')}*\n`;
    }
    output += `\n*Use get_gear_details with ID ${item.id} for complete information*\n`;
    output += '\n---\n\n';
  }
  
  return output;
}

/**
 * Compare gear items with fuzzy subcategory matching
 */
async function compareGear(args) {
  const { category, subcategory, sort_by = 'cost', limit = 10 } = args;
  
  let sql = 'SELECT * FROM gear WHERE category = $1';
  const params = [category];
  let paramCount = 1;
  
  if (subcategory) {
    // Fuzzy match: try exact, then ILIKE with normalized version, then with spaces→underscores
    const normalized = subcategory.toLowerCase().replace(/s$/, '').replace(/\s+/g, '_');
    paramCount++;
    sql += ` AND (subcategory = $${paramCount} OR subcategory ILIKE $${paramCount + 1} OR subcategory ILIKE $${paramCount + 2})`;
    params.push(subcategory);
    paramCount++;
    params.push(`%${normalized}%`);
    paramCount++;
    params.push(`%${subcategory.replace(/\s+/g, '_')}%`);
  }
  
  // Add sorting
  const sortField = {
    'cost': 'cost',
    'damage': "(base_stats->>'damage')",
    'essence': "(base_stats->>'essence')::NUMERIC",
    'availability': 'availability',
    'conceal': "(base_stats->>'conceal')::INTEGER",
    'ammo': "(base_stats->>'ammo')::INTEGER",
  }[sort_by] || 'cost';
  
  sql += ` ORDER BY ${sortField} ${sort_by === 'cost' || sort_by === 'essence' || sort_by === 'conceal' ? 'ASC' : 'DESC'} NULLS LAST LIMIT $${params.length + 1}`;
  params.push(limit);
  
  const result = await pool.query(sql, params);
  
  if (result.rows.length === 0) {
    return `No ${category} items found${subcategory ? ` in subcategory ${subcategory}` : ''}.`;
  }
  
  // Format as comparison table
  let output = `# Gear Comparison: ${category}${subcategory ? ` (${subcategory})` : ''}\n`;
  output += `Sorted by: **${sort_by}**\n\n`;
  
  // Build table based on category
  if (category === 'weapon') {
    output += '| Rank | Name | Damage | Conceal | Ammo | Mode | Cost | Avail |\n';
    output += '|------|------|--------|---------|------|------|------|-------|\n';
    
    result.rows.forEach((item, idx) => {
      const s = item.base_stats;
      output += `| ${idx + 1} | ${item.name} | ${s.damage || '-'} | ${s.conceal || '-'} | ${s.ammo || '-'} | ${s.mode || '-'} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
    });
  } else if (category === 'cyberware') {
    output += '| Rank | Name | Essence | Index | Cost | Avail |\n';
    output += '|------|------|---------|-------|------|-------|\n';
    
    result.rows.forEach((item, idx) => {
      const s = item.base_stats;
      output += `| ${idx + 1} | ${item.name} | ${s.essence || '-'} | ${s.index || '-'} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
    });
  } else if (category === 'armor') {
    output += '| Rank | Name | Ballistic | Impact | Conceal | Cost | Avail |\n';
    output += '|------|------|-----------|--------|---------|------|-------|\n';
    
    result.rows.forEach((item, idx) => {
      const s = item.base_stats;
      output += `| ${idx + 1} | ${item.name} | ${s.ballistic || '-'} | ${s.impact || '-'} | ${s.conceal || '-'} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
    });
  } else {
    // Generic table
    output += '| Rank | Name | Cost | Availability |\n';
    output += '|------|------|------|-------------|\n';
    
    result.rows.forEach((item, idx) => {
      output += `| ${idx + 1} | ${item.name} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
    });
  }
  
  output += '\n---\n\n';
  
  // Show top recommendation
  if (result.rows.length > 0) {
    const top = result.rows[0];
    output += `## 🏆 Top Recommendation: ${top.name}\n\n`;
    if (top.description) output += `${top.description}\n\n`;
    output += `*Use get_gear_details with ID ${top.id} for complete information*\n`;
  }
  
  return output;
}

/**
 * Get detailed gear information
 */
async function getGearDetails(gearId, includeChunks = true) {
  if (includeChunks) {
    // Use the PostgreSQL function to get gear with chunks
    const result = await pool.query('SELECT get_gear_with_chunks($1) as data', [gearId]);
    
    if (!result.rows[0]?.data?.gear) {
      return `Gear item with ID ${gearId} not found.`;
    }
    
    const data = result.rows[0].data;
    const gear = data.gear;
    const chunks = data.chunks || [];
    
    let output = `# ${gear.name}\n\n`;
    output += `**Category:** ${gear.category}`;
    if (gear.subcategory) output += ` > ${gear.subcategory}`;
    output += `\n`;
    
    // Stats section
    output += `\n## Statistics\n\n`;
    output += '```json\n';
    output += JSON.stringify(gear.base_stats, null, 2);
    output += '\n```\n\n';
    
    if (Object.keys(gear.modifiers).length > 0) {
      output += `## Modifiers\n\n`;
      output += '```json\n';
      output += JSON.stringify(gear.modifiers, null, 2);
      output += '\n```\n\n';
    }
    
    if (Object.keys(gear.requirements).length > 0) {
      output += `## Requirements\n\n`;
      output += '```json\n';
      output += JSON.stringify(gear.requirements, null, 2);
      output += '\n```\n\n';
    }
    
    // Game info
    output += `## Game Information\n\n`;
    if (gear.cost) output += `**Cost:** ¥${gear.cost.toLocaleString()}\n`;
    if (gear.availability) output += `**Availability:** ${gear.availability}\n`;
    if (gear.street_index) output += `**Street Index:** ${gear.street_index}\n`;
    if (gear.legality) output += `**Legality:** ${gear.legality}\n`;
    if (gear.source) output += `**Source:** ${gear.source}\n`;
    
    if (gear.description) {
      output += `\n## Description\n\n${gear.description}\n`;
    }
    
    if (gear.game_notes) {
      output += `\n## Game Notes\n\n${gear.game_notes}\n`;
    }
    
    if (gear.tags && gear.tags.length > 0) {
      output += `\n**Tags:** ${gear.tags.join(', ')}\n`;
    }
    
    // Linked chunks
    if (chunks.length > 0) {
      output += `\n## Related Rules & Lore (${chunks.length} chunks)\n\n`;
      chunks.forEach((chunk, idx) => {
        output += `### ${idx + 1}. ${chunk.content_type} (confidence: ${chunk.confidence})\n`;
        output += `${chunk.content.substring(0, 300)}${chunk.content.length > 300 ? '...' : ''}\n\n`;
      });
    }
    
    // Data quality info
    output += `\n---\n*Data Quality: ${gear.data_quality}/10 | Source: ${gear.source_file}*\n`;
    if (gear.loaded_from && gear.loaded_from.length > 1) {
      output += `*Merged from: ${gear.loaded_from.join(', ')}*\n`;
    }
    
    return output;
  } else {
    // Just get the gear without chunks
    const result = await pool.query('SELECT * FROM gear WHERE id = $1', [gearId]);
    
    if (result.rows.length === 0) {
      return `Gear item with ID ${gearId} not found.`;
    }
    
    const gear = result.rows[0];
    
    let output = `# ${gear.name}\n\n`;
    output += JSON.stringify(gear, null, 2);
    
    return output;
  }
}

/**
 * Execute multi-source query
 */
async function executeMultiSourceQuery(classification, limit = 10) {
  const results = {};
  
  // Query structured tables if needed
  if (classification.data_sources.includes('structured')) {
    if (classification.tables.includes('spells')) {
      results.spells = await querySpells(classification, limit);
    }
    if (classification.tables.includes('powers')) {
      results.powers = await queryPowers(classification, limit);
    }
    if (classification.tables.includes('totems')) {
      results.totems = await queryTotems(classification, limit);
    }
    if (classification.tables.includes('gear')) {
      results.gear = await queryGear(classification, limit);
    }
  }
  
  // Query text chunks if needed
  if (classification.data_sources.includes('chunks')) {
    const chunkClassification = {
      categories: classification.chunk_categories || ['general'],
      content_types: ['rule_mechanic', 'introduction'],
      keywords: classification.search_terms || [classification.item_name || ''],
    };
    results.chunks = await searchDatabase(chunkClassification, limit);
  }
  
  return results;
}

/**
 * Format multi-source results
 */
function formatMultiSourceResults(results, classification) {
  const { intent, item_name } = classification;
  let output = '';
  
  // Format based on intent
  if (intent === 'lookup' && item_name) {
    // Specific item lookup
    if (results.spells && results.spells.length > 0) {
      const spell = results.spells[0];
      output += `# ${spell.name}\n\n`;
      output += `## Spell Statistics\n\n`;
      output += `- **Category:** ${spell.category}\n`;
      output += `- **Type:** ${spell.spell_type}\n`;
      output += `- **Target:** ${spell.target_type || 'N/A'}\n`;
      output += `- **Duration:** ${spell.duration}\n`;
      output += `- **Drain:** ${spell.drain_code}\n`;
      output += `- **Range:** ${spell.range_type || 'LOS'}\n\n`;
      
      if (spell.description) {
        output += `## Description\n\n${spell.description}\n\n`;
      }
      
      if (spell.page_reference) {
        output += `*Source: ${spell.page_reference}*\n\n`;
      }
    } else if (results.powers && results.powers.length > 0) {
      const power = results.powers[0];
      output += `# ${power.name}\n\n`;
      output += `## Power Statistics\n\n`;
      output += `- **Type:** ${power.power_type}\n`;
      output += `- **Cost:** ${power.power_point_cost} Power Points\n\n`;
      
      if (power.description) {
        output += `## Description\n\n${power.description}\n\n`;
      }
      
      if (power.page_reference) {
        output += `*Source: ${power.page_reference}*\n\n`;
      }
    } else if (results.totems && results.totems.length > 0) {
      const totem = results.totems[0];
      output += `# ${totem.name} Totem\n\n`;
      
      if (totem.advantages) {
        output += `## Advantages\n${totem.advantages}\n\n`;
      }
      
      if (totem.disadvantages) {
        output += `## Disadvantages\n${totem.disadvantages}\n\n`;
      }
      
      if (totem.environment) {
        output += `**Environment:** ${totem.environment}\n\n`;
      }
      
      if (totem.description) {
        output += `## Description\n\n${totem.description}\n\n`;
      }
      
      if (totem.page_reference) {
        output += `*Source: ${totem.page_reference}*\n\n`;
      }
    }
    
    // Add related rules/explanation if available
    if (results.chunks && results.chunks.length > 0 && classification.needs_explanation) {
      output += `## Related Rules & Information\n\n`;
      for (const chunk of results.chunks.slice(0, 2)) {
        output += `### ${chunk.title}\n${chunk.content.substring(0, 500)}...\n\n`;
      }
    }
  } else if (intent === 'list') {
    // List all items of a type
    if (results.spells && results.spells.length > 0) {
      output += `# Spells`;
      if (classification.category_filter) {
        output += ` (${classification.category_filter})`;
      }
      output += ` - ${results.spells.length} found\n\n`;
      
      output += '| Name | Category | Type | Drain | Duration |\n';
      output += '|------|----------|------|-------|----------|\n';
      
      for (const spell of results.spells) {
        output += `| ${spell.name} | ${spell.category} | ${spell.spell_type} | ${spell.drain_code} | ${spell.duration} |\n`;
      }
    } else if (results.powers && results.powers.length > 0) {
      output += `# Adept Powers - ${results.powers.length} found\n\n`;
      
      output += '| Name | Type | Cost | Description |\n';
      output += '|------|------|------|-------------|\n';
      
      for (const power of results.powers) {
        const desc = power.description ? power.description.substring(0, 50) + '...' : '';
        output += `| ${power.name} | ${power.power_type} | ${power.power_point_cost} | ${desc} |\n`;
      }
    } else if (results.totems && results.totems.length > 0) {
      output += `# Totems - ${results.totems.length} found\n\n`;
      
      for (const totem of results.totems) {
        output += `## ${totem.name}\n`;
        if (totem.advantages) output += `**Advantages:** ${totem.advantages}\n`;
        if (totem.disadvantages) output += `**Disadvantages:** ${totem.disadvantages}\n`;
        output += '\n';
      }
    } else if (results.gear && results.gear.length > 0) {
      const gear = results.gear[0];
      output += `# Gear`;
      if (gear.category) {
        output += ` (${gear.category})`;
      }
      output += ` - ${results.gear.length} found\n\n`;
      
      // Format based on category
      if (gear.category === 'weapon') {
        output += '| Name | Damage | Conceal | Ammo | Mode | Cost | Avail |\n';
        output += '|------|--------|---------|------|------|------|-------|\n';
        
        for (const item of results.gear) {
          const s = item.base_stats;
          output += `| ${item.name} | ${s.damage || '-'} | ${s.conceal || '-'} | ${s.ammo || '-'} | ${s.mode || '-'} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
        }
      } else {
        output += '| Name | Category | Cost | Availability |\n';
        output += '|------|----------|------|-------------|\n';
        
        for (const item of results.gear) {
          output += `| ${item.name} | ${item.subcategory || item.category} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
        }
      }
    }
  } else if (intent === 'compare') {
    // Compare/rank items
    if (results.gear && results.gear.length > 0) {
      const gear = results.gear[0];
      output += `# Gear Comparison`;
      if (gear.category) {
        output += `: ${gear.category}`;
      }
      output += `\nSorted by: **${classification.sort_by || 'cost'}**\n\n`;
      
      // Format based on category
      if (gear.category === 'weapon') {
        output += '| Rank | Name | Damage | Conceal | Ammo | Mode | Cost | Avail |\n';
        output += '|------|------|--------|---------|------|------|------|-------|\n';
        
        results.gear.forEach((item, idx) => {
          const s = item.base_stats;
          output += `| ${idx + 1} | ${item.name} | ${s.damage || '-'} | ${s.conceal || '-'} | ${s.ammo || '-'} | ${s.mode || '-'} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
        });
      } else {
        output += '| Rank | Name | Category | Cost | Availability |\n';
        output += '|------|------|----------|------|-------------|\n';
        
        results.gear.forEach((item, idx) => {
          output += `| ${idx + 1} | ${item.name} | ${item.subcategory || item.category} | ¥${item.cost?.toLocaleString() || '-'} | ${item.availability || '-'} |\n`;
        });
      }
      
      // Show top recommendation
      if (results.gear.length > 0) {
        const top = results.gear[0];
        output += `\n## 🏆 Top Recommendation: ${top.name}\n\n`;
        if (top.description) output += `${top.description}\n\n`;
        output += `*Use get_gear_details with ID ${top.id} for complete information*\n`;
      }
    }
  } else if (intent === 'rules' || intent === 'hybrid') {
    // Rules explanation or hybrid
    if (results.chunks && results.chunks.length > 0) {
      output += `# Rules & Information (${results.chunks.length} found)\n\n`;
      
      for (let i = 0; i < results.chunks.length; i++) {
        const chunk = results.chunks[i];
        output += `## ${i + 1}. ${chunk.title}\n`;
        output += `**Category:** ${chunk.category}`;
        if (chunk.subcategory) output += ` > ${chunk.subcategory}`;
        output += `\n\n${chunk.content}\n\n---\n\n`;
      }
    }
    
    // Add structured data if hybrid
    if (intent === 'hybrid' && (results.spells || results.powers || results.totems)) {
      output += `\n## Reference Data\n\n`;
      if (results.spells) {
        output += `**Spells:** ${results.spells.map(s => s.name).join(', ')}\n`;
      }
      if (results.powers) {
        output += `**Powers:** ${results.powers.map(p => p.name).join(', ')}\n`;
      }
      if (results.totems) {
        output += `**Totems:** ${results.totems.map(t => t.name).join(', ')}\n`;
      }
    }
  }
  
  if (!output) {
    output = 'No results found. Try rephrasing your query.';
  }
  
  return output;
}

/**
 * Log query to database for analytics
 */
async function logQuery(queryText, limit, rankingCriteria, classification, executionTime, resultCount, errorMessage = null) {
  try {
    await pool.query(`
      INSERT INTO query_logs (
        query_text,
        query_limit,
        ranking_criteria,
        classification,
        intent,
        data_sources,
        tables_queried,
        execution_time_ms,
        result_count,
        error_message
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    `, [
      queryText,
      limit,
      rankingCriteria,
      JSON.stringify(classification),
      classification.intent,
      classification.data_sources,
      classification.tables || [],
      executionTime,
      resultCount,
      errorMessage
    ]);
  } catch (error) {
    // Don't fail the query if logging fails
    console.error('Failed to log query:', error.message);
  }
}

/**
 * Manage campaigns
 */
async function manageCampaigns(args) {
  const { action, campaign_id, name, gm_name, description, settings, status } = args;
  
  switch (action) {
    case 'create': {
      if (!name) {
        throw new Error('Campaign name is required for create action');
      }
      
      const result = await pool.query(`
        INSERT INTO campaigns (name, gm_name, description, settings, status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
      `, [name, gm_name || null, description || null, settings || {}, status || 'planning']);
      
      const campaign = result.rows[0];
      return `# Campaign Created\n\n**ID:** ${campaign.id}\n**Name:** ${campaign.name}\n**GM:** ${campaign.gm_name || 'Not set'}\n**Status:** ${campaign.status}\n\nCampaign created successfully!`;
    }
    
    case 'list': {
      const result = await pool.query('SELECT * FROM campaigns ORDER BY created_at DESC');
      
      if (result.rows.length === 0) {
        return 'No campaigns found.';
      }
      
      let output = `# Campaigns (${result.rows.length} found)\n\n`;
      output += '| ID | Name | GM | Status | Created |\n';
      output += '|----|------|-------|--------|----------|\n';
      
      for (const campaign of result.rows) {
        const created = new Date(campaign.created_at).toLocaleDateString();
        output += `| ${campaign.id} | ${campaign.name} | ${campaign.gm_name || '-'} | ${campaign.status} | ${created} |\n`;
      }
      
      return output;
    }
    
    case 'get': {
      if (!campaign_id) {
        throw new Error('Campaign ID is required for get action');
      }
      
      const result = await pool.query('SELECT * FROM campaigns WHERE id = $1', [campaign_id]);
      
      if (result.rows.length === 0) {
        return `Campaign with ID ${campaign_id} not found.`;
      }
      
      const campaign = result.rows[0];
      let output = `# ${campaign.name}\n\n`;
      output += `**ID:** ${campaign.id}\n`;
      output += `**GM:** ${campaign.gm_name || 'Not set'}\n`;
      output += `**Status:** ${campaign.status}\n`;
      output += `**Created:** ${new Date(campaign.created_at).toLocaleString()}\n\n`;
      
      if (campaign.description) {
        output += `## Description\n\n${campaign.description}\n\n`;
      }
      
      if (campaign.settings && Object.keys(campaign.settings).length > 0) {
        output += `## Settings\n\n\`\`\`json\n${JSON.stringify(campaign.settings, null, 2)}\n\`\`\`\n\n`;
      }
      
      return output;
    }
    
    case 'update': {
      if (!campaign_id) {
        throw new Error('Campaign ID is required for update action');
      }
      
      const updates = [];
      const values = [];
      let paramCount = 0;
      
      if (name !== undefined) {
        paramCount++;
        updates.push(`name = $${paramCount}`);
        values.push(name);
      }
      if (gm_name !== undefined) {
        paramCount++;
        updates.push(`gm_name = $${paramCount}`);
        values.push(gm_name);
      }
      if (description !== undefined) {
        paramCount++;
        updates.push(`description = $${paramCount}`);
        values.push(description);
      }
      if (settings !== undefined) {
        paramCount++;
        updates.push(`settings = $${paramCount}`);
        values.push(settings);
      }
      if (status !== undefined) {
        paramCount++;
        updates.push(`status = $${paramCount}`);
        values.push(status);
      }
      
      if (updates.length === 0) {
        throw new Error('No fields to update');
      }
      
      paramCount++;
      values.push(campaign_id);
      
      const result = await pool.query(`
        UPDATE campaigns
        SET ${updates.join(', ')}
        WHERE id = $${paramCount}
        RETURNING *
      `, values);
      
      if (result.rows.length === 0) {
        return `Campaign with ID ${campaign_id} not found.`;
      }
      
      return `Campaign "${result.rows[0].name}" updated successfully!`;
    }
    
    case 'delete': {
      if (!campaign_id) {
        throw new Error('Campaign ID is required for delete action');
      }
      
      const result = await pool.query('DELETE FROM campaigns WHERE id = $1 RETURNING name', [campaign_id]);
      
      if (result.rows.length === 0) {
        return `Campaign with ID ${campaign_id} not found.`;
      }
      
      return `Campaign "${result.rows[0].name}" deleted successfully!`;
    }
    
    default:
      throw new Error(`Unknown action: ${action}`);
  }
}

/**
 * Manage house rules
 */
async function manageHouseRules(args) {
  const { action, campaign_id, rule_id, rule_name, rule_type, category, description, rule_text, mechanical_effect, applies_to, modifier_value, conditions, priority, is_active } = args;
  
  switch (action) {
    case 'create': {
      if (!rule_name) {
        throw new Error('Rule name is required for create action');
      }
      
      const result = await pool.query(`
        INSERT INTO house_rules (
          campaign_id, rule_name, rule_type, category, description, rule_text,
          mechanical_effect, applies_to, modifier_value, conditions, priority, is_active
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING *
      `, [
        campaign_id || null,
        rule_name,
        rule_type || 'custom',
        category || null,
        description || null,
        rule_text || null,
        mechanical_effect || {},
        applies_to || {},
        modifier_value || null,
        conditions || {},
        priority || 0,
        is_active !== false
      ]);
      
      const rule = result.rows[0];
      return `# House Rule Created\n\n**ID:** ${rule.id}\n**Name:** ${rule.rule_name}\n**Type:** ${rule.rule_type}\n**Campaign:** ${rule.campaign_id || 'Global'}\n**Active:** ${rule.is_active}\n\nHouse rule created successfully!`;
    }
    
    case 'list': {
      let sql = 'SELECT * FROM house_rules WHERE 1=1';
      const params = [];
      
      if (campaign_id !== undefined) {
        if (campaign_id === null) {
          sql += ' AND campaign_id IS NULL';
        } else {
          params.push(campaign_id);
          sql += ` AND campaign_id = $${params.length}`;
        }
      }
      
      sql += ' ORDER BY priority DESC, created_at DESC';
      
      const result = await pool.query(sql, params);
      
      if (result.rows.length === 0) {
        return 'No house rules found.';
      }
      
      let output = `# House Rules (${result.rows.length} found)\n\n`;
      output += '| ID | Name | Type | Campaign | Active | Priority |\n';
      output += '|----|------|------|----------|--------|----------|\n';
      
      for (const rule of result.rows) {
        const campaignLabel = rule.campaign_id || 'Global';
        const active = rule.is_active ? '✓' : '✗';
        output += `| ${rule.id} | ${rule.rule_name} | ${rule.rule_type} | ${campaignLabel} | ${active} | ${rule.priority} |\n`;
      }
      
      return output;
    }
    
    case 'get': {
      if (!rule_id) {
        throw new Error('Rule ID is required for get action');
      }
      
      const result = await pool.query('SELECT * FROM house_rules WHERE id = $1', [rule_id]);
      
      if (result.rows.length === 0) {
        return `House rule with ID ${rule_id} not found.`;
      }
      
      const rule = result.rows[0];
      let output = `# ${rule.rule_name}\n\n`;
      output += `**ID:** ${rule.id}\n`;
      output += `**Type:** ${rule.rule_type}\n`;
      output += `**Category:** ${rule.category || 'Not set'}\n`;
      output += `**Campaign:** ${rule.campaign_id || 'Global'}\n`;
      output += `**Active:** ${rule.is_active ? 'Yes' : 'No'}\n`;
      output += `**Priority:** ${rule.priority}\n\n`;
      
      if (rule.description) {
        output += `## Description\n\n${rule.description}\n\n`;
      }
      
      if (rule.rule_text) {
        output += `## Rule Text\n\n${rule.rule_text}\n\n`;
      }
      
      if (rule.mechanical_effect && Object.keys(rule.mechanical_effect).length > 0) {
        output += `## Mechanical Effect\n\n\`\`\`json\n${JSON.stringify(rule.mechanical_effect, null, 2)}\n\`\`\`\n\n`;
      }
      
      if (rule.applies_to && Object.keys(rule.applies_to).length > 0) {
        output += `## Applies To\n\n\`\`\`json\n${JSON.stringify(rule.applies_to, null, 2)}\n\`\`\`\n\n`;
      }
      
      if (rule.conditions && Object.keys(rule.conditions).length > 0) {
        output += `## Conditions\n\n\`\`\`json\n${JSON.stringify(rule.conditions, null, 2)}\n\`\`\`\n\n`;
      }
      
      return output;
    }
    
    case 'update': {
      if (!rule_id) {
        throw new Error('Rule ID is required for update action');
      }
      
      const updates = [];
      const values = [];
      let paramCount = 0;
      
      if (rule_name !== undefined) {
        paramCount++;
        updates.push(`rule_name = $${paramCount}`);
        values.push(rule_name);
      }
      if (rule_type !== undefined) {
        paramCount++;
        updates.push(`rule_type = $${paramCount}`);
        values.push(rule_type);
      }
      if (category !== undefined) {
        paramCount++;
        updates.push(`category = $${paramCount}`);
        values.push(category);
      }
      if (description !== undefined) {
        paramCount++;
        updates.push(`description = $${paramCount}`);
        values.push(description);
      }
      if (rule_text !== undefined) {
        paramCount++;
        updates.push(`rule_text = $${paramCount}`);
        values.push(rule_text);
      }
      if (mechanical_effect !== undefined) {
        paramCount++;
        updates.push(`mechanical_effect = $${paramCount}`);
        values.push(mechanical_effect);
      }
      if (applies_to !== undefined) {
        paramCount++;
        updates.push(`applies_to = $${paramCount}`);
        values.push(applies_to);
      }
      if (modifier_value !== undefined) {
        paramCount++;
        updates.push(`modifier_value = $${paramCount}`);
        values.push(modifier_value);
      }
      if (conditions !== undefined) {
        paramCount++;
        updates.push(`conditions = $${paramCount}`);
        values.push(conditions);
      }
      if (priority !== undefined) {
        paramCount++;
        updates.push(`priority = $${paramCount}`);
        values.push(priority);
      }
      if (is_active !== undefined) {
        paramCount++;
        updates.push(`is_active = $${paramCount}`);
        values.push(is_active);
      }
      
      if (updates.length === 0) {
        throw new Error('No fields to update');
      }
      
      paramCount++;
      values.push(rule_id);
      
      const result = await pool.query(`
        UPDATE house_rules
        SET ${updates.join(', ')}
        WHERE id = $${paramCount}
        RETURNING *
      `, values);
      
      if (result.rows.length === 0) {
        return `House rule with ID ${rule_id} not found.`;
      }
      
      return `House rule "${result.rows[0].rule_name}" updated successfully!`;
    }
    
    case 'toggle': {
      if (!rule_id) {
        throw new Error('Rule ID is required for toggle action');
      }
      
      const result = await pool.query(`
        UPDATE house_rules
        SET is_active = NOT is_active
        WHERE id = $1
        RETURNING *
      `, [rule_id]);
      
      if (result.rows.length === 0) {
        return `House rule with ID ${rule_id} not found.`;
      }
      
      const rule = result.rows[0];
      return `House rule "${rule.rule_name}" is now ${rule.is_active ? 'active' : 'inactive'}!`;
    }
    
    case 'delete': {
      if (!rule_id) {
        throw new Error('Rule ID is required for delete action');
      }
      
      const result = await pool.query('DELETE FROM house_rules WHERE id = $1 RETURNING rule_name', [rule_id]);
      
      if (result.rows.length === 0) {
        return `House rule with ID ${rule_id} not found.`;
      }
      
      return `House rule "${result.rows[0].rule_name}" deleted successfully!`;
    }
    
    default:
      throw new Error(`Unknown action: ${action}`);
  }
}

/**
 * Main query handler with enhanced routing
 */
async function queryShadowrun(query, limit, rankingCriteria) {
  const startTime = Date.now();
  let classification = null;
  let resultCount = 0;
  let errorMessage = null;
  
  try {
    // Step 1: Multi-stage intent classification (pattern → keyword → LLM)
    classification = await intentClassifier.classify(query);
    console.error('Intent classification:', JSON.stringify(classification, null, 2));
    
    // Step 2: Determine result limit
    const resultLimit = limit || 10;
    
    // Step 3: Execute multi-source query
    const results = await executeMultiSourceQuery(classification, resultLimit);
    
    // Count total results
    resultCount = (results.spells?.length || 0) + 
                  (results.powers?.length || 0) + 
                  (results.totems?.length || 0) + 
                  (results.gear?.length || 0) +
                  (results.chunks?.length || 0);
    
    console.error('Query results:', {
      spells: results.spells?.length || 0,
      powers: results.powers?.length || 0,
      totems: results.totems?.length || 0,
      gear: results.gear?.length || 0,
      chunks: results.chunks?.length || 0,
      total: resultCount
    });
    
    // Step 4: Format and return results
    const formatted = formatMultiSourceResults(results, classification);
    
    // Log successful query
    const executionTime = Date.now() - startTime;
    await logQuery(query, limit, rankingCriteria, classification, executionTime, resultCount);
    
    return formatted;
  } catch (error) {
    console.error('Query error:', error);
    errorMessage = error.message;
    
    // Log failed query
    const executionTime = Date.now() - startTime;
    if (classification) {
      await logQuery(query, limit, rankingCriteria, classification, executionTime, resultCount, errorMessage);
    }
    
    throw error;
  }
}

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'query_shadowrun',
        description: 'Unified query tool for Shadowrun 2nd Edition rules, gear, and lore. Automatically detects query type and returns relevant information. Supports rules questions, gear listings, gear comparisons with ranking, and lore queries.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Your question or request (e.g., "How does initiative work?", "Show me all heavy pistols", "What dragon runs Saeder-Krupp?")',
            },
            limit: {
              type: 'number',
              description: 'Maximum number of results to return (optional, defaults vary by query type)',
            },
            ranking_criteria: {
              type: 'string',
              description: 'For gear comparisons: how to rank items (damage, reach, conceal, ammo, mode, cost)',
              enum: ['damage', 'reach', 'conceal', 'ammo', 'mode', 'cost', 'all'],
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'roll_dice',
        description: 'Roll dice using standard notation (e.g., "2d6", "1d20+5", "3d8-2"). Returns individual rolls, sum, modifier, and total.',
        inputSchema: {
          type: 'object',
          properties: {
            notation: {
              type: 'string',
              description: 'Dice notation (e.g., "2d6" for two six-sided dice, "1d20+5" for one twenty-sided die plus 5)',
            },
          },
          required: ['notation'],
        },
      },
      {
        name: 'roll_multiple_dice',
        description: 'Roll multiple different dice at once. Useful for rolling several different types of dice in a single call.',
        inputSchema: {
          type: 'object',
          properties: {
            notations: {
              type: 'array',
              items: {
                type: 'string',
              },
              description: 'Array of dice notations to roll (e.g., ["2d6", "1d20+5", "3d8"])',
            },
          },
          required: ['notations'],
        },
      },
      {
        name: 'roll_with_advantage',
        description: 'Roll with advantage (D&D 5e mechanic): roll the dice twice and take the higher result. Commonly used for ability checks when the character has advantage.',
        inputSchema: {
          type: 'object',
          properties: {
            notation: {
              type: 'string',
              description: 'Dice notation (e.g., "1d20" for a d20 roll with advantage)',
            },
          },
          required: ['notation'],
        },
      },
      {
        name: 'roll_with_disadvantage',
        description: 'Roll with disadvantage (D&D 5e mechanic): roll the dice twice and take the lower result. Commonly used for ability checks when the character has disadvantage.',
        inputSchema: {
          type: 'object',
          properties: {
            notation: {
              type: 'string',
              description: 'Dice notation (e.g., "1d20" for a d20 roll with disadvantage)',
            },
          },
          required: ['notation'],
        },
      },
      {
        name: 'roll_with_target_number',
        description: 'Roll dice and count successes against a target number (Shadowrun-style). Supports exploding dice with ! notation. Each die that meets or exceeds the target number counts as a success.',
        inputSchema: {
          type: 'object',
          properties: {
            notation: {
              type: 'string',
              description: 'Dice notation (e.g., "6d6" or "6d6!" for exploding dice)',
            },
            target_number: {
              type: 'number',
              description: 'The target number for counting successes (e.g., 5 means each roll of 5 or 6 on a d6 is a success)',
            },
          },
          required: ['notation', 'target_number'],
        },
      },
      {
        name: 'roll_opposed',
        description: 'Perform an opposed roll between two sets of dice (Shadowrun-style). Each side rolls dice against their target number, and net successes determine the winner.',
        inputSchema: {
          type: 'object',
          properties: {
            notation1: {
              type: 'string',
              description: "First roller's dice notation (e.g., \"6d6!\" for 6 exploding d6)",
            },
            target_number1: {
              type: 'number',
              description: "First roller's target number",
            },
            notation2: {
              type: 'string',
              description: "Opponent's dice notation (e.g., \"4d6!\" for 4 exploding d6)",
            },
            target_number2: {
              type: 'number',
              description: "Opponent's target number",
            },
          },
          required: ['notation1', 'target_number1', 'notation2', 'target_number2'],
        },
      },
      {
        name: 'roll_initiative',
        description: 'Roll initiative for a single character (Shadowrun-style). Initiative dice NEVER explode, even if ! is in the notation. Returns initiative score and phase breakdown.',
        inputSchema: {
          type: 'object',
          properties: {
            notation: {
              type: 'string',
              description: 'Initiative dice notation (e.g., "2d6+10" for Reaction 2 + Initiative 10)',
            },
          },
          required: ['notation'],
        },
      },
      {
        name: 'track_initiative',
        description: 'Track initiative for multiple characters with complete phase breakdown. Automatically handles tie-breaking (higher modifier wins). Shows which characters act in each phase from highest to lowest.',
        inputSchema: {
          type: 'object',
          properties: {
            characters: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: {
                    type: 'string',
                    description: 'Character name',
                  },
                  notation: {
                    type: 'string',
                    description: 'Initiative dice notation (e.g., "2d6+10")',
                  },
                },
                required: ['name', 'notation'],
              },
              description: 'Array of characters with their initiative dice',
            },
          },
          required: ['characters'],
        },
      },
      {
        name: 'roll_with_pools',
        description: 'Roll with dice pools (Shadowrun-style). Tracks multiple pools separately (skill, Combat Pool, Karma Pool, etc.). You can call this once with all pools, or make separate calls for skill first, then ask user about pool allocation, then call again for pools. All results include complete roll arrays.',
        inputSchema: {
          type: 'object',
          properties: {
            pools: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: {
                    type: 'string',
                    description: 'Pool name (e.g., "Firearms Skill", "Combat Pool", "Karma Pool", "Smartlink Bonus")',
                  },
                  notation: {
                    type: 'string',
                    description: 'Dice notation for this pool (e.g., "6d6!" for skill, "4d6!" for combat pool)',
                  },
                },
                required: ['name', 'notation'],
              },
              description: 'Array of dice pools to roll',
            },
            target_number: {
              type: 'number',
              description: 'Target number for success (applies to all pools)',
            },
          },
          required: ['pools', 'target_number'],
        },
      },
      {
        name: 'roll_opposed_pools',
        description: "Opposed roll with dice pools. General-purpose for ANY opposed test (combat/damage resistance, stealth vs perception, social tests, spell resistance, etc.). Provides complete data for both sides - you interpret based on test type. For damage resistance: if defender's Combat Pool alone > attacker total = dodge. Common pools: Combat Pool, Karma Pool, Hacking Pool, Task Pool, Spell Pool, Astral Pool, Control Pool, or custom names.",
        inputSchema: {
          type: 'object',
          properties: {
            side1_pools: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  notation: { type: 'string' },
                },
                required: ['name', 'notation'],
              },
              description: 'Pools for side 1 (e.g., attacker, sneaker, caster)',
            },
            side1_target_number: {
              type: 'number',
              description: 'Target number for side 1',
            },
            side2_pools: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  notation: { type: 'string' },
                },
                required: ['name', 'notation'],
              },
              description: 'Pools for side 2 (e.g., defender, watcher, target)',
            },
            side2_target_number: {
              type: 'number',
              description: 'Target number for side 2',
            },
            side1_label: {
              type: 'string',
              description: 'Label for side 1 (optional, default "Side 1")',
            },
            side2_label: {
              type: 'string',
              description: 'Label for side 2 (optional, default "Side 2")',
            },
          },
          required: ['side1_pools', 'side1_target_number', 'side2_pools', 'side2_target_number'],
        },
      },
      {
        name: 'reroll_failures',
        description: 'Re-roll failed dice using Karma Pool (Shadowrun). Cost escalates: 1st re-roll = 1 Karma, 2nd = 2 Karma, 3rd = 3 Karma, etc. Use this iteratively - present results to user, ask if they want to spend Karma to re-roll remaining failures. Track the reroll_iteration to calculate escalating costs.',
        inputSchema: {
          type: 'object',
          properties: {
            failed_dice: {
              type: 'array',
              items: { type: 'number' },
              description: 'Array of failed die values to re-roll (from the failures array in previous roll)',
            },
            target_number: {
              type: 'number',
              description: 'Target number for successes',
            },
            sides: {
              type: 'number',
              description: 'Number of sides on the die (default 6)',
            },
            exploding: {
              type: 'boolean',
              description: 'Whether dice explode on max value (default true)',
            },
            reroll_iteration: {
              type: 'number',
              description: 'Which re-roll attempt (1st, 2nd, 3rd, etc.) - determines Karma cost',
            },
          },
          required: ['failed_dice', 'target_number'],
        },
      },
      {
        name: 'avoid_disaster',
        description: 'Avoid critical failure when all dice come up 1 (Rule of One). Costs 1 Karma to convert disaster to simple failure. No re-roll allowed after using this. Only use when roll result has all_ones = true.',
        inputSchema: {
          type: 'object',
          properties: {
            roll_result: {
              type: 'object',
              description: 'The original roll result object with all_ones = true',
            },
          },
          required: ['roll_result'],
        },
      },
      {
        name: 'buy_karma_dice',
        description: 'Buy additional dice using Karma Pool. 1 Karma per die, up to a maximum (usually skill/attribute level). These dice are rolled and added to the test. Use before or during a test to boost chances.',
        inputSchema: {
          type: 'object',
          properties: {
            karma_dice_count: {
              type: 'number',
              description: 'Number of Karma dice to buy (1 Karma each)',
            },
            target_number: {
              type: 'number',
              description: 'Target number for successes',
            },
            sides: {
              type: 'number',
              description: 'Number of sides on the die (default 6)',
            },
            exploding: {
              type: 'boolean',
              description: 'Whether dice explode on max value (default true)',
            },
            max_allowed: {
              type: 'number',
              description: 'Optional cap on Karma dice (usually skill/attribute level)',
            },
          },
          required: ['karma_dice_count', 'target_number'],
        },
      },
      {
        name: 'buy_successes',
        description: 'Buy raw successes using Karma Pool. 1 Karma per success. REQUIRES at least 1 natural success in the original roll. This Karma is PERMANENTLY spent and does NOT refresh. Use sparingly for critical moments. Warn user about permanent cost.',
        inputSchema: {
          type: 'object',
          properties: {
            current_successes: {
              type: 'number',
              description: 'Number of successes already achieved (must be at least 1)',
            },
            successes_to_buy: {
              type: 'number',
              description: 'Number of successes to purchase (1 Karma each, permanent)',
            },
          },
          required: ['current_successes', 'successes_to_buy'],
        },
      },
      {
        name: 'lookup_gear',
        description: 'Search for gear by name, category, stats, or tags. Returns matching items with complete stats from the gear database. Use this for finding specific equipment.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Text search (name or description)',
            },
            category: {
              type: 'string',
              description: 'Filter by category',
              enum: ['weapon', 'armor', 'cyberware', 'vehicle', 'bioware', 'magical', 'drug', 'totem', 'spell', 'power'],
            },
            subcategory: {
              type: 'string',
              description: 'Filter by subcategory (e.g., "heavy_pistol", "light_armor")',
            },
            max_cost: {
              type: 'number',
              description: 'Maximum cost in nuyen',
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: 'Filter by tags (e.g., ["smartlink", "silenced"])',
            },
            limit: {
              type: 'number',
              description: 'Maximum number of results (default 10)',
            },
          },
        },
      },
      {
        name: 'compare_gear',
        description: 'Compare multiple gear items side-by-side with ranking. Useful for helping players choose equipment. Returns detailed comparison table.',
        inputSchema: {
          type: 'object',
          properties: {
            category: {
              type: 'string',
              description: 'Gear category to compare',
              enum: ['weapon', 'armor', 'cyberware', 'vehicle', 'bioware', 'magical', 'drug', 'totem', 'spell', 'power'],
            },
            subcategory: {
              type: 'string',
              description: 'Optional subcategory filter',
            },
            sort_by: {
              type: 'string',
              description: 'How to rank items',
              enum: ['cost', 'damage', 'essence', 'availability', 'conceal', 'ammo'],
            },
            limit: {
              type: 'number',
              description: 'Maximum number of items to compare (default 10)',
            },
          },
          required: ['category'],
        },
      },
      {
        name: 'get_gear_details',
        description: 'Get complete details for a specific gear item by ID, including linked rules chunks and lore. Use after lookup_gear to get full information.',
        inputSchema: {
          type: 'object',
          properties: {
            gear_id: {
              type: 'number',
              description: 'Gear item ID from lookup_gear results',
            },
            include_chunks: {
              type: 'boolean',
              description: 'Include linked narrative/rules chunks (default true)',
            },
          },
          required: ['gear_id'],
        },
      },
      {
        name: 'manage_campaigns',
        description: 'Create, list, update, or delete campaigns. Campaigns group characters and house rules together.',
        inputSchema: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              description: 'Action to perform',
              enum: ['create', 'list', 'get', 'update', 'delete'],
            },
            campaign_id: {
              type: 'number',
              description: 'Campaign ID (required for get, update, delete)',
            },
            name: {
              type: 'string',
              description: 'Campaign name (required for create)',
            },
            gm_name: {
              type: 'string',
              description: 'GM name (optional)',
            },
            description: {
              type: 'string',
              description: 'Campaign description (optional)',
            },
            settings: {
              type: 'object',
              description: 'Campaign settings as JSON (optional)',
            },
            status: {
              type: 'string',
              description: 'Campaign status',
              enum: ['planning', 'active', 'on_hold', 'completed', 'archived'],
            },
          },
          required: ['action'],
        },
      },
      {
        name: 'manage_house_rules',
        description: 'Create, list, update, toggle, or delete house rules for a campaign. House rules modify game mechanics like karma costs, attribute limits, spell casting, etc.',
        inputSchema: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              description: 'Action to perform',
              enum: ['create', 'list', 'get', 'update', 'toggle', 'delete'],
            },
            campaign_id: {
              type: 'number',
              description: 'Campaign ID (required for create, list; null for global rules)',
            },
            rule_id: {
              type: 'number',
              description: 'House rule ID (required for get, update, toggle, delete)',
            },
            rule_name: {
              type: 'string',
              description: 'Rule name (required for create)',
            },
            rule_type: {
              type: 'string',
              description: 'Type of rule',
              enum: ['karma_multiplier', 'attribute_limit', 'skill_cost', 'essence_cost', 'initiation_cost', 'healing_rate', 'custom'],
            },
            category: {
              type: 'string',
              description: 'Rule category (magic, combat, matrix, etc.)',
            },
            description: {
              type: 'string',
              description: 'Human-readable description',
            },
            rule_text: {
              type: 'string',
              description: 'Detailed rule text for humans',
            },
            mechanical_effect: {
              type: 'object',
              description: 'AI-parseable mechanical effects as JSON',
            },
            applies_to: {
              type: 'object',
              description: 'What this rule applies to (character types, spell types, etc.)',
            },
            modifier_value: {
              type: 'number',
              description: 'Numeric modifier value (for multipliers, etc.)',
            },
            conditions: {
              type: 'object',
              description: 'Conditions for when rule applies',
            },
            priority: {
              type: 'number',
              description: 'Rule priority (higher applies first, default 0)',
            },
            is_active: {
              type: 'boolean',
              description: 'Whether rule is active',
            },
          },
          required: ['action'],
        },
      },
      {
        name: 'create_character',
        description: 'Create a new Shadowrun character with basic info, attributes, skills, and gear. Returns character ID for future updates.',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Character name (required)',
            },
            campaign_id: {
              type: 'number',
              description: 'Campaign ID (optional)',
            },
            metatype: {
              type: 'string',
              description: 'Metatype (human, elf, dwarf, ork, troll)',
              enum: ['human', 'elf', 'dwarf', 'ork', 'troll'],
            },
            archetype: {
              type: 'string',
              description: 'Character archetype (street samurai, decker, mage, etc.)',
            },
            attributes: {
              type: 'object',
              description: 'Starting attributes (body, quickness, strength, charisma, intelligence, willpower, essence, magic, reaction)',
            },
            skills: {
              type: 'array',
              description: 'Starting skills array [{name, rating, specialization}]',
            },
            starting_nuyen: {
              type: 'number',
              description: 'Starting money (default 5000)',
            },
            starting_karma: {
              type: 'number',
              description: 'Starting karma pool (default 0)',
            },
          },
          required: ['name', 'metatype'],
        },
      },
      {
        name: 'get_character',
        description: 'Retrieve complete character data including attributes, skills, gear, cyberware, spells, and active modifiers.',
        inputSchema: {
          type: 'object',
          properties: {
            character_id: {
              type: 'number',
              description: 'Character ID',
            },
            include_history: {
              type: 'boolean',
              description: 'Include change history (default false)',
            },
            include_modifiers: {
              type: 'boolean',
              description: 'Include active modifiers (default true)',
            },
          },
          required: ['character_id'],
        },
      },
      {
        name: 'update_character',
        description: 'Update character with karma expenditure, gear, cyberware, spells, powers, and more. Supports auto-karma calculation, house rules, and complete audit trail.',
        inputSchema: {
          type: 'object',
          properties: {
            character_id: {
              type: 'number',
              description: 'Character ID to update',
            },
            update_type: {
              type: 'string',
              description: 'Type of update to perform',
              enum: ['attribute', 'skill', 'spell', 'power', 'gear', 'cyberware', 'contact', 'karma', 'initiate', 'damage', 'modifier'],
            },
            update_data: {
              type: 'object',
              description: 'Update-specific data (structure varies by update_type)',
            },
            karma_cost: {
              type: 'number',
              description: 'Override auto-calculated karma cost (optional)',
            },
            use_house_rules: {
              type: 'boolean',
              description: 'Apply house rule modifications (default true)',
            },
            reason: {
              type: 'string',
              description: 'Reason for this change (for audit trail)',
            },
            gm_override: {
              type: 'boolean',
              description: 'Bypass validation rules (GM only, default false)',
            },
            session_date: {
              type: 'string',
              description: 'When this change occurred (ISO date, optional)',
            },
          },
          required: ['character_id', 'update_type', 'update_data'],
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'query_shadowrun') {
      const { query, limit, ranking_criteria } = args;
      
      if (!query) {
        throw new Error('Query parameter is required');
      }

      const result = await queryShadowrun(query, limit, ranking_criteria);
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } else if (name === 'roll_dice') {
      const result = await callDiceAPI('roll', { notation: args.notation });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_multiple_dice') {
      const result = await callDiceAPI('roll_multiple', { notations: args.notations });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_with_advantage') {
      const result = await callDiceAPI('roll_advantage', { notation: args.notation });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_with_disadvantage') {
      const result = await callDiceAPI('roll_disadvantage', { notation: args.notation });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_with_target_number') {
      const result = await callDiceAPI('roll_tn', {
        notation: args.notation,
        tn: args.target_number,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_opposed') {
      const result = await callDiceAPI('roll_opposed', {
        notation1: args.notation1,
        tn1: args.target_number1,
        notation2: args.notation2,
        tn2: args.target_number2,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_initiative') {
      const result = await callDiceAPI('roll_initiative', { notation: args.notation });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'track_initiative') {
      const result = await callDiceAPIPOST('track_initiative', {
        characters: args.characters,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_with_pools') {
      const result = await callDiceAPIPOST('roll_with_pools', {
        pools: args.pools,
        target_number: args.target_number,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'roll_opposed_pools') {
      const result = await callDiceAPIPOST('roll_opposed_pools', {
        side1: {
          pools: args.side1_pools,
          target_number: args.side1_target_number,
          label: args.side1_label || 'Side 1',
        },
        side2: {
          pools: args.side2_pools,
          target_number: args.side2_target_number,
          label: args.side2_label || 'Side 2',
        },
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'reroll_failures') {
      const result = await callDiceAPIPOST('reroll_failures', {
        failed_dice: args.failed_dice,
        target_number: args.target_number,
        sides: args.sides || 6,
        exploding: args.exploding !== false,
        reroll_iteration: args.reroll_iteration,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'avoid_disaster') {
      const result = await callDiceAPIPOST('avoid_disaster', {
        roll_result: args.roll_result,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'buy_karma_dice') {
      const result = await callDiceAPI('buy_karma_dice', {
        karma_dice_count: args.karma_dice_count,
        target_number: args.target_number,
        sides: args.sides || 6,
        exploding: args.exploding !== false,
        max_allowed: args.max_allowed,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'buy_successes') {
      const result = await callDiceAPI('buy_successes', {
        current_successes: args.current_successes,
        successes_to_buy: args.successes_to_buy,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    } else if (name === 'lookup_gear') {
      const result = await lookupGear(args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'compare_gear') {
      const result = await compareGear(args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'get_gear_details') {
      const result = await getGearDetails(args.gear_id, args.include_chunks !== false);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'manage_campaigns') {
      const result = await manageCampaigns(args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'manage_house_rules') {
      const result = await manageHouseRules(args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'create_character') {
      const result = await createCharacter(pool, args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'get_character') {
      const result = await getCharacter(pool, args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else if (name === 'update_character') {
      const result = await updateCharacter(pool, args);
      return {
        content: [{ type: 'text', text: result }],
      };
    } else {
      throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Start the server
 */
async function main() {
  // Test database connection
  try {
    await pool.query('SELECT NOW()');
    console.error('Database connection successful');
  } catch (error) {
    console.error('Database connection failed:', error.message);
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Shadowrun GM Unified MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
