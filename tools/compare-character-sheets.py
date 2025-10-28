#!/usr/bin/env python3
"""
Compare original character sheets with v1 exported versions
"""
import os
from pathlib import Path

def compare_files(original_path, v1_path):
    """Compare two character sheet files"""
    
    if not os.path.exists(original_path):
        return f"❌ Original file not found: {original_path}"
    
    if not os.path.exists(v1_path):
        return f"❌ V1 file not found: {v1_path}"
    
    with open(original_path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    with open(v1_path, 'r', encoding='utf-8') as f:
        v1 = f.read()
    
    # Count lines
    orig_lines = original.split('\n')
    v1_lines = v1.split('\n')
    
    # Find differences
    differences = []
    
    # Check for major section presence
    sections = [
        "## Basic Information",
        "## Attributes",
        "## Derived Stats",
        "## Edges and Flaws",
        "## Skills",
        "## Cyberware/Bioware",
        "## Gear",
        "## Magic",
        "## Contacts",
        "## Background",
        "## Notes"
    ]
    
    for section in sections:
        in_orig = section in original
        in_v1 = section in v1
        if in_orig != in_v1:
            differences.append(f"  Section '{section}': Original={in_orig}, V1={in_v1}")
    
    # Compare line counts
    if len(orig_lines) != len(v1_lines):
        differences.append(f"  Line count: Original={len(orig_lines)}, V1={len(v1_lines)}")
    
    # Check for enriched data markers
    enriched_markers = [
        "No penalty for using off-hand",  # Ambidexterity description
        "One attribute can exceed racial maximum",  # Exceptional Attribute
        "Character has lost memories",  # Amnesia
    ]
    
    enriched_count = sum(1 for marker in enriched_markers if marker in v1)
    
    if differences:
        result = f"⚠️  Differences found:\n" + "\n".join(differences)
    else:
        result = f"✅ Structure matches!"
    
    result += f"\n  Enriched descriptions: {enriched_count}/{len(enriched_markers)}"
    
    return result

def main():
    """Compare all character sheets"""
    print("="*70)
    print("COMPARING ORIGINAL VS V1 CHARACTER SHEETS")
    print("="*70)
    
    # Map character names to file names
    characters = {
        "Platinum": "Platinum.md",
        "Kent Jefferies": "Kent Jefferies.md",
    }
    
    # Get all files in characters/ directory
    char_dir = Path("characters")
    v1_dir = Path("characters/v1")
    
    # Find all markdown files in characters/ (excluding subdirectories)
    original_files = [f for f in char_dir.glob("*.md") if f.is_file()]
    
    print(f"\nFound {len(original_files)} original character sheets\n")
    
    for orig_file in sorted(original_files):
        char_name = orig_file.stem
        v1_file = v1_dir / f"{char_name}.md"
        
        print(f"\n{char_name}:")
        print("-" * 70)
        result = compare_files(str(orig_file), str(v1_file))
        print(result)
    
    print("\n" + "="*70)
    print("COMPARISON COMPLETE")
    print("="*70)
    print("\nKey:")
    print("  ✅ = Structure matches between original and v1")
    print("  ⚠️  = Differences detected (may be expected)")
    print("  ❌ = File missing")
    print("\nNote: V1 files include enriched descriptions from database")

if __name__ == "__main__":
    main()
