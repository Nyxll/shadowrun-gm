#!/usr/bin/env python3
"""
Test spellcasting with timing information
"""
import os
import sys
import json
import asyncio
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from decimal import Decimal
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.dice_roller import DiceRoller

load_dotenv()

# Database connection
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB', 'postgres')
}

def convert_db_types(obj):
    """Recursively convert UUID and Decimal types to JSON-serializable types"""
    if isinstance(obj, dict):
        return {k: convert_db_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_db_types(item) for item in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

def get_connection():
    """Get database connection"""
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)

async def cast_spell(
    caster_name: str,
    spell_name: str,
    force: int,
    target_name: str,
    spell_pool_dice: int,
    drain_pool_dice: int
):
    """
    Cast spell with timing - simplified version from game-server.py
    """
    import time
    
    # Start overall timing
    start_time = time.time()
    timings = {}
    
    # Database connection timing
    db_start = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    timings['db_connection'] = time.time() - db_start
    
    try:
        # Get caster character data
        query_start = time.time()
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.street_name,
                c.current_magic,
                c.current_willpower,
                c.current_intelligence
            FROM characters c
            WHERE LOWER(c.name) = LOWER(%s) 
               OR LOWER(COALESCE(c.street_name, '')) = LOWER(%s)
        """, (caster_name, caster_name))
        
        caster = cursor.fetchone()
        timings['get_character'] = time.time() - query_start
        
        if not caster:
            return {"error": f"Character '{caster_name}' not found"}
        
        char_id = caster['id']
        magic_rating = caster['current_magic']
        
        if not magic_rating or magic_rating == 0:
            return {"error": f"{caster_name} has no magic rating"}
        
        # Validate Magic Pool split
        total_pool_used = spell_pool_dice + drain_pool_dice
        if total_pool_used > magic_rating:
            return {
                "error": f"Magic Pool exceeded: {total_pool_used} dice requested but only {magic_rating} available"
            }
        
        # Check if character knows this spell
        query_start = time.time()
        cursor.execute("""
            SELECT spell_category, spell_type, drain_modifier
            FROM character_spells
            WHERE character_id = %s AND LOWER(spell_name) = LOWER(%s)
        """, (char_id, spell_name))
        
        spell_data = cursor.fetchone()
        timings['check_spell'] = time.time() - query_start
        
        if not spell_data:
            return {"error": f"{caster_name} does not know the spell '{spell_name}'"}
        
        spell_category = spell_data['spell_category']
        drain_modifier = spell_data.get('drain_modifier', 0)
        
        # Get Sorcery skill
        query_start = time.time()
        cursor.execute("""
            SELECT current_rating, specialization
            FROM character_skills
            WHERE character_id = %s AND LOWER(skill_name) = 'sorcery'
        """, (char_id,))
        
        skill_row = cursor.fetchone()
        sorcery_skill = skill_row['current_rating'] if skill_row else 0
        timings['get_sorcery'] = time.time() - query_start
        
        if sorcery_skill == 0:
            return {"error": f"{caster_name} has no Sorcery skill"}
        
        # Check for totem bonus/penalty
        query_start = time.time()
        cursor.execute("""
            SELECT c.totem, t.favored_categories, t.opposed_categories, t.bonus_dice, t.penalty_dice
            FROM characters c
            LEFT JOIN totems t ON c.totem = t.totem_name
            WHERE c.id = %s
        """, (char_id,))
        
        totem_row = cursor.fetchone()
        timings['check_totem'] = time.time() - query_start
        totem_bonus = 0
        totem_penalty = 0
        totem_name = None
        
        if totem_row and totem_row['totem']:
            totem_name = totem_row['totem']
            favored_categories = totem_row['favored_categories'] or []
            opposed_categories = totem_row['opposed_categories'] or []
            
            if spell_category in favored_categories:
                totem_bonus = totem_row['bonus_dice'] or 2
            
            if spell_category in opposed_categories:
                totem_penalty = totem_row['penalty_dice'] or -2
        
        # Check for applicable foci
        query_start = time.time()
        cursor.execute("""
            SELECT 
                focus_name,
                focus_type,
                force,
                spell_category,
                specific_spell,
                bonus_dice,
                tn_modifier
            FROM character_foci
            WHERE character_id = %s 
              AND bonded = true
              AND focus_type = 'spell'
              AND (
                  (specific_spell IS NULL AND LOWER(spell_category) = LOWER(%s))
                  OR LOWER(specific_spell) = LOWER(%s)
              )
            ORDER BY force DESC
        """, (char_id, spell_category, spell_name))
        
        foci = cursor.fetchall()
        timings['get_foci'] = time.time() - query_start
        
        # Apply best applicable focus
        focus_bonus = 0
        focus_name = None
        focus_force = 0
        
        for focus in foci:
            if focus['force'] >= force:
                focus_bonus = focus.get('bonus_dice', 0)
                focus_name = focus['focus_name']
                focus_force = focus['force']
                break
        
        # Calculate dice pools
        spell_dice_pool = sorcery_skill + spell_pool_dice + totem_bonus + totem_penalty + focus_bonus
        drain_dice_pool = caster['current_willpower'] + drain_pool_dice
        
        # Target Number = Force of spell
        target_number = force
        
        # Drain calculation
        base_drain = force // 2
        total_drain = base_drain + drain_modifier
        drain_code = "M" if force <= 6 else "S"
        
        # Roll spellcasting test
        roll_start = time.time()
        spell_result = DiceRoller.roll_with_target_number(spell_dice_pool, target_number)
        
        # Roll drain resistance
        drain_result = DiceRoller.roll_with_target_number(drain_dice_pool, total_drain)
        timings['dice_rolls'] = time.time() - roll_start
        
        # Calculate damage taken
        drain_damage = max(0, total_drain - drain_result.successes)
        
        # Determine spell success
        spell_success = spell_result.successes > 0
        
        # Calculate total time
        timings['total'] = time.time() - start_time
        
        result = {
            "caster": caster_name,
            "spell": spell_name,
            "spell_category": spell_category,
            "force": force,
            "target": target_name,
            "magic_rating": magic_rating,
            "spell_pool_dice": spell_pool_dice,
            "drain_pool_dice": drain_pool_dice,
            "sorcery_skill": sorcery_skill,
            "totem_bonus": totem_bonus,
            "totem_penalty": totem_penalty,
            "totem_name": totem_name,
            "focus_bonus": focus_bonus,
            "focus_name": focus_name,
            "focus_force": focus_force,
            "spell_dice_pool": spell_dice_pool,
            "target_number": target_number,
            "spell_roll": {
                "rolls": spell_result.rolls,
                "successes": spell_result.successes,
                "result": "success" if spell_success else "failure"
            },
            "drain": {
                "base_level": base_drain,
                "modifier": drain_modifier,
                "total_level": total_drain,
                "code": drain_code,
                "resist_dice": drain_dice_pool,
                "resist_roll": {
                    "rolls": drain_result.rolls,
                    "successes": drain_result.successes
                },
                "damage_taken": drain_damage,
                "damage_type": drain_code
            },
            "summary": f"{caster_name} casts {spell_name} at Force {force}. " +
                      (f"Totem {totem_name} grants +{totem_bonus} dice. " if totem_bonus > 0 else "") +
                      (f"Totem {totem_name} imposes {totem_penalty} dice penalty. " if totem_penalty < 0 else "") +
                      (f"Using {focus_name} (Force {focus_force}). " if focus_name else "") +
                      f"Spell: {spell_dice_pool}d6 vs TN {target_number} = {spell_result.successes} successes. " +
                      f"Drain: {drain_dice_pool}d6 vs {total_drain}{drain_code} = {drain_result.successes} successes, {drain_damage} damage taken.",
            
            # Performance timing
            "performance": {
                "timings_ms": {k: round(v * 1000, 2) for k, v in timings.items()},
                "total_ms": round(timings['total'] * 1000, 2),
                "breakdown": {
                    "database_queries": round((timings.get('get_character', 0) + 
                                               timings.get('check_spell', 0) + 
                                               timings.get('get_sorcery', 0) + 
                                               timings.get('check_totem', 0) + 
                                               timings.get('get_foci', 0)) * 1000, 2),
                    "dice_rolling": round(timings.get('dice_rolls', 0) * 1000, 2),
                    "overhead": round((timings.get('db_connection', 0)) * 1000, 2)
                }
            }
        }
        
        return convert_db_types(result)
    
    finally:
        cursor.close()
        conn.close()

async def test_spellcasting():
    """Test spellcasting with timing"""
    
    print("=" * 80)
    print("TESTING SPELLCASTING WITH TIMING")
    print("=" * 80)
    
    # Test 1: Basic spell
    print("\n1. Testing basic spell (Levitate at Force 4) with Block")
    print("-" * 80)
    
    result = await cast_spell(
        caster_name="Block",
        spell_name="Levitate",
        force=4,
        target_name="self",
        spell_pool_dice=2,
        drain_pool_dice=2
    )
    
    print(json.dumps(result, indent=2))
    
    if "performance" in result:
        print("\n" + "=" * 80)
        print("PERFORMANCE TIMING BREAKDOWN")
        print("=" * 80)
        perf = result["performance"]
        
        print(f"\nTotal Time: {perf['total_ms']:.2f}ms")
        print(f"\nDetailed Timings:")
        for key, value in perf["timings_ms"].items():
            if key != "total":
                print(f"  {key:20s}: {value:6.2f}ms")
        
        print(f"\nBreakdown by Category:")
        for key, value in perf["breakdown"].items():
            print(f"  {key:20s}: {value:6.2f}ms")
    else:
        print("\n⚠️  WARNING: No performance timing in response!")
    
    # Test 2: Higher force spell
    print("\n\n2. Testing higher force spell (Powerball at Force 8) with Block")
    print("-" * 80)
    
    result2 = await cast_spell(
        caster_name="Block",
        spell_name="Powerball",
        force=8,
        target_name="enemy",
        spell_pool_dice=2,
        drain_pool_dice=4
    )
    
    if "performance" in result2:
        perf2 = result2["performance"]
        print(f"\nTotal Time: {perf2['total_ms']:.2f}ms")
        print(f"Database Queries: {perf2['breakdown']['database_queries']:.2f}ms")
        print(f"Dice Rolling: {perf2['breakdown']['dice_rolling']:.2f}ms")
        print(f"Overhead: {perf2['breakdown']['overhead']:.2f}ms")
    else:
        print("\n⚠️  WARNING: No performance timing in response!")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_spellcasting())
