-- Migration 018: Add Force Column to Character Spells
-- Tracks the force at which each spell was learned
-- This is important for some campaigns/house rules

ALTER TABLE character_spells 
ADD COLUMN IF NOT EXISTS learned_force INTEGER;

-- Add comment
COMMENT ON COLUMN character_spells.learned_force IS 'Force at which the spell was learned (optional, some campaigns track this)';
