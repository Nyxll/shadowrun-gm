-- ============================================================================
-- HOUSE RULES MANAGEMENT SYSTEM
-- ============================================================================
-- Flexible system for storing and applying custom campaign rules
-- Supports karma multipliers, attribute limits, skill costs, and custom mechanics
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
    
    -- Campaign status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'on_hold', 'completed', 'archived')),
    
    -- Dates
    start_date DATE,
    last_session DATE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_gm ON campaigns(gm_name);

-- ----------------------------------------------------------------------------
-- HOUSE RULES: Custom rule modifications
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS house_rules (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,  -- NULL = global rule
    
    -- Rule identification
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50) NOT NULL CHECK (rule_type IN (
        'karma_multiplier',
        'attribute_limit',
        'skill_cost',
        'essence_cost',
        'initiation_cost',
        'spell_cost',
        'power_cost',
        'gear_cost',
        'healing_rate',
        'damage_modifier',
        'custom'
    )),
    
    -- Rule configuration (flexible JSONB)
    rule_config JSONB DEFAULT '{}',
    
    -- Rule state
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,  -- Higher priority rules apply first
    
    -- Documentation
    description TEXT,
    examples TEXT,
    notes TEXT,
    
    -- Metadata
    created_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_campaign_rule_name UNIQUE(campaign_id, rule_name)
);

CREATE INDEX idx_house_rules_campaign ON house_rules(campaign_id);
CREATE INDEX idx_house_rules_type ON house_rules(rule_type);
CREATE INDEX idx_house_rules_active ON house_rules(is_active);
CREATE INDEX idx_house_rules_priority ON house_rules(priority DESC);

-- GIN index for JSONB rule_config
CREATE INDEX idx_house_rules_config ON house_rules USING gin(rule_config);

-- ----------------------------------------------------------------------------
-- RULE APPLICATION LOG: Track when rules are applied
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rule_application_log (
    id SERIAL PRIMARY KEY,
    house_rule_id INTEGER REFERENCES house_rules(id) ON DELETE SET NULL,
    character_id INTEGER REFERENCES sr_characters(id) ON DELETE CASCADE,
    
    -- What was affected
    applied_to VARCHAR(50),  -- 'attribute_increase', 'skill_learn', etc.
    original_cost INTEGER,
    modified_cost INTEGER,
    
    -- Context
    rule_config_snapshot JSONB,  -- Snapshot of rule config at time of application
    application_context JSONB,   -- Additional context about the application
    
    -- Metadata
    applied_at TIMESTAMP DEFAULT NOW(),
    applied_by VARCHAR(200)
);

CREATE INDEX idx_rule_app_log_rule ON rule_application_log(house_rule_id);
CREATE INDEX idx_rule_app_log_character ON rule_application_log(character_id);
CREATE INDEX idx_rule_app_log_time ON rule_application_log(applied_at);

-- ----------------------------------------------------------------------------
-- HELPER FUNCTIONS
-- ----------------------------------------------------------------------------

-- Function to get active house rules for a campaign
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
    WHERE is_active = true
      AND (campaign_id = camp_id OR (campaign_id IS NULL AND camp_id IS NULL))
      AND (r_type IS NULL OR house_rules.rule_type = r_type)
    ORDER BY priority DESC, id;
END;
$$ LANGUAGE plpgsql;

-- Function to apply karma multiplier from house rules
CREATE OR REPLACE FUNCTION apply_karma_house_rules(
    base_cost INTEGER,
    camp_id INTEGER,
    cost_type VARCHAR  -- 'attribute', 'skill', 'spell', etc.
)
RETURNS INTEGER AS $$
DECLARE
    final_cost INTEGER := base_cost;
    rule RECORD;
    multiplier NUMERIC := 1.0;
BEGIN
    -- Get all active karma multiplier rules
    FOR rule IN 
        SELECT * FROM get_active_house_rules(camp_id, 'karma_multiplier')
    LOOP
        -- Check if this rule applies to the cost type
        IF rule.rule_config->>'applies_to' IS NULL 
           OR rule.rule_config->'applies_to' @> to_jsonb(cost_type) THEN
            multiplier := multiplier * COALESCE((rule.rule_config->>'multiplier')::NUMERIC, 1.0);
        END IF;
    END LOOP;
    
    final_cost := FLOOR(base_cost * multiplier);
    
    RETURN final_cost;
END;
$$ LANGUAGE plpgsql;

-- Function to check attribute limit overrides
CREATE OR REPLACE FUNCTION get_attribute_limit(
    camp_id INTEGER,
    metatype_id INTEGER,
    attr_name VARCHAR
)
RETURNS INT4RANGE AS $$
DECLARE
    base_range INT4RANGE;
    rule RECORD;
    min_val INTEGER;
    max_val INTEGER;
BEGIN
    -- Get base range from metatype
    EXECUTE format('SELECT %I FROM metatypes WHERE id = $1', attr_name || '_range')
    INTO base_range
    USING metatype_id;
    
    min_val := lower(base_range);
    max_val := upper(base_range);
    
    -- Check for house rule overrides
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

-- Function to log rule application
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
    -- Get current rule config
    SELECT rule_config INTO rule_snapshot
    FROM house_rules
    WHERE id = rule_id;
    
    -- Insert log entry
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
-- VIEWS
-- ----------------------------------------------------------------------------

-- View: Campaign summary with active rules count
CREATE OR REPLACE VIEW campaign_summary AS
SELECT 
    c.id,
    c.name,
    c.gm_name,
    c.status,
    c.start_date,
    c.last_session,
    COUNT(DISTINCT hr.id) as active_rules_count,
    COUNT(DISTINCT sc.id) as character_count
FROM campaigns c
LEFT JOIN house_rules hr ON hr.campaign_id = c.id AND hr.is_active = true
LEFT JOIN sr_characters sc ON sc.campaign_id = c.id AND sc.status = 'active'
GROUP BY c.id, c.name, c.gm_name, c.status, c.start_date, c.last_session;

-- View: Rule application statistics
CREATE OR REPLACE VIEW rule_application_stats AS
SELECT 
    hr.id as rule_id,
    hr.rule_name,
    hr.rule_type,
    hr.campaign_id,
    COUNT(ral.id) as times_applied,
    AVG(ral.modified_cost - ral.original_cost) as avg_cost_change,
    MIN(ral.applied_at) as first_applied,
    MAX(ral.applied_at) as last_applied
FROM house_rules hr
LEFT JOIN rule_application_log ral ON ral.house_rule_id = hr.id
GROUP BY hr.id, hr.rule_name, hr.rule_type, hr.campaign_id;

-- ----------------------------------------------------------------------------
-- TRIGGERS
-- ----------------------------------------------------------------------------

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_house_rule_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_house_rule_timestamp
    BEFORE UPDATE ON house_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_house_rule_timestamp();

CREATE TRIGGER trigger_update_campaign_timestamp
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_house_rule_timestamp();

-- ----------------------------------------------------------------------------
-- SAMPLE DATA / TEMPLATES
-- ----------------------------------------------------------------------------

-- Common house rule templates (commented out - uncomment to use)
/*
-- Half karma costs for all character advancement
INSERT INTO house_rules (rule_name, rule_type, rule_config, description, is_active)
VALUES (
    'Half Karma Costs',
    'karma_multiplier',
    '{"multiplier": 0.5, "applies_to": ["attribute", "skill", "spell", "power", "initiation"]}',
    'All karma costs are halved to speed up character advancement',
    false
);

-- Increased attribute caps
INSERT INTO house_rules (rule_name, rule_type, rule_config, description, is_active)
VALUES (
    'Heroic Attributes',
    'attribute_limit',
    '{"attribute": "all", "max_override": 12}',
    'All attributes can be raised to 12 instead of racial maximums',
    false
);

-- Cheaper knowledge skills
INSERT INTO house_rules (rule_name, rule_type, rule_config, description, is_active)
VALUES (
    'Cheap Knowledge Skills',
    'skill_cost',
    '{"skill_category": "knowledge", "cost_multiplier": 0.5}',
    'Knowledge skills cost half the normal karma',
    false
);

-- Reduced essence cost for cyberware
INSERT INTO house_rules (rule_name, rule_type, rule_config, description, is_active)
VALUES (
    'Biocompatible Cyberware',
    'essence_cost',
    '{"cyberware_multiplier": 0.8, "bioware_multiplier": 0.5}',
    'Cyberware costs 80% essence, bioware costs 50%',
    false
);

-- Faster healing
INSERT INTO house_rules (rule_name, rule_type, rule_config, description, is_active)
VALUES (
    'Fast Healing',
    'healing_rate',
    '{"multiplier": 24, "applies_to": ["physical", "stun"]}',
    'Characters heal 1 box per hour instead of per day',
    false
);
*/

-- ----------------------------------------------------------------------------
-- COMMENTS
-- ----------------------------------------------------------------------------

COMMENT ON TABLE campaigns IS 'Campaign/game tracking for organizing characters and house rules';
COMMENT ON TABLE house_rules IS 'Custom rule modifications for campaigns (karma costs, limits, etc.)';
COMMENT ON TABLE rule_application_log IS 'Audit trail of when house rules are applied to characters';

COMMENT ON COLUMN house_rules.rule_config IS 'JSONB configuration - structure varies by rule_type';
COMMENT ON COLUMN house_rules.priority IS 'Higher priority rules apply first (useful for stacking rules)';

COMMENT ON FUNCTION get_active_house_rules IS 'Get all active house rules for a campaign, optionally filtered by type';
COMMENT ON FUNCTION apply_karma_house_rules IS 'Apply karma multiplier house rules to a base cost';
COMMENT ON FUNCTION get_attribute_limit IS 'Get attribute limits with house rule overrides applied';
COMMENT ON FUNCTION log_rule_application IS 'Log when a house rule is applied to a character';
