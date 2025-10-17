# Intent Classification Accuracy Improvement Analysis

## Current State: 84% Accuracy (84/100 tests passed)

### Failed Test Cases Analysis (16 failures)

#### Category 1: Ambiguous "Available/Exist" Queries (3 failures)
1. **"what spells are available?"** - Expected: SPELL_LOOKUP, Got: LIST_QUERY
2. **"what sniper rifles exist?"** - Expected: LIST_QUERY, Got: no match
3. **"list cyberware"** - Expected: LIST_QUERY, Got: no match

**Root Cause**: Pattern matcher treats "available" as LIST_QUERY trigger, but test expects SPELL_LOOKUP. The word "exist" and bare "list X" aren't caught.

**Solution**: 
- Add context-aware logic: "what X are available?" should check if X is a category (spells, powers) vs subcategory (heavy pistols)
- Add pattern: `list (cyberware|bioware|armor|vehicles)` → LIST_QUERY
- Add pattern: `what .* (exist|available)` → LIST_QUERY

#### Category 2: Generic Gear Terms (5 failures)
1. **"armor jacket stats"** - Expected: GEAR_LOOKUP, Got: SPELL_LOOKUP (false positive on "armor spell")
2. **"smartlink info"** - Expected: GEAR_LOOKUP, Got: no match
3. **"datajack details"** - Expected: GEAR_LOOKUP, Got: no match
4. **"wired reflexes stats"** - Expected: GEAR_LOOKUP, Got: no match
5. **"weapon stats"** - Expected: GEAR_LOOKUP, Got: no match

**Root Cause**: Missing cyberware/gear item names in patterns. "armor" triggers spell pattern incorrectly.

**Solution**:
- Add cyberware dictionary: smartlink, datajack, wired reflexes, cybereyes, cyberears, etc.
- Add pattern: `(smartlink|datajack|wired reflexes|cyberdeck|chipjack) (info|details|stats)` → GEAR_LOOKUP
- Fix "armor" pattern to require "spell" after it: `armor spell` not just `armor`
- Add generic: `(weapon|armor|cyberware|gear) (stats|info|details)` → GEAR_LOOKUP

#### Category 3: Single-Word Edge Cases (2 failures)
1. **"Bear"** - Expected: TOTEM_LOOKUP, Got: no match
2. **"predator"** - Expected: GEAR_LOOKUP, Got: no match

**Root Cause**: Single-word queries need entity recognition. "Bear" could be totem or animal. "Predator" could be weapon or movie.

**Solution**:
- Create entity dictionary with confidence scores:
  - "Bear" → 90% TOTEM_LOOKUP (it's a common totem)
  - "Predator" → 85% GEAR_LOOKUP (Ares Predator is iconic weapon)
  - "Fireball" → 95% SPELL_LOOKUP (already works)
- Add single-word pattern matching with entity lookup

#### Category 4: "Show All" Pattern (1 failure)
1. **"show all shotguns"** - Expected: LIST_QUERY, Got: GEAR_LOOKUP

**Root Cause**: "show" pattern matches GEAR_LOOKUP before LIST_QUERY check.

**Solution**:
- Pattern priority: "show all X" should match LIST_QUERY before "show X"
- Add explicit pattern: `show all (.*?)` → LIST_QUERY (higher priority)

#### Category 5: Comparison Ambiguity (1 failure)
1. **"compare Ares Predator and Colt Manhunter"** - Expected: GEAR_COMPARISON, Got: GEAR_LOOKUP

**Root Cause**: "compare X and Y" pattern exists but "Ares Predator" triggers GEAR_LOOKUP first.

**Solution**:
- Check for "compare" keyword BEFORE checking for specific item names
- Pattern priority: comparison patterns should run before lookup patterns

#### Category 6: Rules vs Magic Confusion (3 failures)
1. **"what are the rules for magic?"** - Expected: RULES_QUESTION, Got: GEAR_LOOKUP
2. **"when do I use karma?"** - Expected: RULES_QUESTION, Got: no match
3. **"magic rules"** - Expected: RULES_QUESTION, Got: SPELL_LOOKUP
4. **"spell drain mechanics"** - Expected: RULES_QUESTION, Got: SPELL_LOOKUP

**Root Cause**: "magic" and "spell" keywords trigger SPELL_LOOKUP even when asking about rules/mechanics.

**Solution**:
- Add context detection: "rules for X" → RULES_QUESTION (regardless of X)
- Add pattern: `(when|why|where) (do I|should I|can I) (use|spend|get) (karma|essence|nuyen)` → RULES_QUESTION
- Add pattern: `(.*) (rules|mechanics|system)` → RULES_QUESTION
- Priority: "X rules" or "X mechanics" should be RULES_QUESTION before SPELL_LOOKUP

## Improvement Strategy: Path to 95%+ Accuracy

### Phase 1: Quick Wins (Expected: +8% accuracy, 92% total)

#### 1.1 Fix Pattern Priority Issues
- Move comparison patterns before lookup patterns
- Move "show all" before "show"
- Move "X rules/mechanics" before spell/power keywords

#### 1.2 Add Missing Cyberware/Gear Entities
```javascript
const CYBERWARE_ITEMS = [
  'smartlink', 'datajack', 'wired reflexes', 'cybereyes', 'cyberears',
  'chipjack', 'skillwires', 'cyberdeck', 'dermal plating', 'bone lacing',
  'muscle replacement', 'reflex recorder', 'smartgun link'
];

const COMMON_GEAR = [
  'armor jacket', 'lined coat', 'helmet', 'riot shield',
  'medkit', 'trauma patch', 'stim patch', 'antidote patch'
];
```

#### 1.3 Add Context-Aware Rules Detection
```javascript
// Pattern: "X rules" or "X mechanics" → RULES_QUESTION
if (/\b(rules|mechanics|system|how does)\b/i.test(query)) {
  return { intent: 'RULES_QUESTION', confidence: 0.85 };
}
```

### Phase 2: Entity Recognition (Expected: +3% accuracy, 95% total)

#### 2.1 Build Entity Dictionary
```javascript
const ENTITY_DICTIONARY = {
  // Totems (high confidence)
  'bear': { intent: 'TOTEM_LOOKUP', confidence: 0.90 },
  'wolf': { intent: 'TOTEM_LOOKUP', confidence: 0.90 },
  'eagle': { intent: 'TOTEM_LOOKUP', confidence: 0.90 },
  'raven': { intent: 'TOTEM_LOOKUP', confidence: 0.90 },
  'cat': { intent: 'TOTEM_LOOKUP', confidence: 0.85 },
  'snake': { intent: 'TOTEM_LOOKUP', confidence: 0.85 },
  
  // Iconic weapons (high confidence)
  'predator': { intent: 'GEAR_LOOKUP', confidence: 0.85 },
  'manhunter': { intent: 'GEAR_LOOKUP', confidence: 0.90 },
  'panther': { intent: 'GEAR_LOOKUP', confidence: 0.80 },
  'vindicator': { intent: 'GEAR_LOOKUP', confidence: 0.85 },
  
  // Spells (very high confidence)
  'fireball': { intent: 'SPELL_LOOKUP', confidence: 0.95 },
  'manaball': { intent: 'SPELL_LOOKUP', confidence: 0.95 },
  'heal': { intent: 'SPELL_LOOKUP', confidence: 0.85 },
  'invisibility': { intent: 'SPELL_LOOKUP', confidence: 0.90 },
  
  // Powers (high confidence)
  'improved reflexes': { intent: 'POWER_LOOKUP', confidence: 0.95 },
  'killing hands': { intent: 'POWER_LOOKUP', confidence: 0.90 },
  'mystic armor': { intent: 'POWER_LOOKUP', confidence: 0.90 },
};
```

#### 2.2 Single-Word Query Handler
```javascript
// For single-word queries, check entity dictionary
if (words.length === 1) {
  const entity = ENTITY_DICTIONARY[query.toLowerCase()];
  if (entity) {
    return entity;
  }
}
```

### Phase 3: Advanced Context Analysis (Expected: +2% accuracy, 97% total)

#### 3.1 Multi-Word Context Windows
```javascript
// Check 2-3 word combinations for context
const trigrams = extractTrigrams(query);
for (const trigram of trigrams) {
  if (trigram.includes('rules') || trigram.includes('mechanics')) {
    return { intent: 'RULES_QUESTION', confidence: 0.85 };
  }
  if (trigram.includes('compare') || trigram.includes('vs')) {
    return { intent: 'GEAR_COMPARISON', confidence: 0.85 };
  }
}
```

#### 3.2 Negation Detection
```javascript
// "not a spell" should not trigger SPELL_LOOKUP
if (/\b(not|isn't|aren't|doesn't)\s+\w+\s+(spell|power|totem)/i.test(query)) {
  // Skip spell/power/totem patterns
}
```

#### 3.3 Question Type Analysis
```javascript
const QUESTION_TYPES = {
  'what is': 'lookup',      // "what is X?" → lookup
  'what are': 'list',       // "what are X?" → list
  'how does': 'rules',      // "how does X work?" → rules
  'how to': 'rules',        // "how to do X?" → rules
  'when do': 'rules',       // "when do I X?" → rules
  'why': 'rules',           // "why X?" → rules
  'compare': 'comparison',  // "compare X" → comparison
  'which': 'comparison',    // "which X is better?" → comparison
};
```

### Phase 4: Machine Learning Enhancement (Expected: +1-2% accuracy, 98-99% total)

#### 4.1 Query Log Analysis
- Collect real production queries
- Analyze patterns in misclassified queries
- Auto-generate new patterns from common failures

#### 4.2 TF-IDF Scoring
```javascript
// Calculate term importance across intent types
const tfidf = calculateTFIDF(query, intentExamples);
const scores = {};
for (const intent of INTENT_TYPES) {
  scores[intent] = tfidf.score(query, intent);
}
return maxIntent(scores);
```

#### 4.3 Embedding Similarity (Optional)
- Pre-compute embeddings for example queries
- Compare new query embedding to examples
- Use cosine similarity for classification
- Fallback to LLM only if similarity < 0.7

## Implementation Priority

### Immediate (This Session)
1. ✅ Fix pattern priority (comparison before lookup)
2. ✅ Add cyberware/gear entity lists
3. ✅ Add "X rules/mechanics" pattern
4. ✅ Fix "show all" vs "show" priority
5. ✅ Add entity dictionary for single-word queries

### Short Term (Next Session)
1. Add context-aware "available/exist" handling
2. Implement question type analysis
3. Add negation detection
4. Expand entity dictionary to 100+ items

### Medium Term (Future Enhancement)
1. Implement TF-IDF scoring
2. Add query log analysis
3. Build auto-pattern generator
4. A/B test against LLM-only baseline

### Long Term (Advanced)
1. Train lightweight ML model on query logs
2. Implement embedding similarity
3. Add active learning (learn from corrections)
4. Build confidence calibration system

## Expected Results

| Phase | Changes | Expected Accuracy | Time to Implement |
|-------|---------|------------------|-------------------|
| Current | Baseline | 84% | - |
| Phase 1 | Quick wins | 92% | 30 minutes |
| Phase 2 | Entity recognition | 95% | 1 hour |
| Phase 3 | Context analysis | 97% | 2 hours |
| Phase 4 | ML enhancement | 98-99% | 4-8 hours |

## Success Metrics

### Target: 95% Accuracy
- **Achievable**: Yes, with Phase 1 + Phase 2
- **Time Required**: ~1.5 hours
- **Complexity**: Low-Medium
- **Risk**: Low (backward compatible)

### Stretch Goal: 98% Accuracy
- **Achievable**: Yes, with all phases
- **Time Required**: ~8 hours
- **Complexity**: Medium-High
- **Risk**: Medium (requires testing)

## Recommendation

**Implement Phase 1 immediately** to reach 92% accuracy with minimal effort. This fixes the low-hanging fruit and provides immediate value.

**Then implement Phase 2** to reach 95% accuracy target. This adds entity recognition which is straightforward and high-impact.

**Phase 3 and 4 can wait** for future iterations based on production usage patterns and actual user queries.

## Next Steps

1. Implement Phase 1 fixes (30 min)
2. Run tests → expect 92% accuracy
3. Implement Phase 2 entity recognition (1 hour)
4. Run tests → expect 95% accuracy
5. Commit and document improvements
6. Monitor production usage for further optimization opportunities
