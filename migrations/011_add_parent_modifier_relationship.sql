-- Migration 011: Add parent-child relationship to character_modifiers
-- This enables proper linking of augmentation items to their effects

-- Add parent_modifier_id column
ALTER TABLE character_modifiers 
ADD COLUMN IF NOT EXISTS parent_modifier_id UUID REFERENCES character_modifiers(id) ON DELETE CASCADE;

-- Add essence_cost column (move from JSONB to proper column for cyberware)
ALTER TABLE character_modifiers 
ADD COLUMN IF NOT EXISTS essence_cost DECIMAL(3,2);

-- Create index for parent-child lookups
CREATE INDEX IF NOT EXISTS idx_modifiers_parent ON character_modifiers(parent_modifier_id);

-- Add comments
COMMENT ON COLUMN character_modifiers.parent_modifier_id IS 'Links child modifiers (effects) to parent augmentation entry';
COMMENT ON COLUMN character_modifiers.essence_cost IS 'Essence cost for cyberware parent entries';
COMMENT ON COLUMN character_modifiers.modifier_data IS 'JSONB for bioware body_index_cost and other complex data';
