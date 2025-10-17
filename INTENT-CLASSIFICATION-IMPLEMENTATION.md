# Intent Classification System - Implementation Strategy

## 🧠 Ultra-Deep Analysis

### Current State Assessment

**Existing System (server-unified.js)**:
- Uses `classifyQueryEnhanced()` - single LLM call to OpenAI GPT-4o-mini
- Returns complex classification object with intent, data_sources, tables, etc.
- **Cost**: ~$0.0001 per query (400 tokens @ $0.15/1M input)
- **Latency**: ~500-1500ms per query
- **Accuracy**: ~85% (relies entirely on LLM understanding)
- **Problem**: Every query requires expensive LLM call

**Target System (Multi-Stage Pipeline)**:
- Stage 1: Pattern Matching (regex) - 100ms, free
- Stage 2: Keyword Analysis (dictionary) - 50ms, free  
- Stage 3: Embedding Similarity (optional) - 200ms, ~$0.00002
- Stage 4: LLM Fallback (current system) - 1000ms, $0.0001
- **Expected**: 90% of queries resolved in <200ms at near-zero cost

### Architecture Decision: Incremental Refactor

**Strategy**: Don't replace, augment and measure

```javascript
// Phase 1: Add pattern/keyword stages BEFORE LLM
async function classifyQuery(query) {
  // NEW: Try pattern matching first
  const patternResult = patternMatcher.match(query);
  if (patternResult && patternResult.confidence > 0.85) {
    return convertToClassification(patternResult);
  }
  
  // NEW: Try keyword analysis
  const keywordResult = keywordAnalyzer.analyze(query);
  if (keywordResult && keywordResult.confidence > 0.75) {
    return convertToClassification(keywordResult);
  }
  
  // EXISTING: Fall back to LLM (current system)
  return await classifyQueryEnhanced(query);
}
```

**Benefits**:
1. Zero risk - existing system still works
2. Measurable improvement - track which stage is used
3. Gradual rollout - can disable stages if issues arise
4. A/B testing - compare accuracy of each stage

## 📐 Detailed Design

### Stage 1: Pattern Matcher

**File**: `lib/intent/pattern-matcher.js`

**Core Insight**: Most queries follow predictable patterns

```javascript
class PatternMatcher {
  constructor() {
    this.patterns = {
      // GEAR_LOOKUP patterns
      GEAR_LOOKUP: [
        // "show me X", "what is X", "stats for X"
        /\b(show|display|get|find)\b.*\b(me|us)\b.*?([A-Z][a-zA-Z\s]+)/i,
        /^what\s+(is|are)\s+(?:the\s+)?(.+?)\??$/i,
        /\b(stats?|info|details?)\b.*\b(for|on|about)\b\s+(.+)/i,
        /^look\s*up\s+(.+)/i,
      ],
      
      // GEAR_COMPARISON patterns
      GEAR_COMPARISON: [
        // "compare X and Y", "X vs Y", "best X"
        /\bcompare\b.*?\b(and|vs|versus)\b/i,
        /\b(better|best|top|rank)\b.*?\b(for|by)\b/i,
        /^rank\s+(.+?)\s+by\s+(.+)/i,
      ],
      
      // RULES_QUESTION patterns
      RULES_QUESTION: [
        // "how does X work", "explain X", "what are the rules for X"
        /^how\s+(does|do|did)\s+(.+?)\s+work/i,
        /^explain\s+(.+)/i,
        /\brules?\b.*\b(for|about|on)\b/i,
        /^what\s+are\s+the\s+rules/i,
      ],
      
      // SPELL_LOOKUP patterns (specific to spells)
      SPELL_LOOKUP: [
        /\b(fireball|manaball|stunball|powerball)\b/i,
        /\b(spell|magic|mana|drain)\b.*\b(stats?|info|details?)\b/i,
        /^list\s+(all\s+)?.*?\bspells?\b/i,
      ],
      
      // POWER_LOOKUP patterns (adept powers)
      POWER_LOOKUP: [
        /\b(adept|critter)\s+powers?\b/i,
        /\bimproved\s+(reflexes|ability|sense)\b/i,
        /^list\s+(all\s+)?.*?\bpowers?\b/i,
      ],
      
      // TOTEM_LOOKUP patterns
      TOTEM_LOOKUP: [
        /\b(bear|wolf|eagle|raven|snake|cat)\s+totem\b/i,
        /^list\s+(all\s+)?.*?\btotems?\b/i,
        /\bshamanic?\b.*\btotems?\b/i,
      ],
    };
  }
  
  match(query) {
    for (const [intent, patterns] of Object.entries(this.patterns)) {
      for (const pattern of patterns) {
        const match = query.match(pattern);
        if (match) {
          return {
            intent,
            confidence: 0.9,
            method: 'pattern',
            matches: match.slice(1).filter(Boolean),
            pattern: pattern.source,
          };
        }
      }
    }
    return null;
  }
}
```

**Conversion to Classification Format**:

```javascript
function convertPatternToClassification(patternResult) {
  const { intent, matches } = patternResult;
  
  // Map simplified intents to full classification
  const intentMap = {
    GEAR_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['gear'],
      item_name: matches[0] || null,
    },
    SPELL_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['spells'],
      item_name: matches[0] || null,
    },
    POWER_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['powers'],
      item_name: matches[0] || null,
    },
    TOTEM_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['totems'],
      item_name: matches[0] || null,
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
      search_terms: matches,
      chunk_categories: ['general'],
    },
  };
  
  return {
    ...intentMap[intent],
    classification_method: 'pattern',
    confidence: patternResult.confidence,
  };
}
```

### Stage 2: Keyword Analyzer

**File**: `lib/intent/keyword-analyzer.js`

**Core Insight**: Keywords reveal intent even without perfect grammar

```javascript
class KeywordAnalyzer {
  constructor() {
    this.keywords = {
      // Spell-related keywords
      SPELL_LOOKUP: {
        primary: ['spell', 'magic', 'mana', 'drain', 'force'],
        secondary: ['cast', 'sustain', 'ritual', 'sorcery'],
        categories: ['combat', 'detection', 'health', 'illusion', 'manipulation'],
        weight: 1.0,
      },
      
      // Power-related keywords
      POWER_LOOKUP: {
        primary: ['power', 'adept', 'critter', 'ability'],
        secondary: ['improved', 'enhanced', 'mystic'],
        weight: 1.0,
      },
      
      // Totem-related keywords
      TOTEM_LOOKUP: {
        primary: ['totem', 'shaman', 'spirit'],
        secondary: ['bear', 'wolf', 'eagle', 'raven', 'advantage', 'disadvantage'],
        weight: 1.0,
      },
      
      // Gear-related keywords
      GEAR_LOOKUP: {
        primary: ['weapon', 'armor', 'gun', 'pistol', 'rifle', 'cyberware'],
        secondary: ['damage', 'ammo', 'conceal', 'essence', 'cost'],
        weight: 0.9,
      },
      
      // Comparison keywords
      GEAR_COMPARISON: {
        primary: ['compare', 'better', 'best', 'rank', 'top', 'versus', 'vs'],
        secondary: ['damage', 'cost', 'rating'],
        weight: 1.0,
      },
      
      // Rules keywords
      RULES_QUESTION: {
        primary: ['how', 'why', 'when', 'explain', 'rules', 'mechanics'],
        secondary: ['work', 'calculate', 'determine', 'resolve'],
        weight: 0.8,
      },
    };
  }
  
  analyze(query) {
    const queryLower = query.toLowerCase();
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
      
      // Category keywords (for spells)
      if (config.categories) {
        for (const category of config.categories) {
          if (queryLower.includes(category)) {
            score += 1.0;
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
    const confidence = Math.min(maxScore / 3.0, 1.0);
    
    if (confidence > 0.6) {
      return {
        intent: maxIntent,
        confidence,
        method: 'keyword',
        scores,
      };
    }
    
    return null;
  }
}
```

### Integration Point: Unified Classifier

**File**: `lib/intent/intent-classifier.js`

```javascript
import { PatternMatcher } from './pattern-matcher.js';
import { KeywordAnalyzer } from './keyword-analyzer.js';

class IntentClassifier {
  constructor(openaiClient) {
    this.patternMatcher = new PatternMatcher();
    this.keywordAnalyzer = new KeywordAnalyzer();
    this.openaiClient = openaiClient;
    
    this.stats = {
      pattern: 0,
      keyword: 0,
      llm: 0,
      total: 0,
    };
  }
  
  async classify(query) {
    this.stats.total++;
    const startTime = Date.now();
    
    // Stage 1: Pattern matching (fastest, free)
    const patternResult = this.patternMatcher.match(query);
    if (patternResult && patternResult.confidence > 0.85) {
      this.stats.pattern++;
      const classification = convertPatternToClassification(patternResult);
      classification.time_ms = Date.now() - startTime;
      classification.method = 'pattern';
      return classification;
    }
    
    // Stage 2: Keyword analysis (fast, free)
    const keywordResult = this.keywordAnalyzer.analyze(query);
    if (keywordResult && keywordResult.confidence > 0.75) {
      this.stats.keyword++;
      const classification = convertKeywordToClassification(keywordResult, query);
      classification.time_ms = Date.now() - startTime;
      classification.method = 'keyword';
      return classification;
    }
    
    // Stage 3: LLM classification (slow, costs money)
    this.stats.llm++;
    const classification = await this.classifyWithLLM(query);
    classification.time_ms = Date.now() - startTime;
    classification.method = 'llm';
    return classification;
  }
  
  async classifyWithLLM(query) {
    // Use existing classifyQueryEnhanced function
    return await classifyQueryEnhanced(query);
  }
  
  getStats() {
    const { pattern, keyword, llm, total } = this.stats;
    return {
      total,
      pattern: { count: pattern, percent: ((pattern / total) * 100).toFixed(1) },
      keyword: { count: keyword, percent: ((keyword / total) * 100).toFixed(1) },
      llm: { count: llm, percent: ((llm / total) * 100).toFixed(1) },
      cost_savings: {
        // Assuming $0.0001 per LLM call
        saved: ((pattern + keyword) * 0.0001).toFixed(4),
        spent: (llm * 0.0001).toFixed(4),
      },
    };
  }
}

// Conversion functions
function convertPatternToClassification(patternResult) {
  // Implementation from above
}

function convertKeywordToClassification(keywordResult, query) {
  const { intent } = keywordResult;
  
  // Extract item name from query if lookup
  let item_name = null;
  if (intent.includes('LOOKUP')) {
    // Simple extraction: take last 2-3 words
    const words = query.split(/\s+/);
    item_name = words.slice(-2).join(' ');
  }
  
  const intentMap = {
    SPELL_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['spells'],
      item_name,
    },
    POWER_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['powers'],
      item_name,
    },
    TOTEM_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['totems'],
      item_name,
    },
    GEAR_LOOKUP: {
      intent: 'lookup',
      data_sources: ['structured'],
      tables: ['gear'],
      item_name,
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
  };
  
  return {
    ...intentMap[intent],
    classification_method: 'keyword',
    confidence: keywordResult.confidence,
  };
}

export { IntentClassifier };
```

## 📊 Implementation Plan

### Phase 1: Foundation (Day 1)

**Goal**: Create pattern matcher and keyword analyzer

**Tasks**:
1. Create `lib/intent/` directory
2. Implement `pattern-matcher.js` with 20+ patterns
3. Implement `keyword-analyzer.js` with keyword dictionaries
4.
