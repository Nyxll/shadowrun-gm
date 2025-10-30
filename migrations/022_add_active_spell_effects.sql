-- Migration 022: Add Active Spell Effects Tracking
-- Tracks sustained spells, temporary effects, and permanent spell effects

-- Create active_spell_effects table
CREATE TABLE IF NOT EXISTS active_spell_effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    caster_id UUID REFERENCES characters(id) ON DELETE SET NULL,
    spell_name VARCHAR(100) NOT NULL,
    spell_class VARCHAR(50),
    effect_type VARCHAR(50) NOT NULL CHECK (effect_type IN ('instant', 'sustained', 'permanent', 'temporary')),
    force INTEGER NOT NULL CHECK (force > 0),
    magnitude INTEGER,
    target_attribute VARCHAR(50),
    effect_data JSONB DEFAULT '{}',
    is_sustained BOOLEAN DEFAULT false,
    sustained_by UUID REFERENCES characters(id) ON DELETE SET NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_active_effects_character 
    ON active_spell_effects(character_id) 
    WHERE ended_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_active_effects_sustained 
    ON active_spell_effects(sustained_by) 
    WHERE is_sustained = true AND ended_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_active_effects_caster 
    ON active_spell_effects(caster_id) 
    WHERE ended_at IS NULL;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_active_spell_effects_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_active_spell_effects_updated_at
    BEFORE UPDATE ON active_spell_effects
    FOR EACH ROW
    EXECUTE FUNCTION update_active_spell_effects_updated_at();

-- Add comments
COMMENT ON TABLE active_spell_effects IS 'Tracks active spell effects on characters, including sustained spells';
COMMENT ON COLUMN active_spell_effects.character_id IS 'Character affected by the spell';
COMMENT ON COLUMN active_spell_effects.caster_id IS 'Character who cast the spell (may be same as character_id)';
COMMENT ON COLUMN active_spell_effects.effect_type IS 'Type of effect: instant, sustained, permanent, or temporary';
COMMENT ON COLUMN active_spell_effects.force IS 'Force at which spell was cast';
COMMENT ON COLUMN active_spell_effects.magnitude IS 'Effect strength (e.g., successes for attribute increase, armor bonus)';
COMMENT ON COLUMN active_spell_effects.target_attribute IS 'Attribute affected (for attribute modifier spells)';
COMMENT ON COLUMN active_spell_effects.effect_data IS 'Flexible JSONB storage for spell-specific effect data';
COMMENT ON COLUMN active_spell_effects.is_sustained IS 'True if spell requires active sustaining';
COMMENT ON COLUMN active_spell_effects.sustained_by IS 'Character sustaining the spell (usually caster_id)';
COMMENT ON COLUMN active_spell_effects.ended_at IS 'When effect ended (NULL = still active)';
