-- Migration 017: Add Missing Magic Fields
-- Adds magic_pool, spell_pool, initiate_level, metamagics, magical_group, tradition

ALTER TABLE characters 
ADD COLUMN IF NOT EXISTS magic_pool INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS spell_pool INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS initiate_level INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS metamagics TEXT[],
ADD COLUMN IF NOT EXISTS magical_group TEXT,
ADD COLUMN IF NOT EXISTS tradition TEXT;

-- Add comments
COMMENT ON COLUMN characters.magic_pool IS 'Magic Pool dice available for spellcasting and drain resistance';
COMMENT ON COLUMN characters.spell_pool IS 'Spell Pool dice (if applicable)';
COMMENT ON COLUMN characters.initiate_level IS 'Initiate grade/level for initiated mages';
COMMENT ON COLUMN characters.metamagics IS 'Array of metamagic techniques (centering, quickening, anchoring, etc.)';
COMMENT ON COLUMN characters.magical_group IS 'Magical group/lodge membership';
COMMENT ON COLUMN characters.tradition IS 'Magical tradition (Shamanic, Hermetic, etc.)';
