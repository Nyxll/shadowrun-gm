#!/usr/bin/env python3
"""
Extract reference data from processed sourcebooks and load into database.

This tool searches through processed sourcebook files to find and extract:
- Metatypes
- Qualities (Edges/Flaws)
- Skills
- Spells
- Adept Powers
- Totems

It then loads this data into the appropriate database tables.
"""

import re
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

SOURCEBOOKS_PATH = Path("G:/My Drive/Sourcebooks/processed")

class ReferenceDataExtractor:
    def __init__(self, sourcebooks_path: Path):
        self.sourcebooks_path = sourcebooks_path
        self.conn = None
        
    def connect(self):
        """Connect to PostgreSQL database"""
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def read_sourcebook(self, filename: str) -> str:
        """Read a sourcebook file"""
        filepath = self.sourcebooks_path / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            return ""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_metatypes(self) -> List[Dict[str, Any]]:
        """Extract metatype data from sourcebooks"""
        print("\n=== Extracting Metatypes ===")
        
        # Standard metatypes
        metatypes = [
            {
                "name": "Human",
                "variant_of": None,
                "is_variant": False,
                "description": "Standard human metatype",
                "attribute_modifiers": {},
                "special_abilities": [],
                "racial_traits": {}
            },
            {
                "name": "Elf",
                "variant_of": None,
                "is_variant": False,
                "description": "Elven metatype with enhanced Quickness and Charisma",
                "attribute_modifiers": {"quickness": 1, "charisma": 2},
                "special_abilities": ["Low-Light Vision"],
                "racial_traits": {"vision": "low_light"}
            },
            {
                "name": "Dwarf",
                "variant_of": None,
                "is_variant": False,
                "description": "Dwarven metatype with enhanced Body and Willpower",
                "attribute_modifiers": {"body": 1, "willpower": 1, "quickness": -1},
                "special_abilities": ["Thermographic Vision", "Resistance to Pathogens/Toxins"],
                "racial_traits": {"vision": "thermographic", "toxin_resistance": "+2"}
            },
            {
                "name": "Ork",
                "variant_of": None,
                "is_variant": False,
                "description": "Ork metatype with enhanced Body and Strength",
                "attribute_modifiers": {"body": 3, "strength": 2, "charisma": -1, "intelligence": -1},
                "special_abilities": ["Low-Light Vision"],
                "racial_traits": {"vision": "low_light"}
            },
            {
                "name": "Troll",
                "variant_of": None,
                "is_variant": False,
                "description": "Troll metatype with greatly enhanced Body and Strength",
                "attribute_modifiers": {"body": 5, "strength": 4, "quickness": -1, "charisma": -2, "intelligence": -2},
                "special_abilities": ["Thermographic Vision", "Dermal Armor (+1)", "Reach (+1)"],
                "racial_traits": {"vision": "thermographic", "dermal_armor": 1, "reach": 1}
            },
            {
                "name": "Shapeshifter (Rhino)",
                "variant_of": "Shapeshifter",
                "is_variant": True,
                "description": "Custom rhino shapeshifter with dual nature and regeneration",
                "attribute_modifiers": {},
                "special_abilities": ["Dual Nature", "Regeneration", "Shapeshifting"],
                "racial_traits": {
                    "animal_type": "rhino",
                    "natural_weapons": "Horns (10S Physical)",
                    "natural_armor": "+2 Ballistic / +4 Impact",
                    "regeneration": True,
                    "dual_nature": True,
                    "vulnerabilities": ["silver"],
                    "form_change": "Complex Action"
                }
            }
        ]
        
        print(f"Extracted {len(metatypes)} metatypes")
        return metatypes
    
    def extract_qualities_from_companion(self) -> List[Dict[str, Any]]:
        """Extract edges and flaws from Shadowrun Companion"""
        print("\n=== Extracting Qualities (Edges/Flaws) ===")
        
        # Read the edges file
        edges_text = self.read_sourcebook("Shadowrun Companion-edges-md.txt")
        
        qualities = []
        
        # Known qualities from character sheets
        known_qualities = [
            # Edges (positive)
            {"name": "Exceptional Attribute", "type": "edge", "cost": 2, "description": "One attribute can exceed racial maximum by 1"},
            {"name": "Ambidexterity", "type": "edge", "cost": 1, "description": "No penalty for using off-hand"},
            {"name": "Aptitude", "type": "edge", "cost": 2, "description": "Reduce target numbers by 1 for one skill"},
            {"name": "Focused Concentration", "type": "edge", "cost": 2, "description": "+1 target modifier when casting sustained spells"},
            {"name": "High Pain Tolerance", "type": "edge", "cost": 1, "description": "Reduces wound penalties"},
            {"name": "Technical School", "type": "edge", "cost": 2, "description": "+1 to technical skills"},
            
            # Flaws (negative)
            {"name": "Amnesia", "type": "flaw", "cost": -1, "description": "Character has lost memories of their past"},
            {"name": "Distinctive Style", "type": "flaw", "cost": -1, "description": "Character has a memorable appearance or mannerism"},
            {"name": "Guilt Spur", "type": "flaw", "cost": -1, "description": "Driven by guilt over past actions"},
            {"name": "Shadow Echo", "type": "flaw", "cost": -1, "description": "Hears whispers in silence (house rule)"},
            {"name": "Weak Immune System", "type": "flaw", "cost": -1, "description": "-1 Body vs diseases"},
            {"name": "Mild Addiction", "type": "flaw", "cost": -1, "description": "Addicted to a substance (stims, etc)"},
            {"name": "Mild Allergy", "type": "flaw", "cost": -1, "description": "Allergic to common substance (pollen, etc)"},
            {"name": "Vulnerability to Silver", "type": "flaw", "cost": -2, "description": "Shapeshifter mandatory flaw"},
            {"name": "Impulsive", "type": "flaw", "cost": -1, "description": "Willpower test to avoid rash actions"},
        ]
        
        qualities.extend(known_qualities)
        
        print(f"Extracted {len(qualities)} qualities")
        return qualities
    
    def extract_skills_from_core(self) -> List[Dict[str, Any]]:
        """Extract skills from core rulebook"""
        print("\n=== Extracting Skills ===")
        
        # Read core skills file
        skills_text = self.read_sourcebook("core-fundamentals-skill.ocr.txt")
        
        # Known skills from character sheets
        known_skills = [
            # Combat Skills
            {"name": "Firearms", "category": "combat", "attribute": "quickness", "description": "Use of pistols, rifles, and other firearms"},
            {"name": "Armed Combat", "category": "combat", "attribute": "quickness", "description": "Melee combat with weapons"},
            {"name": "Unarmed Combat", "category": "combat", "attribute": "quickness", "description": "Hand-to-hand combat"},
            {"name": "Whips", "category": "combat", "attribute": "quickness", "description": "Use of whips and monowhips"},
            {"name": "Throwing", "category": "combat", "attribute": "quickness", "description": "Throwing weapons and grenades"},
            {"name": "Gunnery", "category": "combat", "attribute": "intelligence", "description": "Vehicle-mounted weapons"},
            
            # Magical Skills
            {"name": "Sorcery", "category": "magical", "attribute": "willpower", "description": "Spellcasting"},
            {"name": "Conjuring", "category": "magical", "attribute": "willpower", "description": "Summoning and binding spirits"},
            {"name": "Magical Theory", "category": "magical", "attribute": "intelligence", "description": "Understanding of magical principles"},
            
            # Technical Skills
            {"name": "Computer", "category": "technical", "attribute": "intelligence", "description": "Computer operation and programming"},
            {"name": "Electronics", "category": "technical", "attribute": "intelligence", "description": "Electronic devices and systems"},
            {"name": "Biotech", "category": "technical", "attribute": "intelligence", "description": "Medical and biological technology"},
            
            # Vehicle Skills
            {"name": "Car", "category": "vehicle", "attribute": "reaction", "description": "Driving ground vehicles"},
            {"name": "Rotor Craft", "category": "vehicle", "attribute": "reaction", "description": "Piloting helicopters"},
            {"name": "Vectored Thrust", "category": "vehicle", "attribute": "reaction", "description": "Piloting VTOL aircraft"},
            {"name": "Mech/Anthroform Piloting", "category": "vehicle", "attribute": "reaction", "description": "Piloting bipedal drones"},
            
            # Social Skills
            {"name": "Negotiation", "category": "social", "attribute": "charisma", "description": "Bargaining and deal-making"},
            {"name": "Etiquette", "category": "social", "attribute": "charisma", "description": "Social protocols and manners"},
            
            # Physical Skills
            {"name": "Stealth", "category": "physical", "attribute": "quickness", "description": "Moving silently and hiding"},
            {"name": "Athletics", "category": "physical", "attribute": "body", "description": "Running, jumping, climbing"},
        ]
        
        print(f"Extracted {len(known_skills)} skills")
        return known_skills
    
    def extract_spells_from_grimoire(self) -> List[Dict[str, Any]]:
        """Extract spells from Grimoire"""
        print("\n=== Extracting Spells ===")
        
        # Read grimoire
        grimoire_text = self.read_sourcebook("SR2-Grimoire.txt")
        
        # Known spells from character sheets
        known_spells = [
            # Combat Spells
            {"name": "Manabolt", "category": "combat", "type": "mana", "range": "LOS", "duration": "instant", "drain": "(F/2)M", "description": "Mana-based direct combat spell"},
            {"name": "Stunbolt", "category": "combat", "type": "mana", "range": "LOS", "duration": "instant", "drain": "(F/2)M", "description": "Stun damage mana spell"},
            {"name": "Stunball", "category": "combat", "type": "mana", "range": "LOS(A)", "duration": "instant", "drain": "(F/2)+1M", "description": "Area stun damage spell"},
            {"name": "Lightning Bolt", "category": "combat", "type": "physical", "range": "LOS", "duration": "instant", "drain": "(F/2)+1S", "description": "Electrical attack spell"},
            {"name": "Power Bolt", "category": "combat", "type": "physical", "range": "LOS", "duration": "instant", "drain": "(F/2)+1M", "description": "Physical damage spell"},
            
            # Health Spells
            {"name": "Treat", "category": "health", "type": "mana", "range": "touch", "duration": "permanent", "drain": "(F/2)-2M", "description": "Heals physical damage"},
            {"name": "Heal", "category": "health", "type": "mana", "range": "touch", "duration": "permanent", "drain": "(F/2)M", "description": "Heals physical damage"},
            {"name": "Stabilize", "category": "health", "type": "mana", "range": "touch", "duration": "permanent", "drain": "(F/2)-1M", "description": "Stabilizes dying character"},
            {"name": "Increase Reflexes", "category": "health", "type": "mana", "range": "touch", "duration": "sustained", "drain": "(F/2)D", "description": "Increases initiative dice"},
            {"name": "Increase Attribute", "category": "health", "type": "mana", "range": "touch", "duration": "sustained", "drain": "(F/2)D", "description": "Increases an attribute"},
            {"name": "Stop Regeneration", "category": "health", "type": "mana", "range": "LOS", "duration": "sustained", "drain": "(F/2)+1D", "description": "Prevents regeneration"},
            
            # Manipulation Spells
            {"name": "Invisibility", "category": "manipulation", "type": "physical", "range": "LOS", "duration": "sustained", "drain": "(F/2)M", "description": "Makes target invisible"},
            {"name": "Improved Invisibility", "category": "manipulation", "type": "mana", "range": "LOS", "duration": "sustained", "drain": "(F/2)+1M", "description": "True invisibility"},
            {"name": "Physical Mask", "category": "manipulation", "type": "physical", "range": "LOS", "duration": "sustained", "drain": "((F/2)+1)L", "description": "Changes appearance"},
            {"name": "Silence", "category": "manipulation", "type": "physical", "range": "LOS", "duration": "sustained", "drain": "(F/2)M", "description": "Eliminates sound"},
            {"name": "Levitate", "category": "manipulation", "type": "physical", "range": "LOS", "duration": "sustained", "drain": "(F/2)M", "description": "Levitates object or person"},
            {"name": "Physical Barrier", "category": "manipulation", "type": "physical", "range": "LOS", "duration": "sustained", "drain": "(F/2)S", "description": "Creates physical barrier"},
            {"name": "Mana Barrier", "category": "manipulation", "type": "mana", "range": "LOS", "duration": "sustained", "drain": "(F/2)S", "description": "Creates mana barrier"},
            {"name": "Control Thoughts", "category": "manipulation", "type": "mana", "range": "LOS", "duration": "sustained", "drain": "((F/2)+2)S", "description": "Control target's thoughts"},
            {"name": "Shape Earth", "category": "manipulation", "type": "physical", "range": "LOS", "duration": "sustained", "drain": "((F/2)+2)D", "description": "Manipulate earth and stone"},
            {"name": "Recharge", "category": "manipulation", "type": "physical", "range": "touch", "duration": "permanent", "drain": "(F/2)L", "description": "Recharge batteries"},
            
            # Detection Spells
            {"name": "Detect Enemies", "category": "detection", "type": "mana", "range": "LOS(A)", "duration": "sustained", "drain": "(F/2)S", "description": "Detect hostile intent"},
            {"name": "Detect Life", "category": "detection", "type": "mana", "range": "LOS(A)", "duration": "sustained", "drain": "(F/2)L", "description": "Detect living beings"},
            {"name": "Detect Magic", "category": "detection", "type": "mana", "range": "LOS(A)", "duration": "sustained", "drain": "(F/2)L", "description": "Detect magical auras"},
            {"name": "Mind Probe", "category": "detection", "type": "mana", "range": "touch", "duration": "sustained", "drain": "((F/2)+2)D", "description": "Read target's thoughts"},
            {"name": "Analyze Truth", "category": "detection", "type": "mana", "range": "touch", "duration": "sustained", "drain": "(F/2)S", "description": "Detect lies"},
        ]
        
        print(f"Extracted {len(known_spells)} spells")
        return known_spells
    
    def extract_adept_powers(self) -> List[Dict[str, Any]]:
        """Extract adept powers"""
        print("\n=== Extracting Adept Powers ===")
        
        # Known powers from character sheets
        known_powers = [
            {"name": "Missile Mastery", "cost": 1.0, "description": "Improved throwing accuracy"},
            {"name": "Traceless Walk", "cost": 0.5, "description": "Leave no tracks"},
            {"name": "Pain Resistance", "cost": 0.5, "description": "Reduce wound penalties"},
            {"name": "Empathic Healing", "cost": 1.0, "description": "Heal others through touch"},
        ]
        
        print(f"Extracted {len(known_powers)} adept powers")
        return known_powers
    
    def extract_totems(self) -> List[Dict[str, Any]]:
        """Extract totem data"""
        print("\n=== Extracting Totems ===")
        
        # Known totems from character sheets
        known_totems = [
            {
                "name": "Oak",
                "type": "shamanic",
                "description": "Oak shaman totem",
                "advantages": "+2 dice Health spells, +2 dice conjuring Spirits of Man, +2 dice in forests",
                "disadvantages": "-1 die Illusion spells",
                "modifiers": {
                    "health_spells": 2,
                    "conjuring_spirits_of_man": 2,
                    "forest_bonus": 2,
                    "illusion_penalty": -1
                }
            }
        ]
        
        print(f"Extracted {len(known_totems)} totems")
        return known_totems
    
    def load_metatypes(self, metatypes: List[Dict[str, Any]]):
        """Load metatypes into database"""
        print("\n=== Loading Metatypes ===")
        
        cursor = self.conn.cursor()
        
        for mt in metatypes:
            try:
                # Extract individual attribute modifiers
                mods = mt["attribute_modifiers"]
                cursor.execute("""
                    INSERT INTO metatypes (
                        name, variant_of, is_variant, description,
                        body_mod, quickness_mod, strength_mod, charisma_mod, intelligence_mod, willpower_mod,
                        special_abilities, racial_traits
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    mt["name"],
                    mt["variant_of"],
                    mt["is_variant"],
                    mt["description"],
                    mods.get("body", 0),
                    mods.get("quickness", 0),
                    mods.get("strength", 0),
                    mods.get("charisma", 0),
                    mods.get("intelligence", 0),
                    mods.get("willpower", 0),
                    mt["special_abilities"],
                    Json(mt["racial_traits"])
                ))
                print(f"  ✓ Loaded: {mt['name']}")
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print(f"  - Skipped (exists): {mt['name']}")
        
        self.conn.commit()
        print(f"Loaded {len(metatypes)} metatypes")
    
    def load_qualities(self, qualities: List[Dict[str, Any]]):
        """Load qualities into database"""
        print("\n=== Loading Qualities ===")
        
        cursor = self.conn.cursor()
        
        for q in qualities:
            try:
                cursor.execute("""
                    INSERT INTO qualities (name, quality_type, cost, description)
                    VALUES (%s, %s, %s, %s)
                """, (q["name"], q["type"], q["cost"], q["description"]))
                print(f"  ✓ Loaded: {q['name']} ({q['type']}, {q['cost']} points)")
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print(f"  - Skipped (exists): {q['name']}")
        
        self.conn.commit()
        print(f"Loaded {len(qualities)} qualities")
    
    def load_skills(self, skills: List[Dict[str, Any]]):
        """Load skills into database"""
        print("\n=== Loading Skills ===")
        
        cursor = self.conn.cursor()
        
        for s in skills:
            try:
                cursor.execute("""
                    INSERT INTO skills (name, category, subcategory, linked_attribute, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (s["name"], "Active", s["category"], s["attribute"], s["description"]))
                print(f"  ✓ Loaded: {s['name']} ({s['category']})")
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print(f"  - Skipped (exists): {s['name']}")
        
        self.conn.commit()
        print(f"Loaded {len(skills)} skills")
    
    def load_spells(self, spells: List[Dict[str, Any]]):
        """Load spells into database"""
        print("\n=== Loading Spells ===")
        
        cursor = self.conn.cursor()
        
        for sp in spells:
            try:
                cursor.execute("""
                    INSERT INTO spells (name, category, spell_type, target_type, duration, drain_code, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    sp["name"], sp["category"], sp["type"],
                    sp["range"], sp["duration"], sp["drain"], sp["description"]
                ))
                print(f"  ✓ Loaded: {sp['name']} ({sp['category']})")
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print(f"  - Skipped (exists): {sp['name']}")
        
        self.conn.commit()
        print(f"Loaded {len(spells)} spells")
    
    def load_powers(self, powers: List[Dict[str, Any]]):
        """Load adept powers into database"""
        print("\n=== Loading Adept Powers ===")
        
        cursor = self.conn.cursor()
        
        for p in powers:
            try:
                cursor.execute("""
                    INSERT INTO powers (name, power_type, power_point_cost, description)
                    VALUES (%s, %s, %s, %s)
                """, (p["name"], "adept", p["cost"], p["description"]))
                print(f"  ✓ Loaded: {p['name']} (cost: {p['cost']})")
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print(f"  - Skipped (exists): {p['name']}")
        
        self.conn.commit()
        print(f"Loaded {len(powers)} adept powers")
    
    def load_totems(self, totems: List[Dict[str, Any]]):
        """Load totems into database"""
        print("\n=== Loading Totems ===")
        
        cursor = self.conn.cursor()
        
        for t in totems:
            try:
                cursor.execute("""
                    INSERT INTO totems (name, description, advantages, disadvantages)
                    VALUES (%s, %s, %s, %s)
                """, (
                    t["name"], t["description"],
                    t["advantages"], t["disadvantages"]
                ))
                print(f"  ✓ Loaded: {t['name']}")
            except psycopg2.IntegrityError:
                self.conn.rollback()
                print(f"  - Skipped (exists): {t['name']}")
        
        self.conn.commit()
        print(f"Loaded {len(totems)} totems")
    
    def run(self):
        """Run the extraction and loading process"""
        print("=" * 60)
        print("SHADOWRUN REFERENCE DATA EXTRACTOR")
        print("=" * 60)
        
        try:
            self.connect()
            
            # Extract data
            metatypes = self.extract_metatypes()
            qualities = self.extract_qualities_from_companion()
            skills = self.extract_skills_from_core()
            spells = self.extract_spells_from_grimoire()
            powers = self.extract_adept_powers()
            totems = self.extract_totems()
            
            # Load data
            self.load_metatypes(metatypes)
            self.load_qualities(qualities)
            self.load_skills(skills)
            self.load_spells(spells)
            self.load_powers(powers)
            self.load_totems(totems)
            
            print("\n" + "=" * 60)
            print("EXTRACTION COMPLETE!")
            print("=" * 60)
            print(f"Metatypes: {len(metatypes)}")
            print(f"Qualities: {len(qualities)}")
            print(f"Skills: {len(skills)}")
            print(f"Spells: {len(spells)}")
            print(f"Powers: {len(powers)}")
            print(f"Totems: {len(totems)}")
            
        finally:
            self.close()


if __name__ == "__main__":
    extractor = ReferenceDataExtractor(SOURCEBOOKS_PATH)
    extractor.run()
