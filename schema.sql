-- Shadowrun GM Database Schema
-- Phase 1: Rules System

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

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

-- Indexes for performance
-- Vector similarity search index (using ivfflat for approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS rules_content_embedding_idx ON rules_content 
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Full-text search index
CREATE INDEX IF NOT EXISTS rules_content_fts_idx ON rules_content 
  USING GIN(to_tsvector('english', title || ' ' || content));

-- Category filtering
CREATE INDEX IF NOT EXISTS rules_content_category_idx ON rules_content(category);
CREATE INDEX IF NOT EXISTS rules_content_subcategory_idx ON rules_content(subcategory);

-- Tag search
CREATE INDEX IF NOT EXISTS rules_content_tags_idx ON rules_content USING GIN(tags);

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rules_content_updated_at BEFORE UPDATE ON rules_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing (optional - can be removed after testing)
-- INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
-- ('Initiative', 'Initiative determines the order in which characters act during a Combat Turn...', 'combat', 'initiative', ARRAY['initiative', 'combat', 'reaction']);
