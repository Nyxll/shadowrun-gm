-- Shadowrun GM Database Schema - Enhanced
-- Includes: Rules, Clarifications, and Comprehensive Logging

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Rules content table
CREATE TABLE IF NOT EXISTS rules_content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Content
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  
  -- Classification
  category TEXT NOT NULL, -- 'combat', 'magic', 'matrix', 'character_creation', 'skills', 'gear_mechanics', 'general'
  subcategory TEXT, -- 'initiative', 'damage', 'spellcasting', 'target_numbers', etc.
  
  -- Source tracking
  source_file TEXT, -- e.g., 'core-fundamentals.ocr.txt'
  source_book TEXT, -- 'Shadowrun 2nd Edition Core'
  
  -- Search optimization
  tags TEXT[], -- ['initiative', 'combat_pool', 'reaction']
  
  -- Vector embedding for semantic search (OpenAI text-embedding-3-small = 1536 dimensions)
  embedding vector(1536),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CLARIFICATIONS & ERRATA
-- ============================================================================

-- Rule clarifications, errata, and house rules
CREATE TABLE IF NOT EXISTS rule_clarifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Link to original rule (optional - can be general clarification)
  rule_id UUID REFERENCES rules_content(id) ON DELETE CASCADE,
  
  -- Clarification details
  clarification_type TEXT NOT NULL, -- 'errata', 'limitation', 'clarification', 'house_rule', 'faq'
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  
  -- Source and authority
  source TEXT NOT NULL, -- 'official', 'community', 'gm', 'faq'
  source_reference TEXT, -- URL, book page, forum post, etc.
  
  -- Priority (higher = more important to show)
  priority INTEGER DEFAULT 0,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- LOGGING TABLES
-- ============================================================================

-- Query analytics logging
CREATE TABLE IF NOT EXISTS query_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Query details
  query_text TEXT NOT NULL,
  query_type TEXT, -- 'simple', 'multi-topic', 'category', 'advanced'
  category_filter TEXT,
  
  -- Results
  results_count INTEGER,
  execution_time_ms INTEGER,
  search_rank_scores JSONB, -- Store relevance scores for analysis
  
  -- Session tracking
  user_session_id TEXT,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Clarification usage logging
CREATE TABLE IF NOT EXISTS clarification_usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  clarification_id UUID REFERENCES rule_clarifications(id) ON DELETE CASCADE,
  rule_id UUID REFERENCES rules_content(id) ON DELETE CASCADE,
  
  -- Context
  query_context TEXT,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Chunking quality metrics
CREATE TABLE IF NOT EXISTS chunking_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Source
  source_file TEXT NOT NULL,
  chunk_id UUID,
  
  -- Metrics
  chunk_size INTEGER,
  ai_confidence_score FLOAT,
  category TEXT,
  subcategory TEXT,
  processing_time_ms INTEGER,
  ai_model_used TEXT,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Embedding performance logging
CREATE TABLE IF NOT EXISTS embedding_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Operation
  operation_type TEXT NOT NULL, -- 'generate', 'search'
  content_length INTEGER,
  embedding_model TEXT,
  
  -- Performance
  generation_time_ms INTEGER,
  api_cost DECIMAL(10,4), -- Track API costs
  
  -- Error tracking
  error_message TEXT,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Error and exception logging
CREATE TABLE IF NOT EXISTS error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Error details
  error_type TEXT NOT NULL, -- 'database', 'api', 'validation', 'network', etc.
  error_message TEXT NOT NULL,
  stack_trace TEXT,
  
  -- Context
  context JSONB, -- Request details, user input, etc.
  
  -- Severity
  severity TEXT NOT NULL, -- 'info', 'warning', 'error', 'critical'
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Operation
  operation TEXT NOT NULL, -- 'query', 'insert', 'update', 'delete', etc.
  
  -- Timing
  duration_ms INTEGER,
  database_time_ms INTEGER,
  api_time_ms INTEGER,
  
  -- Resources
  memory_usage_mb INTEGER,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Data quality logs
CREATE TABLE IF NOT EXISTS data_quality_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Check details
  check_type TEXT NOT NULL, -- 'duplicate', 'missing_embedding', 'invalid_category', etc.
  affected_records INTEGER,
  details JSONB,
  
  -- Resolution
  auto_fixed BOOLEAN DEFAULT false,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Rules content indexes
CREATE INDEX IF NOT EXISTS rules_content_embedding_idx ON rules_content 
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX IF NOT EXISTS rules_content_fts_idx ON rules_content 
  USING GIN(to_tsvector('english', title || ' ' || content));

CREATE INDEX IF NOT EXISTS rules_content_category_idx ON rules_content(category);
CREATE INDEX IF NOT EXISTS rules_content_subcategory_idx ON rules_content(subcategory);
CREATE INDEX IF NOT EXISTS rules_content_tags_idx ON rules_content USING GIN(tags);

-- Clarifications indexes
CREATE INDEX IF NOT EXISTS clarifications_rule_id_idx ON rule_clarifications(rule_id);
CREATE INDEX IF NOT EXISTS clarifications_type_idx ON rule_clarifications(clarification_type);
CREATE INDEX IF NOT EXISTS clarifications_active_idx ON rule_clarifications(is_active);
CREATE INDEX IF NOT EXISTS clarifications_priority_idx ON rule_clarifications(priority DESC);

-- Logging indexes (for analytics queries)
CREATE INDEX IF NOT EXISTS query_logs_timestamp_idx ON query_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS query_logs_query_type_idx ON query_logs(query_type);
CREATE INDEX IF NOT EXISTS query_logs_results_count_idx ON query_logs(results_count);

CREATE INDEX IF NOT EXISTS clarification_usage_timestamp_idx ON clarification_usage_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS clarification_usage_clarification_idx ON clarification_usage_logs(clarification_id);

CREATE INDEX IF NOT EXISTS chunking_metrics_timestamp_idx ON chunking_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS chunking_metrics_source_idx ON chunking_metrics(source_file);

CREATE INDEX IF NOT EXISTS embedding_logs_timestamp_idx ON embedding_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS embedding_logs_operation_idx ON embedding_logs(operation_type);

CREATE INDEX IF NOT EXISTS error_logs_timestamp_idx ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS error_logs_severity_idx ON error_logs(severity);
CREATE INDEX IF NOT EXISTS error_logs_type_idx ON error_logs(error_type);

CREATE INDEX IF NOT EXISTS performance_metrics_timestamp_idx ON performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS performance_metrics_operation_idx ON performance_metrics(operation);

CREATE INDEX IF NOT EXISTS data_quality_timestamp_idx ON data_quality_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS data_quality_check_type_idx ON data_quality_logs(check_type);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at
CREATE TRIGGER update_rules_content_updated_at 
  BEFORE UPDATE ON rules_content
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clarifications_updated_at 
  BEFORE UPDATE ON rule_clarifications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Most common queries
CREATE OR REPLACE VIEW v_common_queries AS
SELECT 
  query_text,
  COUNT(*) as query_count,
  AVG(results_count) as avg_results,
  AVG(execution_time_ms) as avg_execution_time_ms
FROM query_logs
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY query_text
ORDER BY query_count DESC
LIMIT 100;

-- Zero-result queries (indicates missing content)
CREATE OR REPLACE VIEW v_zero_result_queries AS
SELECT 
  query_text,
  COUNT(*) as occurrence_count,
  MAX(timestamp) as last_occurrence
FROM query_logs
WHERE results_count = 0
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY query_text
ORDER BY occurrence_count DESC;

-- Slow queries
CREATE OR REPLACE VIEW v_slow_queries AS
SELECT 
  query_text,
  execution_time_ms,
  results_count,
  timestamp
FROM query_logs
WHERE execution_time_ms > 1000 -- Queries taking more than 1 second
  AND timestamp > NOW() - INTERVAL '7 days'
ORDER BY execution_time_ms DESC;

-- Most used clarifications
CREATE OR REPLACE VIEW v_popular_clarifications AS
SELECT 
  c.id,
  c.title,
  c.clarification_type,
  COUNT(u.id) as usage_count,
  MAX(u.timestamp) as last_used
FROM rule_clarifications c
LEFT JOIN clarification_usage_logs u ON c.id = u.clarification_id
WHERE c.is_active = true
GROUP BY c.id, c.title, c.clarification_type
ORDER BY usage_count DESC;

-- Recent errors
CREATE OR REPLACE VIEW v_recent_errors AS
SELECT 
  error_type,
  severity,
  error_message,
  timestamp
FROM error_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- API cost summary
CREATE OR REPLACE VIEW v_api_costs AS
SELECT 
  DATE(timestamp) as date,
  embedding_model,
  COUNT(*) as operations,
  SUM(api_cost) as total_cost,
  AVG(generation_time_ms) as avg_time_ms
FROM embedding_logs
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp), embedding_model
ORDER BY date DESC;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE rules_content IS 'Core rules content with vector embeddings for semantic search';
COMMENT ON TABLE rule_clarifications IS 'Errata, clarifications, limitations, and house rules';
COMMENT ON TABLE query_logs IS 'Analytics for user queries and search performance';
COMMENT ON TABLE clarification_usage_logs IS 'Track which clarifications are most referenced';
COMMENT ON TABLE chunking_metrics IS 'Quality metrics for AI chunking and categorization';
COMMENT ON TABLE embedding_logs IS 'Performance and cost tracking for embedding generation';
COMMENT ON TABLE error_logs IS 'Error and exception tracking for debugging';
COMMENT ON TABLE performance_metrics IS 'System performance monitoring';
COMMENT ON TABLE data_quality_logs IS 'Data quality checks and validation results';
