-- Migration: Enhance query_logs for Training Data
-- Description: Add columns to support training data, GM responses, and dice rolls
-- Version: 005
-- Date: 2025-10-17

-- Add training-specific columns to existing query_logs table
ALTER TABLE query_logs 
ADD COLUMN IF NOT EXISTS is_training_data BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS expected_intent VARCHAR(50),
ADD COLUMN IF NOT EXISTS gm_response TEXT,
ADD COLUMN IF NOT EXISTS dice_rolls JSONB,
ADD COLUMN IF NOT EXISTS confidence DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS classification_method VARCHAR(20),
ADD COLUMN IF NOT EXISTS training_source VARCHAR(100);

-- Add computed column for correctness (PostgreSQL compatible)
ALTER TABLE query_logs 
ADD COLUMN IF NOT EXISTS is_correct BOOLEAN;

-- Create function to update is_correct
CREATE OR REPLACE FUNCTION update_query_correctness()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.expected_intent IS NOT NULL THEN
    NEW.is_correct := (NEW.expected_intent = NEW.intent);
  ELSE
    NEW.is_correct := NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update is_correct
DROP TRIGGER IF EXISTS trigger_update_query_correctness ON query_logs;
CREATE TRIGGER trigger_update_query_correctness
  BEFORE INSERT OR UPDATE ON query_logs
  FOR EACH ROW
  EXECUTE FUNCTION update_query_correctness();

-- Indexes for training queries
CREATE INDEX IF NOT EXISTS idx_query_logs_training 
  ON query_logs(is_training_data) 
  WHERE is_training_data = TRUE;

CREATE INDEX IF NOT EXISTS idx_query_logs_correct 
  ON query_logs(is_correct) 
  WHERE is_correct IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_query_logs_expected_intent 
  ON query_logs(expected_intent) 
  WHERE expected_intent IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_query_logs_classification_method 
  ON query_logs(classification_method) 
  WHERE classification_method IS NOT NULL;

-- Training analytics view
CREATE OR REPLACE VIEW training_analytics AS
SELECT 
  expected_intent,
  intent as detected_intent,
  COUNT(*) as total_queries,
  SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_count,
  SUM(CASE WHEN NOT is_correct THEN 1 ELSE 0 END) as incorrect_count,
  ROUND(100.0 * SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as accuracy_pct,
  ROUND(AVG(confidence), 3) as avg_confidence,
  classification_method,
  training_source
FROM query_logs
WHERE is_training_data = TRUE
GROUP BY expected_intent, intent, classification_method, training_source
ORDER BY total_queries DESC;

-- View for misclassified training queries
CREATE OR REPLACE VIEW training_errors AS
SELECT 
  id,
  timestamp,
  query_text,
  expected_intent,
  intent as detected_intent,
  confidence,
  classification_method,
  classification
FROM query_logs
WHERE is_training_data = TRUE 
  AND is_correct = FALSE
ORDER BY timestamp DESC;

-- View for training progress
CREATE OR REPLACE VIEW training_progress AS
SELECT 
  training_source,
  COUNT(*) as total_queries,
  SUM(CASE WHEN gm_response IS NOT NULL THEN 1 ELSE 0 END) as processed_queries,
  SUM(CASE WHEN gm_response IS NULL THEN 1 ELSE 0 END) as pending_queries,
  ROUND(100.0 * SUM(CASE WHEN gm_response IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as completion_pct
FROM query_logs
WHERE is_training_data = TRUE
GROUP BY training_source;

-- View for intent distribution
CREATE OR REPLACE VIEW training_intent_distribution AS
SELECT 
  expected_intent,
  COUNT(*) as query_count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM query_logs WHERE is_training_data = TRUE), 2) as percentage,
  SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
  ROUND(100.0 * SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as accuracy_pct
FROM query_logs
WHERE is_training_data = TRUE
GROUP BY expected_intent
ORDER BY query_count DESC;

COMMENT ON COLUMN query_logs.is_training_data IS 'Flag indicating this is training data, not a real user query';
COMMENT ON COLUMN query_logs.expected_intent IS 'The correct intent for training data (ground truth)';
COMMENT ON COLUMN query_logs.gm_response IS 'The GM response text for this query';
COMMENT ON COLUMN query_logs.dice_rolls IS 'JSON array of dice roll specifications required for this query';
COMMENT ON COLUMN query_logs.confidence IS 'Classification confidence score (0.00-1.00)';
COMMENT ON COLUMN query_logs.classification_method IS 'Method used: pattern, keyword, embedding, llm';
COMMENT ON COLUMN query_logs.training_source IS 'Source of training data (e.g., gm-train.txt)';
COMMENT ON COLUMN query_logs.is_correct IS 'Auto-computed: does detected intent match expected intent?';

COMMENT ON VIEW training_analytics IS 'Aggregated training accuracy metrics by intent and method';
COMMENT ON VIEW training_errors IS 'Misclassified training queries for review';
COMMENT ON VIEW training_progress IS 'Training data processing progress by source';
COMMENT ON VIEW training_intent_distribution IS 'Distribution of intents in training data';
