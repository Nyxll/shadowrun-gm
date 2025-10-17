-- Quick Insert: Variable Force Casting House Rule
-- Copy and paste this into your database

INSERT INTO house_rules (
    campaign_id,
    rule_name,
    rule_type,
    category,
    description,
    rule_text,
    mechanical_effect,
    applies_to,
    conditions,
    is_active
)
VALUES (
    1, -- Replace with your campaign_id
    'Variable Force Casting',
    'custom',
    'magic',
    'Cast spells at any force from 1 to learned maximum',
    'Magicians may cast spells at any force from 1 up to the spell''s learned force rating. All calculations use the chosen force, not the learned maximum.',
    '{
        "type": "spell_force_flexibility",
        "effect": "variable_force_casting",
        "rules": {
            "learned_force_is_maximum": true,
            "minimum_force": 1,
            "force_selection": "caster_choice_at_casting",
            "calculations_use": "chosen_force_not_learned_force"
        }
    }'::jsonb,
    '{"character_types": ["mage", "shaman", "aspected_magician"], "spell_types": ["all"]}'::jsonb,
    '{"when_casting": true, "requires_learned_spell": true}'::jsonb,
    true
);
