-- Sample Clarifications and Errata for Shadowrun 2nd Edition
-- These demonstrate the clarifications system

-- Heavy Pistol Full Auto Limitation
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'limitation',
  'Heavy Pistols Cannot Fire Full Auto',
  'No heavy pistol in Shadowrun 2nd Edition has full auto capability. Heavy pistols are limited to semi-automatic (SA) or burst-fire (BF) modes only. Examples:
  
- Ares Predator II: Semi-automatic only
- Savalette Guardian: Burst-fire with complex action
- Ruger Thunderbolt: Burst-fire only

Full auto capability is reserved for submachine guns, assault rifles, and machine guns.',
  'official',
  'Shadowrun 2nd Edition Core Rulebook, Gear Section',
  10
);

-- Smartlink Clarification
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'clarification',
  'Smartlink Requires Both Cyberware and Weapon Modification',
  'To receive the -2 target number modifier from a smartlink, a character must have BOTH:

1. Smartlink cyberware (headware) installed
2. A weapon with smartlink modification

Smart goggles provide only a -1 modifier and do not require cyberware, but still require the weapon to have smartlink modification.

The smartlink system creates a direct neural interface between the weapon and the user, providing real-time targeting data, ammunition count, and weapon status.',
  'official',
  'Shadowrun 2nd Edition Core Rulebook, p. 241',
  8
);

-- Thermographic Vision in Darkness
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'clarification',
  'Thermographic Vision Modifiers',
  'When using thermographic vision (from cyber eyes or natural metahuman vision):

- Full Darkness: +4 modifier (natural vision) or +2 modifier (cyber eyes)
- The slash notation in the Visibility Table (e.g., +4/+2) indicates: first number for natural thermographic vision, second for cyber eyes
- Thermographic vision detects heat signatures, making it highly effective in darkness
- Thermal smoke blocks thermographic vision just as normal smoke blocks normal vision

Note: Most metahumans with natural thermographic vision use the first number, while characters with cyber eyes use the second (better) number.',
  'official',
  'Shadowrun 2nd Edition Core Rulebook, Visibility Table',
  7
);

-- Recoil Compensation
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'clarification',
  'Recoil Compensation Stacking',
  'Recoil compensation from multiple sources stacks additively:

- Gas-vent system: Reduces recoil by rating (1-3)
- Gyro-mount: Reduces recoil by 6
- Shock pads: Reduce recoil by 1
- Bipod/tripod: Eliminates recoil when properly set up

Example: A weapon with gas-vent 2 and shock pads provides 3 points of recoil compensation.

Important: Recoil compensation reduces the recoil modifier, but cannot reduce it below 0. Excess compensation is wasted.',
  'official',
  'Shadowrun 2nd Edition Core Rulebook, p. 240',
  6
);

-- Combat Pool Allocation
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'faq',
  'Combat Pool Must Be Allocated Before Rolling',
  'Combat Pool dice must be allocated BEFORE making the test roll. You cannot:

- Roll your base dice first, see the result, then decide to add Combat Pool
- Add Combat Pool after seeing the target number
- Split Combat Pool allocation between attack and defense in the same action

Best Practice: Declare all Combat Pool allocations at the start of your action, before any dice are rolled.

Combat Pool refreshes at the start of each Combat Turn (not Combat Phase).',
  'community',
  'Shadowrun FAQ, Dumpshock Forums',
  5
);

-- Initiative Ties
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'errata',
  'Initiative Tie-Breaking',
  'When two or more characters have the same Initiative score:

1. Higher Reaction attribute acts first
2. If Reaction is tied, higher Intelligence acts first  
3. If still tied, simultaneous actions (or GM decides)

This errata clarifies the core rulebook which was ambiguous about tie-breaking procedures.',
  'official',
  'Shadowrun 2nd Edition Errata v1.2',
  4
);

-- Staged Success Interpretation
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'house_rule',
  'Staged Success for Skill Tests (House Rule)',
  'For skill tests without explicit staging rules, use this guideline:

- 0 successes: Critical Failure (something goes wrong)
- 1 success: Marginal Success (barely accomplished)
- 2-3 successes: Success (task completed normally)
- 4-5 successes: Excellent Success (task completed with style)
- 6+ successes: Exceptional Success (beyond expectations)

This house rule provides consistent staging for tests that don''t have specific success level rules.',
  'gm',
  'House Rule',
  3
);

-- Weapon Range Categories
INSERT INTO rule_clarifications (
  clarification_type,
  title,
  content,
  source,
  source_reference,
  priority
) VALUES (
  'clarification',
  'Weapon Range Categories Vary by Weapon Type',
  'Different weapon types have different range brackets:

Heavy Pistols (e.g., Ares Predator):
- Short: 0-5m (TN 4)
- Medium: 6-20m (TN 5)
- Long: 21-40m (TN 6)
- Extreme: 41-60m (TN 9)

Submachine Guns:
- Short: 0-10m (TN 4)
- Medium: 11-40m (TN 5)
- Long: 41-80m (TN 6)
- Extreme: 81-150m (TN 9)

Always check the specific weapon''s range table in the gear section.',
  'official',
  'Shadowrun 2nd Edition Core Rulebook, Weapon Tables',
  6
);
