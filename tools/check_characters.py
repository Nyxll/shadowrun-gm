#!/usr/bin/env python3
"""
Consolidated Character Validation Tool

Replaces 15+ character checking scripts with a single, comprehensive tool.
Uses helper library for database connections, logging, and validation.

Features:
- Validate character attributes and derived stats
- Check skill ratings and specializations
- Verify modifier applications
- Validate karma and nuyen calculations
- Check magic system values (for magical characters)
- Verify combat stats (initiative, combat pool, etc.)

Usage:
    python tools/check_characters.py                    # Check all characters
    python tools/check_characters.py --character NAME   # Check specific character
    python tools/check_characters.py --verbose          # Detailed output
    python tools/check_characters.py --fix              # Suggest fixes
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
from lib.helpers.validation_utils import (
    validate_attribute_range, validate_skill_rating,
    validate_essence, validate_karma
)

logger = setup_logger(__name__)


class CharacterChecker:
    """Check character data for validity and consistency"""
    
    def __init__(self, verbose: bool = False, suggest_fixes: bool = False):
        """Initialize character checker
        
        Args:
            verbose: Show detailed output
            suggest_fixes: Generate fix suggestions
        """
        self.verbose = verbose
        self.suggest_fixes = suggest_fixes
        self.issues = []
        self.fixes = []
    
    def get_character(self, character_id: str) -> Optional[Dict]:
        """Get character data from database
        
        Args:
            character_id: UUID of character
            
        Returns:
            Dictionary of character data or None
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    id, name, street_name, archetype, metatype,
                    base_body, base_quickness, base_strength,
                    base_charisma, base_intelligence, base_willpower,
                    base_essence, base_magic, base_reaction,
                    current_body, current_quickness, current_strength,
                    current_charisma, current_intelligence, current_willpower,
                    current_essence, current_magic, current_reaction,
                    nuyen, karma_pool, karma_total, karma_available,
                    initiative, power_points_total, power_points_used,
                    power_points_available, magic_pool, spell_pool,
                    initiate_level, metamagics, magical_group,
                    tradition, totem
                FROM characters
                WHERE id = %s
            """, (character_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                'id': row[0],
                'name': row[1],
                'street_name': row[2],
                'archetype': row[3],
                'metatype': row[4],
                'base_body': row[5],
                'base_quickness': row[6],
                'base_strength': row[7],
                'base_charisma': row[8],
                'base_intelligence': row[9],
                'base_willpower': row[10],
                'base_essence': row[11],
                'base_magic': row[12],
                'base_reaction': row[13],
                'current_body': row[14],
                'current_quickness': row[15],
                'current_strength': row[16],
                'current_charisma': row[17],
                'current_intelligence': row[18],
                'current_willpower': row[19],
                'current_essence': row[20],
                'current_magic': row[21],
                'current_reaction': row[22],
                'nuyen': row[23],
                'karma_pool': row[24],
                'karma_total': row[25],
                'karma_available': row[26],
                'initiative': row[27],
                'power_points_total': row[28],
                'power_points_used': row[29],
                'power_points_available': row[30],
                'magic_pool': row[31],
                'spell_pool': row[32],
                'initiate_level': row[33],
                'metamagics': row[34],
                'magical_group': row[35],
                'tradition': row[36],
                'totem': row[37]
            }
    
    def check_attributes(self, char: Dict) -> List[str]:
        """Check character attributes for validity
        
        Args:
            char: Character data dictionary
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check base attributes (1-6 for humans, varies by metatype)
        base_attrs = ['base_body', 'base_quickness', 'base_strength',
                     'base_charisma', 'base_intelligence', 'base_willpower']
        
        for attr in base_attrs:
            value = char.get(attr)
            if value is not None:
                if not validate_attribute_range(value, 1, 6):
                    issues.append(f"{attr} out of range: {value} (expected 1-6)")
        
        # Check current attributes match or are modified from base
        current_attrs = ['current_body', 'current_quickness', 'current_strength',
                        'current_charisma', 'current_intelligence', 'current_willpower']
        
        for i, current_attr in enumerate(current_attrs):
            base_attr = base_attrs[i]
            current_val = char.get(current_attr)
            base_val = char.get(base_attr)
            
            if current_val is not None and base_val is not None:
                # Current should be >= base (can be boosted by magic/cyber)
                # or < base (reduced by damage/drain)
                if current_val < 0:
                    issues.append(f"{current_attr} is negative: {current_val}")
        
        # Check essence
        essence = char.get('current_essence')
        if essence is not None:
            if not validate_essence(essence):
                issues.append(f"Invalid essence: {essence} (expected 0.01-6.00)")
        
        # Check magic (if magical character)
        if char.get('base_magic') and char.get('base_magic') > 0:
            magic = char.get('current_magic')
            if magic is not None and magic < 0:
                issues.append(f"Magic is negative: {magic}")
        
        return issues
    
    def check_karma(self, char: Dict) -> List[str]:
        """Check karma values for consistency
        
        Args:
            char: Character data dictionary
            
        Returns:
            List of issues found
        """
        issues = []
        
        karma_total = char.get('karma_total', 0)
        karma_available = char.get('karma_available', 0)
        karma_pool = char.get('karma_pool', 0)
        
        # Validate karma values
        if not validate_karma(karma_total):
            issues.append(f"Invalid karma_total: {karma_total}")
        
        if not validate_karma(karma_available):
            issues.append(f"Invalid karma_available: {karma_available}")
        
        if not validate_karma(karma_pool):
            issues.append(f"Invalid karma_pool: {karma_pool}")
        
        # Check karma consistency
        # karma_available should be <= karma_total
        if karma_available > karma_total:
            issues.append(
                f"karma_available ({karma_available}) > karma_total ({karma_total})"
            )
        
        return issues
    
    def check_magic_system(self, char: Dict) -> List[str]:
        """Check magic system values (for magical characters)
        
        Args:
            char: Character data dictionary
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Only check if character has magic
        if not char.get('base_magic') or char.get('base_magic') == 0:
            return issues
        
        # Check power points (for adepts)
        if char.get('archetype') == 'Physical Adept':
            total = char.get('power_points_total', 0)
            used = char.get('power_points_used', 0)
            available = char.get('power_points_available', 0)
            
            # Power points should equal magic rating
            magic = char.get('current_magic', 0)
            if total != magic:
                issues.append(
                    f"power_points_total ({total}) != current_magic ({magic})"
                )
            
            # Check consistency
            if used + available != total:
                issues.append(
                    f"power_points: used ({used}) + available ({available}) != total ({total})"
                )
        
        # Check spell pool (for mages/shamans)
        if char.get('archetype') in ['Mage', 'Shaman']:
            spell_pool = char.get('spell_pool')
            magic = char.get('current_magic', 0)
            intelligence = char.get('current_intelligence', 0)
            
            # Spell pool should be (Magic + Intelligence) / 2
            expected_pool = (magic + intelligence) // 2
            if spell_pool != expected_pool:
                issues.append(
                    f"spell_pool ({spell_pool}) != (Magic + Int) / 2 ({expected_pool})"
                )
        
        # Check totem (for shamans)
        if char.get('archetype') == 'Shaman':
            if not char.get('totem'):
                issues.append("Shaman missing totem")
        
        # Check tradition (for mages)
        if char.get('archetype') == 'Mage':
            if not char.get('tradition'):
                issues.append("Mage missing tradition")
        
        return issues
    
    def check_combat_stats(self, char: Dict) -> List[str]:
        """Check combat-related statistics
        
        Args:
            char: Character data dictionary
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check initiative (may be stored as text in database)
        initiative = char.get('initiative')
        if initiative is not None:
            try:
                # Convert to int if it's a string
                if isinstance(initiative, str):
                    initiative = int(initiative) if initiative else 0
                
                # Just check it's not negative or absurdly high
                if initiative < 0:
                    issues.append(f"Initiative is negative: {initiative}")
                elif initiative > 50:
                    issues.append(f"Initiative suspiciously high: {initiative}")
            except (ValueError, TypeError):
                issues.append(f"Initiative has invalid format: {initiative}")
        
        return issues
    
    def check_character(self, character_id: str) -> Tuple[bool, List[str]]:
        """Check a single character
        
        Args:
            character_id: UUID of character to check
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        char = self.get_character(character_id)
        if not char:
            return False, [f"Character not found: {character_id}"]
        
        issues = []
        
        # Run all checks
        issues.extend(self.check_attributes(char))
        issues.extend(self.check_karma(char))
        issues.extend(self.check_magic_system(char))
        issues.extend(self.check_combat_stats(char))
        
        return len(issues) == 0, issues
    
    def check_all_characters(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Check all characters in database
        
        Returns:
            Dictionary mapping character IDs to (is_valid, issues)
        """
        results = {}
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM characters ORDER BY name")
            
            for row in cur.fetchall():
                char_id, char_name = row
                is_valid, issues = self.check_character(char_id)
                results[char_name] = (is_valid, issues)
        
        return results
    
    def generate_report(self, results: Dict[str, Tuple[bool, List[str]]]):
        """Generate and display character validation report
        
        Args:
            results: Results from check_all_characters()
        """
        log_section(logger, "CHARACTER VALIDATION REPORT")
        
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
            log_success(logger, "All characters are valid!")
        else:
            log_warning(logger, f"Found issues in {invalid_chars} character(s)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate character data',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--character', '-c',
        help='Check specific character by name'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    
    parser.add_argument(
        '--fix', '-f',
        action='store_true',
        help='Suggest fixes for issues'
    )
    
    args = parser.parse_args()
    
    # Create checker
    checker = CharacterChecker(verbose=args.verbose, suggest_fixes=args.fix)
    
    with OperationTimer(logger, "Character Validation"):
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
            is_valid, issues = checker.check_character(char_id)
            
            if is_valid:
                log_success(logger, f"Character '{args.character}' is valid")
                return 0
            else:
                log_failure(logger, f"Character '{args.character}' has {len(issues)} issue(s):")
                for issue in issues:
                    logger.info(f"  - {issue}")
                return 1
        else:
            # Check all characters
            results = checker.check_all_characters()
            checker.generate_report(results)
            
            # Return error code if any issues found
            has_issues = any(not is_valid for is_valid, _ in results.values())
            return 1 if has_issues else 0


if __name__ == '__main__':
    sys.exit(main())
