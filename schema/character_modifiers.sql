-- ============================================================================
-- CHARACTER MODIFIERS SYSTEM
-- ============================================================================
-- Flexible modifier system for tracking all character stat modifications
-- Handles: cyberware, spells, adept powers, gear, wounds, experimental effects
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CHARACTER MODIFIERS: All stat modifications
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_modifiers (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES sr_characters(id) ON DELETE CASCADE,
    
    -- What's being modified (flexible target system)
    modifier_target VARCHAR(50) NOT NULL,  -- 'body', 'reaction', 'combat_pool', 'mental_skills', etc.
    modifier_value INTEGER NOT NULL,       -- +2, -1, etc. (0 for non-numeric effects)
    modifier_type VARCHAR(20) NOT NULL CHECK (modifier_type IN ('permanent', 'sustained', 'temporary', 'conditional')),
    
    -- Source tracking
    source_type VARCHAR(50) NOT NULL,      -- 'cyberware', 'spell', 'adept_power', 'drug', 'gear', 'wound', 'quality'
    source_id INTEGER,                     -- ID from relevant table (gear_id, spell_id, power_id, etc.)
    source_name VARCHAR(200),              -- Human-readable source name
    
    -- Duration tracking
    duration_type VARCHAR(20),             -- 'permanent', 'sustained', 'rounds', 'minutes', 'hours', 'until_healed'
    duration_remaining INTEGER,            -- For temporary effects (rounds, minutes, etc.)
    expires_at TIMESTAMP,                  -- For time-based effects
    
    -- Conditions and activation
    condition_text TEXT,                   -- "Only with smartlink-equipped weapon", "In astral space", etc.
    is_active BOOLEAN DEFAULT TRUE,        -- Can be toggled on/off
    
    -- Complex modifier data (JSONB for ultimate flexibility)
    modifier_data JSONB DEFAULT '{}',      -- Store ANY complex effect data
    
    -- Stacking rules
    stacks_with TEXT[],                    -- Array of modifier names this stacks with
    replaces TEXT[],                       -- Array of modifier names this replaces
    max_stack INTEGER,                     -- Maximum stacking instances (NULL = unlimited)
    
    -- Special flags
    is_experimental BOOLEAN DEFAULT FALSE, -- Experimental/prototype gear
    is_unique BOOLEAN DEFAULT FALSE,       -- One-of-a-kind item
    is_homebrew BOOLEAN DEFAULT FALSE,     -- GM-created content
    requires_gm_approval BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    notes TEXT,                            -- Player-visible notes
    gm_notes TEXT,                         -- GM-only notes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_char_mods_character ON character_modifiers(character_id);
CREATE INDEX idx_char_mods_target ON character_modifiers(modifier_target);
CREATE INDEX idx_char_mods_active ON character_modifiers(is_active);
CREATE INDEX idx_char_mods_source ON character_modifiers(source_type, source_id);
CREATE INDEX idx_char_mods_type ON character_modifiers(modifier_type);
CREATE INDEX idx_char_mods_expires ON character_modifiers(expires_at) WHERE expires_at IS NOT NULL;

-- GIN index for JSONB modifier_data
CREATE INDEX idx_char_mods_data ON character_modifiers USING gin(modifier_data);

-- ----------------------------------------------------------------------------
-- HELPER FUNCTIONS
-- ----------------------------------------------------------------------------

-- Function to get all active modifiers for a specific target
CREATE OR REPLACE FUNCTION get_active_modifiers(char_id INTEGER, target_name VARCHAR)
RETURNS TABLE (
    modifier_id INTEGER,
    modifier_value INTEGER,
    source_name VARCHAR,
    modifier_type VARCHAR,
    is_experimental BOOLEAN,
    modifier_data JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        character_modifiers.modifier_value,
        character_modifiers.source_name,
        character_modifiers.modifier_type,
        character_modifiers.is_experimental,
        character_modifiers.modifier_data
    FROM character_modifiers
    WHERE character_id = char_id
      AND modifier_target = target_name
      AND is_active = true
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY modifier_type, modifier_value DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate total modifier for a target
CREATE OR REPLACE FUNCTION calculate_modifier_total(char_id INTEGER, target_name VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    total INTEGER := 0;
BEGIN
    SELECT COALESCE(SUM(modifier_value), 0) INTO total
    FROM character_modifiers
    WHERE character_id = char_id
      AND modifier_target = target_name
      AND is_active = true
      AND (expires_at IS NULL OR expires_at > NOW());
    
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Function to get augmented attribute value
CREATE OR REPLACE FUNCTION get_augmented_attribute(char_id INTEGER, attr_name VARCHAR)
RETURNS JSONB AS $$
DECLARE
    base_value INTEGER;
    modifier_total INTEGER;
    result JSONB;
BEGIN
    -- Get base attribute value from character
    SELECT (attributes->>attr_name)::INTEGER INTO base_value
    FROM sr_characters
    WHERE id = char_id;
    
    -- Calculate total modifiers
    modifier_total := calculate_modifier_total(char_id, attr_name);
    
    -- Build result JSON
    result := jsonb_build_object(
        'base', base_value,
        'modifier', modifier_total,
        'augmented', base_value + modifier_total
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate Combat Pool
CREATE OR REPLACE FUNCTION calculate_combat_pool(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    quickness INTEGER;
    intelligence INTEGER;
    base_pool INTEGER;
    modifier_total INTEGER;
    result JSONB;
BEGIN
    -- Get augmented Quickness and Intelligence
    SELECT (get_augmented_attribute(char_id, 'quickness')->>'augmented')::INTEGER INTO quickness;
    SELECT (get_augmented_attribute(char_id, 'intelligence')->>'augmented')::INTEGER INTO intelligence;
    
    -- Base Combat Pool = (Quickness + Intelligence) / 2 (round down)
    base_pool := (quickness + intelligence) / 2;
    
    -- Add direct combat_pool modifiers
    modifier_total := calculate_modifier_total(char_id, 'combat_pool');
    
    result := jsonb_build_object(
        'base', base_pool,
        'modifier', modifier_total,
        'total', base_pool + modifier_total
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate Spell Pool (for mages/shamans)
CREATE OR REPLACE FUNCTION calculate_spell_pool(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    magic_rating INTEGER;
    base_pool INTEGER;
    modifier_total INTEGER;
    result JSONB;
BEGIN
    -- Get augmented Magic rating
    SELECT (get_augmented_attribute(char_id, 'magic')->>'augmented')::INTEGER INTO magic_rating;
    
    -- Base Spell Pool = Magic × 2
    base_pool := magic_rating * 2;
    
    -- Add direct spell_pool modifiers (from foci, etc.)
    modifier_total := calculate_modifier_total(char_id, 'spell_pool');
    
    result := jsonb_build_object(
        'base', base_pool,
        'modifier', modifier_total,
        'total', base_pool + modifier_total
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate Initiative
CREATE OR REPLACE FUNCTION calculate_initiative(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    reaction INTEGER;
    base_dice INTEGER := 1;
    dice_modifiers INTEGER;
    result JSONB;
BEGIN
    -- Get augmented Reaction
    SELECT (get_augmented_attribute(char_id, 'reaction')->>'augmented')::INTEGER INTO reaction;
    
    -- Get initiative dice modifiers (Wired Reflexes, Improved Reflexes, etc.)
    dice_modifiers := calculate_modifier_total(char_id, 'initiative_dice');
    
    result := jsonb_build_object(
        'reaction', reaction,
        'base_dice', base_dice,
        'bonus_dice', dice_modifiers,
        'total_dice', base_dice + dice_modifiers,
        'formula', reaction || ' + ' || (base_dice + dice_modifiers) || 'D6'
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to expire temporary modifiers
CREATE OR REPLACE FUNCTION expire_temporary_modifiers()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    -- Deactivate expired modifiers
    UPDATE character_modifiers
    SET is_active = false
    WHERE expires_at IS NOT NULL
      AND expires_at <= NOW()
      AND is_active = true;
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Function to decrement duration-based modifiers
CREATE OR REPLACE FUNCTION decrement_modifier_durations(rounds INTEGER DEFAULT 1)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    -- Decrement duration_remaining
    UPDATE character_modifiers
    SET duration_remaining = duration_remaining - rounds
    WHERE duration_type IN ('rounds', 'minutes', 'hours')
      AND duration_remaining IS NOT NULL
      AND duration_remaining > 0
      AND is_active = true;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    -- Deactivate modifiers that reached 0
    UPDATE character_modifiers
    SET is_active = false
    WHERE duration_remaining IS NOT NULL
      AND duration_remaining <= 0
      AND is_active = true;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- VIEWS
-- ----------------------------------------------------------------------------

-- View: Character summary with augmented stats
CREATE OR REPLACE VIEW character_augmented_stats AS
SELECT 
    c.id,
    c.name,
    c.player_name,
    
    -- Base attributes
    (c.attributes->>'body')::INTEGER as base_body,
    (c.attributes->>'quickness')::INTEGER as base_quickness,
    (c.attributes->>'strength')::INTEGER as base_strength,
    (c.attributes->>'charisma')::INTEGER as base_charisma,
    (c.attributes->>'intelligence')::INTEGER as base_intelligence,
    (c.attributes->>'willpower')::INTEGER as base_willpower,
    (c.attributes->>'reaction')::INTEGER as base_reaction,
    (c.attributes->>'magic')::INTEGER as base_magic,
    
    -- Augmented attributes
    (get_augmented_attribute(c.id, 'body')->>'augmented')::INTEGER as aug_body,
    (get_augmented_attribute(c.id, 'quickness')->>'augmented')::INTEGER as aug_quickness,
    (get_augmented_attribute(c.id, 'strength')->>'augmented')::INTEGER as aug_strength,
    (get_augmented_attribute(c.id, 'charisma')->>'augmented')::INTEGER as aug_charisma,
    (get_augmented_attribute(c.id, 'intelligence')->>'augmented')::INTEGER as aug_intelligence,
    (get_augmented_attribute(c.id, 'willpower')->>'augmented')::INTEGER as aug_willpower,
    (get_augmented_attribute(c.id, 'reaction')->>'augmented')::INTEGER as aug_reaction,
    (get_augmented_attribute(c.id, 'magic')->>'augmented')::INTEGER as aug_magic,
    
    -- Derived stats
    calculate_combat_pool(c.id) as combat_pool,
    calculate_spell_pool(c.id) as spell_pool,
    calculate_initiative(c.id) as initiative,
    
    -- Essence and Karma
    c.essence,
    c.karma_pool,
    c.good_karma
FROM sr_characters c;

-- View: All active modifiers summary
CREATE OR REPLACE VIEW active_modifiers_summary AS
SELECT 
    cm.character_id,
    c.name as character_name,
    cm.modifier_target,
    COUNT(*) as modifier_count,
    SUM(cm.modifier_value) as total_modifier,
    array_agg(cm.source_name ORDER BY cm.modifier_value DESC) as sources
FROM character_modifiers cm
JOIN sr_characters c ON c.id = cm.character_id
WHERE cm.is_active = true
  AND (cm.expires_at IS NULL OR cm.expires_at > NOW())
GROUP BY cm.character_id, c.name, cm.modifier_target
ORDER BY cm.character_id, cm.modifier_target;

-- ----------------------------------------------------------------------------
-- TRIGGERS
-- ----------------------------------------------------------------------------

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modifier_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_modifier_timestamp
    BEFORE UPDATE ON character_modifiers
    FOR EACH ROW
    EXECUTE FUNCTION update_modifier_timestamp();

-- ----------------------------------------------------------------------------
-- COMMENTS
-- ----------------------------------------------------------------------------

COMMENT ON TABLE character_modifiers IS 'Flexible modifier system for all character stat modifications';
COMMENT ON COLUMN character_modifiers.modifier_target IS 'What is being modified (body, reaction, combat_pool, mental_skills, special_ability, etc.)';
COMMENT ON COLUMN character_modifiers.modifier_data IS 'JSONB field for complex effect data - can store ANY kind of modifier information';
COMMENT ON COLUMN character_modifiers.stacks_with IS 'Array of modifier names this effect stacks with';
COMMENT ON COLUMN character_modifiers.is_experimental IS 'Flag for experimental/prototype gear effects';
COMMENT ON COLUMN character_modifiers.is_unique IS 'Flag for one-of-a-kind item effects';

COMMENT ON FUNCTION get_active_modifiers IS 'Get all active modifiers for a specific target (e.g., all reaction modifiers)';
COMMENT ON FUNCTION calculate_modifier_total IS 'Calculate total modifier value for a target';
COMMENT ON FUNCTION get_augmented_attribute IS 'Get base, modifier, and augmented value for an attribute';
COMMENT ON FUNCTION calculate_combat_pool IS 'Calculate Combat Pool with all modifiers';
COMMENT ON FUNCTION calculate_spell_pool IS 'Calculate Spell Pool with all modifiers';
COMMENT ON FUNCTION calculate_initiative IS 'Calculate Initiative with reaction and dice modifiers';
COMMENT ON FUNCTION expire_temporary_modifiers IS 'Deactivate modifiers that have expired (run periodically)';
COMMENT ON FUNCTION decrement_modifier_durations IS 'Decrement duration counters for round/minute/hour based effects';
