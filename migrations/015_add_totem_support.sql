-- Migration 015: Add Totem Support for Shamans
-- Adds totem field to characters and creates totems reference table with ALL SR2 totems
-- INCLUDES opposed categories (negative dice modifiers)

-- Add totem field to characters table
ALTER TABLE characters 
ADD COLUMN IF NOT EXISTS totem VARCHAR(50);

-- Drop existing totems table if it exists (clean slate)
DROP TABLE IF EXISTS totems CASCADE;

-- Create totems reference table
CREATE TABLE totems (
    totem_name VARCHAR(50) PRIMARY KEY,
    favored_categories TEXT[] NOT NULL,
    opposed_categories TEXT[],  -- Spell categories that get -2 dice (disadvantages)
    bonus_dice INTEGER DEFAULT 2,
    penalty_dice INTEGER DEFAULT -2,  -- Penalty for opposed categories
    spirit_type VARCHAR(50),
    description TEXT
);

-- Populate with ALL Shadowrun 2nd Edition totems (55 total) with advantages AND disadvantages
INSERT INTO totems (totem_name, favored_categories, opposed_categories, bonus_dice, spirit_type, description) VALUES
    ('Agwe (Loa)', ARRAY['Illusion'], NULL, 2, 'Sea', '+2 dice for illusion spells; +2 dice for banishing water spirits. Increases shaman''s Body and Charisma, Swimming Skill, and all Social skills.'),
    ('Azaca (Loa)', ARRAY['Health'], NULL, 2, 'Any', '+2 dice for health spells; +2 dice for banishing Spirits of the Land. Increases shaman''s Quickness and Body, Stealth Skill, and all skills related to plant life, woodcraft, or agriculture.'),
    ('Bear', ARRAY['Health'], NULL, 2, 'Forest', '+2 dice for all health spells; +2 dice for conjuring forest spirits.'),
    ('Boar', ARRAY['Combat'], ARRAY['Illusion'], 2, 'Forest', '+2 dice for combat spells; +1 service from any spirit summoned for combat purposes.'),
    ('Bull', ARRAY['Health', 'Detection'], NULL, 2, 'Any', '+2 dice for health spells; +1 die for combat and detection spells.'),
    ('Cat', ARRAY['Illusion'], ARRAY['Combat'], 2, 'City', '+2 dice for illusion spells; +2 dice for conjuring city spirits.'),
    ('Coyote', ARRAY[]::TEXT[], NULL, 2, 'Any', 'None'),
    ('Creator', ARRAY[]::TEXT[], ARRAY['Combat'], 2, 'Forest', '+2 dice for enchantments; +1 die for conjuring hearth and city spirits.'),
    ('Damballah Wedo (Loa)', ARRAY['Detection'], NULL, 2, 'Sky', '+2 dice for detection spells; +2 dice for banishing Spirits of the Air. Increases shaman''s Intelligence and all Knowledge skills.'),
    ('Dog', ARRAY['Detection'], NULL, 2, 'City', '+2 dice for detection spells; +2 dice for conjuring field and hearth spirits.'),
    ('Dragonslayer', ARRAY['Combat'], ARRAY['Combat', 'Illusion'], 2, 'Any', '+3 dice for combat spells; +1 die for conjuring hearth spirits.'),
    ('Eagle', ARRAY['Detection'], NULL, 2, 'Mountain', '+2 dice for detection spells; +2 dice for conjuring wind spirits.'),
    ('Erzulie (Loa)', ARRAY['Illusion'], NULL, 2, 'Any', '+2 dice for detection and illusion spells. Increases shaman''s Charisma and Etiquette, Negotiation, and Psychology skills.'),
    ('Firebringer', ARRAY['Manipulation'], ARRAY['Illusion'], 2, 'City', '+2 dice for detection and manipulation spells; +2 dice for conjuring Spirits of Man.'),
    ('Gargoyle', ARRAY['Illusion'], NULL, 2, 'City', '+1 die for detection and illusion spells; +2 dice for conjuring city spirits.'),
    ('Gator', ARRAY['Detection'], ARRAY['Illusion'], 2, 'City', '+2 dice for combat and detection spells; +2 dice for conjuring spirits of the swamp, lake, or river (if wilderness totem is chosen) or city spirits (if urban totem is chosen).'),
    ('Gecko', ARRAY['Illusion'], ARRAY['Combat'], 2, 'Any', '+2 dice for manipulation or illusion spells; +1 die for resisting the effects of poison.'),
    ('Ghede (Loa)', ARRAY['Manipulation'], NULL, 2, 'Any', '+2 dice for casting health and manipulation spells. Increases shaman''s Intelligence and Biotech and Negotiation skills. The shaman is immune to the effects of pain, gaining a point of Pain Resistance ...'),
    ('Goose (Nene)', ARRAY['Combat'], NULL, 2, 'Mountain', '+1 die for combat spells; +3 dice for conjuring mountain spirits.'),
    ('Goose', ARRAY['Combat', 'Detection'], NULL, 2, 'City', '+2 dice for detection spells; +1 die for combat spells; +2 dice for conjuring wind spirits (wilderness totem); +2 dice for conjuring city spirits (urban totem).'),
    ('Great Mother', ARRAY['Health'], NULL, 2, 'Forest', '+2 dice for all health spells; +2 dice for conjuring all field and forest spirits and Spirits of the Waters.'),
    ('Griffin', ARRAY['Combat'], NULL, 2, 'Mountain', '+2 dice for combat spells; +2 dice for conjuring Spirits of the Sky.'),
    ('Horned God', ARRAY['Combat'], NULL, 2, 'Any', '+2 dice for all combat spells; +2 dice for conjuring all Spirits of the Land.'),
    ('Horse', ARRAY['Health'], ARRAY['Combat', 'Illusion'], 2, 'Forest', '+2 dice for health spells; use of the critter power Enhanced Movement (3 times per day).'),
    ('Iguana', ARRAY['Health'], NULL, 2, 'Forest', '+2 dice for health spells; +2 dice for conjuring desert spirits.'),
    ('Jaguar', ARRAY[]::TEXT[], ARRAY['Health'], 2, 'Any', '+2 dice for conjuring jungle spirits.'),
    ('Legba (Loa)', ARRAY['Manipulation'], NULL, 2, 'Any', '+2 dice for detection and manipulation spells. Increases shaman''s Charisma and Social and Knowledge skills.'),
    ('Leviathan', ARRAY['Manipulation'], ARRAY['Illusion'], 2, 'Sea', '+1 die for health and manipulation spells; +2 dice for conjuring sea spirits.'),
    ('Loco and Ayizan (Loa)', ARRAY['Health', 'Detection'], NULL, 2, 'Any', '+2 dice for detection spells (Loco), +2 dice for health spells (Ayizan); +2 dice for conjuring other loa (both). Increases shaman''s Magical Theory Skill (Loco), Biotech Skill (Ayizan), Psychology, Soc...'),
    ('Moon', ARRAY['Detection', 'Illusion'], ARRAY['Combat'], 2, 'Water', '+2 dice for manipulation and illusion spells; +1 die for detection spells; +2 dice for conjuring water spirits.'),
    ('Moon Maiden', ARRAY[]::TEXT[], NULL, 2, 'Any', 'None'),
    ('Oak', ARRAY['Health'], NULL, 2, 'Forest', '+2 dice for health spells; +2 dice to conjure forest spirits and Spirits of Man in structures constructed wholly or partially of oak.'),
    ('Ogoun (Loa)', ARRAY['Health'], NULL, 2, 'Any', '+2 dice for combat and health spells. Increases Strength, Reaction, and Combat skills. The shaman gains (magical) Impact armor equal to the loa''s Force.'),
    ('Owl', ARRAY[]::TEXT[], NULL, 2, 'City', '+2 dice for any sorcery or conjuring by night.'),
    ('Pegasus', ARRAY['Health'], NULL, 2, 'Sky', '+1 die to detection and health spells; +2 dice for conjuring Spirits of the Sky.'),
    ('Phoenix', ARRAY['Illusion'], NULL, 2, 'Desert', '+1 die for health and illusion spells; can conjure spirits of the Great Fiery Firmament (see source text).'),
    ('Plumed Serpent', ARRAY[]::TEXT[], NULL, 2, 'Any', '+2 dice for any information-gathering spell.'),
    ('Prairie Dog', ARRAY['Detection', 'Illusion'], ARRAY['Combat'], 2, 'Water', '+2 dice for detection spells; +1 die for illusion spells; +1 die for Charisma Tests; +2 dice for conjuring Spirits of the Land. Fire-Bringer shamans devote themselves to the betterment of others, even...'),
    ('Puma', ARRAY['Illusion'], NULL, 2, 'Desert', '+2 dice for illusion spells.'),
    ('Raccoon', ARRAY['Manipulation'], ARRAY['Combat'], 2, 'City', '+2 dice for manipulation spells; +2 dice for conjuring city spirits.'),
    ('Rat', ARRAY['Illusion'], ARRAY['Combat'], 2, 'City', '+2 dice for detection and illusion spells; +2 dice for conjuring all Spirits of Man.'),
    ('Raven', ARRAY['Manipulation'], ARRAY['Combat'], 2, 'Sky', '+2 dice for manipulation spells; +2 dice for conjuring wind spirits.'),
    ('Sea', ARRAY['Manipulation'], NULL, 2, 'Sea', '+2 dice for health and transformation manipulation spells; +2 dice for conjuring saltwater spirits and ship spirits (hearth spirits).'),
    ('Serpent', ARRAY['Manipulation'], NULL, 2, 'Mountain', '+2 dice for health and manipulation spells; +2 dice for conjuring mountain spirits.'),
    ('Shark', ARRAY['Detection'], NULL, 2, 'Sea', '+2 dice for combat and detection spells; +2 dice for conjuring sea spirits.'),
    ('Snake', ARRAY['Detection'], ARRAY['Combat'], 2, 'City', '+2 dice for health, illusion, and detection spells; +2 dice for conjuring any one Spirit of the Land (shaman''s choice, wilderness totem only); +2 dice for conjuring any one Spirit of Man (shaman''s cho...'),
    ('Spider', ARRAY['Illusion'], NULL, 2, 'Any', '+2 dice for illusion spells; +1 die for conjuring spells.'),
    ('Stag', ARRAY['Health', 'Illusion'], ARRAY['Manipulation'], 2, 'Forest', '+2 dice for health spells; +1 die for illusion spells; +2 dice for conjuring forest spirits; -1 to all target numbers for tests involving communication with and reactions from sentient animals.'),
    ('Sun', ARRAY['Detection'], NULL, 2, 'Prairie', '+2 dice for combat, health, and detection spells; +2 dice for conjuring any spirit in direct sunlight.'),
    ('Turtle', ARRAY['Illusion'], ARRAY['Combat'], 2, 'Sea', '+2 dice for illusion spells; +2 dice for conjuring sea spirits.'),
    ('Whale', ARRAY['Combat'], ARRAY['Illusion'], 2, 'Sea', '+2 dice for combat spells; +2 dice for conjuring sea spirits.'),
    ('Wild Huntsman', ARRAY['Illusion'], NULL, 2, 'Forest', '+2 dice for perception and illusion spells; +2 dice for conjuring storm spirits.'),
    ('Wildcat', ARRAY['Health'], ARRAY['Illusion'], 2, 'Any', '+2 dice for combat and health spells; +2 dice for conjuring any nature spirit during hours of darkness.'),
    ('Wolf', ARRAY['Combat'], NULL, 2, 'Forest', '+2 dice for detection and combat spells; +2 dice for conjuring forest or prairie spirits (shaman''s choice).'),
    ('Wyrm', ARRAY['Manipulation'], NULL, 2, 'Mountain', '+2 dice for health and manipulation spells; +2 dice for conjuring mountain spirits.')
ON CONFLICT (totem_name) DO NOTHING;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_characters_totem ON characters(totem);

-- Add comments
COMMENT ON TABLE totems IS 'Reference table for shaman totems with spell category modifiers (55 totems from SR2 with advantages AND disadvantages)';
COMMENT ON COLUMN characters.totem IS 'Shaman totem (provides +2 dice bonus to favored categories, -2 dice penalty to opposed categories)';
COMMENT ON COLUMN totems.opposed_categories IS 'Spell categories that receive -2 dice penalty (totem disadvantages)';
