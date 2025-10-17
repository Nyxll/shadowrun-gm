-- ============================================================================
-- SHADOWRUN 2E CHARACTER SYSTEM SCHEMA
-- ============================================================================
-- Complete schema for character building and storage
-- Includes: metatypes, qualities, skills, powers, spells, totems, creatures, characters, contacts
-- ============================================================================

-- ============================================================================
-- CHARACTER BUILDING REFERENCE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- METATYPES: Races and variants
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metatypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    variant_of VARCHAR(100),  -- NULL for base types, parent name for variants
    is_variant BOOLEAN DEFAULT FALSE,
    
    -- Attribute modifiers
    body_mod INTEGER DEFAULT 0,
    quickness_mod INTEGER DEFAULT 0,
    strength_mod INTEGER DEFAULT 0,
    charisma_mod INTEGER DEFAULT 0,
    intelligence_mod INTEGER DEFAULT 0,
    willpower_mod INTEGER DEFAULT 0,
    
    -- Attribute ranges
    body_range INT4RANGE,
    quickness_range INT4RANGE,
    strength_range INT4RANGE,
    charisma_range INT4RANGE,
    intelligence_range INT4RANGE,
    willpower_range INT4RANGE,
    
    -- Special abilities
    special_abilities TEXT[],
    racial_traits JSONB DEFAULT '{}',  -- Variant-specific data
    
    -- Metadata
    description TEXT,
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_metatype_name UNIQUE(name)
);

CREATE INDEX idx_metatypes_variant ON metatypes(variant_of) WHERE variant_of IS NOT NULL;
CREATE INDEX idx_metatypes_search ON metatypes USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- QUALITIES: Edges and Flaws combined
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS qualities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    quality_type VARCHAR(20) NOT NULL CHECK (quality_type IN ('edge', 'flaw')),
    
    -- Cost (positive for edges, negative for flaws)
    cost INTEGER NOT NULL,
    
    -- Requirements and restrictions
    requirements JSONB DEFAULT '{}',  -- metatype, magic rating, etc.
    incompatible_with TEXT[],  -- Other quality names
    
    -- Effects
    game_effects JSONB DEFAULT '{}',  -- Structured effects
    description TEXT,
    game_notes TEXT,
    
    -- Metadata
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_quality_name UNIQUE(name, quality_type)
);

CREATE INDEX idx_qualities_type ON qualities(quality_type);
CREATE INDEX idx_qualities_cost ON qualities(cost);
CREATE INDEX idx_qualities_search ON qualities USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- SKILLS: All skills with categories
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('Active', 'Knowledge', 'Language')),
    subcategory VARCHAR(100),  -- Combat, Physical, Technical, etc.
    
    -- Linked attribute
    linked_attribute VARCHAR(20),  -- Body, Quickness, Strength, etc.
    
    -- Defaulting
    can_default BOOLEAN DEFAULT TRUE,
    default_modifier INTEGER DEFAULT -1,  -- Usually -1 or cannot default
    
    -- Specializations
    specializations TEXT[],
    
    -- Skill details
    description TEXT,
    game_notes TEXT,
    
    -- Metadata
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_skill_name UNIQUE(name)
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_subcategory ON skills(subcategory);
CREATE INDEX idx_skills_attribute ON skills(linked_attribute);
CREATE INDEX idx_skills_search ON skills USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- POWERS: Adept powers and critter powers
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS powers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    power_type VARCHAR(50) NOT NULL CHECK (power_type IN ('adept', 'critter', 'both')),
    
    -- Cost (for adept powers)
    power_point_cost DECIMAL(3,2),  -- 0.25, 0.5, 1.0, etc.
    
    -- Activation
    activation_type VARCHAR(50),  -- Sustained, Permanent, etc.
    activation_requirements TEXT,
    
    -- Effects
    game_effects JSONB DEFAULT '{}',
    levels JSONB DEFAULT '[]',  -- For powers with multiple levels
    
    -- Description
    description TEXT,
    game_notes TEXT,
    
    -- Metadata
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_power_name UNIQUE(name, power_type)
);

CREATE INDEX idx_powers_type ON powers(power_type);
CREATE INDEX idx_powers_cost ON powers(power_point_cost);
CREATE INDEX idx_powers_search ON powers USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- SPELLS: All spells
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS spells (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- Combat, Detection, Health, Illusion, Manipulation
    
    -- Spell type
    spell_type VARCHAR(20) NOT NULL CHECK (spell_type IN ('Physical', 'Mana')),
    
    -- Target
    target_type VARCHAR(50),  -- Area, LOS, Touch, etc.
    
    -- Drain
    drain_code VARCHAR(50),  -- e.g., "(Force ÷ 2)M" or "Force L"
    drain_level VARCHAR(10),  -- L, M, S, D
    
    -- Duration and range
    duration VARCHAR(50),
    range VARCHAR(50),
    
    -- Description
    description TEXT,
    game_notes TEXT,
    
    -- Metadata
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_spell_name UNIQUE(name)
);

CREATE INDEX idx_spells_category ON spells(category);
CREATE INDEX idx_spells_type ON spells(spell_type);
CREATE INDEX idx_spells_search ON spells USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- TOTEMS: Shamanic totems
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS totems (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    
    -- Advantages and disadvantages
    advantages TEXT,
    disadvantages TEXT,
    
    -- Environment
    environment VARCHAR(100),  -- Urban, Forest, Desert, etc.
    
    -- Description
    description TEXT,
    game_notes TEXT,
    
    -- Metadata
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_totem_name UNIQUE(name)
);

CREATE INDEX idx_totems_search ON totems USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CREATURES: Spirits, Elementals, and Critters
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS creatures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    creature_type VARCHAR(50) NOT NULL CHECK (creature_type IN ('spirit', 'elemental', 'critter')),
    subtype VARCHAR(100),  -- City Spirit, Fire Elemental, Hellhound, etc.
    
    -- Core attributes
    body INTEGER,
    quickness INTEGER,
    strength INTEGER,
    charisma INTEGER,
    intelligence INTEGER,
    willpower INTEGER,
    essence INTEGER,
    magic INTEGER,
    reaction INTEGER,
    
    -- Combat stats
    initiative VARCHAR(50),
    combat_pool INTEGER,
    
    -- Abilities and powers (flexible JSONB)
    abilities JSONB DEFAULT '{}',  -- Powers, immunities, weaknesses
    stats JSONB DEFAULT '{}',  -- Force-based stats for spirits, special abilities
    combat_data JSONB DEFAULT '{}',  -- Attack types, damage codes, reach
    
    -- Description
    description TEXT,
    game_notes TEXT,
    
    -- Metadata
    source VARCHAR(100),
    page_reference VARCHAR(50),
    
    -- Deduplication & tracking
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_creature_name UNIQUE(name, creature_type)
);

CREATE INDEX idx_creatures_type ON creatures(creature_type);
CREATE INDEX idx_creatures_subtype ON creatures(subtype);
CREATE INDEX idx_creatures_search ON creatures USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ============================================================================
-- CHARACTER & CAMPAIGN STORAGE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CHARACTERS: Player characters and NPCs
-- Note: Using sr_characters to avoid conflict with existing characters table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sr_characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    player_name VARCHAR(200),  -- NULL for NPCs
    is_npc BOOLEAN DEFAULT FALSE,
    
    -- Core info
    metatype_id INTEGER REFERENCES metatypes(id),
    
    -- Attributes (JSONB for flexibility)
    attributes JSONB DEFAULT '{
        "body": 1,
        "quickness": 1,
        "strength": 1,
        "charisma": 1,
        "intelligence": 1,
        "willpower": 1,
        "essence": 6.0,
        "magic": 0,
        "reaction": 1
    }',
    
    -- Derived stats
    essence DECIMAL(3,2) DEFAULT 6.00,
    karma_pool INTEGER DEFAULT 0,
    good_karma INTEGER DEFAULT 0,
    
    -- Character building data (all JSONB for flexibility)
    skills_data JSONB DEFAULT '[]',  -- [{skill_id, rating, specialization}, ...]
    qualities_taken JSONB DEFAULT '[]',  -- [quality_id, ...]
    gear_owned JSONB DEFAULT '[]',  -- [{gear_id, quantity, notes}, ...]
    cyberware_installed JSONB DEFAULT '[]',  -- [{gear_id, essence_cost, notes}, ...]
    spells_known JSONB DEFAULT '[]',  -- [spell_id, ...]
    powers_active JSONB DEFAULT '[]',  -- [{power_id, level, notes}, ...]
    contacts_list JSONB DEFAULT '[]',  -- [{contact_id, loyalty, connection}, ...]
    
    -- Biography and notes
    biography JSONB DEFAULT '{
        "background": "",
        "appearance": "",
        "personality": "",
        "notes": ""
    }',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_played TIMESTAMP,
    
    -- Campaign tracking
    campaign_id INTEGER,  -- For future campaign management
    status VARCHAR(50) DEFAULT 'active'  -- active, retired, deceased
);

CREATE INDEX idx_sr_characters_player ON sr_characters(player_name);
CREATE INDEX idx_sr_characters_metatype ON sr_characters(metatype_id);
CREATE INDEX idx_sr_characters_npc ON sr_characters(is_npc);
CREATE INDEX idx_sr_characters_search ON sr_characters USING gin(to_tsvector('english', name || ' ' || COALESCE(player_name, '')));

-- ----------------------------------------------------------------------------
-- CONTACTS: NPCs, fixers, street docs, etc.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    archetype VARCHAR(100),  -- Fixer, Street Doc, Decker, etc.
    
    -- Contact ratings
    connection INTEGER CHECK (connection BETWEEN 1 AND 10),
    loyalty INTEGER CHECK (loyalty BETWEEN 1 AND 10),
    
    -- Details
    description TEXT,
    services TEXT,  -- What they can provide
    location VARCHAR(200),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contacts_archetype ON contacts(archetype);
CREATE INDEX idx_contacts_search ON contacts USING gin(to_tsvector('english', name || ' ' || COALESCE(archetype, '') || ' ' || COALESCE(description, '')));

-- ============================================================================
-- AUDIT & HISTORY TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Load history for all reference tables
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reference_load_history (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,  -- insert, update, merge, skip
    source_file VARCHAR(255),
    item_name VARCHAR(255),
    old_data JSONB,
    new_data JSONB,
    reason TEXT,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ref_history_table ON reference_load_history(table_name, record_id);
CREATE INDEX idx_ref_history_action ON reference_load_history(action);
CREATE INDEX idx_ref_history_time ON reference_load_history(loaded_at);

-- ----------------------------------------------------------------------------
-- Character change history
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_history (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES sr_characters(id) ON DELETE CASCADE,
    change_type VARCHAR(50) NOT NULL,  -- attribute_change, skill_gain, gear_purchase, etc.
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    changed_by VARCHAR(200),  -- Player or GM name
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_char_history_character ON character_history(character_id);
CREATE INDEX idx_char_history_type ON character_history(change_type);
CREATE INDEX idx_char_history_time ON character_history(changed_at);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate total essence cost from cyberware
CREATE OR REPLACE FUNCTION calculate_essence_cost(char_id INTEGER)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    total_cost DECIMAL(3,2) := 0.00;
    cyberware_item JSONB;
BEGIN
    -- Sum up essence costs from cyberware_installed JSONB array
    FOR cyberware_item IN 
        SELECT jsonb_array_elements(cyberware_installed) 
        FROM sr_characters 
        WHERE id = char_id
    LOOP
        total_cost := total_cost + COALESCE((cyberware_item->>'essence_cost')::DECIMAL(3,2), 0.00);
    END LOOP;
    
    RETURN total_cost;
END;
$$ LANGUAGE plpgsql;

-- Function to get character's current essence
CREATE OR REPLACE FUNCTION get_current_essence(char_id INTEGER)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    base_essence DECIMAL(3,2) := 6.00;
    cyber_cost DECIMAL(3,2);
BEGIN
    cyber_cost := calculate_essence_cost(char_id);
    RETURN base_essence - cyber_cost;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Character summary with metatype name
CREATE OR REPLACE VIEW character_summary AS
SELECT 
    c.id,
    c.name,
    c.player_name,
    c.is_npc,
    m.name as metatype,
    c.essence,
    c.karma_pool,
    c.good_karma,
    c.status,
    c.last_played
FROM sr_characters c
LEFT JOIN metatypes m ON c.metatype_id = m.id;

-- View: All reference data counts
CREATE OR REPLACE VIEW reference_data_stats AS
SELECT 
    'metatypes' as table_name, COUNT(*) as count FROM metatypes
UNION ALL
SELECT 'qualities', COUNT(*) FROM qualities
UNION ALL
SELECT 'skills', COUNT(*) FROM skills
UNION ALL
SELECT 'powers', COUNT(*) FROM powers
UNION ALL
SELECT 'spells', COUNT(*) FROM spells
UNION ALL
SELECT 'totems', COUNT(*) FROM totems
UNION ALL
SELECT 'creatures', COUNT(*) FROM creatures
UNION ALL
SELECT 'gear', COUNT(*) FROM gear
UNION ALL
SELECT 'sr_characters', COUNT(*) FROM sr_characters
UNION ALL
SELECT 'contacts', COUNT(*) FROM contacts;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE metatypes IS 'Character races and variants (Human, Elf, Dwarf, Ork, Troll, Drakes, Ghouls, etc.)';
COMMENT ON TABLE qualities IS 'Character edges and flaws combined in one table';
COMMENT ON TABLE skills IS 'All skills with categories, linked attributes, and specializations';
COMMENT ON TABLE powers IS 'Adept powers and critter powers';
COMMENT ON TABLE spells IS 'All spells with drain, target, and type information';
COMMENT ON TABLE totems IS 'Shamanic totems with advantages and disadvantages';
COMMENT ON TABLE creatures IS 'Spirits, elementals, and critters with flexible JSONB storage';
COMMENT ON TABLE sr_characters IS 'Player characters and NPCs with JSONB storage for flexibility';
COMMENT ON TABLE contacts IS 'NPCs, fixers, street docs, and other contacts';
COMMENT ON TABLE reference_load_history IS 'Audit trail for all reference data loading';
COMMENT ON TABLE character_history IS 'Change history for character modifications';
