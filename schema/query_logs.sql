-- Query Logging System
-- Tracks all queries to help tune the AI classification and improve results

-- Drop existing table if it exists
DROP TABLE IF EXISTS query_logs CASCADE;

CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Query details
    query_text TEXT NOT NULL,
    query_limit INTEGER,
    ranking_criteria TEXT,
    
    -- AI Classification results
    classification JSONB,
    intent TEXT,
    data_sources TEXT[],
    tables_queried TEXT[],
    
    -- Query execution
    execution_time_ms INTEGER,
    result_count INTEGER,
    error_message TEXT,
    
    -- Result quality (can be updated later for feedback)
    user_feedback TEXT, -- 'good', 'bad', 'needs_improvement'
    feedback_notes TEXT,
    
    -- Metadata
    session_id TEXT,
    user_agent TEXT
);

-- Indexes for common queries (created after table)
CREATE INDEX IF NOT EXISTS idx_query_logs_timestamp ON query_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_intent ON query_logs(intent) WHERE intent IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_query_logs_feedback ON query_logs(user_feedback) WHERE user_feedback IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_query_logs_error ON query_logs(error_message) WHERE error_message IS NOT NULL;

-- View for query analytics
CREATE OR REPLACE VIEW query_analytics AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    intent,
    COUNT(*) as query_count,
    AVG(execution_time_ms) as avg_execution_time,
    AVG(result_count) as avg_results,
    COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as error_count,
    COUNT(CASE WHEN user_feedback = 'good' THEN 1 END) as good_feedback,
    COUNT(CASE WHEN user_feedback = 'bad' THEN 1 END) as bad_feedback
FROM query_logs
GROUP BY DATE_TRUNC('day', timestamp), intent
ORDER BY date DESC, query_count DESC;

-- View for most common queries
CREATE OR REPLACE VIEW common_queries AS
SELECT 
    query_text,
    COUNT(*) as frequency,
    intent,
    AVG(result_count) as avg_results,
    MAX(timestamp) as last_queried
FROM query_logs
GROUP BY query_text, intent
ORDER BY frequency DESC
LIMIT 100;

-- View for problematic queries (errors or bad feedback)
CREATE OR REPLACE VIEW problematic_queries AS
SELECT 
    id,
    timestamp,
    query_text,
    intent,
    classification,
    error_message,
    user_feedback,
    feedback_notes
FROM query_logs
WHERE error_message IS NOT NULL 
   OR user_feedback = 'bad'
ORDER BY timestamp DESC;

COMMENT ON TABLE query_logs IS 'Logs all queries to track usage patterns and improve AI classification';
COMMENT ON COLUMN query_logs.classification IS 'Full JSON classification result from AI';
COMMENT ON COLUMN query_logs.user_feedback IS 'User feedback on result quality: good, bad, needs_improvement';
