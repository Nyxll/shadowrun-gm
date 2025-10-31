# Combat Narrative Issues - Analysis & Solutions

## Problem Summary

When Grok receives ranged combat results, it's **fabricating narratives** instead of using the actual data returned by the MCP tool.

## Example Issue

**User Query**: "Platinum wants to shoot a rat 57 meters away with his Predator"

**MCP Tool Returns (CORRECT)**:
```json
{
  "dice_pool": 9,
  "roll": {
    "rolls": [1,4,1,1,4,1,3,5,6,4],
    "successes": 0,
    "pool_size": 9
  }
}
```

**Grok's Narrative (WRONG)**:
> "Platinum rolls **9 dice** (Quickness 6 + Pistol 3)"

**Reality**:
- Firearms skill is **9** (base 7 + 2 from bioware)
- NOT "Quickness 6 + Pistol 3"
- Grok is making up skill breakdowns

## Root Causes

### 1. Dice Pool Explanation Missing
The MCP returns `dice_pool: 9` but doesn't explain WHERE it came from:
- Firearms skill: 9
- Combat pool: 0 (not asked for)
- Total: 9

### 2. Combat Pool Not Prompted
The tool has a `combat_pool` parameter but Grok never asks the user:
- "Do you want to add combat pool dice?"
- "How many combat pool dice to commit?"

### 3. Exploding Dice Confusion
- Roll shows 10 dice when pool_size is 9
- This is CORRECT (one 6 exploded)
- But it confuses Grok into thinking there's an error

### 4. Grok Fabricates Instead of Reports
Grok should say:
> "Rolled 9 dice (Firearms 9): [1,4,1,1,4,1,3,5,6,4] - one 6 exploded. 0 successes."

Instead it says:
> "Rolled 9 dice (Quickness 6 + Pistol 3)" ← FABRICATED

## Solutions

### Solution 1: Add Skill Breakdown to MCP Response

**File**: `lib/mcp_operations.py`

Add to ranged_combat return:
```python
result = {
    "character": character_name,
    "weapon": weapon_name,
    # ... existing fields ...
    "dice_pool": dice_pool,
    "dice_pool_breakdown": {
        "firearms_skill": firearms_skill['current_rating'],
        "combat_pool": combat_pool,
        "total": dice_pool
    },
    "roll": roll_dict,
    # ... rest ...
}
```

### Solution 2: Add Combat Pool Prompt to Tool Definition

**File**: `lib/server/tool_definitions.py`

Update ranged_combat description:
```python
"description": """Calculate and execute ranged combat attack.

IMPORTANT: Before calling this tool, ask the user:
1. "Do you want to commit combat pool dice to this attack?"
2. If yes: "How many combat pool dice? (Max: character's combat pool rating)"

Then include the combat_pool parameter with their answer (0 if none).
```

### Solution 3: Add Exploding Dice Explanation

**File**: `lib/mcp_operations.py`

Add to result:
```python
"roll_explanation": f"Rolled {dice_pool} dice. " + 
    (f"{len(roll_result.rolls) - dice_pool} dice exploded (Rule of 6). " 
     if len(roll_result.rolls) > dice_pool else "") +
    f"Final: {roll_result.successes} successes vs TN {tn_result['finalTN']}"
```

### Solution 4: Improve Summary Field

Current summary:
```python
"summary": f"{character_name} fires {weapon_name} at {distance}m..."
```

Better summary:
```python
"summary": f"{character_name} fires {weapon_name} at {distance}m ({range_cat} range). " +
          f"Firearms {firearms_skill['current_rating']}" +
          (f" + {combat_pool} combat pool" if combat_pool > 0 else "") +
          f" = {dice_pool} dice vs TN {tn_result['finalTN']}. " +
          f"Rolled: {roll_result.rolls}" +
          (f" ({len(roll_result.rolls) - dice_pool} exploded)" 
           if len(roll_result.rolls) > dice_pool else "") +
          f". {roll_result.successes} successes. " +
          ("HIT!" if roll_result.successes > 0 else "MISS!")
```

## Implementation Priority

1. **HIGH**: Add dice_pool_breakdown to response
2. **HIGH**: Update tool description to prompt for combat pool
3. **MEDIUM**: Add roll_explanation field
4. **MEDIUM**: Improve summary field
5. **LOW**: Add validation that Grok used actual data

## Testing

After fixes, test with:
```
Platinum wants to shoot a rat 57 meters away with his Predator. 
He commits 3 combat pool dice.
```

Expected response should include:
- Firearms 9 + Combat Pool 3 = 12 dice
- Actual rolls shown with exploded dice noted
- No fabricated skill breakdowns
