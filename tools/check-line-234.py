#!/usr/bin/env python3
with open('characters/Platinum.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(233, 237):
        print(f'Line {i+1}: {repr(lines[i])}')
