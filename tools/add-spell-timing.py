#!/usr/bin/env python3
"""
Add comprehensive timing instrumentation to cast_spell method
This script shows the changes needed - apply manually to game-server.py
"""

print("""
Add timing to each database query in _cast_spell method:

1. After getting character (already done):
   timings['get_character'] = time.time() - query_start

2. After checking spell:
   query_start = time.time()
   cursor.execute("SELECT spell_category...")
   timings['check_spell'] = time.time() - query_start

3. After getting Sorcery skill:
   query_start = time.time()
   cursor.execute("SELECT current_rating FROM character_skills...")
   timings['get_sorcery'] = time.time() - query_start

4. After checking totem:
   query_start = time.time()
   cursor.execute("SELECT c.totem, t.favored_categories...")
   timings['check_totem'] = time.time() - query_start

5. After getting foci:
   query_start = time.time()
   cursor.execute("SELECT focus_name, focus_type...")
   timings['get_foci'] = time.time() - query_start

6. After dice rolls:
   roll_start = time.time()
   spell_result = DiceRoller.roll_with_target_number(...)
   drain_result = DiceRoller.roll_with_target_number(...)
   timings['dice_rolls'] = time.time() - roll_start

7. Add total time and include in response:
   timings['total'] = time.time() - start_time
   
   result = {
       ...existing fields...,
       "performance": {
           "timings_ms": {k: round(v * 1000, 2) for k, v in timings.items()},
           "total_ms": round(timings['total'] * 1000, 2)
       }
   }

This will show:
- db_connection: Time to connect to database
- get_character: Time to fetch character data
- check_spell: Time to verify spell knowledge
- get_sorcery: Time to get Sorcery skill
- check_totem: Time to check totem bonuses
- get_foci: Time to get spell foci
- dice_rolls: Time for both spell and drain rolls
- total: Total execution time

Example output:
{
    "performance": {
        "timings_ms": {
            "db_connection": 5.23,
            "get_character": 12.45,
            "check_spell": 8.67,
            "get_sorcery": 6.34,
            "check_totem": 15.89,
            "get_foci": 22.11,
            "dice_rolls": 0.45,
            "total": 71.14
        },
        "total_ms": 71.14
    }
}
""")
