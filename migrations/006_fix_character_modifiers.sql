-- Migration: Fix Character Modifiers and Add House Rules
-- Date: 2025-10-21
-- Description: Correct modifier parsing errors and add house rule cyberware entries

BEGIN;

-- ============================================================================
-- PART 1: Fix Platinum's Modifiers
-- ============================================================================

-- Get Platinum's character ID
DO $$
DECLARE
    platinum_id UUID;
BEGIN
    SELECT id INTO platinum_id FROM characters WHERE street_name = 'Platinum';
    
    -- Delete incorrect modifiers
    DELETE FROM character_modifiers 
    WHERE character_id = platinum_id;
    
    -- Add corrected modifiers
    
    -- Wired Reflexes 3 (Beta-Grade)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES 
        (platinum_id, 'initiative_dice', 'initiative', 3, 'Wired Reflexes 3 (Beta-Grade)', 'cyberware', true),
        (platinum_id, 'attribute', 'reaction', 6, 'Wired Reflexes 3 (Beta-Grade)', 'cyberware', true);
    
    -- Reaction Enhancers 6 (Delta-Grade)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (platinum_id, 'attribute', 'reaction', 6, 'Reaction Enhancers 6 (Delta-Grade)', 'cyberware', true);
    
    -- Smartlink-2 AEGIS (house rule - updated name)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, is_homebrew)
    VALUES 
        (platinum_id, 'tn_modifier', 'firearms', -3, 'Smartlink-2 AEGIS', 'cyberware', true, true),
        (platinum_id, 'skill_dice', 'gunnery', 1, 'Smartlink-2 AEGIS', 'cyberware', true, true);
    
    -- Datajack (Delta-Grade)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (platinum_id, 'pool', 'task_pool', 1, 'Datajack (Delta-Grade)', 'cyberware', true);
    
    -- Cybereyes (missing modifiers for vision enhancements)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, modifier_data)
    VALUES (platinum_id, 'vision', 'cybereyes', 0, 'Cybereyes', 'cyberware', true, 
            '{"thermographic": true, "vision_magnification": 3, "lowlight": true, "flare_compensation": true, "negates_glare": true, "negates_blinding": true}'::jsonb);
    
    -- Enhanced Articulation (corrected)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES 
        (platinum_id, 'attribute', 'reaction', 1, 'Enhanced Articulation', 'bioware', true),
        (platinum_id, 'skill_dice', 'athletics', 1, 'Enhanced Articulation', 'bioware', true);
    
    -- Cerebral Booster 3 (house rule - corrected)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, is_homebrew)
    VALUES 
        (platinum_id, 'attribute', 'intelligence', 3, 'Cerebral Booster 3', 'bioware', true, true),
        (platinum_id, 'pool', 'task_pool', 1, 'Cerebral Booster 3', 'bioware', true, true);
    
    -- Supra-Thyroid Gland (corrected - adds to all physical attributes)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES 
        (platinum_id, 'attribute', 'body', 1, 'Supra-Thyroid Gland', 'bioware', true),
        (platinum_id, 'attribute', 'quickness', 1, 'Supra-Thyroid Gland', 'bioware', true),
        (platinum_id, 'attribute', 'strength', 1, 'Supra-Thyroid Gland', 'bioware', true),
        (platinum_id, 'attribute', 'reaction', 1, 'Supra-Thyroid Gland', 'bioware', true);
    
    -- Muscle Augmentation 4 (corrected - adds to both Quickness AND Strength)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES 
        (platinum_id, 'attribute', 'quickness', 4, 'Muscle Augmentation 4', 'bioware', true),
        (platinum_id, 'attribute', 'strength', 4, 'Muscle Augmentation 4', 'bioware', true);
    
    -- Mnemonic Enhancer 4
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (platinum_id, 'skill_dice', 'knowledge_language', 2, 'Mnemonic Enhancer 4', 'bioware', true);
    
    -- Reflex Recorder (Firearms) - missing modifier
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (platinum_id, 'skill_dice', 'firearms', 1, 'Reflex Recorder (Firearms)', 'cyberware', true);
    
END $$;

-- ============================================================================
-- PART 2: Fix Oak's Spell Modifiers
-- ============================================================================

DO $$
DECLARE
    oak_id UUID;
BEGIN
    SELECT id INTO oak_id FROM characters WHERE street_name = 'Oak';
    
    -- Delete all current spell modifiers
    DELETE FROM character_modifiers 
    WHERE character_id = oak_id;
    
    -- Add corrected spell modifiers
    
    -- Increase Reflexes 3 (Spell Lock) - only initiative dice, NO reaction
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (oak_id, 'initiative_dice', 'initiative', 3, 'Spell Lock: Increase Reflexes 3', 'spell', true);
    
    -- Increase Attribute+4 for Charisma (Quickened)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (oak_id, 'attribute', 'charisma', 4, 'Quickened: Increase Attribute+4 (Charisma)', 'spell', true);
    
    -- Increase Attribute+4 for Intelligence (Quickened)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (oak_id, 'attribute', 'intelligence', 4, 'Quickened: Increase Attribute+4 (Intelligence)', 'spell', true);
    
    -- Increase Attribute+4 for Willpower (Spell Lock - changed from Quickened)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (oak_id, 'attribute', 'willpower', 4, 'Spell Lock: Increase Attribute+4 (Willpower)', 'spell', true);
    
END $$;

-- ============================================================================
-- PART 3: Add House Rule Cyberware Entries
-- ============================================================================

-- First, delete any existing house rules with these names, then insert fresh
DELETE FROM house_rules WHERE rule_name IN ('Cerebral Booster 3', 'NeuroSync Processor', 'Smartlink-2 AEGIS', 'Smartlink-3 Prototype');

INSERT INTO house_rules (rule_name, rule_type, description, is_active, created_at)
VALUES 
    ('Cerebral Booster 3', 'custom', 'Enhanced cerebral booster beyond standard Shadowtech rules. Provides +3 Intelligence and +1 Task Pool. Only 2 exist in standard rules, but campaign has 3 characters with this upgrade.', true, NOW()),
    ('NeuroSync Processor', 'custom', 'Completely custom house-ruled cyberware for Edom/Manticore. Provides enhanced matrix and mental processing capabilities.', true, NOW()),
    ('Smartlink-2 AEGIS', 'custom', 'Project AEGIS enhanced smartlink system. Provides standard smartlink-2 benefits (-3 TN firearms) plus +1 dice to Gunnery skill.', true, NOW()),
    ('Smartlink-3 Prototype', 'custom', 'Prototype smartlink-3 system for Axel. Provides enhanced targeting beyond standard smartlink-2.', true, NOW());

-- Link house rule cyberware to character modifiers
DO $$
DECLARE
    cerebral_rule_id INTEGER;
    neurosync_rule_id INTEGER;
    aegis_rule_id INTEGER;
    prototype_rule_id INTEGER;
    platinum_id UUID;
    manticore_id UUID;
    axel_id UUID;
BEGIN
    -- Get house rule IDs
    SELECT id INTO cerebral_rule_id FROM house_rules WHERE rule_name = 'Cerebral Booster 3';
    SELECT id INTO neurosync_rule_id FROM house_rules WHERE rule_name = 'NeuroSync Processor';
    SELECT id INTO aegis_rule_id FROM house_rules WHERE rule_name = 'Smartlink-2 AEGIS';
    SELECT id INTO prototype_rule_id FROM house_rules WHERE rule_name = 'Smartlink-3 Prototype';
    
    -- Get character IDs
    SELECT id INTO platinum_id FROM characters WHERE street_name = 'Platinum';
    SELECT id INTO manticore_id FROM characters WHERE street_name = 'Manticore';
    SELECT id INTO axel_id FROM characters WHERE street_name = 'Axel';
    
    -- Link Cerebral Booster 3 to all three characters
    UPDATE character_modifiers 
    SET house_rule_id = cerebral_rule_id
    WHERE source = 'Cerebral Booster 3' 
    AND character_id IN (platinum_id, manticore_id, axel_id);
    
    -- Link NeuroSync Processor to Manticore
    UPDATE character_modifiers 
    SET house_rule_id = neurosync_rule_id, is_homebrew = true
    WHERE source LIKE 'NeuroSync%' 
    AND character_id = manticore_id;
    
    -- Link Smartlink-2 AEGIS to Platinum
    UPDATE character_modifiers 
    SET house_rule_id = aegis_rule_id
    WHERE source = 'Smartlink-2 AEGIS' 
    AND character_id = platinum_id;
    
    -- Link Smartlink-3 Prototype to Axel
    UPDATE character_modifiers 
    SET house_rule_id = prototype_rule_id, is_homebrew = true
    WHERE source LIKE 'Smartlink-3%' 
    AND character_id = axel_id;
    
END $$;

COMMIT;

-- Verification queries
SELECT 'Platinum Modifiers:' as info;
SELECT cm.source, cm.modifier_type, cm.target_name, cm.modifier_value, cm.is_homebrew, hr.rule_name as house_rule
FROM character_modifiers cm
JOIN characters c ON cm.character_id = c.id
LEFT JOIN house_rules hr ON cm.house_rule_id = hr.id
WHERE c.street_name = 'Platinum'
ORDER BY cm.source;

SELECT 'Oak Modifiers:' as info;
SELECT cm.source, cm.modifier_type, cm.target_name, cm.modifier_value
FROM character_modifiers cm
JOIN characters c ON cm.character_id = c.id
WHERE c.street_name = 'Oak'
ORDER BY cm.source;
