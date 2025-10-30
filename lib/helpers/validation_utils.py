"""
Validation utilities for data integrity

This module provides common validation patterns used across
tools and tests to ensure data consistency.
"""
from typing import Any, List, Optional, Dict
import re

def validate_character_name(name: str) -> bool:
    """Validate character name format
    
    Args:
        name: Character name to validate
    
    Returns:
        True if valid, False otherwise
    
    Rules:
        - Must be at least 2 characters
        - Can contain letters, numbers, spaces, hyphens, apostrophes
    
    Example:
        assert validate_character_name("Platinum")
        assert validate_character_name("Street Razor")
        assert not validate_character_name("A")
    """
    if not name or len(name) < 2:
        return False
    # Allow letters, numbers, spaces, hyphens, apostrophes
    return bool(re.match(r"^[A-Za-z0-9\s\-']+$", name))

def validate_attribute_value(value: int, min_val: int = 1, max_val: int = 20) -> bool:
    """Validate attribute is within valid range
    
    Args:
        value: Attribute value to validate
        min_val: Minimum valid value (default 1)
        max_val: Maximum valid value (default 20)
    
    Returns:
        True if valid, False otherwise
    
    Example:
        assert validate_attribute_value(6)
        assert not validate_attribute_value(0)
        assert not validate_attribute_value(21)
    """
    return min_val <= value <= max_val

# Alias for compatibility
validate_attribute_range = validate_attribute_value

def validate_karma(karma: int) -> bool:
    """Validate karma value (0-9999 reasonable range)
    
    Args:
        karma: Karma value to validate
    
    Returns:
        True if valid (0-9999), False otherwise
    
    Example:
        assert validate_karma(100)
        assert validate_karma(0)
        assert not validate_karma(-1)
        assert not validate_karma(10000)
    """
    return 0 <= karma <= 9999

def validate_skill_rating(rating: int) -> bool:
    """Validate skill rating (0-12 in SR2)
    
    Args:
        rating: Skill rating to validate
    
    Returns:
        True if valid (0-12), False otherwise
    
    Example:
        assert validate_skill_rating(6)
        assert validate_skill_rating(0)  # Untrained
        assert not validate_skill_rating(13)
    """
    return 0 <= rating <= 12

def validate_essence(essence: float) -> bool:
    """Validate essence value (0.0-6.0)
    
    Args:
        essence: Essence value to validate
    
    Returns:
        True if valid (0.0-6.0), False otherwise
    
    Example:
        assert validate_essence(6.0)
        assert validate_essence(3.5)
        assert not validate_essence(6.1)
        assert not validate_essence(-0.1)
    """
    return 0.0 <= essence <= 6.0

def validate_magic(magic: int) -> bool:
    """Validate magic attribute (0-12)
    
    Args:
        magic: Magic attribute to validate
    
    Returns:
        True if valid (0-12), False otherwise
    
    Example:
        assert validate_magic(6)
        assert validate_magic(0)  # Mundane
        assert not validate_magic(13)
    """
    return 0 <= magic <= 12

def validate_force(force: int, max_force: int = 12) -> bool:
    """Validate spell force (1-12 typically)
    
    Args:
        force: Force rating to validate
        max_force: Maximum force (default 12)
    
    Returns:
        True if valid, False otherwise
    
    Example:
        assert validate_force(6)
        assert not validate_force(0)
        assert not validate_force(13)
    """
    return 1 <= force <= max_force

def validate_metatype(metatype: str) -> bool:
    """Validate metatype is recognized
    
    Args:
        metatype: Metatype to validate
    
    Returns:
        True if valid metatype, False otherwise
    
    Example:
        assert validate_metatype("Human")
        assert validate_metatype("Elf")
        assert not validate_metatype("Klingon")
    """
    valid_metatypes = {
        'Human', 'Elf', 'Dwarf', 'Ork', 'Troll',
        'human', 'elf', 'dwarf', 'ork', 'troll'
    }
    return metatype in valid_metatypes

def check_required_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
    """Check for missing required fields
    
    Args:
        data: Dictionary to check
        required: List of required field names
    
    Returns:
        List of missing field names (empty if all present)
    
    Example:
        data = {'name': 'Platinum', 'metatype': 'Human'}
        missing = check_required_fields(data, ['name', 'metatype', 'body'])
        assert missing == ['body']
    """
    return [field for field in required if field not in data or data[field] is None]

def validate_target_number(tn: int) -> bool:
    """Validate target number (2-20 typically)
    
    Args:
        tn: Target number to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        assert validate_target_number(4)
        assert not validate_target_number(1)
        assert not validate_target_number(21)
    """
    return 2 <= tn <= 20

def validate_dice_pool(pool: int) -> bool:
    """Validate dice pool size (0-50 reasonable max)
    
    Args:
        pool: Dice pool size to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        assert validate_dice_pool(10)
        assert validate_dice_pool(0)
        assert not validate_dice_pool(-1)
        assert not validate_dice_pool(100)
    """
    return 0 <= pool <= 50

def validate_damage_code(code: str) -> bool:
    """Validate damage code format (e.g., "6M", "10D", "4L")
    
    Args:
        code: Damage code to validate
    
    Returns:
        True if valid format, False otherwise
    
    Example:
        assert validate_damage_code("6M")
        assert validate_damage_code("10D")
        assert validate_damage_code("4L")
        assert not validate_damage_code("6X")
        assert not validate_damage_code("M6")
    """
    # Format: number + letter (L/M/D/S)
    return bool(re.match(r'^\d+[LMDS]$', code, re.IGNORECASE))

def validate_availability(avail: str) -> bool:
    """Validate availability rating (e.g., "4/48 hours", "8/2 weeks", "Always")
    
    Args:
        avail: Availability string to validate
    
    Returns:
        True if valid format, False otherwise
    
    Example:
        assert validate_availability("4/48 hours")
        assert validate_availability("8/2 weeks")
        assert validate_availability("Always")
        assert not validate_availability("invalid")
    """
    if avail.lower() in ['always', 'never', 'special']:
        return True
    # Format: number/time period
    return bool(re.match(r'^\d+/\d+\s*(hours?|days?|weeks?|months?)$', avail, re.IGNORECASE))

def validate_cost(cost: Any) -> bool:
    """Validate cost value (number or special string)
    
    Args:
        cost: Cost to validate (int, float, or string)
    
    Returns:
        True if valid, False otherwise
    
    Example:
        assert validate_cost(1000)
        assert validate_cost(1500.50)
        assert validate_cost("Special")
        assert not validate_cost(-100)
    """
    if isinstance(cost, (int, float)):
        return cost >= 0
    if isinstance(cost, str):
        return cost.lower() in ['special', 'varies', 'n/a', 'free']
    return False

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input by removing dangerous characters
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    
    Example:
        clean = sanitize_input("Hello<script>alert('xss')</script>")
        assert "<script>" not in clean
    """
    if not text:
        return ""
    
    # Remove HTML/script tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove SQL injection attempts
    dangerous_patterns = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+',
        r'--',
        r'/\*.*?\*/',
    ]
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Truncate to max length
    return text[:max_length]

def validate_json_structure(data: Dict, required_keys: List[str]) -> tuple[bool, List[str]]:
    """Validate JSON structure has required keys
    
    Args:
        data: Dictionary to validate
        required_keys: List of required top-level keys
    
    Returns:
        Tuple of (is_valid, missing_keys)
    
    Example:
        data = {'name': 'Test', 'type': 'character'}
        valid, missing = validate_json_structure(data, ['name', 'type', 'stats'])
        assert not valid
        assert missing == ['stats']
    """
    missing = [key for key in required_keys if key not in data]
    return (len(missing) == 0, missing)
