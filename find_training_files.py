#!/usr/bin/env python3
from pathlib import Path

tools = Path('tools')

# Find training-related files
keywords = ['training', 'parse', 'process', 'analyze']

print("TRAINING-RELATED FILES IN TOOLS/")
print("=" * 70)

for keyword in keywords:
    files = [f.name for f in tools.glob('*') if f.is_file() and keyword in f.name.lower()]
    if files:
        print(f"\n{keyword.upper()}:")
        for f in sorted(files):
            print(f"  - {f}")

# Also check root directory
print("\n\nTRAINING FILES IN ROOT:")
print("=" * 70)
root = Path('.')
for f in root.glob('*training*'):
    if f.is_file():
        print(f"  - {f.name}")
