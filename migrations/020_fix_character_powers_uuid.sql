-- Migration: Fix character_powers to use UUID for character_id
-- This makes it consistent with all other character-related tables

BEGIN;

-- Step 1: Check if character_powers exists and has data
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'character_powers') THEN
        -- Step 2: Add new UUID column
        ALTER TABLE character_powers ADD COLUMN character_id_uuid UUID;
        
        -- Step 3: Populate UUID column by looking up from characters table
        -- Match on the integer ID if possible, otherwise leave NULL
        UPDATE character_powers cp
        SET character_id_uuid = c.id
        FROM characters c
        WHERE cp.character_id::text = c.id::text
           OR cp.character_id = (c.id::text::int);  -- Try both approaches
        
        -- Step 4: Drop old integer column
        ALTER TABLE character_powers DROP COLUMN character_id;
        
        -- Step 5: Rename UUID column to character_id
        ALTER TABLE character_powers RENAME COLUMN character_id_uuid TO character_id;
        
        -- Step 6: Add NOT NULL constraint
        ALTER TABLE character_powers ALTER COLUMN character_id SET NOT NULL;
        
        -- Step 7: Add foreign key constraint
        ALTER TABLE character_powers 
        ADD CONSTRAINT fk_character_powers_character 
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE;
        
        -- Step 8: Create index for performance
        CREATE INDEX IF NOT EXISTS idx_character_powers_character_id 
        ON character_powers(character_id);
        
        RAISE NOTICE 'Successfully migrated character_powers.character_id to UUID';
    ELSE
        RAISE NOTICE 'Table character_powers does not exist, skipping migration';
    END IF;
END $$;

COMMIT;
