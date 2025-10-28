#!/usr/bin/env python3
import re

with open('data-load-final-1.sql', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== POWERS TABLE ===")
powers = re.search(r'INSERT INTO powers.*?;', content, re.DOTALL)
if powers:
    print(powers.group(0)[:300])
    print("\nChecking patterns:")
    print("  ARRAY[]::text[] in powers:", "ARRAY[]::text[]" in powers.group(0))
    print("  '[]'::jsonb in powers:", "'[]'::jsonb" in powers.group(0))

print("\n=== METATYPES TABLE ===")
metatypes = re.search(r'INSERT INTO metatypes.*?;', content, re.DOTALL)
if metatypes:
    print(metatypes.group(0)[:300])
    print("\nChecking patterns:")
    print("  ARRAY[]::text[] in metatypes:", "ARRAY[]::text[]" in metatypes.group(0))
    print("  '[]'::jsonb in metatypes:", "'[]'::jsonb" in metatypes.group(0))

print("\n=== GEAR TABLE ===")
gear = re.search(r'INSERT INTO gear.*?;', content, re.DOTALL)
if gear:
    print(gear.group(0)[:300])
    print("\nChecking patterns:")
    print("  ARRAY[]::text[] in gear:", "ARRAY[]::text[]" in gear.group(0))
    print("  '[]'::jsonb in gear:", "'[]'::jsonb" in gear.group(0))
