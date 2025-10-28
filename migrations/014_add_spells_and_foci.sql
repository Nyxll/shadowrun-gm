-- ============================================================================
-- Migration 014: Add Spells and Foci Tables
-- Adds proper spell and fetish/focus tracking for spellcasters
-- ============================================================================

-- ============================================================================
-- CHARACTER SPELLS TABLE
-- Tracks spells known by each character
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_spells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    spell_name TEXT NOT NULL,
    spell_category TEXT NOT NULL,  -- 'combat', 'detection', 'health', 'illusion', 'manipulation'
    spell_type TEXT NOT NULL,      -- 'mana', 'physical'
    target_type TEXT,              -- 'LOS', 'touch', 'area', 'self'
    duration TEXT,                 -- 'instant', 'sustained', 'permanent'
    drain_modifier INTEGER DEFAULT 0,  -- Modifier to drain (e.g., +2 for deadly spells)
    
    -- SPELL DETAILS
    description TEXT,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(character_id, spell_name)
);

CREATE INDEX IF NOT EXISTS idx_spells_character ON character_spells(character_id);
CREATE INDEX IF NOT EXISTS idx_spells_category ON character_spells(spell_category);

-- ============================================================================
-- CHARACTER FOCI TABLE
-- Tracks magical foci (fetishes, power foci, weapon foci, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_foci (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    focus_name TEXT NOT NULL,
    focus_type TEXT NOT NULL,      -- 'spell', 'power', 'weapon', 'spirit', 'sustaining'
    force INTEGER NOT NULL,
    
    -- FOR SPELL FOCI
    spell_category TEXT,           -- 'combat', 'health', 'manipulation', etc.
    specific_spell TEXT,           -- NULL for category foci, spell name for specific foci
    
    -- BONUSES
    bonus_dice INTEGER DEFAULT 0,  -- Extra dice when using this focus
    tn_modifier INTEGER DEFAULT 0, -- TN reduction when using this focus
    
    -- METADATA
    bonded BOOLEAN DEFAULT TRUE,
    karma_cost INTEGER,            -- Karma spent to bond
    description TEXT,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(character_id, focus_name)
);

CREATE INDEX IF NOT EXISTS idx_foci_character ON character_foci(character_id);
CREATE INDEX IF NOT EXISTS idx_foci_type ON character_foci(focus_type);
CREATE INDEX IF NOT EXISTS idx_foci_category ON character_foci(spell_category);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE character_spells IS 'Spells known by each character';
COMMENT ON TABLE character_foci IS 'Magical foci including fetishes, power foci, weapon foci';

COMMENT ON COLUMN character_foci.focus_type IS 'Type of focus: spell, power, weapon, spirit, sustaining';
COMMENT ON COLUMN character_foci.spell_category IS 'For spell foci: combat, health, manipulation, etc.';
COMMENT ON COLUMN character_foci.specific_spell IS 'NULL for category foci, specific spell name for spell-specific foci';
COMMENT ON COLUMN character_foci.bonus_dice IS 'Extra dice added to spellcasting pool when using this focus';
COMMENT ON COLUMN character_foci.tn_modifier IS 'TN reduction when using this focus (usually 0 for fetishes)';
