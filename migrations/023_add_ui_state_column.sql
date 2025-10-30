-- Migration 023: Add ui_state column to characters table
-- This column stores UI preferences and state for the character sheet

ALTER TABLE characters 
ADD COLUMN IF NOT EXISTS ui_state JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN characters.ui_state IS 'Stores UI preferences and state for character sheet display';
