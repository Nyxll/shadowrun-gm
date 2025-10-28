-- Migration 012: Add body_index_cost column for bioware
-- Matches essence_cost column for cyberware - proper symmetry

-- Add body_index_cost column
ALTER TABLE character_modifiers
ADD COLUMN body_index_cost DECIMAL(4,2);

COMMENT ON COLUMN character_modifiers.body_index_cost IS 
'Body Index cost for bioware augmentations (parent entries only). Parallel to essence_cost for cyberware.';

-- Migrate existing data from modifier_data JSONB to dedicated column
UPDATE character_modifiers
SET body_index_cost = (modifier_data->>'body_index_cost')::DECIMAL(4,2)
WHERE modifier_type = 'augmentation'
  AND source_type = 'bioware'
  AND modifier_data IS NOT NULL
  AND modifier_data->>'body_index_cost' IS NOT NULL;

-- Verify migration
DO $$
DECLARE
    migrated_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO migrated_count
    FROM character_modifiers
    WHERE modifier_type = 'augmentation'
      AND source_type = 'bioware'
      AND body_index_cost IS NOT NULL;
    
    RAISE NOTICE 'Migrated % bioware items to body_index_cost column', migrated_count;
END $$;
