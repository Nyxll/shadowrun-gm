# Interactive Clarification & Learning System - Complete Design

## 🎯 System Overview

A comprehensive system that:
1. Asks users for clarification when uncertain
2. Logs all interactions for learning
3. Automatically improves patterns from user feedback
4. Provides multi-turn conversation support

## 📊 Database Schema

### Core Tables

```sql
-- Store all query attempts with classification results
CREATE TABLE IF NOT EXISTS query_attempts (
  id SERIAL PRIMARY KEY,
  session_id UUID,
  query_text TEXT NOT NULL,
  normalized_query TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  
  -- Classification results
  intent_detected VARCHAR(50),
  confidence DECIMAL(3,2),
  classification_method VARCHAR(20), -- 'pattern', 'keyword', 'llm', 'clarified', 'learned'
  
  -- Alternatives considered
  alternatives JSONB,
  
  -- User interaction
  needed_clarification BOOLEAN DEFAULT FALSE,
  clarification_shown JSONB,
  user_response TEXT,
  final_intent VARCHAR(50),
  
  -- Context
  previous_query_id INTEGER REFERENCES query_attempts(id),
  conversation_turn INTEGER DEFAULT 1,
  
  -- Metadata
  user_agent TEXT,
  execution_time_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_qa_query_text ON query_attempts(query_text);
CREATE INDEX IF NOT EXISTS idx_qa_normalized ON query_attempts(normalized_query);
CREATE INDEX IF NOT EXISTS idx_qa_intent ON query_attempts(intent_detected);
CREATE INDEX IF NOT EXISTS idx_qa_confidence ON query_attempts(confidence);
CREATE INDEX IF NOT EXISTS idx_qa_timestamp ON query_attempts(timestamp);
CREATE INDEX IF NOT EXISTS idx_qa_session ON query_attempts(session_id);

-- Store clarification interactions
CREATE TABLE IF NOT EXISTS clarification_interactions (
  id SERIAL PRIMARY KEY,
  query_attempt_id INTEGER REFERENCES query_attempts(id) ON DELETE CASCADE,
  timestamp TIMESTAMP DEFAULT NOW(),
  
  -- What we asked
  clarification_type VARCHAR(50), -- 'multiple_choice', 'rephrase', 'disambiguation'
  options_presented JSONB,
  
  -- What user chose
  user_selection INTEGER,
  user_text_response TEXT,
  
  -- Outcome
  resolved_intent VARCHAR(50),
  was_helpful BOOLEAN DEFAULT TRUE,
  resolution_time_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_ci_query_attempt ON clarification_interactions(query_attempt_id);
CREATE INDEX IF NOT EXISTS idx_ci_type ON clarification_interactions(clarification_type);
CREATE INDEX IF NOT EXISTS idx_ci_resolved ON clarification_interactions(resolved_intent);

-- Store learned patterns from user feedback
CREATE TABLE IF NOT EXISTS learned_patterns (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Pattern details
  pattern_text TEXT NOT NULL,
  pattern_type VARCHAR(20), -- 'regex', 'keyword', 'phrase', 'entity'
  intent VARCHAR(50) NOT NULL,
  confidence DECIMAL(3,2) DEFAULT 0.75,
  
  -- Learning metadata
  learned_from_query_ids INTEGER[],
  occurrence_count INTEGER DEFAULT 1,
  success_count INTEGER DEFAULT 0,
  failure_count INTEGER DEFAULT 0,
  success_rate DECIMAL(3,2),
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  verified_by VARCHAR(100),
  verified_at TIMESTAMP,
  
  -- Examples
  example_queries TEXT[],
  
  UNIQUE(pattern_text, intent, pattern_type)
);

CREATE INDEX IF NOT EXISTS idx_lp_intent ON learned_patterns(intent);
CREATE INDEX IF NOT EXISTS idx_lp_type ON learned_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_lp_active ON learned_patterns(is_active);
CREATE INDEX IF NOT EXISTS idx_lp_success_rate ON learned_patterns(success_rate);

-- Track pattern performance over time
CREATE TABLE IF NOT EXISTS pattern_performance (
  id SERIAL PRIMARY KEY,
  pattern_id INTEGER REFERENCES learned_patterns(id) ON DELETE CASCADE,
  date DATE DEFAULT CURRENT_DATE,
  
  -- Metrics
  times_matched INTEGER DEFAULT 0,
  times_correct INTEGER DEFAULT 0,
  times_incorrect INTEGER DEFAULT 0,
  avg_confidence DECIMAL(3,2),
  
  -- User feedback
  positive_feedback INTEGER DEFAULT 0,
  negative_feedback INTEGER DEFAULT 0,
  
  UNIQUE(pattern_id, date)
);

CREATE INDEX IF NOT EXISTS idx_pp_pattern ON pattern_performance(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pp_date ON pattern_performance(date);

-- Analytics view for pattern effectiveness
CREATE OR REPLACE VIEW pattern_analytics AS
SELECT 
  lp.id,
  lp.pattern_text,
  lp.pattern_type,
  lp.intent,
  lp.confidence,
  lp.occurrence_count,
  lp.success_rate,
  lp.is_active,
  lp.is_verified,
  COUNT(DISTINCT pp.date) as days_active,
  SUM(pp.times_matched) as total_matches,
  SUM(pp.times_correct) as total_correct,
  SUM(pp.times_incorrect) as total_incorrect,
  CASE 
    WHEN SUM(pp.times_matched) > 0 
    THEN ROUND(SUM(pp.times_correct)::DECIMAL / SUM(pp.times_matched) * 100, 2)
    ELSE 0 
  END as actual_accuracy
FROM learned_patterns lp
LEFT JOIN pattern_performance pp ON lp.id = pp.pattern_id
GROUP BY lp.id, lp.pattern_text, lp.pattern_type, lp.intent, 
         lp.confidence, lp.occurrence_count, lp.success_rate, 
         lp.is_active, lp.is_verified;
```

## 🏗️ System Architecture

### Component Hierarchy

```
EnhancedIntentClassifier (orchestrator)
├── LearnedPatternMatcher (highest priority)
├── PatternMatcher (static patterns)
├── KeywordAnalyzer (keyword scoring)
├── ClarificationEngine (generates clarifications)
├── LearningEngine (learns from feedback)
└── LLM Fallback (last resort)
```

### Classification Flow

```
Query Input
    ↓
Normalize Query
    ↓
Try Learned Patterns (confidence >= 0.85)
    ↓ [no match]
Try Static Patterns (confidence >= 0.90)
    ↓ [no match]
Try Keyword Analysis (confidence >= 0.75)
    ↓ [low confidence 0.50-0.74]
Generate Clarification Request
    ↓
Return to User with Options
    ↓
User Selects Option
    ↓
Log Interaction
    ↓
Learn New Patterns
    ↓
Execute Query with Resolved Intent
```

## 🔧 Implementation Components

### 1. Clarification Engine

**Purpose**: Generate user-friendly clarification requests

**Features**:
- Multiple choice options
- Entity disambiguation
- Rephrase suggestions
- Context-aware messaging

**Output Format**:
```json
{
  "needs_clarification": true,
  "clarification": {
    "type": "multiple_choice",
    "message": "I'm not sure what you're asking about. Please choose:",
    "options": [
      {
        "id": 1,
        "intent": "SPELL_LOOKUP",
        "label": "🔮 Spell Information",
        "description": "Get details about a specific spell",
        "example": "e.g., 'What is the Fireball spell?'",
        "confidence": 0.65
      },
      {
        "id": 2,
        "intent": "RULES_QUESTION",
        "label": "📖 Game Rules",
        "description": "Understand game mechanics",
        "example": "e.g., 'How does spellcasting work?'",
        "confidence": 0.55
      }
    ],
    "allow_rephrase": true,
    "rephrase_prompt": "Or rephrase your question to be more specific"
  }
}
```

### 2. Learning Engine

**Purpose**: Extract patterns from user feedback and improve classification

**Learning Strategies**:

1. **Phrase Extraction**: Extract 2-3 word phrases from resolved queries
2. **Keyword Identification**: Identify significant words (length > 3, not stop words)
3. **Entity Recognition**: Learn entity→intent mappings
4. **Pattern Validation**: Track success rate, deactivate poor performers

**Learning Triggers**:
- User selects clarification option
- User provides feedback on results
- Admin manually verifies patterns

**Pattern Confidence Calculation**:
```javascript
confidence = base_confidence * (success_rate / 100) * min(occurrence_count / 10, 1.0)
```

### 3. Learned Pattern Matcher

**Purpose**: Apply patterns learned from user interactions

**Matching Logic**:
1. Check exact phrase matches (highest priority)
2. Check keyword matches (medium priority)
3. Check entity matches (context-dependent)
4. Combine scores from multiple pattern matches

**Performance Tracking**:
- Log every match attempt
- Track correct vs incorrect classifications
- Calculate daily success rates
- Auto-deactivate patterns with <50% success rate

### 4. Session Management

**Purpose**: Track multi-turn conversations

**Features**:
- Session ID generation (UUID)
- Conversation context preservation
- Previous query reference
- Turn counting

## 📈 Analytics & Monitoring

### Key Metrics

1. **Classification Accuracy**
   - Overall accuracy by method
   - Accuracy by intent type
   - Confidence calibration

2. **Clarification Effectiveness**
   - Clarification request rate
   - Resolution success rate
   - Average turns to resolution

3. **Learning Performance**
   - Patterns learned per day
   - Pattern success rates
   - Coverage improvement over time

4. **User Experience**
   - Average query resolution time
   - Clarification satisfaction
   - Rephrase frequency

### Analytics Queries

```sql
-- Daily classification method breakdown
SELECT 
  DATE(timestamp) as date,
  classification_method,
  COUNT(*) as count,
  AVG(confidence) as avg_confidence,
  COUNT(CASE WHEN needed_clarification THEN 1 END) as clarifications_needed
FROM query_attempts
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp), classification_method
ORDER BY date DESC, count DESC;

-- Most common ambiguous queries
SELECT 
  normalized_query,
  COUNT(*) as occurrences,
  COUNT(DISTINCT final_intent) as different_intents,
  ARRAY_AGG(DISTINCT final_intent) as intents_resolved_to
FROM query_attempts
WHERE needed_clarification = true
GROUP BY normalized_query
HAVING COUNT(*) > 1
ORDER BY occurrences DESC
LIMIT 20;

-- Pattern learning effectiveness
SELECT 
  lp.pattern_text,
  lp.intent,
  lp.occurrence_count,
  lp.success_rate,
  pa.actual_accuracy,
  pa.total_matches,
  lp.is_verified
FROM learned_patterns lp
JOIN pattern_analytics pa ON lp.id = pa.id
WHERE lp.is_active = true
ORDER BY pa.actual_accuracy DESC, pa.total_matches DESC
LIMIT 50;

-- Clarification resolution time
SELECT 
  ci.clarification_type,
  COUNT(*) as total_clarifications,
  AVG(ci.resolution_time_ms) as avg_resolution_ms,
  COUNT(CASE WHEN ci.was_helpful THEN 1 END) as successful,
  ROUND(COUNT(CASE WHEN ci.was_helpful THEN 1 END)::DECIMAL / COUNT(*) * 100, 2) as success_rate
FROM clarification_interactions ci
GROUP BY ci.clarification_type
ORDER BY total_clarifications DESC;
```

## 🚀 Deployment Strategy

### Phase 1: Database Setup
1. Create tables and indexes
2. Create analytics views
3. Set up monitoring queries

### Phase 2: Core Implementation
1. Implement ClarificationEngine
2. Implement LearningEngine
3. Implement LearnedPatternMatcher
4. Integrate with EnhancedIntentClassifier

### Phase 3: Testing
1. Unit tests for each component
2. Integration tests for full flow
3. Load testing for performance
4. A/B testing vs current system

### Phase 4: Gradual Rollout
1. Enable for 10% of queries (shadow mode)
2. Monitor metrics and adjust
3. Increase to 50% of queries
4. Full rollout with monitoring

## 🎯 Success Criteria

### Immediate (Week 1)
- ✅ Database schema deployed
- ✅ Core components implemented
- ✅ Basic clarification working
- ✅ Logging all interactions

### Short Term (Month 1)
- ✅ 100+ learned patterns
- ✅ 90%+ clarification resolution rate
- ✅ 5% reduction in LLM calls
- ✅ Analytics dashboard functional

### Long Term (Quarter 1)
- ✅ 500+ verified patterns
- ✅ 95%+ overall accuracy
- ✅ 20% reduction in LLM calls
- ✅ Auto-learning fully automated

## 🔮 Future Enhancements

1. **Active Learning**: Proactively ask users to verify uncertain classifications
2. **Collaborative Filtering**: Learn from similar users' query patterns
3. **Semantic Clustering**: Group similar queries for batch learning
4. **Confidence Calibration**: Auto-adjust confidence thresholds based on accuracy
5. **Multi-language Support**: Learn patterns in different languages
6. **Voice Query Support**: Handle spoken queries with clarification
7. **Contextual Memory**: Remember user preferences across sessions
8. **Federated Learning**: Share learned patterns across deployments (privacy-preserving)

## 📝 Implementation Checklist

- [ ] Create database schema
- [ ] Implement ClarificationEngine class
- [ ] Implement LearningEngine class
- [ ] Implement LearnedPatternMatcher class
- [ ] Enhance IntentClassifier with clarification support
- [ ] Add session management
- [ ] Create analytics queries
- [ ] Build admin dashboard for pattern verification
- [ ] Write comprehensive tests
- [ ] Deploy and monitor
