#!/usr/bin/env python3
"""
Audit all tools in the tools/ directory

This script analyzes all Python files in tools/ and categorizes them by:
- Function (import, check, fix, test, generate)
- Status (active, obsolete, duplicate)
- Dependencies
- Last modified date
- Lines of code

Generates: docs/TOOL-INVENTORY.md
"""
import sys
from pathlib import Path
import re
from datetime import datetime
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.logging_utils import setup_logger, log_section, log_success, log_table, OperationTimer

logger = setup_logger(__name__)

def categorize_by_name(filename: str) -> str:
    """Categorize tool by filename pattern"""
    name_lower = filename.lower()
    
    # Import tools
    if name_lower.startswith(('import-', 'load-', 'upload-')):
        return 'import'
    
    # Check/verify tools
    if name_lower.startswith(('check-', 'verify-', 'inspect-', 'audit-', 'show-', 'find-')):
        return 'check'
    
    # Fix/apply tools
    if name_lower.startswith(('fix-', 'apply-', 'migrate-', 'ensure-', 'rebuild-')):
        return 'fix'
    
    # Test/debug tools
    if name_lower.startswith(('test-', 'debug-')):
        return 'test'
    
    # Generate/create/export tools
    if name_lower.startswith(('generate-', 'create-', 'export-', 'add-')):
        return 'generate'
    
    # Compare/analyze tools
    if name_lower.startswith(('compare-',)):
        return 'analyze'
    
    return 'other'

def detect_version_suffix(filename: str) -> tuple[bool, str]:
    """Detect if file has version suffix like -v6, -v7, etc."""
    match = re.search(r'-v(\d+)\.py$', filename)
    if match:
        return True, match.group(1)
    return False, ''

def count_lines(filepath: Path) -> int:
    """Count lines of code in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

def get_file_age_days(filepath: Path) -> int:
    """Get file age in days"""
    try:
        mtime = filepath.stat().st_mtime
        age = datetime.now().timestamp() - mtime
        return int(age / 86400)  # Convert to days
    except:
        return 0

def analyze_dependencies(filepath: Path) -> list:
    """Analyze what the file imports"""
    deps = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for common patterns
            if 'psycopg2' in content or 'get_db_connection' in content:
                deps.append('database')
            if 'import json' in content or 'json.load' in content:
                deps.append('json')
            if 'requests' in content:
                deps.append('http')
            if 'from lib.' in content:
                deps.append('lib')
            if 'dotenv' in content:
                deps.append('env')
                
    except:
        pass
    return deps

def main():
    """Audit all tools"""
    
    with OperationTimer(logger, "Tool Audit"):
        tools_dir = Path(__file__).parent
        
        # Find all Python files
        all_files = list(tools_dir.glob('*.py'))
        logger.info(f"Found {len(all_files)} Python files in tools/")
        
        # Analyze each file
        tools = []
        for filepath in all_files:
            filename = filepath.name
            
            # Skip this audit script
            if filename == 'audit_all_tools.py':
                continue
            
            category = categorize_by_name(filename)
            is_versioned, version = detect_version_suffix(filename)
            lines = count_lines(filepath)
            age_days = get_file_age_days(filepath)
            deps = analyze_dependencies(filepath)
            
            # Determine status
            status = 'active'
            if is_versioned:
                status = 'versioned'
            elif age_days > 90 and lines < 50:
                status = 'possibly_obsolete'
            
            tools.append({
                'filename': filename,
                'category': category,
                'status': status,
                'version': version,
                'lines': lines,
                'age_days': age_days,
                'dependencies': deps
            })
        
        # Sort by category, then filename
        tools.sort(key=lambda x: (x['category'], x['filename']))
        
        # Generate statistics
        log_section(logger, "STATISTICS")
        
        by_category = defaultdict(int)
        by_status = defaultdict(int)
        total_lines = 0
        
        for tool in tools:
            by_category[tool['category']] += 1
            by_status[tool['status']] += 1
            total_lines += tool['lines']
        
        logger.info(f"Total tools: {len(tools)}")
        logger.info(f"Total lines of code: {total_lines:,}")
        logger.info("")
        
        # Category breakdown
        log_table(logger, 
            ["Category", "Count", "Percentage"],
            [[cat, count, f"{count/len(tools)*100:.1f}%"] 
             for cat, count in sorted(by_category.items(), key=lambda x: -x[1])]
        )
        
        logger.info("")
        
        # Status breakdown
        log_table(logger,
            ["Status", "Count", "Percentage"],
            [[status, count, f"{count/len(tools)*100:.1f}%"]
             for status, count in sorted(by_status.items(), key=lambda x: -x[1])]
        )
        
        # Generate markdown report
        log_section(logger, "GENERATING REPORT")
        
        report_path = Path(__file__).parent.parent / 'docs' / 'TOOL-INVENTORY.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Tool Inventory - Complete Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Tools:** {len(tools)}\n")
            f.write(f"- **Total Lines:** {total_lines:,}\n")
            f.write(f"- **Categories:** {len(by_category)}\n\n")
            
            # Category breakdown
            f.write("### By Category\n\n")
            f.write("| Category | Count | Percentage | Avg Lines |\n")
            f.write("|----------|-------|------------|----------|\n")
            for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
                avg_lines = sum(t['lines'] for t in tools if t['category'] == cat) / count
                f.write(f"| {cat} | {count} | {count/len(tools)*100:.1f}% | {avg_lines:.0f} |\n")
            f.write("\n")
            
            # Status breakdown
            f.write("### By Status\n\n")
            f.write("| Status | Count | Percentage |\n")
            f.write("|--------|-------|------------|\n")
            for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
                f.write(f"| {status} | {count} | {count/len(tools)*100:.1f}% |\n")
            f.write("\n")
            
            # Detailed listings by category
            f.write("## Detailed Listings\n\n")
            
            for category in sorted(by_category.keys()):
                cat_tools = [t for t in tools if t['category'] == category]
                f.write(f"### {category.upper()} Tools ({len(cat_tools)} files)\n\n")
                
                f.write("| Filename | Lines | Age (days) | Status | Dependencies |\n")
                f.write("|----------|-------|------------|--------|-------------|\n")
                
                for tool in cat_tools:
                    deps_str = ', '.join(tool['dependencies']) if tool['dependencies'] else '-'
                    f.write(f"| {tool['filename']} | {tool['lines']} | {tool['age_days']} | {tool['status']} | {deps_str} |\n")
                
                f.write("\n")
            
            # Consolidation recommendations
            f.write("## Consolidation Recommendations\n\n")
            
            # Versioned files
            versioned = [t for t in tools if t['status'] == 'versioned']
            if versioned:
                f.write(f"### Versioned Files ({len(versioned)} files)\n\n")
                f.write("These files have version suffixes (e.g., -v6, -v7) and should be consolidated:\n\n")
                
                # Group by base name
                by_base = defaultdict(list)
                for tool in versioned:
                    base = re.sub(r'-v\d+\.py$', '', tool['filename'])
                    by_base[base].append(tool)
                
                for base, versions in sorted(by_base.items()):
                    f.write(f"**{base}**: {len(versions)} versions\n")
                    for v in sorted(versions, key=lambda x: x['version']):
                        f.write(f"  - {v['filename']} ({v['lines']} lines, {v['age_days']} days old)\n")
                    f.write("\n")
            
            # Possibly obsolete
            obsolete = [t for t in tools if t['status'] == 'possibly_obsolete']
            if obsolete:
                f.write(f"### Possibly Obsolete ({len(obsolete)} files)\n\n")
                f.write("Small files (< 50 lines) not modified in 90+ days:\n\n")
                for tool in sorted(obsolete, key=lambda x: -x['age_days']):
                    f.write(f"- {tool['filename']} ({tool['lines']} lines, {tool['age_days']} days old)\n")
                f.write("\n")
            
            # Consolidation targets
            f.write("### Consolidation Targets\n\n")
            
            targets = {
                'import': ('import_characters.py', 'import_spells.py', 'import_gear.py'),
                'check': ('check_schema.py', 'check_characters.py', 'check_modifiers.py', 
                         'check_magic.py', 'check_gear.py', 'verify_integrity.py'),
                'fix': ('apply_migration.py', 'fix_schema.py', 'fix_data.py', 
                       'cleanup_test_data.py', 'ensure_system.py'),
                'generate': ('generate_tool_defs.py', 'export_characters.py', 
                            'process_training.py', 'generate_reports.py'),
            }
            
            for cat, target_files in targets.items():
                cat_count = by_category.get(cat, 0)
                if cat_count > 0:
                    f.write(f"**{cat.upper()}**: {cat_count} files → {len(target_files)} files\n")
                    for target in target_files:
                        f.write(f"  - {target}\n")
                    f.write("\n")
        
        log_success(logger, f"Report generated: {report_path}")
        
        # Summary
        logger.info("")
        log_section(logger, "AUDIT COMPLETE")
        logger.info(f"Analyzed {len(tools)} tools")
        logger.info(f"Total lines: {total_lines:,}")
        logger.info(f"Report: docs/TOOL-INVENTORY.md")
        
        return 0

if __name__ == '__main__':
    sys.exit(main())
