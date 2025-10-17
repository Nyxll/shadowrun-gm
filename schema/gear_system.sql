-- ============================================
-- SHADOWRUN 2E GEAR SYSTEM SCHEMA
-- ============================================
-- This schema implements a hybrid approach:
-- - Structured data for queryable stats
-- - Links to narrative chunks for context
-- - Deduplication to handle CSV/DAT overlap
-- ============================================

-- ============================================
-- MAIN GEAR TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS gear (
    id SERIAL PRIMARY KEY,
    
    -- Identity
    name TEXT NOT NULL,
    category TEXT NOT NULL,  -- weapon, armor, cyberware, vehicle, bioware, magical, drug, totem, spell, power
    subcategory TEXT,        -- heavy_pistol, light_armor, headware, etc.
    
    -- Core stats (flexible JSONB for different gear types)
    base_stats JSONB NOT NULL DEFAULT '{}',
    -- Examples:
    -- Weapons: {"damage": "9M", "conceal": 5, "ammo": "15(c)", "mode": "SA", "weight": 2.25, "reach": 0}
    -- Armor: {"ballistic": 5, "impact": 3, "conceal": 6}
    -- Cyberware: {"essence": 0.2, "index": 0.9, "surgery_time": "1 hour"}
    -- Vehicles: {"speed": 120, "handling": 3, "armor": 2, "signature": 3}
    -- Spells: {"target": "4", "drain": "M", "type": "Manipulation"}
    -- Powers: {"cost": 2, "type": "Physical"}
    
    -- Modifiers (what this gear does to character stats)
    modifiers JSONB DEFAULT '{}',
    -- Example: {"attributes": {"STR": 2, "BOD": 1}, "skills": {"Firearms": 1}, "initiative": 1}
    
    -- Requirements (what's needed to use this)
    requirements JSONB DEFAULT '{}',
    -- Example: {"min_str": 4, "skill": "Firearms", "essence_available": 0.5, "magic": 6}
    
    -- Searchable tags
    tags TEXT[] DEFAULT '{}',
    -- Example: ['smartlink', 'silenced', 'military', 'rare', 'concealable', 'legal']
    
    -- Text fields
    description TEXT,
    game_notes TEXT,          -- Special rules, usage notes
    source TEXT,              -- Book reference (e.g., "SR2 p.123", "Grimoire p.45")
    
    -- Availability & Cost
    availability TEXT,        -- "4/48hrs", "8/7days", "Always", etc.
    cost INTEGER,
    street_index NUMERIC(3,2),
    legality TEXT,            -- "Legal", "Permit Required", "Illegal", etc.
    
    -- Data Quality & Lineage
    data_source TEXT NOT NULL DEFAULT 'manual',  -- 'csv', 'dat', 'manual'
    source_file TEXT,         -- 'CYBERWARE.csv', 'GEAR.DAT', etc.
    loaded_from TEXT[] DEFAULT '{}',  -- Track all sources if merged
    data_quality INTEGER DEFAULT 5,   -- 1-10 rating (CSV=8, DAT=5, manual=10)
    
    -- Metadata
    is_custom BOOLEAN DEFAULT FALSE,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Full-text search (will be populated by trigger instead of generated column)
    search_vector tsvector
);

-- ============================================
-- GEAR-CHUNK LINKING TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS gear_chunk_links (
    id SERIAL PRIMARY KEY,
    gear_id INTEGER NOT NULL REFERENCES gear(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES rules_content(id) ON DELETE CASCADE,
    link_type TEXT DEFAULT 'description',  -- 'description', 'rules', 'example', 'lore', 'stats'
    confidence NUMERIC(3,2) DEFAULT 1.0,   -- Auto-linking confidence score (0.0-1.0)
    notes TEXT,                            -- Why this link was made
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(gear_id, chunk_id, link_type)
);

-- ============================================
-- AUDIT TRAIL FOR DEDUPLICATION
-- ============================================

CREATE TABLE IF NOT EXISTS gear_load_history (
    id SERIAL PRIMARY KEY,
    gear_id INTEGER REFERENCES gear(id) ON DELETE SET NULL,
    action TEXT NOT NULL,     -- 'insert', 'update', 'merge', 'skip'
    source_file TEXT NOT NULL,
    item_name TEXT NOT NULL,
    item_category TEXT NOT NULL,
    old_data JSONB,           -- Previous state (for updates/merges)
    new_data JSONB,           -- New state
    reason TEXT,              -- Why this action was taken
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_gear_category ON gear(category);
CREATE INDEX IF NOT EXISTS idx_gear_subcategory ON gear(subcategory);
CREATE INDEX IF NOT EXISTS idx_gear_name ON gear(name);
CREATE INDEX IF NOT EXISTS idx_gear_name_lower ON gear(LOWER(name));

-- Deduplication index (prevent exact duplicates)
CREATE UNIQUE INDEX IF NOT EXISTS idx_gear_unique_name_category 
ON gear(LOWER(TRIM(name)), category);

-- JSONB indexes for stat queries
CREATE INDEX IF NOT EXISTS idx_gear_stats ON gear USING GIN(base_stats);
CREATE INDEX IF NOT EXISTS idx_gear_modifiers ON gear USING GIN(modifiers);
CREATE INDEX IF NOT EXISTS idx_gear_requirements ON gear USING GIN(requirements);

-- Array index for tags
CREATE INDEX IF NOT EXISTS idx_gear_tags ON gear USING GIN(tags);

-- Cost and availability
CREATE INDEX IF NOT EXISTS idx_gear_cost ON gear(cost) WHERE cost IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_gear_availability ON gear(availability) WHERE availability IS NOT NULL;

-- Full-text search
CREATE INDEX IF NOT EXISTS idx_gear_search ON gear USING GIN(search_vector);

-- Data quality and source tracking
CREATE INDEX IF NOT EXISTS idx_gear_custom ON gear(is_custom);
CREATE INDEX IF NOT EXISTS idx_gear_data_source ON gear(data_source);
CREATE INDEX IF NOT EXISTS idx_gear_quality ON gear(data_quality);

-- Chunk linking indexes
CREATE INDEX IF NOT EXISTS idx_gear_links_gear ON gear_chunk_links(gear_id);
CREATE INDEX IF NOT EXISTS idx_gear_links_chunk ON gear_chunk_links(chunk_id);
CREATE INDEX IF NOT EXISTS idx_gear_links_type ON gear_chunk_links(link_type);

-- Audit trail indexes
CREATE INDEX IF NOT EXISTS idx_gear_history_gear ON gear_load_history(gear_id);
CREATE INDEX IF NOT EXISTS idx_gear_history_action ON gear_load_history(action);
CREATE INDEX IF NOT EXISTS idx_gear_history_timestamp ON gear_load_history(timestamp);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to search gear by text
CREATE OR REPLACE FUNCTION search_gear(
    search_term TEXT, 
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    category TEXT,
    subcategory TEXT,
    description TEXT,
    cost INTEGER,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.id,
        g.name,
        g.category,
        g.subcategory,
        g.description,
        g.cost,
        ts_rank(g.search_vector, plainto_tsquery('english', search_term)) AS rank
    FROM gear g
    WHERE g.search_vector @@ plainto_tsquery('english', search_term)
    ORDER BY rank DESC, g.name
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to get gear with linked chunks
CREATE OR REPLACE FUNCTION get_gear_with_chunks(gear_id_param INTEGER)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'gear', row_to_json(g.*),
        'chunks', COALESCE(
            (SELECT json_agg(json_build_object(
                'chunk_id', rc.id,
                'content', rc.content,
                'content_type', rc.content_type,
                'link_type', gcl.link_type,
                'confidence', gcl.confidence
            ) ORDER BY gcl.confidence DESC, rc.id)
            FROM gear_chunk_links gcl
            JOIN rules_content rc ON gcl.chunk_id = rc.id
            WHERE gcl.gear_id = g.id),
            '[]'::json
        )
    ) INTO result
    FROM gear g
    WHERE g.id = gear_id_param;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to find similar gear (for deduplication)
CREATE OR REPLACE FUNCTION find_similar_gear(
    item_name TEXT,
    item_category TEXT,
    similarity_threshold REAL DEFAULT 0.7
)
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    category TEXT,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.id,
        g.name,
        g.category,
        similarity(LOWER(g.name), LOWER(item_name)) AS sim
    FROM gear g
    WHERE g.category = item_category
      AND similarity(LOWER(g.name), LOWER(item_name)) >= similarity_threshold
    ORDER BY sim DESC;
END;
$$ LANGUAGE plpgsql;

-- Enable pg_trgm extension for similarity search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: All weapons with key stats
CREATE OR REPLACE VIEW weapons_summary AS
SELECT 
    id,
    name,
    subcategory,
    base_stats->>'damage' as damage,
    (base_stats->>'conceal')::INTEGER as conceal,
    base_stats->>'ammo' as ammo,
    base_stats->>'mode' as mode,
    (base_stats->>'reach')::INTEGER as reach,
    cost,
    availability,
    tags,
    data_quality
FROM gear
WHERE category = 'weapon'
ORDER BY subcategory, name;

-- View: All cyberware with essence cost
CREATE OR REPLACE VIEW cyberware_summary AS
SELECT 
    id,
    name,
    subcategory,
    (base_stats->>'essence')::NUMERIC as essence_cost,
    (base_stats->>'index')::NUMERIC as cyberware_index,
    cost,
    modifiers,
    tags,
    data_quality
FROM gear
WHERE category = 'cyberware'
ORDER BY essence_cost, name;

-- View: All armor
CREATE OR REPLACE VIEW armor_summary AS
SELECT 
    id,
    name,
    subcategory,
    (base_stats->>'ballistic')::INTEGER as ballistic,
    (base_stats->>'impact')::INTEGER as impact,
    (base_stats->>'conceal')::INTEGER as conceal,
    cost,
    availability,
    tags,
    data_quality
FROM gear
WHERE category = 'armor'
ORDER BY ballistic DESC, impact DESC;

-- View: All spells
CREATE OR REPLACE VIEW spells_summary AS
SELECT 
    id,
    name,
    subcategory,
    base_stats->>'type' as spell_type,
    base_stats->>'target' as target_number,
    base_stats->>'drain' as drain,
    description,
    source,
    data_quality
FROM gear
WHERE category = 'spell'
ORDER BY spell_type, name;

-- View: All totems
CREATE OR REPLACE VIEW totems_summary AS
SELECT 
    id,
    name,
    description,
    modifiers,
    requirements,
    tags,
    source,
    data_quality
FROM gear
WHERE category = 'totem'
ORDER BY name;

-- View: Deduplication report
CREATE OR REPLACE VIEW gear_dedup_report AS
SELECT 
    g.name,
    g.category,
    g.data_source,
    g.source_file,
    array_to_string(g.loaded_from, ', ') as all_sources,
    g.data_quality,
    COUNT(glh.id) as load_events,
    MAX(glh.timestamp) as last_updated
FROM gear g
LEFT JOIN gear_load_history glh ON g.id = glh.gear_id
GROUP BY g.id, g.name, g.category, g.data_source, g.source_file, g.loaded_from, g.data_quality
HAVING COUNT(glh.id) > 1  -- Items loaded multiple times
ORDER BY load_events DESC, g.name;

-- ============================================
-- TRIGGERS
-- ============================================

-- Update timestamp on modification
CREATE OR REPLACE FUNCTION update_gear_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER gear_update_timestamp
    BEFORE UPDATE ON gear
    FOR EACH ROW
    EXECUTE FUNCTION update_gear_timestamp();

-- Update search vector on insert/update
CREATE OR REPLACE FUNCTION update_gear_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        coalesce(NEW.name, '') || ' ' ||
        coalesce(NEW.description, '') || ' ' ||
        coalesce(NEW.game_notes, '') || ' ' ||
        coalesce(array_to_string(NEW.tags, ' '), '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER gear_search_vector_update
    BEFORE INSERT OR UPDATE ON gear
    FOR EACH ROW
    EXECUTE FUNCTION update_gear_search_vector();

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE gear IS 'Main gear/equipment table for Shadowrun 2E. Supports weapons, armor, cyberware, vehicles, magic items, and more.';
COMMENT ON COLUMN gear.base_stats IS 'JSONB field containing gear-specific stats. Structure varies by category.';
COMMENT ON COLUMN gear.modifiers IS 'JSONB field containing stat modifiers this gear provides to characters.';
COMMENT ON COLUMN gear.data_quality IS 'Quality rating 1-10. CSV files=8, DAT files=5, manual entries=10.';
COMMENT ON COLUMN gear.loaded_from IS 'Array tracking all source files if item was merged from multiple sources.';

COMMENT ON TABLE gear_chunk_links IS 'Links gear items to narrative/rules chunks for context and detailed information.';
COMMENT ON TABLE gear_load_history IS 'Audit trail for data loading and deduplication decisions.';

COMMENT ON FUNCTION search_gear IS 'Full-text search across gear names, descriptions, and tags.';
COMMENT ON FUNCTION get_gear_with_chunks IS 'Retrieve complete gear details including linked narrative chunks.';
COMMENT ON FUNCTION find_similar_gear IS 'Find potentially duplicate gear using fuzzy name matching.';
