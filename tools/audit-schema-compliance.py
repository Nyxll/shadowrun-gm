#!/usr/bin/env python3
"""
Audit all Python files for schema compliance issues
Finds operations that don't use proper schema patterns
"""

import os
import re
from pathlib import Path

def audit_file(filepath):
    """Audit a single file for schema issues"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for character_skills queries without both base_rating and current_rating
    for i, line in enumerate(lines, 1):
        # Look for SELECT from character_skills
        if 'SELECT' in line and 'character_skills' in line:
            # Check if both base_rating and current_rating are present
            # Look at the next few lines to capture multi-line queries
            query_block = '\n'.join(lines[max(0, i-1):min(len(lines), i+10)])
            
            has_base = 'base_rating' in query_block
            has_current = 'current_rating' in query_block
            
            if not (has_base and has_current):
                issues.append({
                    'line': i,
                    'type': 'character_skills_incomplete',
                    'message': f'Query missing {"base_rating" if not has_base else "current_rating"}',
                    'code': line.strip()
                })
        
        # Check for INSERT/UPDATE to character_skills
        if ('INSERT INTO character_skills' in line or 'UPDATE character_skills' in line):
            query_block = '\n'.join(lines[max(0, i-1):min(len(lines), i+10)])
            
            has_base = 'base_rating' in query_block
            has_current = 'current_rating' in query_block
            
            if not (has_base and has_current):
                issues.append({
                    'line': i,
                    'type': 'character_skills_incomplete_write',
                    'message': f'Write operation missing {"base_rating" if not has_base else "current_rating"}',
                    'code': line.strip()
                })
        
        # Check for direct character_id usage without lookup
        if 'character_id' in line and 'WHERE' in line:
            # Check if there's a character lookup pattern nearby
            context = '\n'.join(lines[max(0, i-20):min(len(lines), i+5)])
            
            has_lookup = (
                'get_character_id' in context or
                'lookup_character' in context or
                'character_name' in context or
                'SELECT id FROM characters WHERE name' in context
            )
            
            if not has_lookup and 'def ' not in line:
                issues.append({
                    'line': i,
                    'type': 'missing_character_lookup',
                    'message': 'Using character_id without visible character name lookup',
                    'code': line.strip()
                })
    
    return issues

def main():
    """Audit all Python files in lib/ and game-server.py"""
    print("="*80)
    print("SCHEMA COMPLIANCE AUDIT")
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
            
            # Group by type
            by_type = {}
            for issue in issues:
                issue_type = issue['type']
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append(issue)
            
            for issue_type, type_issues in by_type.items():
                print(f"\n{issue_type.upper().replace('_', ' ')} ({len(type_issues)} issues):")
                print("-" * 80)
                
                for issue in type_issues:
                    print(f"  Line {issue['line']}: {issue['message']}")
                    print(f"    {issue['code'][:100]}")
    
    print("\n" + "="*80)
    print(f"SUMMARY: {total_issues} issues found in {files_with_issues} files")
    print("="*80)
    
    if total_issues > 0:
        print("\nRECOMMENDATIONS:")
        print("1. All character_skills queries must include BOTH base_rating AND current_rating")
        print("2. All operations should lookup character by name first, then use UUID")
        print("3. Never assume character_id type - always convert name → UUID")

if __name__ == "__main__":
    main()
