#!/usr/bin/env python3
with open('game-server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'stored_description' in line:
        print(f"\n=== Around line {i+1} ===")
        for j in range(max(0, i-10), min(len(lines), i+15)):
            print(f"{j+1}: {lines[j]}", end='')
