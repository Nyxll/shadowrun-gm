#!/usr/bin/env python3
"""
Clean up tools directory by archiving obsolete scripts
"""
import os
import shutil
from pathlib import Path

def cleanup_tools():
    """Archive obsolete tools"""
    tools = Path('tools')
    archive = tools / 'archive'
    
    # Create archive directory if it doesn't exist
    archive.mkdir(exist_ok=True)
    
    # Categories to archive (one-time use scripts)
    archive_prefixes = [
        'check-',      # 115 diagnostic scripts
        'verify-',     # 13 validation scripts
        'debug-',      # 4 debugging scripts
        'test-',       # 57 test scripts (will keep a few)
        'apply-',      # 21 migration scripts (already applied)
        'fix-',        # 45 fix scripts (issues fixed)
        'export-',     # 6 export scripts
        'upload-',     # 6 upload scripts
        'compare-',    # 4 comparison scripts
        'diagnose-',   # 1 diagnostic script
        'audit-',      # 4 audit scripts
    ]
    
    # Files to KEEP (don't archive these)
    keep_files = {
        # Active imports
        'import-characters-v12.py',
        'import-spells-dat.py',
        
        # Active tests
        'test-get-combat-pool.py',
        'test-cyberware-lookup.py',
        'test-range-staging.py',
        
        # Active checks (recent/useful)
        'check-conversation-history.py',
        'check-recent-chat.py',
        'check-platinum-combat-pool.py',
        'check-kent-pools.py',
        'check-house-rules-schema.py',
        'check-modifier-schema.py',
        
        # Active fixes
        'fix-kent-combat-pool.py',
        'fix-platinum-pool.py',
        
        # Active adds
        'add-platinum-house-rules.py',
        'add-platinum-custom-cyberware.py',
        'add-get-combat-pool-tool.py',
        
        # Utilities
        'show-session-history.py',
        'show-all-user-queries.py',
        'find-query-tables.py',
        
        # Migration (current)
        'apply-pool-migration.py',
    }
    
    archived = []
    kept = []
    
    for f in tools.glob('*'):
        if f.is_file() and f.name not in keep_files:
            # Check if file should be archived
            should_archive = any(f.name.startswith(prefix) for prefix in archive_prefixes)
            
            if should_archive:
                # Move to archive
                dest = archive / f.name
                shutil.move(str(f), str(dest))
                archived.append(f.name)
            else:
                kept.append(f.name)
        elif f.name in keep_files:
            kept.append(f.name)
    
    print(f"CLEANUP COMPLETE")
    print(f"=" * 70)
    print(f"Archived: {len(archived)} files")
    print(f"Kept:     {len(kept)} files")
    print(f"\nArchived files moved to: tools/archive/")
    
    return archived, kept

if __name__ == "__main__":
    print("This will archive 276 obsolete tool scripts.")
    print("Files will be moved to tools/archive/")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    input()
    
    archived, kept = cleanup_tools()
    
    print(f"\n✓ Cleanup successful!")
    print(f"\nKept files ({len(kept)}):")
    for f in sorted(kept)[:20]:
        print(f"  - {f}")
    if len(kept) > 20:
        print(f"  ... and {len(kept) - 20} more")
