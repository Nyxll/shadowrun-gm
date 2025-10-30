-- Migration 022: Add Spell Effect Helper Columns to character_modifiers
-- Adds columns to better track sustained spells and spell effects

-- Add helper columns for spell tracking
ALTER TABLE character_modifiers 
ADD COLUMN IF NOT EXISTS spell_force INTEGER,
ADD COLUMN IF NOT EXISTS is_sustained BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS sustained_by UUID REFERENCES characters(id) ON DELETE SET NULL;

-- Create index for sustained spells
CREATE INDEX IF NOT EXISTS idx_modifiers_sustained 
    ON character_modifiers(sustained_by) 
    WHERE is_sustained = true AND deleted_at IS NULL;

-- Create index for spell effects
CREATE INDEX IF NOT EXISTS idx_modifiers_spell_effects
    ON character_modifiers(character_id, source_type)
    WHERE source_type = 'spell' AND deleted_at IS NULL;

-- Add comments
COMMENT ON COLUMN character_modifiers.spell_force IS 'Force at which spell was cast (for spell effects)';
COMMENT ON COLUMN character_modifiers.is_sustained IS 'True if this is a sustained spell effect';
COMMENT ON COLUMN character_modifiers.sustained_by IS 'Character sustaining the spell (usually caster)';
