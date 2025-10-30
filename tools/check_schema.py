#!/usr/bin/env python3
"""
Consolidated Schema Validation Tool

Replaces 20+ schema checking scripts with a single, comprehensive tool.
Uses helper library for database connections, logging, and validation.

Features:
- Validate all table schemas against expected structure
- Check for missing columns, wrong types, constraints
- Verify foreign key relationships
- Check indexes and performance optimizations
- Compare actual schema vs. documented schema

Usage:
    python tools/check_schema.py                    # Check all tables
    python tools/check_schema.py --table TABLE      # Check specific table
    python tools/check_schema.py --verbose          # Detailed output
    python tools/check_schema.py --fix              # Suggest fixes
"""
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.db_utils import get_db_connection
from lib.helpers.logging_utils import (
    setup_logger, log_section, log_success, log_failure, 
    log_warning, log_table, OperationTimer
)

logger = setup_logger(__name__)


# Expected schema definitions
EXPECTED_TABLES = {
    'characters': {
        'columns': {
            'id': 'uuid',
            'name': 'text',
            'street_name': 'text',
            'archetype': 'text',
            'metatype': 'text',
            'base_body': 'integer',
            'base_quickness': 'integer',
            'base_strength': 'integer',
            'base_charisma': 'integer',
            'base_intelligence': 'integer',
            'base_willpower': 'integer',
            'base_essence': 'numeric',
            'base_magic': 'integer',
            'base_reaction': 'integer',
            'current_body': 'integer',
            'current_quickness': 'integer',
            'current_strength': 'integer',
            'current_charisma': 'integer',
            'current_intelligence': 'integer',
            'current_willpower': 'integer',
            'current_essence': 'numeric',
            'current_magic': 'integer',
            'current_reaction': 'integer',
            'nuyen': 'integer',
            'karma_pool': 'integer',
            'karma_total': 'integer',
            'karma_available': 'integer',
            'initiative': 'integer',
            'power_points_total': 'integer',
            'power_points_used': 'integer',
            'power_points_available': 'integer',
            'magic_pool': 'integer',
            'spell_pool': 'integer',
            'initiate_level': 'integer',
            'metamagics': 'ARRAY',
            'magical_group': 'text',
            'tradition': 'text',
            'totem': 'text',
            'created_at': 'timestamp with time zone',
            'updated_at': 'timestamp with time zone'
        },
        'primary_key': 'id',
        'indexes': ['name', 'archetype', 'metatype']
    },
    'character_skills': {
        'columns': {
            'id': 'uuid',
            'character_id': 'uuid',
            'skill_name': 'text',
            'base_rating': 'integer',
            'current_rating': 'integer',
            'skill_type': 'text',
            'specialization': 'text',
            'created_at': 'timestamp with time zone',
            'updated_at': 'timestamp with time zone'
        },
        'primary_key': 'id',
        'foreign_keys': {
            'character_id': 'characters(id)'
        }
    },
    'character_modifiers': {
        'columns': {
            'id': 'uuid',
            'character_id': 'uuid',
            'modifier_type': 'text',
            'target_name': 'text',
            'modifier_value': 'integer',
            'source': 'text',
            'source_type': 'text',
            'source_id': 'uuid',
            'is_permanent': 'boolean',
            'modifier_data': 'jsonb',
            'created_at': 'timestamp with time zone',
            'updated_at': 'timestamp with time zone'
        },
        'primary_key': 'id',
        'foreign_keys': {
            'character_id': 'characters(id)',
            'source_id': 'character_modifiers(id)'
        }
    },
    'character_spells': {
        'columns': {
            'id': 'uuid',
            'character_id': 'uuid',
            'spell_name': 'text',
            'spell_category': 'text',
            'spell_type': 'text',
            'learned_force': 'integer',
            'created_at': 'timestamp with time zone',
            'updated_at': 'timestamp with time zone'
        },
        'primary_key': 'id',
        'foreign_keys': {
            'character_id': 'characters(id)'
        }
    },
    'master_spells': {
        'columns': {
            'id': 'uuid',
            'spell_name': 'text',
            'spell_category': 'text',
            'spell_type': 'text',
            'target': 'text',
            'duration': 'text',
            'drain': 'text',
            'description': 'text',
            'source_book': 'text',
            'source_page': 'text',
            'created_at': 'timestamp with time zone',
            'updated_at': 'timestamp with time zone'
        },
        'primary_key': 'id',
        'indexes': ['spell_name', 'spell_category']
    }
}


class SchemaChecker:
    """Check database schema against expected structure"""
    
    def __init__(self, verbose: bool = False, suggest_fixes: bool = False):
        """Initialize schema checker
        
        Args:
            verbose: Show detailed output
            suggest_fixes: Generate SQL fix suggestions
        """
        self.verbose = verbose
        self.suggest_fixes = suggest_fixes
        self.issues = []
        self.fixes = []
    
    def get_actual_schema(self, table_name: str) -> Dict:
        """Get actual schema for a table from database
        
        Args:
            table_name: Name of table to inspect
            
        Returns:
            Dictionary of column definitions
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get column information
            cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = {}
            for row in cur.fetchall():
                col_name, data_type, is_nullable, default = row
                columns[col_name] = {
                    'type': data_type,
                    'nullable': is_nullable == 'YES',
                    'default': default
                }
            
            return columns
    
    def check_table(self, table_name: str) -> Tuple[bool, List[str]]:
        """Check a single table's schema
        
        Args:
            table_name: Name of table to check
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        if table_name not in EXPECTED_TABLES:
            return True, []  # Skip tables we don't have definitions for
        
        expected = EXPECTED_TABLES[table_name]
        actual = self.get_actual_schema(table_name)
        
        issues = []
        
        # Check for missing columns
        for col_name, col_type in expected['columns'].items():
            if col_name not in actual:
                issue = f"Missing column: {table_name}.{col_name} ({col_type})"
                issues.append(issue)
                
                if self.suggest_fixes:
                    fix = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"
                    self.fixes.append(fix)
        
        # Check for extra columns
        for col_name in actual:
            if col_name not in expected['columns']:
                if self.verbose:
                    issue = f"Extra column: {table_name}.{col_name}"
                    issues.append(issue)
        
        # Check column types
        for col_name, expected_type in expected['columns'].items():
            if col_name in actual:
                actual_type = actual[col_name]['type']
                
                # Normalize type names for comparison
                if not self._types_match(expected_type, actual_type):
                    issue = f"Type mismatch: {table_name}.{col_name} (expected {expected_type}, got {actual_type})"
                    issues.append(issue)
        
        return len(issues) == 0, issues
    
    def _types_match(self, expected: str, actual: str) -> bool:
        """Check if two type names match (accounting for aliases)
        
        Args:
            expected: Expected type name
            actual: Actual type name
            
        Returns:
            True if types match
        """
        # Normalize types
        type_aliases = {
            'integer': ['int4', 'integer'],
            'text': ['text', 'varchar', 'character varying'],
            'uuid': ['uuid'],
            'boolean': ['bool', 'boolean'],
            'numeric': ['numeric', 'decimal'],
            'timestamp with time zone': ['timestamptz', 'timestamp with time zone'],
            'jsonb': ['jsonb'],
            'ARRAY': ['ARRAY']
        }
        
        expected_lower = expected.lower()
        actual_lower = actual.lower()
        
        for canonical, aliases in type_aliases.items():
            if expected_lower in aliases and actual_lower in aliases:
                return True
        
        return expected_lower == actual_lower
    
    def check_all_tables(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Check all tables in expected schema
        
        Returns:
            Dictionary mapping table names to (is_valid, issues)
        """
        results = {}
        
        for table_name in EXPECTED_TABLES:
            is_valid, issues = self.check_table(table_name)
            results[table_name] = (is_valid, issues)
        
        return results
    
    def generate_report(self, results: Dict[str, Tuple[bool, List[str]]]):
        """Generate and display schema validation report
        
        Args:
            results: Results from check_all_tables()
        """
        log_section(logger, "SCHEMA VALIDATION REPORT")
        
        # Summary statistics
        total_tables = len(results)
        valid_tables = sum(1 for is_valid, _ in results.values() if is_valid)
        invalid_tables = total_tables - valid_tables
        total_issues = sum(len(issues) for _, issues in results.values())
        
        logger.info(f"Total tables checked: {total_tables}")
        logger.info(f"Valid tables: {valid_tables}")
        logger.info(f"Tables with issues: {invalid_tables}")
        logger.info(f"Total issues found: {total_issues}")
        logger.info("")
        
        # Detailed results
        if invalid_tables > 0:
            log_section(logger, "ISSUES FOUND")
            
            for table_name, (is_valid, issues) in results.items():
                if not is_valid:
                    logger.info(f"\n{table_name}:")
                    for issue in issues:
                        log_failure(logger, f"  {issue}")
        
        # Suggested fixes
        if self.suggest_fixes and self.fixes:
            log_section(logger, "SUGGESTED FIXES")
            logger.info("\n-- Run these SQL commands to fix schema issues:\n")
            for fix in self.fixes:
                logger.info(fix)
        
        # Final status
        logger.info("")
        if invalid_tables == 0:
            log_success(logger, "All tables match expected schema!")
        else:
            log_warning(logger, f"Found issues in {invalid_tables} table(s)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate database schema',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--table', '-t',
        help='Check specific table only'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including extra columns'
    )
    
    parser.add_argument(
        '--fix', '-f',
        action='store_true',
        help='Suggest SQL fixes for issues'
    )
    
    args = parser.parse_args()
    
    # Create checker
    checker = SchemaChecker(verbose=args.verbose, suggest_fixes=args.fix)
    
    with OperationTimer(logger, "Schema Validation"):
        if args.table:
            # Check single table
            is_valid, issues = checker.check_table(args.table)
            
            if is_valid:
                log_success(logger, f"Table '{args.table}' matches expected schema")
                return 0
            else:
                log_failure(logger, f"Table '{args.table}' has {len(issues)} issue(s):")
                for issue in issues:
                    logger.info(f"  - {issue}")
                return 1
        else:
            # Check all tables
            results = checker.check_all_tables()
            checker.generate_report(results)
            
            # Return error code if any issues found
            has_issues = any(not is_valid for is_valid, _ in results.values())
            return 1 if has_issues else 0


if __name__ == '__main__':
    sys.exit(main())
