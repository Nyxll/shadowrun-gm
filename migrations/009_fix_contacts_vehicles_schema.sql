-- ============================================================================
-- Migration 009: Fix character_contacts and character_vehicles to use UUID
-- The tables existed with INTEGER character_id, need to convert to UUID
-- ============================================================================

-- Drop and recreate character_contacts with correct schema
DROP TABLE IF EXISTS character_contacts CASCADE;

CREATE TABLE character_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    archetype TEXT,
    loyalty INTEGER,
    connection INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contacts_character ON character_contacts(character_id);

-- Drop and recreate character_vehicles with correct schema
DROP TABLE IF EXISTS character_vehicles CASCADE;

CREATE TABLE character_vehicles (
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

CREATE INDEX idx_vehicles_character ON character_vehicles(character_id);

-- Add comments
COMMENT ON TABLE character_contacts IS 'Character contacts with roles and levels';
COMMENT ON TABLE character_vehicles IS 'Character vehicles and drones';
