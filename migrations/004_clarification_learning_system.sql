-- Migration: Clarification and Learning System
-- Description: Add tables for interactive clarification and pattern learning
-- Version: 004
-- Date: 2025-01-17

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

-- Helper function to normalize queries
CREATE OR REPLACE FUNCTION normalize_query(query_text TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN LOWER(TRIM(REGEXP_REPLACE(query_text, '\s+', ' ', 'g')));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Helper function to extract keywords from query
CREATE OR REPLACE FUNCTION extract_keywords(query_text TEXT)
RETURNS TEXT[] AS $$
DECLARE
  words TEXT[];
  word TEXT;
  keywords TEXT[] := '{}';
  stop_words TEXT[] := ARRAY['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'];
BEGIN
  -- Split into words
  words := REGEXP_SPLIT_TO_ARRAY(LOWER(query_text), '\s+');
  
  -- Filter out stop words and short words
  FOREACH word IN ARRAY words
  LOOP
    IF LENGTH(word) > 3 AND NOT (word = ANY(stop_words)) THEN
      keywords := array_append(keywords, word);
    END IF;
  END LOOP;
  
  RETURN keywords;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger to auto-update normalized_query
CREATE OR REPLACE FUNCTION update_normalized_query()
RETURNS TRIGGER AS $$
BEGIN
  NEW.normalized_query := normalize_query(NEW.query_text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_normalize_query
  BEFORE INSERT OR UPDATE ON query_attempts
  FOR EACH ROW
  EXECUTE FUNCTION update_normalized_query();

-- Trigger to auto-update success_rate in learned_patterns
CREATE OR REPLACE FUNCTION update_pattern_success_rate()
RETURNS TRIGGER AS $$
BEGIN
  IF (NEW.success_count + NEW.failure_count) > 0 THEN
    -- Store as decimal 0.00-1.00 (not percentage)
    NEW.success_rate := ROUND(NEW.success_count::DECIMAL / (NEW.success_count + NEW.failure_count), 4);
  ELSE
    NEW.success_rate := NULL;
  END IF;
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_success_rate
  BEFORE INSERT OR UPDATE ON learned_patterns
  FOR EACH ROW
  EXECUTE FUNCTION update_pattern_success_rate();

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON query_attempts TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON clarification_interactions TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON learned_patterns TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON pattern_performance TO your_app_user;
-- GRANT SELECT ON pattern_analytics TO your_app_user;

-- Insert some initial seed patterns (optional)
-- These can be removed or customized based on your needs
INSERT INTO learned_patterns (pattern_text, pattern_type, intent, confidence, is_verified, verified_by, example_queries)
VALUES 
  ('how does .* work', 'regex', 'RULES_QUESTION', 0.85, true, 'system', ARRAY['how does initiative work', 'how does magic work']),
  ('what is .* spell', 'regex', 'SPELL_LOOKUP', 0.90, true, 'system', ARRAY['what is the fireball spell', 'what is manaball spell']),
  ('list all .*', 'regex', 'LIST_QUERY', 0.90, true, 'system', ARRAY['list all spells', 'list all weapons']),
  ('compare .* and .*', 'regex', 'GEAR_COMPARISON', 0.90, true, 'system', ARRAY['compare ares predator and colt manhunter']),
  ('best .* for .*', 'regex', 'GEAR_COMPARISON', 0.85, true, 'system', ARRAY['best pistol for damage', 'best armor for stealth'])
ON CONFLICT (pattern_text, intent, pattern_type) DO NOTHING;

COMMENT ON TABLE query_attempts IS 'Stores all query classification attempts for learning and analytics';
COMMENT ON TABLE clarification_interactions IS 'Tracks user interactions when clarification is needed';
COMMENT ON TABLE learned_patterns IS 'Patterns learned from user feedback to improve classification';
COMMENT ON TABLE pattern_performance IS 'Daily performance metrics for learned patterns';
COMMENT ON VIEW pattern_analytics IS 'Aggregated analytics for pattern effectiveness';
