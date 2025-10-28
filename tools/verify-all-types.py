#!/usr/bin/env python3
import re

with open('data-load-final-1.sql', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== POWERS TABLE ===")
powers = re.search(r'INSERT INTO powers.*?;', content, re.DOTALL)
if powers:
    line = powers.group(0)
    print("Full INSERT (truncated):")
    print(line[:500])
    print("\nColumn values:")
    print("  game_effects:", "'{}'" in line and "'{}'::jsonb" in line)
    print("  levels:", "'[]'::jsonb" in line)
    print("  loaded_from:", "NULL" in line or "ARRAY" in line)

print("\n=== METATYPES TABLE ===")
metatypes = re.search(r'INSERT INTO metatypes.*?;', content, re.DOTALL)
if metatypes:
    line = metatypes.group(0)
    print("Full INSERT (truncated):")
    print(line[:500])
    print("\nColumn values:")
    print("  special_abilities:", "ARRAY[]::text[]" in line)
    print("  racial_traits:", "'{}'::jsonb" in line)

print("\n=== GEAR TABLE ===")
gear = re.search(r'INSERT INTO gear.*?;', content, re.DOTALL)
if gear:
    line = gear.group(0)
    print("Full INSERT (truncated):")
    print(line[:500])
    print("\nColumn values:")
    print("  base_stats:", line.count("'{}'::jsonb") >= 1 or '"' in line and "jsonb" in line)
    print("  modifiers:", line.count("'{}'::jsonb") >= 2)
    print("  requirements:", line.count("'{}'::jsonb") >= 3)
    print("  tags:", "ARRAY[]::text[]" in line)
    print("  loaded_from:", line.count("ARRAY") >= 2 or "NULL" in line)
