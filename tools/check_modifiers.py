#!/usr/bin/env python3
"""
Consolidated Modifier Validation Tool

Replaces 12+ modifier checking scripts with a single, comprehensive tool.
Uses helper library for database connections, logging, and validation.

Features:
- Validate cyberware essence costs and effects
- Check bioware body index calculations
- Verify modifier relationships (parent/child)
- Validate special abilities and conditions
- Check modifier data integrity

Usage:
    python tools/check_modifiers.py                     # Check all modifiers
    python tools/check_modifiers.py --character NAME    # Check character's modifiers
    python tools/check_modifiers.py --type cyberware    # Check specific type
    python tools/check_modifiers.py --verbose           # Detailed output
"""
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.db_utils import get_db_connection
from lib.helpers.logging_utils import (
    setup_logger, log_section, log_success, log_failure, 
    log_warning, log_table, OperationTimer
)

logger = setup_logger(__name__)


class ModifierChecker:
    """Check modifier data for validity and consistency"""
    
    def __init__(self, verbose: bool = False, suggest_fixes: bool = False):
        """Initialize modifier checker
        
        Args:
            verbose: Show detailed output
            suggest_fixes: Generate fix suggestions
        """
        self.verbose = verbose
        self.suggest_fixes = suggest_fixes
        self.issues = []
        self.fixes = []
    
    def get_character_modifiers(self, character_id: str) -> List[Dict]:
        """Get all modifiers for a character
        
        Args:
            character_id: UUID of character
            
        Returns:
            List of modifier dictionaries
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    id, character_id, modifier_type, target_name,
                    modifier_value, source, source_type, source_id,
                    is_permanent, modifier_data
                FROM character_modifiers
                WHERE character_id = %s
                ORDER BY source_type, source
            """, (character_id,))
            
            modifiers = []
            for row in cur.fetchall():
                modifiers.append({
                    'id': row[0],
                    'character_id': row[1],
                    'modifier_type': row[2],
                    'target_name': row[3],
                    'modifier_value': row[4],
                    'source': row[5],
                    'source_type': row[6],
                    'source_id': row[7],
                    'is_permanent': row[8],
                    'modifier_data': row[9] or {}
                })
            
            return modifiers
    
    def check_cyberware_essence(self, modifiers: List[Dict]) -> List[str]:
        """Check cyberware essence costs
        
        Args:
            modifiers: List of modifier dictionaries
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Get cyberware modifiers
        cyberware = [m for m in modifiers if m['source_type'] == 'cyberware']
        
        for mod in cyberware:
            # Check for essence cost in modifier_data
            data = mod.get('modifier_data', {})
            essence_cost = data.get('essence_cost')
            
            if essence_cost is None:
                # Cyberware should have essence cost
                if self.verbose:
                    issues.append(
                        f"Cyberware '{mod['source']}' missing essence_cost in modifier_data"
                    )
            else:
                # Validate essence cost is reasonable (0.01 to 6.0)
                try:
                    cost = float(essence_cost)
                    if cost < 0.01 or cost > 6.0:
                        issues.append(
                            f"Cyberware '{mod['source']}' has invalid essence_cost: {cost}"
                        )
                except (ValueError, TypeError):
                    issues.append(
                        f"Cyberware '{mod['source']}' has non-numeric essence_cost: {essence_cost}"
                    )
        
        return issues
    
    def check_bioware_body_index(self, modifiers: List[Dict]) -> List[str]:
        """Check bioware body index calculations
        
        Args:
            modifiers: List of modifier dictionaries
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Get bioware modifiers
        bioware = [m for m in modifiers if m['source_type'] == 'bioware']
        
        for mod in bioware:
            # Check for body index in modifier_data
            data = mod.get('modifier_data', {})
            body_index = data.get('body_index')
            
            if body_index is None:
                # Bioware should have body index
                if self.verbose:
                    issues.append(
                        f"Bioware '{mod['source']}' missing body_index in modifier_data"
                    )
            else:
                # Validate body index is reasonable (0.1 to 10.0)
                try:
                    index = float(body_index)
                    if index < 0.1 or index > 10.0:
                        issues.append(
                            f"Bioware '{mod['source']}' has invalid body_index: {index}"
                        )
                except (ValueError, TypeError):
                    issues.append(
                        f"Bioware '{mod['source']}' has non-numeric body_index: {body_index}"
                    )
        
        return issues
    
    def check_modifier_relationships(self, modifiers: List[Dict]) -> List[str]:
        """Check parent/child modifier relationships
        
        Args:
            modifiers: List of modifier dictionaries
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Build map of modifier IDs
        modifier_ids = {m['id'] for m in modifiers}
        
        # Check source_id references
        for mod in modifiers:
            source_id = mod.get('source_id')
            if source_id:
                # source_id should reference another modifier
                if source_id not in modifier_ids:
                    # Check if it exists in database at all
                    with get_db_connection() as conn:
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT COUNT(*) FROM character_modifiers WHERE id = %s",
                            (source_id,)
                        )
                        count = cur.fetchone()[0]
                        
                        if count == 0:
                            issues.append(
                                f"Modifier '{mod['source']}' references non-existent source_id: {source_id}"
                            )
                        elif self.verbose:
                            issues.append(
                                f"Modifier '{mod['source']}' references source_id from different character"
                            )
        
        return issues
    
    def check_modifier_values(self, modifiers: List[Dict]) -> List[str]:
        """Check modifier values are reasonable
        
        Args:
            modifiers: List of modifier dictionaries
            
        Returns:
            List of issues found
        """
        issues = []
        
        for mod in modifiers:
            mod_type = mod.get('modifier_type')
            mod_value = mod.get('modifier_value')
            
            if mod_value is None:
                continue
            
            # Check for absurdly high values
            if abs(mod_value) > 50:
                issues.append(
                    f"Modifier '{mod['source']}' has suspiciously high value: {mod_value}"
                )
            
            # Type-specific checks
            if mod_type == 'attribute':
                # Attribute modifiers typically -10 to +10
                if abs(mod_value) > 10:
                    issues.append(
                        f"Attribute modifier '{mod['source']}' unusually high: {mod_value}"
                    )
            
            elif mod_type == 'skill':
                # Skill modifiers typically -6 to +6
                if abs(mod_value) > 6:
                    issues.append(
                        f"Skill modifier '{mod['source']}' unusually high: {mod_value}"
                    )
        
        return issues
    
    def check_special_abilities(self, modifiers: List[Dict]) -> List[str]:
        """Check special abilities in modifier_data
        
        Args:
            modifiers: List of modifier dictionaries
            
        Returns:
            List of issues found
        """
        issues = []
        
        for mod in modifiers:
            data = mod.get('modifier_data', {})
            abilities = data.get('special_abilities', [])
            
            if abilities and not isinstance(abilities, list):
                issues.append(
                    f"Modifier '{mod['source']}' has invalid special_abilities format (not a list)"
                )
        
        return issues
    
    def check_character_modifiers(self, character_id: str, character_name: str) -> Tuple[bool, List[str]]:
        """Check all modifiers for a character
        
        Args:
            character_id: UUID of character
            character_name: Name of character (for reporting)
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        modifiers = self.get_character_modifiers(character_id)
        
        if not modifiers:
            return True, []  # No modifiers is valid
        
        issues = []
        
        # Run all checks
        issues.extend(self.check_cyberware_essence(modifiers))
        issues.extend(self.check_bioware_body_index(modifiers))
        issues.extend(self.check_modifier_relationships(modifiers))
        issues.extend(self.check_modifier_values(modifiers))
        issues.extend(self.check_special_abilities(modifiers))
        
        return len(issues) == 0, issues
    
    def check_all_characters(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Check modifiers for all characters
        
        Returns:
            Dictionary mapping character names to (is_valid, issues)
        """
        results = {}
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM characters ORDER BY name")
            
            for row in cur.fetchall():
                char_id, char_name = row
                is_valid, issues = self.check_character_modifiers(char_id, char_name)
                if issues or self.verbose:  # Only include if has issues or verbose
                    results[char_name] = (is_valid, issues)
        
        return results
    
    def check_by_type(self, modifier_type: str) -> Dict[str, Tuple[bool, List[str]]]:
        """Check modifiers of a specific type across all characters
        
        Args:
            modifier_type: Type to check (e.g., 'cyberware', 'bioware')
            
        Returns:
            Dictionary mapping character names to (is_valid, issues)
        """
        results = {}
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get all characters with this modifier type
            cur.execute("""
                SELECT DISTINCT c.id, c.name
                FROM characters c
                JOIN character_modifiers cm ON c.id = cm.character_id
                WHERE cm.source_type = %s
                ORDER BY c.name
            """, (modifier_type,))
            
            for row in cur.fetchall():
                char_id, char_name = row
                
                # Get only modifiers of this type
                modifiers = self.get_character_modifiers(char_id)
                modifiers = [m for m in modifiers if m['source_type'] == modifier_type]
                
                issues = []
                
                # Run type-specific checks
                if modifier_type == 'cyberware':
                    issues.extend(self.check_cyberware_essence(modifiers))
                elif modifier_type == 'bioware':
                    issues.extend(self.check_bioware_body_index(modifiers))
                
                # Always run general checks
                issues.extend(self.check_modifier_relationships(modifiers))
                issues.extend(self.check_modifier_values(modifiers))
                issues.extend(self.check_special_abilities(modifiers))
                
                if issues or self.verbose:
                    results[char_name] = (len(issues) == 0, issues)
        
        return results
    
    def generate_report(self, results: Dict[str, Tuple[bool, List[str]]], title: str = "MODIFIER VALIDATION REPORT"):
        """Generate and display modifier validation report
        
        Args:
            results: Results from check methods
            title: Report title
        """
        log_section(logger, title)
        
        # Summary statistics
        total_chars = len(results)
        valid_chars = sum(1 for is_valid, _ in results.values() if is_valid)
        invalid_chars = total_chars - valid_chars
        total_issues = sum(len(issues) for _, issues in results.values())
        
        logger.info(f"Total characters checked: {total_chars}")
        logger.info(f"Valid characters: {valid_chars}")
        logger.info(f"Characters with issues: {invalid_chars}")
        logger.info(f"Total issues found: {total_issues}")
        logger.info("")
        
        # Detailed results
        if invalid_chars > 0:
            log_section(logger, "ISSUES FOUND")
            
            for char_name, (is_valid, issues) in results.items():
                if not is_valid:
                    logger.info(f"\n{char_name}:")
                    for issue in issues:
                        log_failure(logger, f"  {issue}")
        
        # Final status
        logger.info("")
        if invalid_chars == 0:
            log_success(logger, "All modifiers are valid!")
        else:
            log_warning(logger, f"Found issues in {invalid_chars} character(s)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate character modifiers',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--character', '-c',
        help='Check specific character by name'
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['cyberware', 'bioware', 'spell', 'adept_power', 'edge', 'flaw'],
        help='Check specific modifier type only'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including characters with no issues'
    )
    
    parser.add_argument(
        '--fix', '-f',
        action='store_true',
        help='Suggest fixes for issues'
    )
    
    args = parser.parse_args()
    
    # Create checker
    checker = ModifierChecker(verbose=args.verbose, suggest_fixes=args.fix)
    
    with OperationTimer(logger, "Modifier Validation"):
        if args.character:
            # Find character by name
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id FROM characters WHERE name = %s OR street_name = %s",
                    (args.character, args.character)
                )
                row = cur.fetchone()
                
                if not row:
                    log_failure(logger, f"Character not found: {args.character}")
                    return 1
                
                char_id = row[0]
            
            # Check single character
            is_valid, issues = checker.check_character_modifiers(char_id, args.character)
            
            if is_valid:
                log_success(logger, f"Character '{args.character}' modifiers are valid")
                return 0
            else:
                log_failure(logger, f"Character '{args.character}' has {len(issues)} modifier issue(s):")
                for issue in issues:
                    logger.info(f"  - {issue}")
                return 1
        
        elif args.type:
            # Check specific modifier type
            results = checker.check_by_type(args.type)
            title = f"{args.type.upper()} VALIDATION REPORT"
            checker.generate_report(results, title)
            
            has_issues = any(not is_valid for is_valid, _ in results.values())
            return 1 if has_issues else 0
        
        else:
            # Check all characters
            results = checker.check_all_characters()
            checker.generate_report(results)
            
            has_issues = any(not is_valid for is_valid, _ in results.values())
            return 1 if has_issues else 0


if __name__ == '__main__':
    sys.exit(main())
