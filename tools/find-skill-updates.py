#!/usr/bin/env python3
"""Find the character_skills UPDATE statements that need fixing"""

from pathlib import Path

def find_skill_updates():
    crud_file = Path("lib/comprehensive_crud.py")
    lines = crud_file.read_text().split('\n')
    
    print("Searching for character_skills UPDATE statements...\n")
    
    for i, line in enumerate(lines, 1):
        if 'UPDATE character_skills' in line:
            # Show context: 5 lines before and 5 lines after
            start = max(0, i-6)
            end = min(len(lines), i+5)
            
            print(f"="*80)
            print(f"Found at line {i}:")
            print(f"="*80)
            for j in range(start, end):
                marker = ">>>" if j == i-1 else "   "
                print(f"{marker} {j+1:4d}: {lines[j]}")
            print()

if __name__ == "__main__":
    find_skill_updates()
