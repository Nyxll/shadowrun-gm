#!/usr/bin/env python3
"""
AI Payload Optimizer
Strips unnecessary data from payloads sent to AI to reduce token usage
"""

def strip_audit_fields(data):
    """
    Remove audit fields and null values from data before sending to AI
    
    Removes:
    - created_at, created_by
    - modified_at, modified_by  
    - deleted_at, deleted_by
    - All null/None values
    
    This significantly reduces token usage in AI context
    """
    if data is None:
        return None
    
    # Fields to always remove
    AUDIT_FIELDS = {
        'created_at', 'created_by',
        'modified_at', 'modified_by',
        'deleted_at', 'deleted_by'
    }
    
    if isinstance(data, dict):
        # Remove audit fields and null values
        return {
            k: strip_audit_fields(v)
            for k, v in data.items()
            if k not in AUDIT_FIELDS and v is not None
        }
    
    elif isinstance(data, list):
        # Process each item in list
        return [strip_audit_fields(item) for item in data if item is not None]
    
    else:
        # Return primitive values as-is
        return data


def optimize_character_data(character_data):
    """
    Optimize character data specifically for AI consumption
    Keeps only fields the AI needs for game mechanics
    """
    if not character_data:
        return character_data
    
    # Strip audit fields and nulls first
    optimized = strip_audit_fields(character_data)
    
    # Additional optimization: remove empty lists/dicts
    if isinstance(optimized, dict):
        return {
            k: v for k, v in optimized.items()
            if v not in ([], {}, '', 0) or k in ['id', 'character_id']  # Keep IDs even if 0
        }
    
    return optimized


def optimize_tool_result(result):
    """
    Optimize any tool result before sending to AI
    """
    return strip_audit_fields(result)


# Example usage and testing
if __name__ == "__main__":
    # Test data with audit fields and nulls
    test_data = {
        "id": "123",
        "name": "Platinum",
        "street_name": "Platinum",
        "created_at": "2024-01-01T00:00:00",
        "created_by": "admin",
        "modified_at": "2024-01-02T00:00:00",
        "modified_by": "admin",
        "deleted_at": None,
        "deleted_by": None,
        "body": 6,
        "quickness": 7,
        "strength": 5,
        "charisma": None,
        "intelligence": 5,
        "willpower": 4,
        "essence": 0.6,
        "magic": None,
        "reaction": 8,
        "skills": [
            {
                "skill_name": "Firearms",
                "base_rating": 6,
                "current_rating": 6,
                "created_at": "2024-01-01T00:00:00",
                "modified_at": None
            }
        ],
        "gear": [],
        "contacts": None
    }
    
    print("Original size:", len(str(test_data)), "chars")
    print()
    
    optimized = optimize_character_data(test_data)
    
    print("Optimized size:", len(str(optimized)), "chars")
    print()
    print("Optimized data:")
    import json
    print(json.dumps(optimized, indent=2))
    
    reduction = (1 - len(str(optimized)) / len(str(test_data))) * 100
    print(f"\nReduction: {reduction:.1f}%")
