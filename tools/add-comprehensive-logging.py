#!/usr/bin/env python3
"""
Add comprehensive logging to MCP operations and CRUD API
This script adds detailed logging statements throughout the codebase
"""

import re
from pathlib import Path

def add_logging_to_mcp_operations():
    """Add comprehensive logging to lib/mcp_operations.py"""
    
    file_path = Path("lib/mcp_operations.py")
    content = file_path.read_text()
    
    # Add logging to calculate_ranged_attack
    content = re.sub(
        r'(async def calculate_ranged_attack\([\s\S]*?\) -> Dict:[\s\S]*?"""[\s\S]*?""")',
        r'\1\n        logger.info(f"[MCP] calculate_ranged_attack: character={character_name}, weapon={weapon_name}, distance={target_distance}m")',
        content
    )
    
    # Add logging to cast_spell
    content = re.sub(
        r'(async def cast_spell\([\s\S]*?\) -> Dict:[\s\S]*?"""[\s\S]*?""")',
        r'\1\n        logger.info(f"[MCP] cast_spell: caster={caster_name}, spell={spell_name}, force={force}")',
        content
    )
    
    # Add logging to get_character
    content = re.sub(
        r'(async def get_character\(self, character_name: str\) -> Dict:[\s\S]*?"""[\s\S]*?""")',
        r'\1\n        logger.info(f"[MCP] get_character: character={character_name}")',
        content
    )
    
    # Add logging to list_characters
    content = re.sub(
        r'(async def list_characters\(self\) -> List\[Dict\]:[\s\S]*?"""[\s\S]*?""")',
        r'\1\n        logger.info("[MCP] list_characters: fetching all characters")',
        content
    )
    
    file_path.write_text(content)
    print(f"✅ Added logging to {file_path}")


def add_logging_to_comprehensive_crud():
    """Add comprehensive logging to lib/comprehensive_crud.py"""
    
    file_path = Path("lib/comprehensive_crud.py")
    content = file_path.read_text()
    
    # This is complex - we'll add a logging decorator instead
    logging_decorator = '''
def log_crud_operation(operation_name):
    """Decorator to log CRUD operations"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            import time
            start = time.time()
            logger.debug(f"[CRUD] {operation_name}: START")
            try:
                result = func(self, *args, **kwargs)
                duration = (time.time() - start) * 1000
                count = len(result) if isinstance(result, list) else 1
                logger.debug(f"[CRUD] {operation_name}: COMPLETE ({count} records, {duration:.2f}ms)")
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                logger.error(f"[CRUD] {operation_name}: ERROR after {duration:.2f}ms - {str(e)}")
                raise
        return wrapper
    return decorator
'''
    
    # Add decorator after imports
    if 'def log_crud_operation' not in content:
        content = content.replace(
            'class ComprehensiveCRUD:',
            f'{logging_decorator}\n\nclass ComprehensiveCRUD:'
        )
    
    file_path.write_text(content)
    print(f"✅ Added logging decorator to {file_path}")


def main():
    """Main function"""
    print("Adding comprehensive logging...")
    print()
    
    add_logging_to_mcp_operations()
    add_logging_to_comprehensive_crud()
    
    print()
    print("✅ Logging additions complete!")
    print()
    print("Next steps:")
    print("1. Review the changes")
    print("2. Test the logging output")
    print("3. Run comprehensive tests")


if __name__ == "__main__":
    main()
