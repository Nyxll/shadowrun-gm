/**
 * Intent Classifier - Unified Multi-Stage Classification System
 * Orchestrates pattern matching, keyword analysis, and LLM fallback
 * Optimizes for speed and cost while maintaining accuracy
 */

import { PatternMatcher } from './pattern-matcher.js';
import { KeywordAnalyzer } from './keyword-analyzer.js';

class IntentClassifier {
  constructor(llmClassifierFunc = null) {
    this.patternMatcher = new PatternMatcher();
    this.keywordAnalyzer = new KeywordAnalyzer();
    this.llmClassifier = llmClassifierFunc; // Function to call LLM (injected)
    
    this.stats = {
      pattern: 0,
      keyword: 0,
      llm: 0,
      total: 0,
      errors: 0,
    };
    
    this.enabled = {
      pattern: true,
      keyword: true,
      llm: true,
    };
  }
  
  /**
   * Classify query using multi-stage pipeline
   * @param {string} query - User query
   * @returns {Promise<Object>} Classification result
   */
  async classify(query) {
    this.stats.total++;
    const startTime = Date.now();
    
    try {
      // Stage 1: Pattern matching (fastest, free, ~60% coverage)
      if (this.enabled.pattern) {
        const patternResult = this.patternMatcher.match(query);
        if (patternResult && patternResult.confidence > 0.85) {
          this.stats.pattern++;
          const classification = this.convertPatternToClassification(patternResult);
          classification.time_ms = Date.now() - startTime;
          classification.method = 'pattern';
          return classification;
        }
      }
      
      // Stage 2: Keyword analysis (fast, free, ~75% coverage)
      if (this.enabled.keyword) {
        const keywordResult = this.keywordAnalyzer.analyze(query);
        if (keywordResult && keywordResult.confidence > 0.75) {
          this.stats.keyword++;
          const classification = this.convertKeywordToClassification(keywordResult);
          classification.time_ms = Date.now() - startTime;
          classification.method = 'keyword';
          return classification;
        }
      }
      
      // Stage 3: LLM classification (slow, costs money, 100% coverage)
      if (this.enabled.llm && this.llmClassifier) {
        this.stats.llm++;
        const classification = await this.llmClassifier(query);
        classification.time_ms = Date.now() - startTime;
        classification.method = classification.method || 'llm';
        return classification;
      }
      
      // Fallback if LLM disabled or not available
      throw new Error('Unable to classify query: all classification methods failed or disabled');
      
    } catch (error) {
      this.stats.errors++;
      console.error('Classification error:', error);
      
      // Return a safe fallback classification
      return {
        intent: 'rules',
        data_sources: ['chunks'],
        tables: [],
        search_terms: [query],
        chunk_categories: ['general'],
        method: 'fallback',
        confidence: 0.5,
        time_ms: Date.now() - startTime,
        error: error.message,
      };
    }
  }
  
  /**
   * Convert pattern match result to full classification format
   * @param {Object} patternResult - Result from pattern matcher
   * @returns {Object} Full classification object
   */
  convertPatternToClassification(patternResult) {
    const { intent, matches, confidence } = patternResult;
    
    // Map simplified intents to full classification format
    const intentMap = {
      SPELL_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['spells'],
        item_name: matches[0] || null,
        item_type: 'spell',
      },
      POWER_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['powers'],
        item_name: matches[0] || null,
        item_type: 'power',
      },
      TOTEM_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['totems'],
        item_name: matches[0] || null,
        item_type: 'totem',
      },
      GEAR_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['gear'],
        item_name: matches[0] || null,
        item_type: 'weapon',
      },
      GEAR_COMPARISON: {
        intent: 'compare',
        data_sources: ['structured'],
        tables: ['gear'],
        sort_by: matches[1] || 'damage',
        category_filter: matches[0] || null,
      },
      RULES_QUESTION: {
        intent: 'rules',
        data_sources: ['chunks'],
        tables: [],
        search_terms: matches.filter(Boolean),
        chunk_categories: ['general'],
      },
      LIST_QUERY: {
        intent: 'list',
        data_sources: ['structured'],
        tables: this.inferTableFromListQuery(matches[0]),
        category_filter: matches[0] || null,
      },
    };
    
    const baseClassification = intentMap[intent] || {
      intent: 'rules',
      data_sources: ['chunks'],
      tables: [],
      search_terms: matches,
    };
    
    return {
      ...baseClassification,
      confidence,
      classification_method: 'pattern',
      pattern_matched: patternResult.pattern,
    };
  }
  
  /**
   * Convert keyword analysis result to full classification format
   * @param {Object} keywordResult - Result from keyword analyzer
   * @returns {Object} Full classification object
   */
  convertKeywordToClassification(keywordResult) {
    const { intent, confidence, query } = keywordResult;
    
    // Extract potential item name
    const itemName = this.keywordAnalyzer.extractItemName(query);
    
    const intentMap = {
      SPELL_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['spells'],
        item_name: itemName,
        item_type: 'spell',
      },
      POWER_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['powers'],
        item_name: itemName,
        item_type: 'power',
      },
      TOTEM_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['totems'],
        item_name: itemName,
        item_type: 'totem',
      },
      GEAR_LOOKUP: {
        intent: 'lookup',
        data_sources: ['structured'],
        tables: ['gear'],
        item_name: itemName,
        item_type: 'weapon',
      },
      GEAR_COMPARISON: {
        intent: 'compare',
        data_sources: ['structured'],
        tables: ['gear'],
        sort_by: 'damage',
      },
      RULES_QUESTION: {
        intent: 'rules',
        data_sources: ['chunks'],
        tables: [],
        search_terms: [query],
        chunk_categories: ['general'],
      },
      LIST_QUERY: {
        intent: 'list',
        data_sources: ['structured'],
        tables: this.inferTableFromQuery(query),
        search_terms: [query],
      },
    };
    
    const baseClassification = intentMap[intent] || {
      intent: 'rules',
      data_sources: ['chunks'],
      tables: [],
      search_terms: [query],
    };
    
    return {
      ...baseClassification,
      confidence,
      classification_method: 'keyword',
      keyword_scores: keywordResult.scores,
    };
  }
  
  /**
   * Infer which table to query from list query text
   * @param {string} queryText - Query text
   * @returns {Array<string>} Table names
   */
  inferTableFromListQuery(queryText) {
    if (!queryText) return ['gear'];
    
    const text = queryText.toLowerCase();
    if (text.includes('spell')) return ['spells'];
    if (text.includes('power')) return ['powers'];
    if (text.includes('totem')) return ['totems'];
    return ['gear'];
  }
  
  /**
   * Infer which table to query from general query text
   * @param {string} query - Full query
   * @returns {Array<string>} Table names
   */
  inferTableFromQuery(query) {
    const queryLower = query.toLowerCase();
    if (queryLower.includes('spell') || queryLower.includes('magic')) return ['spells'];
    if (queryLower.includes('power') || queryLower.includes('adept')) return ['powers'];
    if (queryLower.includes('totem') || queryLower.includes('shaman')) return ['totems'];
    return ['gear'];
  }
  
  /**
   * Enable or disable specific classification stages
   * @param {string} stage - Stage name ('pattern', 'keyword', 'llm')
   * @param {boolean} enabled - Whether to enable the stage
   */
  setStageEnabled(stage, enabled) {
    if (this.enabled.hasOwnProperty(stage)) {
      this.enabled[stage] = enabled;
    }
  }
  
  /**
   * Get classification statistics
   * @returns {Object} Statistics object
   */
  getStats() {
    const { pattern, keyword, llm, total, errors } = this.stats;
    
    if (total === 0) {
      return {
        total: 0,
        message: 'No queries classified yet',
      };
    }
    
    return {
      total,
      errors,
      breakdown: {
        pattern: {
          count: pattern,
          percent: ((pattern / total) * 100).toFixed(1) + '%',
        },
        keyword: {
          count: keyword,
          percent: ((keyword / total) * 100).toFixed(1) + '%',
        },
        llm: {
          count: llm,
          percent: ((llm / total) * 100).toFixed(1) + '%',
        },
      },
      performance: {
        fast_path: pattern + keyword,
        fast_path_percent: (((pattern + keyword) / total) * 100).toFixed(1) + '%',
        slow_path: llm,
        slow_path_percent: ((llm / total) * 100).toFixed(1) + '%',
      },
      cost_savings: {
        // Assuming $0.0001 per LLM call
        saved_calls: pattern + keyword,
        saved_dollars: ((pattern + keyword) * 0.0001).toFixed(4),
        spent_dollars: (llm * 0.0001).toFixed(4),
      },
    };
  }
  
  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      pattern: 0,
      keyword: 0,
      llm: 0,
      total: 0,
      errors: 0,
    };
  }
}

export { IntentClassifier };
