#!/usr/bin/env python3
"""
Generate a detailed cleanup report for manual review
Shows what would be kept vs archived with reasoning
"""
from pathlib import Path
from collections import defaultdict

def analyze_for_cleanup():
    """Analyze tools and generate cleanup recommendations"""
    tools = Path('tools')
    
    # Define what to keep
    keep_always = {
        # Current/latest imports
        'import-characters-v12.py',
        'import-spells-dat.py',
        
        # All test files (unit/functional tests)
        'test-*',
        
        # Utility scripts
        'show-*',
        'find-*',
        'create-*',
        'parse-*',
        'process-*',
        
        # Recent/useful checks
        'check-conversation-history.py',
        'check-recent-chat.py',
        'check-platinum-combat-pool.py',
        'check-kent-pools.py',
        'check-house-rules-schema.py',
        'check-modifier-schema.py',
        
        # Active fixes
        'fix-kent-combat-pool.py',
        'fix-platinum-pool.py',
        
        # Active data tools
        'add-platinum-house-rules.py',
        'add-platinum-custom-cyberware.py',
        'add-get-combat-pool-tool.py',
        
        # Current migration
        'apply-pool-migration.py',
    }
    
    # Categorize all files
    keep = []
    archive_maybe = defaultdict(list)
    
    for f in tools.glob('*'):
        if not f.is_file():
            continue
            
        name = f.name
        
        # Check if explicitly kept
        if name in keep_always:
            keep.append((name, 'Explicitly listed as essential'))
            continue
        
        # Check pattern matches
        kept = False
        for pattern in keep_always:
            if '*' in pattern:
                prefix = pattern.replace('*', '')
                if name.startswith(prefix):
                    keep.append((name, f'Matches pattern: {pattern}'))
                    kept = True
                    break
        
        if kept:
            continue
        
        # Categorize for potential archival
        if name.startswith('check-'):
            archive_maybe['check'].append((name, 'One-time diagnostic script'))
        elif name.startswith('verify-'):
            archive_maybe['verify'].append((name, 'One-time validation script'))
        elif name.startswith('debug-'):
            archive_maybe['debug'].append((name, 'One-time debugging script'))
        elif name.startswith('apply-'):
            archive_maybe['apply'].append((name, 'Migration script (likely already applied)'))
        elif name.startswith('fix-'):
            archive_maybe['fix'].append((name, 'Fix script (issue likely resolved)'))
        elif name.startswith('export-'):
            archive_maybe['export'].append((name, 'Export script (one-time use)'))
        elif name.startswith('upload-'):
            archive_maybe['upload'].append((name, 'Upload script (one-time use)'))
        elif name.startswith('compare-'):
            archive_maybe['compare'].append((name, 'Comparison script (one-time use)'))
        elif name.startswith('diagnose-'):
            archive_maybe['diagnose'].append((name, 'Diagnostic script (one-time use)'))
        elif name.startswith('audit-'):
            archive_maybe['audit'].append((name, 'Audit script (one-time use)'))
        elif name.startswith('import-'):
            archive_maybe['import'].append((name, 'OLD import script (superseded by v12)'))
        elif name.startswith('add-'):
            archive_maybe['add'].append((name, 'Data addition script (one-time use)'))
        elif name.startswith('update-'):
            archive_maybe['update'].append((name, 'Update script (one-time use)'))
        else:
            keep.append((name, 'Does not match archive patterns'))
    
    # Generate report
    print("=" * 80)
    print("TOOLS CLEANUP REVIEW REPORT")
    print("=" * 80)
    
    print(f"\n✓ KEEP ({len(keep)} files)")
    print("-" * 80)
    for name, reason in sorted(keep):
        print(f"  {name:50s} | {reason}")
    
    total_archive = sum(len(files) for files in archive_maybe.values())
    print(f"\n✗ RECOMMEND ARCHIVING ({total_archive} files)")
    print("-" * 80)
    
    for category in sorted(archive_maybe.keys()):
        files = archive_maybe[category]
        print(f"\n  {category.upper()} ({len(files)} files):")
        for name, reason in sorted(files):
            print(f"    {name:48s} | {reason}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files:     {len(keep) + total_archive}")
    print(f"Keep:            {len(keep)} ({len(keep)/(len(keep)+total_archive)*100:.1f}%)")
    print(f"Archive:         {total_archive} ({total_archive/(len(keep)+total_archive)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review this report carefully")
    print("2. Check if any 'ARCHIVE' files are still needed")
    print("3. Update cleanup_tools.py if needed")
    print("4. Run cleanup_tools.py to execute the archival")
    
    # Save report to file
    report_file = Path('tools_cleanup_report.txt')
    with open(report_file, 'w') as f:
        f.write("TOOLS CLEANUP REVIEW REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"KEEP ({len(keep)} files)\n")
        f.write("-" * 80 + "\n")
        for name, reason in sorted(keep):
            f.write(f"{name:50s} | {reason}\n")
        
        f.write(f"\nRECOMMEND ARCHIVING ({total_archive} files)\n")
        f.write("-" * 80 + "\n")
        for category in sorted(archive_maybe.keys()):
            files = archive_maybe[category]
            f.write(f"\n{category.upper()} ({len(files)} files):\n")
            for name, reason in sorted(files):
                f.write(f"  {name:48s} | {reason}\n")
    
    print(f"\n✓ Report saved to: {report_file}")

if __name__ == "__main__":
    analyze_for_cleanup()
