-- ============================================================================
-- Migration 008: Add Complete Character Schema Support
-- Adds all missing columns and tables to support full character data
-- ============================================================================

-- Add missing columns to characters table
ALTER TABLE characters 
ADD COLUMN IF NOT EXISTS metatype TEXT,
ADD COLUMN IF NOT EXISTS sex TEXT,
ADD COLUMN IF NOT EXISTS age TEXT,
ADD COLUMN IF NOT EXISTS height TEXT,
ADD COLUMN IF NOT EXISTS weight TEXT,
ADD COLUMN IF NOT EXISTS hair TEXT,
ADD COLUMN IF NOT EXISTS eyes TEXT,
ADD COLUMN IF NOT EXISTS skin TEXT,
ADD COLUMN IF NOT EXISTS karma_available INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS lifestyle TEXT,
ADD COLUMN IF NOT EXISTS lifestyle_cost INTEGER,
ADD COLUMN IF NOT EXISTS lifestyle_months_prepaid INTEGER,
ADD COLUMN IF NOT EXISTS essence_hole DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS background TEXT,
ADD COLUMN IF NOT EXISTS combat_pool INTEGER,
ADD COLUMN IF NOT EXISTS body_index_current DECIMAL(4,2),
ADD COLUMN IF NOT EXISTS body_index_max DECIMAL(4,2);

-- Add skill_type column to character_skills
ALTER TABLE character_skills
ADD COLUMN IF NOT EXISTS skill_type TEXT DEFAULT 'active';

-- Add cost columns to character_modifiers
ALTER TABLE character_modifiers
ADD COLUMN IF NOT EXISTS essence_cost DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS body_index_cost DECIMAL(4,2);

-- Add weapon-specific columns to character_gear
ALTER TABLE character_gear
ADD COLUMN IF NOT EXISTS damage TEXT,
ADD COLUMN IF NOT EXISTS conceal TEXT,
ADD COLUMN IF NOT EXISTS ammo_capacity TEXT,
ADD COLUMN IF NOT EXISTS ballistic_rating INTEGER,
ADD COLUMN IF NOT EXISTS impact_rating INTEGER;

-- Create character_vehicles table
CREATE TABLE IF NOT EXISTS character_vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    vehicle_name TEXT NOT NULL,
    vehicle_type TEXT,
    handling TEXT,
    speed INTEGER,
    body INTEGER,
    armor INTEGER,
    signature INTEGER,
    pilot INTEGER,
    modifications JSONB DEFAULT '{}'::jsonb,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicles_character ON character_vehicles(character_id);

-- Create character_contacts table
CREATE TABLE IF NOT EXISTS character_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    contact_name TEXT NOT NULL,
    role TEXT,
    level INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contacts_character ON character_contacts(character_id);

-- Create character_edges_flaws table
CREATE TABLE IF NOT EXISTS character_edges_flaws (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'edge' or 'flaw'
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edges_flaws_character ON character_edges_flaws(character_id);
CREATE INDEX IF NOT EXISTS idx_edges_flaws_type ON character_edges_flaws(type);

-- Create character_spells table
CREATE TABLE IF NOT EXISTS character_spells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    spell_name TEXT NOT NULL,
    force INTEGER,
    category TEXT,
    target_type TEXT,
    drain_code TEXT,
    is_quickened BOOLEAN DEFAULT FALSE,
    quickened_successes INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spells_character ON character_spells(character_id);

-- Add comments
COMMENT ON COLUMN characters.metatype IS 'Character metatype (Human, Elf, Dwarf, Ork, Troll)';
COMMENT ON COLUMN characters.karma_available IS 'Karma available to spend';
COMMENT ON COLUMN characters.lifestyle IS 'Lifestyle type (Street, Squatter, Low, Middle, High, Luxury)';
COMMENT ON COLUMN characters.essence_hole IS 'Essence lost that cannot be regained';
COMMENT ON COLUMN characters.combat_pool IS 'Calculated combat pool (Quickness/2)';
COMMENT ON COLUMN characters.body_index_current IS 'Current body index used by bioware';
COMMENT ON COLUMN characters.body_index_max IS 'Maximum body index (Body + Willpower)';

COMMENT ON COLUMN character_skills.skill_type IS 'Type of skill: active, knowledge, or language';

COMMENT ON COLUMN character_modifiers.essence_cost IS 'Essence cost for cyberware';
COMMENT ON COLUMN character_modifiers.body_index_cost IS 'Body index cost for bioware';

COMMENT ON TABLE character_vehicles IS 'Character vehicles and drones';
COMMENT ON TABLE character_contacts IS 'Character contacts with roles and levels';
COMMENT ON TABLE character_edges_flaws IS 'Character edges and flaws from Shadowrun Companion';
COMMENT ON TABLE character_spells IS 'Character spells for mages';
