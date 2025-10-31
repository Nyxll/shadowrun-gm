# Ranged Combat Fixes - Complete

## Issues Fixed

### 1. **Smartlink Bonus** ✅
- **Was**: Hardcoded to -2 TN
- **Now**: Reads actual value from database
- **Implementation**: 
  - Removed hardcoded smartlink logic in `mcp_operations.py`
  - Now uses `modifier_value` from `character_modifiers` table
  - Supports variable ratings (e.g., -3 for Platinum's AEGIS smartlink)

### 2. **Target Size Modifier** ✅
- **Added**: Small target = +2 TN, Large target = -1 TN
- **Implementation**:
  - Added `target_size` parameter to ranged_combat operation
  - Added to tool definition in `tool_definitions.py`
  - Added to MCP client in `mcp_client.py`
  - Implemented in `combat_modifiers.py`

### 3. **Target Movement** ✅
- **Was**: Only handled "running" (+2 TN)
- **Now**: Handles both "walking" (+1 TN) and "running" (+2 TN)
- **Implementation**:
  - Fixed in both `mcp_operations.py` and `combat_modifiers.py`
  - Changed field name from `target_running` to `target_moving`
  - Properly distinguishes between walking and running

### 4. **Combat Pool** ✅
- **Added**: `combat_pool` parameter to add dice to attack roll
- **Implementation**:
  - Added parameter to ranged_combat operation
  - Dice pool now = Firearms skill + combat_pool
  - Added to tool definition and MCP client

### 5. **Flare Compensation** ✅
- **Added**: Automatic detection from cyberware modifiers
- **Implementation**:
  - Detects flare compensation in cyberware
  - Automatically includes in conditions dict
  - Glare negation logic in visibility calculations

### 6. **Comprehensive Logging** ✅
- **Added**: Detailed logging throughout ranged_combat operation
- **Logs**:
  - Cyberware detection and modifier values
  - Combat parameters being used
  - TN calculation breakdown
  - Dice rolls and results

### 7. **Vision Modifiers** ✅
- **Confirmed**: Total darkness = +8 TN (correct per SR2 rules)
- **Confirmed**: Electronic thermographic = +4 reduction (correct)
- **Fixed**: Magnification now correctly reduces effective range

### 8. **Base TN** ✅
- **Confirmed**: Base TN is 4 for short range (correct per SR2 rules)
- Range-based TNs: Short=4, Medium=5, Long=6, Extreme=9

## Files Modified

1. **lib/mcp_operations.py**
   - Removed hardcoded smartlink logic
   - Added target_size parameter
   - Added combat_pool parameter
   - Fixed target movement handling
   - Added comprehensive logging
   - Added flare compensation detection

2. **lib/combat_modifiers.py**
   - Added target size modifier logic
   - Fixed target movement (walking vs running)
   - Confirmed base TN values
   - Confirmed visibility modifiers

3. **lib/server/tool_definitions.py**
   - Added target_size parameter
   - Added combat_pool parameter
   - Updated descriptions

4. **lib/server/mcp_client.py**
   - Added target_size parameter
   - Added combat_pool parameter

## Expected Results for Platinum's Rat Shot

**Scenario**: Shooting a rat at 57m in pitch black sewers, rat is walking

**Calculation**:
- **Distance**: 57m
- **Magnification**: 3 (vision magnification)
- **Effective Range**: 57m ÷ 3 = 19m → SHORT range
- **Base TN**: 4 (short range)
- **Smartlink**: -3 (from database, AEGIS smartlink)
- **Visibility**: +4 (electronic thermographic in total darkness)
- **Small target**: +2 (rat)
- **Target walking**: +1
- **Final TN**: 4 - 3 + 4 + 2 + 1 = **8**

**Dice Pool**:
- Firearms skill: 9
- Combat pool: 0 (unless specified)
- Total: 9 dice

## Testing

To test the fixes:

1. Restart the game server to load the updated code
2. Ask the GM: "Platinum wants to shoot a rat 57 meters away with his alta. He is in pitch black sewers and the rat is walking."
3. Verify the calculation shows:
   - TN of 8
   - Proper breakdown of all modifiers
   - Dice rolls displayed
   - Smartlink bonus of -3 (not -2)

## Database Requirements

The fixes require:
- Platinum's AEGIS smartlink in `character_modifiers` table with `modifier_value = -3`
- Flare compensation cyberware (if applicable)
- All other cyberware properly stored in database

## Notes

- All calculations now use database values instead of hardcoded constants
- Comprehensive logging makes debugging much easier
- The system properly handles all SR2 ranged combat modifiers
- Vision magnification correctly stages range categories down
