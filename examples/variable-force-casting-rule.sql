-- House Rule: Variable Force Casting
-- Allows magicians to cast spells at any force from 1 up to the spell's maximum learned force
-- Example: A Force 5 Manabolt can be cast at Force 1, 2, 3, 4, or 5

-- First, create a campaign (if you don't have one)
INSERT INTO campaigns (name, gm_name, description, settings)
VALUES (
    'My Shadowrun Campaign',
    'GM Name',
    'Campaign with variable force casting house rule',
    '{
        "edition": "2e",
        "starting_year": 2053,
        "house_rules_enabled": true
    }'::jsonb
)
ON CONFLICT (name) DO NOTHING;

-- Insert the Variable Force Casting house rule
INSERT INTO house_rules (
    campaign_id,
    rule_name,
    rule_type,
    category,
    description,
    rule_text,
    mechanical_effect,
    applies_to,
    modifier_value,
    conditions,
    is_active
)
VALUES (
    (SELECT id FROM campaigns WHERE name = 'My Shadowrun Campaign' LIMIT 1),
    'Variable Force Casting',
    'custom',
    'magic',
    'Allows spellcasters to cast spells at any force from 1 up to the spell''s learned maximum force rating',
    
    -- Human-readable rule text
    'When a magician learns a spell at a specific force rating (e.g., Force 5), they may cast that spell at any force level from 1 up to the learned maximum (1, 2, 3, 4, or 5). The caster chooses the casting force when declaring the spell. All effects (damage, drain, target numbers) are calculated based on the chosen casting force, not the learned maximum.',
    
    -- AI-parseable mechanical effect
    '{
        "type": "spell_force_flexibility",
        "effect": "variable_force_casting",
        "rules": {
            "learned_force_is_maximum": true,
            "minimum_force": 1,
            "force_selection": "caster_choice_at_casting",
            "calculations_use": "chosen_force_not_learned_force"
        },
        "examples": [
            {
                "spell": "Manabolt",
                "learned_force": 5,
                "available_forces": [1, 2, 3, 4, 5],
                "scenario": "Caster can choose to cast at Force 3 for less drain"
            },
            {
                "spell": "Heal",
                "learned_force": 6,
                "available_forces": [1, 2, 3, 4, 5, 6],
                "scenario": "Caster can choose Force 2 for minor wounds or Force 6 for serious injuries"
            }
        ],
        "drain_calculation": "Use chosen force, not learned force",
        "damage_calculation": "Use chosen force, not learned force",
        "target_number_calculation": "Use chosen force, not learned force"
    }'::jsonb,
    
    -- What this rule applies to
    '{
        "character_types": ["mage", "shaman", "aspected_magician"],
        "spell_types": ["all"],
        "excludes": []
    }'::jsonb,
    
    -- No numeric modifier (this is a mechanical change)
    NULL,
    
    -- Conditions for when this rule applies
    '{
        "when_casting": true,
        "requires_learned_spell": true,
        "force_must_be_between": {
            "min": 1,
            "max": "learned_force"
        }
    }'::jsonb,
    
    -- Rule is active
    true
);

-- Example: How to query this rule
SELECT 
    rule_name,
    description,
    rule_text,
    mechanical_effect->>'effect' as effect_type,
    mechanical_effect->'rules' as rules,
    mechanical_effect->'examples' as examples
FROM house_rules
WHERE rule_name = 'Variable Force Casting'
    AND is_active = true;

-- Example: How AI would interpret this when a player casts a spell
/*
SCENARIO: Player wants to cast Manabolt (learned at Force 5)

AI LOGIC:
1. Check if Variable Force Casting rule is active
2. Get spell's learned force: 5
3. Available casting forces: 1, 2, 3, 4, 5
4. Ask player: "At what force do you want to cast this spell? (1-5)"
5. Player chooses: Force 3
6. Calculate drain using Force 3 (not Force 5)
7. Calculate damage using Force 3 (not Force 5)
8. Calculate target numbers using Force 3 (not Force 5)

BENEFITS:
- Less drain for routine tasks (cast at lower force)
- Flexibility in combat (adjust force to situation)
- Better resource management (save energy for big spells)
*/

-- Example: Log when this rule is applied
INSERT INTO rule_application_log (
    house_rule_id,
    character_id,
    applied_at,
    context,
    result
)
VALUES (
    (SELECT id FROM house_rules WHERE rule_name = 'Variable Force Casting' LIMIT 1),
    1, -- character_id
    NOW(),
    '{
        "action": "cast_spell",
        "spell_name": "Manabolt",
        "learned_force": 5,
        "chosen_force": 3,
        "reason": "Reduce drain for routine combat"
    }'::jsonb,
    '{
        "drain_target": 3,
        "damage_code": "3M",
        "success": true
    }'::jsonb
);
