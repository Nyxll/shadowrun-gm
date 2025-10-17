/**
 * Keyword Analyzer - Stage 2 of Intent Classification
 * Uses keyword dictionaries to classify queries based on word presence
 * Fast (~50ms), free, ~75% coverage when pattern matching fails
 */

class KeywordAnalyzer {
  constructor() {
    this.keywords = {
      // Spell-related keywords
      SPELL_LOOKUP: {
        primary: ['spell', 'magic', 'mana', 'drain', 'force', 'sorcery'],
        secondary: ['cast', 'sustain', 'ritual', 'hermetic', 'shamanic'],
        categories: ['combat', 'detection', 'health', 'illusion', 'manipulation'],
        items: ['fireball', 'manaball', 'stunball', 'powerball', 'heal', 'armor', 'invisibility', 'levitate'],
        weight: 1.0,
      },
      
      // Power-related keywords
      POWER_LOOKUP: {
        primary: ['power', 'adept', 'critter', 'ability'],
        secondary: ['improved', 'enhanced', 'mystic', 'killing', 'pain', 'combat sense'],
        items: ['reflexes', 'perception', 'armor', 'hands'],
        weight: 1.0,
      },
      
      // Totem-related keywords
      TOTEM_LOOKUP: {
        primary: ['totem', 'shaman', 'spirit', 'shamanic'],
        secondary: ['advantage', 'disadvantage', 'environment'],
        items: ['bear', 'wolf', 'eagle', 'raven', 'snake', 'cat', 'dog', 'lion', 'owl', 'coyote'],
        weight: 1.0,
      },
      
      // Gear-related keywords
      GEAR_LOOKUP: {
        primary: ['weapon', 'armor', 'gun', 'pistol', 'rifle', 'shotgun', 'smg', 'cyberware', 'bioware'],
        secondary: ['damage', 'ammo', 'conceal', 'essence', 'ballistic', 'impact', 'mode'],
        items: ['ares', 'predator', 'colt', 'manhunter', 'beretta', 'ruger', 'uzi', 'ak-97', 'remington'],
        weight: 0.9,
      },
      
      // Comparison keywords
      GEAR_COMPARISON: {
        primary: ['compare', 'better', 'best', 'top', 'rank', 'versus', 'vs'],
        secondary: ['damage', 'cost', 'rating', 'which', 'choose'],
        weight: 1.0,
      },
      
      // Rules keywords
      RULES_QUESTION: {
        primary: ['how', 'why', 'when', 'explain', 'rules', 'mechanics', 'work'],
        secondary: ['calculate', 'determine', 'resolve', 'process'],
        topics: ['initiative', 'combat', 'damage', 'healing', 'hacking', 'rigging', 'astral'],
        weight: 0.8,
      },
      
      // List query keywords
      LIST_QUERY: {
        primary: ['list', 'show', 'all', 'what', 'available'],
        secondary: ['there', 'exist', 'options', 'choices'],
        weight: 0.7,
      },
    };
  }
  
  /**
   * Analyze query using keyword matching
   * @param {string} query - User query
   * @returns {Object|null} Analysis result with intent, confidence, scores
   */
  analyze(query) {
    if (!query || typeof query !== 'string') {
      return null;
    }
    
    const queryLower = query.toLowerCase();
    const words = queryLower.split(/\s+/);
    const scores = {};
    
    for (const [intent, config] of Object.entries(this.keywords)) {
      let score = 0;
      
      // Primary keywords (high weight)
      for (const keyword of config.primary) {
        if (queryLower.includes(keyword)) {
          score += 2.0;
        }
      }
      
      // Secondary keywords (medium weight)
      for (const keyword of config.secondary) {
        if (queryLower.includes(keyword)) {
          score += 0.5;
        }
      }
      
      // Category/topic keywords (medium weight)
      if (config.categories) {
        for (const category of config.categories) {
          if (queryLower.includes(category)) {
            score += 1.0;
          }
        }
      }
      
      if (config.topics) {
        for (const topic of config.topics) {
          if (queryLower.includes(topic)) {
            score += 1.0;
          }
        }
      }
      
      // Specific item names (high weight)
      if (config.items) {
        for (const item of config.items) {
          if (queryLower.includes(item)) {
            score += 1.5;
          }
        }
      }
      
      scores[intent] = score * config.weight;
    }
    
    // Find highest score
    const maxIntent = Object.keys(scores).reduce((a, b) =>
      scores[a] > scores[b] ? a : b
    );
    
    const maxScore = scores[maxIntent];
    
    // Normalize confidence (score of 3.0 = 100% confidence)
    const confidence = Math.min(maxScore / 3.0, 1.0);
    
    // Only return if confidence is above threshold
    if (confidence > 0.6) {
      return {
        intent: maxIntent,
        confidence,
        method: 'keyword',
        scores,
        query: query.trim(),
      };
    }
    
    return null;
  }
  
  /**
   * Extract potential item name from query
   * @param {string} query - User query
   * @returns {string|null} Extracted item name
   */
  extractItemName(query) {
    // Remove common question words and verbs
    const cleaned = query
      .replace(/^(what|show|list|get|find|tell|give)\s+(me|us|about)?\s*/i, '')
      .replace(/^(is|are|the)\s+/i, '')
      .replace(/\?+$/, '')
      .trim();
    
    // Take last 2-4 words as potential item name
    const words = cleaned.split(/\s+/);
    if (words.length <= 4) {
      return cleaned;
    }
    
    return words.slice(-3).join(' ');
  }
  
  /**
   * Get statistics about keyword coverage
   * @returns {Object} Keyword statistics
   */
  getStats() {
    const stats = {};
    for (const [intent, config] of Object.entries(this.keywords)) {
      stats[intent] = {
        primary: config.primary.length,
        secondary: config.secondary.length,
        categories: config.categories?.length || 0,
        topics: config.topics?.length || 0,
        items: config.items?.length || 0,
        weight: config.weight,
      };
    }
    return {
      total_intents: Object.keys(this.keywords).length,
      by_intent: stats,
    };
  }
}

export { KeywordAnalyzer };
