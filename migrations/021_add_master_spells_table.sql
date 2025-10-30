-- ============================================================================
-- Migration 021: Add Master Spells Table
-- Canonical spell definitions with house rule support
-- ============================================================================

-- Master spells table - canonical spell definitions
CREATE TABLE IF NOT EXISTS master_spells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spell_name TEXT NOT NULL UNIQUE,
    spell_class TEXT NOT NULL,  -- 'combat', 'detection', 'health', 'illusion', 'manipulation'
    spell_type TEXT NOT NULL,   -- 'mana', 'physical'
    duration TEXT NOT NULL,     -- 'instant', 'sustained', 'permanent'
    
    -- Drain formula (e.g., "(F/2)S", "[(F/2)+1]D")
    drain_formula TEXT NOT NULL,
    
    -- Reference and metadata
    book_reference TEXT,
    description TEXT,
    
    -- House rule support
    is_house_rule BOOLEAN DEFAULT FALSE,
    house_rule_id INTEGER REFERENCES house_rules(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_master_spells_class ON master_spells(spell_class);
CREATE INDEX IF NOT EXISTS idx_master_spells_type ON master_spells(spell_type);
CREATE INDEX IF NOT EXISTS idx_master_spells_house_rule ON master_spells(is_house_rule);

-- Update character_spells to add missing columns
ALTER TABLE character_spells 
    ADD COLUMN IF NOT EXISTS force INTEGER,
    ADD COLUMN IF NOT EXISTS master_spell_id UUID REFERENCES master_spells(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_character_spells_master ON character_spells(master_spell_id);
CREATE INDEX IF NOT EXISTS idx_character_spells_force ON character_spells(force);

-- Comments
COMMENT ON TABLE master_spells IS 'Canonical spell definitions from rulebooks and house rules';
COMMENT ON COLUMN master_spells.drain_formula IS 'Drain formula string (e.g., "(F/2)S", "[(F/2)+1]D")';
COMMENT ON COLUMN master_spells.is_house_rule IS 'TRUE for custom/homebrew spells';
COMMENT ON COLUMN master_spells.house_rule_id IS 'Links to house_rules table for custom spells';
COMMENT ON COLUMN character_spells.master_spell_id IS 'Reference to canonical spell definition (NULL for fully custom spells)';
COMMENT ON COLUMN character_spells.drain_code IS 'Cached drain code for quick reference (can override master spell)';
COMMENT ON COLUMN character_spells.force IS 'Force at which this spell was learned (NULL for variable force spells)';

-- Migration complete
