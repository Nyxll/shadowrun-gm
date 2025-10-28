-- Migration: Add character_cyberdecks table
-- Stores cyberdeck details for decker characters

CREATE TABLE IF NOT EXISTS character_cyberdecks (
    id SERIAL PRIMARY KEY,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    deck_name VARCHAR(255) NOT NULL,
    mpcp INTEGER,
    hardening INTEGER,
    memory INTEGER,  -- in MP
    storage INTEGER,  -- in MP
    io_speed INTEGER,
    response_increase INTEGER,
    -- Persona programs stored as JSONB
    persona_programs JSONB DEFAULT '{}'::jsonb,
    -- Utilities and special features
    utilities JSONB DEFAULT '{}'::jsonb,
    -- AI companions
    ai_companions JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_cyberdecks_character ON character_cyberdecks(character_id);

COMMENT ON TABLE character_cyberdecks IS 'Cyberdeck details for decker characters';
COMMENT ON COLUMN character_cyberdecks.mpcp IS 'Master Persona Control Program rating';
COMMENT ON COLUMN character_cyberdecks.hardening IS 'Deck hardening rating';
COMMENT ON COLUMN character_cyberdecks.memory IS 'Active memory in MP';
COMMENT ON COLUMN character_cyberdecks.storage IS 'Storage memory in MP';
COMMENT ON COLUMN character_cyberdecks.io_speed IS 'I/O speed rating';
COMMENT ON COLUMN character_cyberdecks.response_increase IS 'Response increase modifier';
COMMENT ON COLUMN character_cyberdecks.persona_programs IS 'Persona programs (Bod, Evasion, Masking, Sensor) as JSONB';
COMMENT ON COLUMN character_cyberdecks.utilities IS 'Utility programs and special features as JSONB';
COMMENT ON COLUMN character_cyberdecks.ai_companions IS 'AI companions/knowbots as JSONB array';
