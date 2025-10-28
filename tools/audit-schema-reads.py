#!/usr/bin/env python3
"""
Audit SELECT operations for schema compliance
Focus on READ operations that might be missing required fields
"""

import os
import re
from pathlib import Path

def audit_file(filepath):
    """Audit a single file for SELECT statement issues"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Look for SELECT from character_skills
        if 'SELECT' in line and 'character_skills' in line:
            # Get the full query (may span multiple lines)
            query_start = i - 1
            query_end = i + 15  # Look ahead
            query_block = '\n'.join(lines[query_start:min(len(lines), query_end)])
            
            # Check if it's SELECT *
            if 'SELECT *' in query_block:
                continue  # SELECT * is fine, gets all columns
            
            # Check if both base_rating and current_rating are in the SELECT
            has_base = 'base_rating' in query_block
            has_current = 'current_rating' in query_block
            
            if not (has_base and has_current):
                # Extract just the SELECT portion
                select_match = re.search(r'SELECT\s+(.+?)\s+FROM', query_block, re.DOTALL | re.IGNORECASE)
                if select_match:
                    selected_fields = select_match.group(1).strip()
                    issues.append({
                        'line': i,
                        'type': 'incomplete_select',
                        'message': f'SELECT missing {"base_rating" if not has_base else "current_rating"}',
                        'code': line.strip(),
                        'selected_fields': selected_fields[:100]
                    })
    
    return issues

def main():
    """Audit all Python files for SELECT statement issues"""
    print("="*80)
    print("SCHEMA READ COMPLIANCE AUDIT")
    print("Checking SELECT statements from character_skills")
    print("="*80)
    print()
    
    files_to_audit = [
        'lib/mcp_operations.py',
        'lib/comprehensive_crud.py',
        'game-server.py',
    ]
    
    # Also check all files in lib/
    lib_dir = Path('lib')
    if lib_dir.exists():
        for py_file in lib_dir.glob('*.py'):
            if str(py_file) not in files_to_audit:
                files_to_audit.append(str(py_file))
    
    total_issues = 0
    files_with_issues = 0
    
    for filepath in files_to_audit:
        if not os.path.exists(filepath):
            continue
        
        issues = audit_file(filepath)
        
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            
            print(f"\n{'='*80}")
            print(f"FILE: {filepath}")
            print(f"{'='*80}")
            
            for issue in issues:
                print(f"\nLine {issue['line']}: {issue['message']}")
                print(f"  Code: {issue['code']}")
                print(f"  Selected: {issue['selected_fields']}")
    
    print("\n" + "="*80)
    if total_issues > 0:
        print(f"FOUND: {total_issues} SELECT statements with incomplete field lists in {files_with_issues} files")
        print("="*80)
        print("\nRECOMMENDATION:")
        print("All SELECT statements from character_skills should either:")
        print("  1. Use SELECT * to get all columns, OR")
        print("  2. Explicitly include BOTH base_rating AND current_rating")
    else:
        print("SUCCESS: All SELECT statements are properly formed!")
        print("="*80)

if __name__ == "__main__":
    main()
