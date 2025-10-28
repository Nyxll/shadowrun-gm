-- Migration: Add Missing Modifiers for Axel and Manticore
-- Date: 2025-10-21
-- Description: Add cybereye vision enhancements and missing modifiers

BEGIN;

-- ============================================================================
-- PART 1: Add Missing Modifiers for Axel
-- ============================================================================

DO $$
DECLARE
    axel_id UUID;
    cerebral_rule_id INTEGER;
BEGIN
    SELECT id INTO axel_id FROM characters WHERE street_name = 'Axel';
    SELECT id INTO cerebral_rule_id FROM house_rules WHERE rule_name = 'Cerebral Booster 3';
    
    -- Add Cybereyes vision enhancements
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, modifier_data)
    VALUES (axel_id, 'vision', 'cybereyes', 0, 'Cybereyes', 'cyberware', true, 
            '{"thermographic": true, "vision_magnification": 3, "lowlight": true}'::jsonb);
    
    -- Add Datajack Task Pool bonus (Delta grade)
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent)
    VALUES (axel_id, 'pool', 'task_pool', 1, 'Datajack (Delta-Grade)', 'cyberware', true);
    
    -- Update Cerebral Booster to add Task Pool and link to house rule
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, is_homebrew, house_rule_id)
    VALUES (axel_id, 'pool', 'task_pool', 1, 'Cerebral Booster', 'bioware', true, true, cerebral_rule_id);
    
    -- Update existing Cerebral Booster to link to house rule
    UPDATE character_modifiers 
    SET house_rule_id = cerebral_rule_id, is_homebrew = true
    WHERE character_id = axel_id AND source = 'Cerebral Booster';
    
END $$;

-- ============================================================================
-- PART 2: Fix Manticore's Smartlink-3 to mark as homebrew
-- ============================================================================

DO $$
DECLARE
    manticore_id UUID;
    prototype_rule_id INTEGER;
BEGIN
    SELECT id INTO manticore_id FROM characters WHERE street_name = 'Manticore';
    SELECT id INTO prototype_rule_id FROM house_rules WHERE rule_name = 'Smartlink-3 Prototype';
    
    -- Update Smartlink-3 Prototype to mark as homebrew and link to house rule
    UPDATE character_modifiers 
    SET is_homebrew = true, house_rule_id = prototype_rule_id
    WHERE character_id = manticore_id AND source = 'Smartlink-3 Prototype';
    
    -- Add Tailored Pheromones 2 modifiers
    INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, modifier_data)
    VALUES (manticore_id, 'skill_dice', 'social', 4, 'Tailored Pheromones 2', 'bioware', true, 
            '{"half_effect_non_dwarves": true}'::jsonb);
    
END $$;

COMMIT;

-- Verification queries
SELECT 'Axel Modifiers:' as info;
SELECT cm.source, cm.modifier_type, cm.target_name, cm.modifier_value, cm.is_homebrew, hr.rule_name as house_rule
FROM character_modifiers cm
JOIN characters c ON cm.character_id = c.id
LEFT JOIN house_rules hr ON cm.house_rule_id = hr.id
WHERE c.street_name = 'Axel'
ORDER BY cm.source;

SELECT 'Manticore Modifiers:' as info;
SELECT cm.source, cm.modifier_type, cm.target_name, cm.modifier_value, cm.is_homebrew, hr.rule_name as house_rule
FROM character_modifiers cm
JOIN characters c ON cm.character_id = c.id
LEFT JOIN house_rules hr ON cm.house_rule_id = hr.id
WHERE c.street_name = 'Manticore'
ORDER BY cm.source;
