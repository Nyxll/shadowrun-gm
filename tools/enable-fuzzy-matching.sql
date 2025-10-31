-- Enable pg_trgm extension for fuzzy text matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify it's enabled
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';
