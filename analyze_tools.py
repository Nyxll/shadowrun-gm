#!/usr/bin/env python3
import os
from pathlib import Path
from collections import defaultdict

tools = Path('tools')

# Categorize by prefix
categories = defaultdict(list)
prefixes = ['check', 'test', 'fix', 'apply', 'import', 'verify', 'update', 
            'add', 'debug', 'export', 'upload', 'show', 'find', 'create',
            'clean', 'compare', 'diagnose', 'enhance', 'enrich', 'ensure',
            'expand', 'extract', 'final', 'parse', 'process', 'rebuild',
            'refactor', 'remove', 'repair', 'restore', 'sync', 'training',
            'view', 'migrate', 'analyze', 'audit', 'calculate', 'combine',
            'count', 'enable']

for f in tools.glob('*'):
    if f.is_file():
        name = f.name.lower()
        categorized = False
        for prefix in prefixes:
            if name.startswith(prefix + '-') or name.startswith(prefix + '_'):
                categories[prefix].append(f.name)
                categorized = True
                break
        if not categorized:
            categories['other'].append(f.name)

total = sum(len(files) for files in categories.values())

print(f"TOOLS DIRECTORY ANALYSIS - BY CATEGORY")
print(f"=" * 70)
print(f"Total files: {total}\n")

# Sort by count
sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

for category, files in sorted_cats:
    if files:
        print(f"{category.upper():15s} {len(files):3d} files ({len(files)/total*100:5.1f}%)")

print(f"\n" + "=" * 70)
print("ARCHIVAL RECOMMENDATIONS")
print("=" * 70)

# Files that are likely obsolete
archive_categories = {
    'check': 'Most check-* scripts are one-time diagnostics',
    'verify': 'Most verify-* scripts are one-time validations', 
    'debug': 'Most debug-* scripts are one-time debugging',
    'test': 'Old test-* scripts (keep only active tests)',
    'apply': 'Old apply-* migration scripts (already applied)',
    'fix': 'Old fix-* scripts (issues already fixed)',
    'export': 'Old export-* scripts',
    'upload': 'Old upload-* scripts',
    'compare': 'Comparison scripts (one-time use)',
    'diagnose': 'Diagnostic scripts (one-time use)',
    'audit': 'Audit scripts (one-time use)',
}

archivable = 0
for cat, reason in archive_categories.items():
    if cat in categories:
        count = len(categories[cat])
        archivable += count
        print(f"\n{cat.upper()} ({count} files)")
        print(f"  Reason: {reason}")
        # Show a few examples
        for f in sorted(categories[cat])[:3]:
            print(f"    - {f}")
        if count > 3:
            print(f"    ... and {count - 3} more")

print(f"\n" + "=" * 70)
print(f"SUMMARY")
print(f"=" * 70)
print(f"Total files:           {total}")
print(f"Can archive:           {archivable} ({archivable/total*100:.1f}%)")
print(f"Should keep:           {total - archivable} ({(total-archivable)/total*100:.1f}%)")

print(f"\nKEEP (Essential tools):")
keep_categories = ['import', 'show', 'find', 'create', 'parse', 'process']
keep_count = sum(len(categories[cat]) for cat in keep_categories if cat in categories)
print(f"  {keep_count} files from: {', '.join(keep_categories)}")
