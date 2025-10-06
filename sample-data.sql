-- Sample Shadowrun 2nd Edition Rules Data
-- Use this to test the MCP server before importing your full RAG database

-- Combat Rules
INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
(
  'Initiative',
  'Initiative determines the order in which characters act during a Combat Turn. Each character rolls Initiative Dice (usually 1d6 + Reaction) at the start of combat. The result determines when they act in each Combat Phase. Characters with higher Initiative scores act first. Initiative is rolled at the beginning of each Combat Turn.',
  'combat',
  'initiative',
  ARRAY['initiative', 'combat', 'reaction', 'combat_turn', 'combat_phase']
),
(
  'Combat Pool',
  'The Combat Pool represents a character''s ability to perform exceptional feats in combat. It equals the character''s Intelligence + Willpower. Combat Pool dice can be allocated to improve attack rolls, defense rolls, or other combat actions. Allocated dice are rolled along with the base dice pool and count toward successes. Combat Pool refreshes at the start of each Combat Turn.',
  'combat',
  'combat_pool',
  ARRAY['combat_pool', 'intelligence', 'willpower', 'dice_pool', 'combat']
),
(
  'Target Numbers',
  'Target Numbers (TNs) represent the difficulty of a task. To succeed at a test, you must roll equal to or higher than the Target Number on your dice. Each die that meets or exceeds the TN counts as one success. The base TN for most actions is 4, but this can be modified by circumstances, range, visibility, and other factors.',
  'general',
  'target_numbers',
  ARRAY['target_number', 'tn', 'success', 'difficulty', 'dice_roll']
),
(
  'Staged Success',
  'Many tests use staged success to determine the degree of success or failure. The stages are typically: Critical Failure (no successes), Failure (some successes but not enough), Success (minimum required successes), and Excellent Success (extra successes beyond the minimum). The number of net successes determines which stage is achieved.',
  'general',
  'staged_success',
  ARRAY['staged_success', 'net_successes', 'success_levels', 'critical_failure']
);

-- Magic Rules
INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
(
  'Spellcasting',
  'To cast a spell, the magician makes a Sorcery Test against a Target Number based on the spell''s Force. The caster must achieve at least as many successes as the spell''s Force to successfully cast it. After casting, the magician must resist Drain, which is based on the spell''s Force and type (Mana or Physical). Drain is resisted with Willpower dice.',
  'magic',
  'spellcasting',
  ARRAY['spellcasting', 'sorcery', 'force', 'drain', 'willpower', 'mana', 'physical']
),
(
  'Drain Resistance',
  'After casting a spell, the magician must resist Drain. The Drain Code is based on the spell''s Force and type. For Mana spells, the Drain is (Force ÷ 2)M. For Physical spells, it''s (Force ÷ 2)S. The magician rolls Willpower dice against a TN equal to (2 + spell Force). Each success reduces the Drain damage by one level on the Damage Resistance Table.',
  'magic',
  'drain',
  ARRAY['drain', 'drain_resistance', 'willpower', 'force', 'damage', 'mana_spell', 'physical_spell']
);

-- Skills
INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
(
  'Skill Tests',
  'To perform a Skill Test, roll a number of dice equal to your Skill Rating. The Target Number is determined by the difficulty of the task. Each die that meets or exceeds the TN counts as one success. The number of successes needed depends on the task - simple tasks may need only 1 success, while complex tasks may require 4 or more.',
  'skills',
  'skill_tests',
  ARRAY['skill_test', 'skill_rating', 'target_number', 'success', 'dice_pool']
),
(
  'Defaulting',
  'If a character doesn''t have the required skill, they can default to the linked attribute. When defaulting, roll the attribute rating with a +4 modifier to the Target Number. Some skills cannot be defaulted (like Sorcery or specialized knowledge skills). Defaulting represents attempting a task with raw talent rather than training.',
  'skills',
  'defaulting',
  ARRAY['defaulting', 'attribute', 'target_number', 'skill_rating', 'untrained']
);

-- Character Creation
INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
(
  'Attribute Priority',
  'During character creation, players distribute priority levels (A through E) among five categories: Race, Magic, Attributes, Skills, and Resources. Priority A provides the most points or options, while Priority E provides the least. This system ensures balanced character creation while allowing for diverse character concepts.',
  'character_creation',
  'priority_system',
  ARRAY['character_creation', 'priority', 'attributes', 'race', 'magic', 'skills', 'resources']
),
(
  'Essence',
  'Essence represents a character''s spiritual wholeness and connection to magic. All characters start with 6 Essence. Cyberware and bioware reduce Essence. Each point of Essence lost also reduces the character''s maximum Magic rating by 1. Characters with 0 Essence die. Essence loss is permanent and cannot be recovered.',
  'character_creation',
  'essence',
  ARRAY['essence', 'cyberware', 'bioware', 'magic', 'spiritual', 'augmentation']
);

-- Gear and Equipment
INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
(
  'Weapon Ranges',
  'Firearms have different range categories: Short, Medium, Long, and Extreme. Each range category applies a modifier to the Target Number. Short range has no modifier, Medium adds +1, Long adds +2, and Extreme adds +3. Some weapons have different range brackets based on their type (pistol, rifle, etc.).',
  'gear_mechanics',
  'weapons',
  ARRAY['weapons', 'range', 'firearms', 'target_number', 'modifiers', 'short_range', 'medium_range', 'long_range']
),
(
  'Armor',
  'Armor provides protection by reducing incoming damage. Each type of armor has a Ballistic and Impact rating. When hit, the armor rating is used as a dice pool to resist damage. Each success reduces the damage by one level on the Damage Resistance Table. Armor can be layered but becomes cumbersome.',
  'gear_mechanics',
  'armor',
  ARRAY['armor', 'ballistic', 'impact', 'damage_resistance', 'protection', 'layered_armor']
);

-- Matrix
INSERT INTO rules_content (title, content, category, subcategory, tags) VALUES
(
  'Matrix Actions',
  'In the Matrix, deckers perform actions using their Computer skill and deck''s MPCP rating. Common actions include accessing systems, running utilities, and engaging IC. Each action has a Target Number based on the system''s security rating. Deckers can perform multiple actions per Combat Turn but each additional action adds +2 to all TNs.',
  'matrix',
  'matrix_actions',
  ARRAY['matrix', 'decker', 'computer', 'mpcp', 'ic', 'security_rating', 'target_number']
);
