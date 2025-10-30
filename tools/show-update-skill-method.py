#!/usr/bin/env python3
"""Show the update_skill method around line 1132"""

from pathlib import Path

def show_method():
    crud_file = Path("lib/comprehensive_crud.py")
    lines = crud_file.read_text().split('\n')
    
    # Find the method containing line 1132
    # Go back to find the def
    for i in range(1131, 0, -1):
        if 'def update_skill' in lines[i]:
            # Show from def to 20 lines after line 1132
            start = i
            end = min(len(lines), 1137)
            
            print(f"Method starting at line {start+1}:")
            print("="*80)
            for j in range(start, end):
                marker = ">>>" if j == 1131 else "   "
                print(f"{marker} {j+1:4d}: {lines[j]}")
            break

if __name__ == "__main__":
    show_method()
