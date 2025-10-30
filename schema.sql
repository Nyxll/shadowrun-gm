-- ============================================================================
-- SHADOWRUN GM - UNIFIED DATABASE SCHEMA
-- Version: 3.0
-- Last Updated: 2025-10-20
-- ============================================================================
-- This is the authoritative schema file for the Shadowrun GM system.
-- Combines character management, modifiers, house rules, and gear systems.
-- ============================================================================

-- ============================================================================
-- CHARACTERS TABLE
-- Core character data with explicit base/current attributes
-- ============================================================================
CREATE TABLE IF NOT EXISTS characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    street_name TEXT,
    character_type TEXT,
    archetype TEXT,
    
    -- BASE ATTRIBUTES (for karma cost calculations)
    base_body INTEGER NOT NULL,
    base_quickness INTEGER NOT NULL,
    base_strength INTEGER NOT NULL,
    base_charisma INTEGER NOT NULL,
    base_intelligence INTEGER NOT NULL,
    base_willpower INTEGER NOT NULL,
    base_essence DECIMAL(3,2) NOT NULL DEFAULT 6.00,
    base_magic INTEGER DEFAULT 0,
    base_reaction INTEGER NOT NULL,
    
    -- CURRENT ATTRIBUTES (cached: base + permanent modifiers)
    current_body INTEGER NOT NULL,
    current_quickness INTEGER NOT NULL,
    current_strength INTEGER NOT NULL,
    current_charisma INTEGER NOT NULL,
    current_intelligence INTEGER NOT NULL,
    current_willpower INTEGER NOT NULL,
    current_essence DECIMAL(3,2) NOT NULL,
    current_magic INTEGER DEFAULT 0,
    current_reaction INTEGER NOT NULL,
    
    -- CONDITIONAL MODIFIERS (JSONB for edge cases)
    conditional_modifiers JSONB DEFAULT '{}'::jsonb,
    
    -- CHARACTER RESOURCES
    nuyen INTEGER DEFAULT 0,
    karma_pool INTEGER DEFAULT 0,
    karma_total INTEGER DEFAULT 0,
    
    -- DERIVED STATS
    initiative TEXT,
    
    -- METADATA
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- UI STATE
    ui_state JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);
CREATE INDEX IF NOT EXISTS idx_characters_street_name ON characters(street_name);

-- ============================================================================
-- CHARACTER SKILLS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    base_rating INTEGER NOT NULL,
    current_rating INTEGER NOT NULL,
    specialization TEXT,
    conditional_bonuses JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(character_id, skill_name)
);

CREATE INDEX IF NOT EXISTS idx_skills_character ON character_skills(character_id);
CREATE INDEX IF NOT EXISTS idx_skills_name ON character_skills(skill_name);

-- ============================================================================
-- CHARACTER MODIFIERS TABLE
-- Permanent modifiers from cyberware, bioware, training, etc.
-- 
-- STRUCTURE:
-- - Parent entries (modifier_type='augmentation'): Represent the item itself
--   * Cyberware: essence_cost stored directly
--   * Bioware: body_index_cost stored in modifier_data JSONB
--   * These are the "inventory" entries
--
-- - Child entries (modifier_type='attribute'/'skill'/etc): Represent effects
--   * Link to parent via parent_modifier_id
--   * Example: Cerebral Booster 3 (parent) -> +3 Intelligence (child)
--
-- LINKING:
-- - parent_modifier_id: Links child modifiers to their parent augmentation
-- - This creates proper parent-child relationships instead of fuzzy matching
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_modifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    -- WHAT IT MODIFIES
    modifier_type TEXT NOT NULL,  -- 'augmentation', 'attribute', 'skill', 'initiative', 'armor', 'combat', 'vision'
    target_name TEXT NOT NULL,    -- 'quickness', 'firearms', 'ranged_tn', etc.
    modifier_value INTEGER NOT NULL,
    
    -- SOURCE TRACKING
    source TEXT NOT NULL,         -- Human-readable source name
    source_type TEXT,             -- 'cyberware', 'bioware', 'spell', 'gear', 'training'
    source_id UUID,               -- Reference to gear/spell/etc if applicable
    
    -- PARENT-CHILD RELATIONSHIP FOR AUGMENTATIONS
    parent_modifier_id UUID REFERENCES character_modifiers(id) ON DELETE CASCADE,
    
    -- AUGMENTATION COSTS (for parent entries only)
    essence_cost DECIMAL(3,2),    -- For cyberware parents
    
    -- SCOPE
    is_permanent BOOLEAN NOT NULL DEFAULT TRUE,
    weapon_specific TEXT,         -- NULL or specific weapon name
    condition TEXT,               -- NULL or condition like 'in_melee', 'at_night'
    
    -- COMPLEX MODIFIER DATA (JSONB for flexibility)
    modifier_data JSONB DEFAULT '{}'::jsonb,  -- For bioware: stores body_index_cost
    
    -- SPECIAL FLAGS
    is_homebrew BOOLEAN DEFAULT FALSE,
    is_experimental BOOLEAN DEFAULT FALSE,
    is_unique BOOLEAN DEFAULT FALSE,
    house_rule_id INTEGER,        -- Reference to house_rules table
    
    -- METADATA
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_modifiers_character ON character_modifiers(character_id);
CREATE INDEX IF NOT EXISTS idx_modifiers_lookup ON character_modifiers(character_id, modifier_type, target_name);
CREATE INDEX IF NOT EXISTS idx_modifiers_source ON character_modifiers(source_type);
CREATE INDEX IF NOT EXISTS idx_modifiers_data ON character_modifiers USING gin(modifier_data);

-- ============================================================================
-- CHARACTER ACTIVE EFFECTS TABLE
-- Temporary/sustained effects from spells, drugs, wounds, etc.
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_active_effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    effect_type TEXT NOT NULL,    -- 'spell', 'drug', 'wound', 'condition'
    effect_name TEXT NOT NULL,
    target_type TEXT NOT NULL,    -- 'attribute', 'skill', 'initiative'
    target_name TEXT NOT NULL,
    modifier_value INTEGER NOT NULL,
    
    duration_type TEXT NOT NULL,  -- 'sustained', 'quickened', 'timed', 'conditional'
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- SPELL METADATA
    caster_id UUID REFERENCES characters(id),
    force INTEGER,
    drain_taken INTEGER,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_effects_character ON character_active_effects(character_id);
CREATE INDEX IF NOT EXISTS idx_effects_active ON character_active_effects(character_id, is_active);

-- ============================================================================
-- CHARACTER GEAR TABLE
-- Weapons, armor, equipment with modifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_gear (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    gear_name TEXT NOT NULL,
    gear_type TEXT NOT NULL,      -- 'weapon', 'armor', 'equipment', 'focus'
    quantity INTEGER DEFAULT 1,
    
    -- MODIFICATIONS (JSONB for flexibility)
    modifications JSONB DEFAULT '{}'::jsonb,
    weapon_stats JSONB,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gear_character ON character_gear(character_id);
CREATE INDEX IF NOT EXISTS idx_gear_type ON character_gear(character_id, gear_type);

-- ============================================================================
-- CHARACTER RELATIONSHIPS TABLE
-- Spells, contacts, enemies, foci, etc.
-- ============================================================================
CREATE TABLE IF NOT EXISTS character_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    
    relationship_type TEXT NOT NULL,  -- 'spell', 'contact', 'enemy', 'ally', 'focus'
    relationship_name TEXT NOT NULL,
    data JSONB NOT NULL,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relationships_character ON character_relationships(character_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON character_relationships(character_id, relationship_type);

-- ============================================================================
-- HOUSE RULES SYSTEM
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    gm_name VARCHAR(200),
    description TEXT,
    setting_notes TEXT,
    status VARCHAR(20) DEFAULT 'active',
    start_date DATE,
    last_session DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS house_rules (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,  -- 'karma_multiplier', 'custom', 'cyberware', etc.
    rule_config JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    
    description TEXT,
    examples TEXT,
    notes TEXT,
    
    created_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_campaign_rule_name UNIQUE(campaign_id, rule_name)
);

CREATE INDEX IF NOT EXISTS idx_house_rules_campaign ON house_rules(campaign_id);
CREATE INDEX IF NOT EXISTS idx_house_rules_type ON house_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_house_rules_active ON house_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_house_rules_config ON house_rules USING gin(rule_config);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_character_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER characters_updated_at
    BEFORE UPDATE ON characters
    FOR EACH ROW
    EXECUTE FUNCTION update_character_timestamp();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE characters IS 'Core character data with base and current attributes for karma tracking';
COMMENT ON TABLE character_modifiers IS 'Permanent modifiers from cyberware, bioware, training, house rules';
COMMENT ON TABLE character_active_effects IS 'Temporary/sustained effects (spells, drugs, wounds)';
COMMENT ON TABLE character_gear IS 'Physical equipment with modifications';
COMMENT ON TABLE house_rules IS 'Custom campaign rules and homebrew content';

COMMENT ON COLUMN characters.ui_state IS 'UI preferences and state for character sheet display';
COMMENT ON COLUMN character_modifiers.modifier_data IS 'JSONB for complex effects (smartlink abilities, conditional bonuses, etc.)';
COMMENT ON COLUMN character_modifiers.source_type IS 'Category of modifier source (cyberware, bioware, spell, gear, training)';
COMMENT ON COLUMN character_modifiers.is_homebrew IS 'Flag for GM-created/house rule content';
COMMENT ON COLUMN character_modifiers.house_rule_id IS 'Reference to house_rules table for custom content';
