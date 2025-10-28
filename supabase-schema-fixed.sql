-- ============================================================================
-- SHADOWRUN GM DATABASE SCHEMA FOR SUPABASE
-- ============================================================================
-- Generated: 2025-10-19
-- Complete schema for Shadowrun 2E GM system
-- 
-- IMPORTANT: Run this in Supabase SQL Editor
-- Extensions (vector, pg_trgm) are already enabled in Supabase
-- ============================================================================

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- SEQUENCES
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS metatypes_id_seq;
CREATE SEQUENCE IF NOT EXISTS powers_id_seq;
CREATE SEQUENCE IF NOT EXISTS spells_id_seq;
CREATE SEQUENCE IF NOT EXISTS totems_id_seq;
CREATE SEQUENCE IF NOT EXISTS gear_id_seq;
CREATE SEQUENCE IF NOT EXISTS gear_chunk_links_id_seq;
CREATE SEQUENCE IF NOT EXISTS campaigns_id_seq;
CREATE SEQUENCE IF NOT EXISTS sr_characters_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_skills_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_spells_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_powers_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_contacts_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_gear_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_history_id_seq;
CREATE SEQUENCE IF NOT EXISTS character_modifiers_id_seq;
CREATE SEQUENCE IF NOT EXISTS house_rules_id_seq;
CREATE SEQUENCE IF NOT EXISTS rule_application_log_id_seq;
CREATE SEQUENCE IF NOT EXISTS query_logs_id_seq;

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- METATYPES: Races and variants
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metatypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    variant_of VARCHAR(100),
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
    racial_traits JSONB DEFAULT '{}',
    
    -- Metadata
    description TEXT,
    source VARCHAR(100),
    page_reference VARCHAR(50),
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_metatype_name UNIQUE(name)
);

CREATE INDEX idx_metatypes_variant ON metatypes(variant_of) WHERE variant_of IS NOT NULL;
CREATE INDEX idx_metatypes_search ON metatypes USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- POWERS: Adept powers and critter powers
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS powers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    power_type VARCHAR(50) NOT NULL,
    power_point_cost NUMERIC,
    activation_type VARCHAR(50),
    activation_requirements TEXT,
    game_effects JSONB DEFAULT '{}',
    levels JSONB DEFAULT '[]',
    description TEXT,
    game_notes TEXT,
    source VARCHAR(100),
    page_reference VARCHAR(50),
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
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
    category VARCHAR(50) NOT NULL,
    spell_type VARCHAR(20) NOT NULL,
    target_type VARCHAR(50),
    drain_code VARCHAR(50),
    drain_level VARCHAR(10),
    duration VARCHAR(50),
    range VARCHAR(50),
    description TEXT,
    game_notes TEXT,
    source VARCHAR(100),
    page_reference VARCHAR(50),
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
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
    advantages TEXT,
    disadvantages TEXT,
    environment VARCHAR(100),
    description TEXT,
    game_notes TEXT,
    source VARCHAR(100),
    page_reference VARCHAR(50),
    data_quality INTEGER DEFAULT 5,
    loaded_from TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_totem_name UNIQUE(name)
);

CREATE INDEX idx_totems_search ON totems USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- ----------------------------------------------------------------------------
-- RULES CONTENT: Semantic chunks from rulebooks
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rules_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    source_file TEXT,
    source_book TEXT,
    tags TEXT[],
    embedding VECTOR(1536),
    content_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX rules_content_category_idx ON rules_content(category);
CREATE INDEX rules_content_subcategory_idx ON rules_content(subcategory);
CREATE INDEX rules_content_content_type_idx ON rules_content(content_type);
CREATE INDEX rules_content_tags_idx ON rules_content USING gin(tags);
CREATE INDEX rules_content_fts_idx ON rules_content USING gin(to_tsvector('english', title || ' ' || content));
CREATE INDEX rules_content_embedding_idx ON rules_content USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);

-- ----------------------------------------------------------------------------
-- GEAR: Equipment, weapons, cyberware, etc.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gear (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    base_stats JSONB NOT NULL DEFAULT '{}',
    modifiers JSONB DEFAULT '{}',
    requirements JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    description TEXT,
    game_notes TEXT,
    source TEXT,
    availability TEXT,
    cost INTEGER,
    street_index NUMERIC,
    legality TEXT,
    data_source TEXT NOT NULL DEFAULT 'manual',
    source_file TEXT,
    loaded_from TEXT[] DEFAULT '{}',
    data_quality INTEGER DEFAULT 5,
    is_custom BOOLEAN DEFAULT FALSE,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    search_vector TSVECTOR
);

CREATE INDEX idx_gear_category ON gear(category);
CREATE INDEX idx_gear_subcategory ON gear(subcategory);
CREATE INDEX idx_gear_name ON gear(name);
CREATE INDEX idx_gear_name_lower ON gear(LOWER(name));
CREATE UNIQUE INDEX idx_gear_unique_name_category ON gear(LOWER(TRIM(name)), category);
CREATE INDEX idx_gear_stats ON gear USING gin(base_stats);
CREATE INDEX idx_gear_modifiers ON gear USING gin(modifiers);
CREATE INDEX idx_gear_requirements ON gear USING gin(requirements);
CREATE INDEX idx_gear_tags ON gear USING gin(tags);
CREATE INDEX idx_gear_cost ON gear(cost) WHERE cost IS NOT NULL;
CREATE INDEX idx_gear_availability ON gear(availability) WHERE availability IS NOT NULL;
CREATE INDEX idx_gear_search ON gear USING gin(search_vector);
CREATE INDEX idx_gear_custom ON gear(is_custom);
CREATE INDEX idx_gear_data_source ON gear(data_source);
CREATE INDEX idx_gear_quality ON gear(data_quality);

-- ----------------------------------------------------------------------------
-- GEAR CHUNK LINKS: Links gear to narrative chunks
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gear_chunk_links (
    id SERIAL PRIMARY KEY,
    gear_id INTEGER NOT NULL REFERENCES gear(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES rules_content(id) ON DELETE CASCADE,
    link_type TEXT DEFAULT 'description',
    confidence NUMERIC(3,2) DEFAULT 1.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(gear_id, chunk_id, link_type)
);

CREATE INDEX idx_gear_links_gear ON gear_chunk_links(gear_id);
CREATE INDEX idx_gear_links_chunk ON gear_chunk_links(chunk_id);
CREATE INDEX idx_gear_links_type ON gear_chunk_links(link_type);

-- ============================================================================
-- CAMPAIGN & CHARACTER TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CAMPAIGNS: Campaign/game tracking
-- ----------------------------------------------------------------------------
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

CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_gm ON campaigns(gm_name);

-- ----------------------------------------------------------------------------
-- CHARACTERS: Player characters and NPCs
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sr_characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    player_name VARCHAR(200),
    is_npc BOOLEAN DEFAULT FALSE,
    metatype_id INTEGER REFERENCES metatypes(id),
    metatype VARCHAR(50),
    archetype VARCHAR(100),
    attributes JSONB DEFAULT '{"body": 1, "quickness": 1, "strength": 1, "charisma": 1, "intelligence": 1, "willpower": 1, "essence": 6.0, "magic": 0, "reaction": 1}',
    essence NUMERIC DEFAULT 6.00,
    karma_pool INTEGER DEFAULT 0,
    good_karma INTEGER DEFAULT 0,
    nuyen INTEGER DEFAULT 0,
    physical_damage INTEGER DEFAULT 0,
    stun_damage INTEGER DEFAULT 0,
    skills_data JSONB DEFAULT '[]',
    qualities_taken JSONB DEFAULT '[]',
    gear_owned JSONB DEFAULT '[]',
    cyberware_installed JSONB DEFAULT '[]',
    spells_known JSONB DEFAULT '[]',
    powers_active JSONB DEFAULT '[]',
    contacts_list JSONB DEFAULT '[]',
    biography JSONB DEFAULT '{"background": "", "appearance": "", "personality": "", "notes": ""}',
    campaign_id INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_played TIMESTAMP
);

CREATE INDEX idx_sr_characters_player ON sr_characters(player_name);
CREATE INDEX idx_sr_characters_metatype ON sr_characters(metatype_id);
CREATE INDEX idx_sr_characters_npc ON sr_characters(is_npc);
CREATE INDEX idx_sr_characters_search ON sr_characters USING gin(to_tsvector('english', name || ' ' || COALESCE(player_name, '')));

-- ----------------------------------------------------------------------------
-- CHARACTER SKILLS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_skills (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES sr_characters(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    rating INTEGER NOT NULL,
    specialization VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, skill_name, specialization)
);

CREATE INDEX idx_character_skills_character ON character_skills(character_id);

-- ----------------------------------------------------------------------------
-- CHARACTER SPELLS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_spells (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES sr_characters(id) ON DELETE CASCADE,
    spell_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    type VARCHAR(50),
    target VARCHAR(50),
    drain VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, spell_name)
);

CREATE INDEX idx_character_spells_character ON character_spells(character_id);

-- ----------------------------------------------------------------------------
-- CHARACTER POWERS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_powers (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES sr_characters(id) ON DELETE CASCADE,
    power_name VARCHAR(100) NOT NULL,
    level INTEGER DEFAULT 1,
    cost NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(character_id, power_name)
);

CREATE INDEX idx_character_powers_character ON character_powers(character_id);

-- ----------------------------------------------------------------------------
-- CHARACTER CONTACTS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_contacts (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES sr_characters(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    archetype VARCHAR(100),
    loyalty INTEGER,
    connection INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_character_contacts_character ON character_contacts(character_id);

-- ----------------------------------------------------------------------------
-- CHARACTER GEAR
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_gear (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES sr_characters(id) ON DELETE CASCADE,
    gear_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    quantity INTEGER DEFAULT 1,
    cost INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_character_gear_character ON character_gear(character_id);

-- ----------------------------------------------------------------------------
-- CHARACTER HISTORY
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS character_history (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES sr_characters(id) ON DELETE CASCADE,
    change_type VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    changed_by VARCHAR(200),
    changed_at TIMESTAMP DEFAULT NOW(),
    karma_spent INTEGER DEFAULT 0,
    session_date TIMESTAMP
);

CREATE INDEX idx_char_history_character ON character_history(character_id);
CREATE INDEX idx_char_history_type ON character_history(change_type);
CREATE INDEX idx_char_history_time ON character_history(changed_at);

-- ============================================================================
-- CHARACTER MODIFIERS SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS character_modifiers (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES sr_characters(id) ON DELETE CASCADE,
    modifier_target VARCHAR(50) NOT NULL,
    modifier_value INTEGER NOT NULL,
    modifier_type VARCHAR(20) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_id INTEGER,
    source_name VARCHAR(200),
    duration_type VARCHAR(20),
    duration_remaining INTEGER,
    expires_at TIMESTAMP,
    condition_text TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    modifier_data JSONB DEFAULT '{}',
    stacks_with TEXT[],
    replaces TEXT[],
    max_stack INTEGER,
    is_experimental BOOLEAN DEFAULT FALSE,
    is_unique BOOLEAN DEFAULT FALSE,
    is_homebrew BOOLEAN DEFAULT FALSE,
    requires_gm_approval BOOLEAN DEFAULT FALSE,
    notes TEXT,
    gm_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_char_mods_character ON character_modifiers(character_id);
CREATE INDEX idx_char_mods_target ON character_modifiers(modifier_target);
CREATE INDEX idx_char_mods_active ON character_modifiers(is_active);
CREATE INDEX idx_char_mods_source ON character_modifiers(source_type, source_id);
CREATE INDEX idx_char_mods_type ON character_modifiers(modifier_type);
CREATE INDEX idx_char_mods_expires ON character_modifiers(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_char_mods_data ON character_modifiers USING gin(modifier_data);

-- ============================================================================
-- HOUSE RULES SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS house_rules (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    rule_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    description TEXT,
    examples TEXT,
    notes TEXT,
    created_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(campaign_id, rule_name)
);

CREATE INDEX idx_house_rules_campaign ON house_rules(campaign_id);
CREATE INDEX idx_house_rules_type ON house_rules(rule_type);
CREATE INDEX idx_house_rules_active ON house_rules(is_active);
CREATE INDEX idx_house_rules_priority ON house_rules(priority DESC);
CREATE INDEX idx_house_rules_config ON house_rules USING gin(rule_config);

-- ----------------------------------------------------------------------------
-- RULE APPLICATION LOG
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rule_application_log (
    id SERIAL PRIMARY KEY,
    house_rule_id INTEGER REFERENCES house_rules(id) ON DELETE SET NULL,
    character_id INTEGER REFERENCES sr_characters(id) ON DELETE CASCADE,
    applied_to VARCHAR(50),
    original_cost INTEGER,
    modified_cost INTEGER,
    rule_config_snapshot JSONB,
    application_context JSONB,
    applied_at TIMESTAMP DEFAULT NOW(),
    applied_by VARCHAR(200)
);

CREATE INDEX idx_rule_app_log_rule ON rule_application_log(house_rule_id);
CREATE INDEX idx_rule_app_log_character ON rule_application_log(character_id);
CREATE INDEX idx_rule_app_log_time ON rule_application_log(applied_at);

-- ============================================================================
-- QUERY LOGGING SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    query_text TEXT NOT NULL,
    query_limit INTEGER,
    ranking_criteria TEXT,
    classification JSONB,
    intent TEXT,
    data_sources TEXT[],
    tables_queried TEXT[],
    execution_time_ms INTEGER,
    result_count INTEGER,
    error_message TEXT,
    user_feedback TEXT,
    feedback_notes TEXT,
    session_id TEXT,
    user_agent TEXT,
    is_training_data BOOLEAN DEFAULT FALSE,
    expected_intent VARCHAR(50),
    gm_response TEXT,
    dice_rolls JSONB,
    confidence NUMERIC,
    classification_method VARCHAR(20),
    training_source VARCHAR(100),
    is_correct BOOLEAN
);

CREATE INDEX idx_query_logs_intent ON query_logs(intent) WHERE intent IS NOT NULL;
CREATE INDEX idx_query_logs_feedback ON query_logs(user_feedback) WHERE user_feedback IS NOT NULL;
CREATE INDEX idx_query_logs_error ON query_logs(error_message) WHERE error_message IS NOT NULL;
CREATE INDEX idx_query_logs_training ON query_logs(is_training_data) WHERE is_training_data = TRUE;
CREATE INDEX idx_query_logs_expected_intent ON query_logs(expected_intent) WHERE expected_intent IS NOT NULL;
CREATE INDEX idx_query_logs_correct ON query_logs(is_correct) WHERE is_correct IS NOT NULL;
CREATE INDEX idx_query_logs_classification_method ON query_logs(classification_method) WHERE classification_method IS NOT NULL;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Character Modifier Functions
-- ----------------------------------------------------------------------------

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
      AND is_active = TRUE
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY modifier_type, modifier_value DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_modifier_total(char_id INTEGER, target_name VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    total INTEGER := 0;
BEGIN
    SELECT COALESCE(SUM(modifier_value), 0) INTO total
    FROM character_modifiers
    WHERE character_id = char_id
      AND modifier_target = target_name
      AND is_active = TRUE
      AND (expires_at IS NULL OR expires_at > NOW());
    
    RETURN total;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_augmented_attribute(char_id INTEGER, attr_name VARCHAR)
RETURNS JSONB AS $$
DECLARE
    base_value INTEGER;
    modifier_total INTEGER;
    result JSONB;
BEGIN
    SELECT (attributes->>attr_name)::INTEGER INTO base_value
    FROM sr_characters
    WHERE id = char_id;
    
    modifier_total := calculate_modifier_total(char_id, attr_name);
    
    result := jsonb_build_object(
        'base', base_value,
        'modifier', modifier_total,
        'augmented', base_value + modifier_total
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_combat_pool(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    quickness INTEGER;
    intelligence INTEGER;
    base_pool INTEGER;
    modifier_total INTEGER;
    result JSONB;
BEGIN
    SELECT (get_augmented_attribute(char_id, 'quickness')->>'augmented')::INTEGER INTO quickness;
    SELECT (get_augmented_attribute(char_id, 'intelligence')->>'augmented')::INTEGER INTO intelligence;
    
    base_pool := (quickness + intelligence) / 2;
    modifier_total := calculate_modifier_total(char_id, 'combat_pool');
    
    result := jsonb_build_object(
        'base', base_pool,
        'modifier', modifier_total,
        'total', base_pool + modifier_total
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_spell_pool(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    magic_rating INTEGER;
    base_pool INTEGER;
    modifier_total INTEGER;
    result JSONB;
BEGIN
    SELECT (get_augmented_attribute(char_id, 'magic')->>'augmented')::INTEGER INTO magic_rating;
    
    base_pool := magic_rating * 2;
    modifier_total := calculate_modifier_total(char_id, 'spell_pool');
    
    result := jsonb_build_object(
        'base', base_pool,
        'modifier', modifier_total,
        'total', base_pool + modifier_total
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_initiative(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    reaction INTEGER;
    base_dice INTEGER := 1;
    dice_modifiers INTEGER;
    result JSONB;
BEGIN
    SELECT (get_augmented_attribute(char_id, 'reaction')->>'augmented')::INTEGER INTO reaction;
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

CREATE OR REPLACE FUNCTION calculate_essence_cost(char_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    total_cost DECIMAL(3,2) := 0.00;
    cyberware_item JSONB;
BEGIN
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

CREATE OR REPLACE FUNCTION get_current_essence(char_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    base_essence DECIMAL(3,2) := 6.00;
    cyber_cost DECIMAL(3,2);
BEGIN
    cyber_cost := calculate_essence_cost(char_id);
    RETURN base_essence - cyber_cost;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION expire_temporary_modifiers()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE character_modifiers
    SET is_active = FALSE
    WHERE expires_at IS NOT NULL
      AND expires_at <= NOW()
      AND is_active = TRUE;
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrement_modifier_durations(rounds INTEGER DEFAULT 1)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE character_modifiers
    SET duration_remaining = duration_remaining - rounds
    WHERE duration_type IN ('rounds', 'minutes', 'hours')
      AND duration_remaining IS NOT NULL
      AND duration_remaining > 0
      AND is_active = TRUE;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    UPDATE character_modifiers
    SET is_active = FALSE
    WHERE duration_remaining IS NOT NULL
      AND duration_remaining <= 0
      AND is_active = TRUE;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- House Rules Functions
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_active_house_rules(camp_id INTEGER DEFAULT NULL, r_type VARCHAR DEFAULT NULL)
RETURNS TABLE (
    rule_id INTEGER,
    rule_name VARCHAR,
    rule_type VARCHAR,
    rule_config JSONB,
    priority INTEGER,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        house_rules.rule_name,
        house_rules.rule_type,
        house_rules.rule_config,
        house_rules.priority,
        house_rules.description
    FROM house_rules
    WHERE is_active = TRUE
      AND (campaign_id = camp_id OR (campaign_id IS NULL AND camp_id IS NULL))
      AND (r_type IS NULL OR house_rules.rule_type = r_type)
    ORDER BY priority DESC, id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION apply_karma_house_rules(base_cost INTEGER, camp_id INTEGER, cost_type VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    final_cost INTEGER := base_cost;
    rule RECORD;
    multiplier NUMERIC := 1.0;
BEGIN
    FOR rule IN 
        SELECT * FROM get_active_house_rules(camp_id, 'karma_multiplier')
    LOOP
        IF rule.rule_config->>'applies_to' IS NULL 
           OR rule.rule_config->'applies_to' @> to_jsonb(cost_type) THEN
            multiplier := multiplier * COALESCE((rule.rule_config->>'multiplier')::NUMERIC, 1.0);
        END IF;
    END LOOP;
    
    final_cost := FLOOR(base_cost * multiplier);
    RETURN final_cost;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_attribute_limit(camp_id INTEGER, metatype_id INTEGER, attr_name VARCHAR)
RETURNS INT4RANGE AS $$
DECLARE
    base_range INT4RANGE;
    rule RECORD;
    min_val INTEGER;
    max_val INTEGER;
BEGIN
    EXECUTE format('SELECT %I FROM metatypes WHERE id = $1', attr_name || '_range')
    INTO base_range
    USING metatype_id;
    
    min_val := lower(base_range);
    max_val := upper(base_range);
    
    FOR rule IN 
        SELECT * FROM get_active_house_rules(camp_id, 'attribute_limit')
    LOOP
        IF rule.rule_config->>'attribute' = attr_name THEN
            min_val := COALESCE((rule.rule_config->>'min_override')::INTEGER, min_val);
            max_val := COALESCE((rule.rule_config->>'max_override')::INTEGER, max_val);
        END IF;
    END LOOP;
    
    RETURN int4range(min_val, max_val, '[]');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION log_rule_application(
    rule_id INTEGER,
    char_id INTEGER,
    applied_to_type VARCHAR,
    orig_cost INTEGER,
    mod_cost INTEGER,
    context JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
DECLARE
    rule_snapshot JSONB;
BEGIN
    SELECT rule_config INTO rule_snapshot
    FROM house_rules
    WHERE id = rule_id;
    
    INSERT INTO rule_application_log (
        house_rule_id,
        character_id,
        applied_to,
        original_cost,
        modified_cost,
        rule_config_snapshot,
        application_context
    ) VALUES (
        rule_id,
        char_id,
        applied_to_type,
        orig_cost,
        mod_cost,
        rule_snapshot,
        context
    );
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- Gear Functions
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION search_gear(search_term TEXT, max_results INTEGER DEFAULT 10)
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

CREATE OR REPLACE FUNCTION find_similar_gear(item_name TEXT, item_category TEXT, similarity_threshold REAL DEFAULT 0.7)
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

-- ----------------------------------------------------------------------------
-- Query Helper Functions
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION normalize_query(query_text TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(TRIM(REGEXP_REPLACE(query_text, '\s+', ' ', 'g')));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION extract_keywords(query_text TEXT)
RETURNS TEXT[] AS $$
DECLARE
    words TEXT[];
    word TEXT;
    keywords TEXT[] := '{}';
    stop_words TEXT[] := ARRAY['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'];
BEGIN
    words := REGEXP_SPLIT_TO_ARRAY(LOWER(query_text), '\s+');
    
    FOREACH word IN ARRAY words
    LOOP
        IF LENGTH(word) > 3 AND NOT (word = ANY(stop_words)) THEN
            keywords := array_append(keywords, word);
        END IF;
    END LOOP;
    
    RETURN keywords;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_gear_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

CREATE OR REPLACE FUNCTION update_modifier_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_house_rule_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_query_correctness()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expected_intent IS NOT NULL THEN
        NEW.is_correct := (NEW.expected_intent = NEW.intent);
    ELSE
        NEW.is_correct := NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER gear_update_timestamp
    BEFORE UPDATE ON gear
    FOR EACH ROW
    EXECUTE FUNCTION update_gear_timestamp();

CREATE TRIGGER gear_search_vector_update
    BEFORE INSERT OR UPDATE ON gear
    FOR EACH ROW
    EXECUTE FUNCTION update_gear_search_vector();

CREATE TRIGGER trigger_update_modifier_timestamp
    BEFORE UPDATE ON character_modifiers
    FOR EACH ROW
    EXECUTE FUNCTION update_modifier_timestamp();

CREATE TRIGGER trigger_update_house_rule_timestamp
    BEFORE UPDATE ON house_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_house_rule_timestamp();

CREATE TRIGGER trigger_update_campaign_timestamp
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_house_rule_timestamp();

CREATE TRIGGER update_rules_content_updated_at
    BEFORE UPDATE ON rules_content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_query_correctness
    BEFORE INSERT OR UPDATE ON query_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_query_correctness();

-- ============================================================================
-- SCHEMA COMPLETE
-- ============================================================================
-- This schema includes all tables, indexes, functions, and triggers needed
-- for the Shadowrun GM system. Run this script in Supabase SQL Editor.
-- ============================================================================
