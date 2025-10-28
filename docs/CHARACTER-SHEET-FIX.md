# Character Sheet Loading Fix

## Issue
Character sheets were failing to load with a 500 Internal Server Error when clicking on a character name in the web interface.

## Root Cause
The `/api/character/{character_name}` endpoint in `game-server.py` was using the old v1 schema column name `rating` for character skills, but the database had been migrated to v2 schema which uses `current_rating`.

### Error Message
```
Database error: column "rating" does not exist
LINE 2: SELECT skill_name, rating, specialization
```

## Fix Applied

### File: `game-server.py`

**Line 1206 - Skills Query:**
```python
# BEFORE (v1 schema):
SELECT skill_name, rating, specialization

# AFTER (v2 schema):
SELECT skill_name, current_rating, specialization
```

**Line 1227 - Skills Response Mapping:**
```python
# BEFORE:
"rating": skill["rating"]

# AFTER:
"rating": skill["current_rating"]
```

## Testing

### Automated Test
Run the automated test script:
```bash
python tests/test-character-sheet-loading.py
```

This will:
1. Test the `/api/characters` endpoint
2. Test the `/api/character/Platinum` endpoint
3. Verify all character data sections load correctly
4. Print manual testing steps

### Manual Testing Steps

1. **Start the game server:**
   ```bash
   python game-server.py
   ```

2. **Open browser to:** http://localhost:8001

3. **Verify initial state:**
   - "Loaded 6 characters from database" message appears
   - "Connected to game server" message appears
   - Status shows "Characters loaded - Ready for scenario creation"

4. **Select a character:**
   - Click on the "Select a character..." dropdown
   - Type "Platinum" to filter/select
   - Verify "Platinum (null)" appears in dropdown

5. **Add character to session:**
   - Click the "ADD CHARACTER" button
   - Verify "Added Platinum to session" message appears
   - Verify "Platinum" appears in Active Characters list with red X button

6. **View character sheet:**
   - Click on "Platinum" name in Active Characters list
   - Verify character sheet modal opens
   - Verify all sections display correctly:
     * BASIC INFORMATION (Name, Street Name, Archetype, Nuyen, Karma, etc.)
     * ATTRIBUTES (Body, Quickness, Strength, Charisma, Intelligence, Willpower)
     * DICE POOLS (Combat Pool)
     * **SKILLS** (Athletics, Cars, etc.) ← **THIS WAS THE BUG**
     * GEAR (weapons, armor, cyberware, etc.)

7. **Verify no errors:**
   - Check browser console (F12) for errors
   - Check server terminal for 500 errors
   - Should see: `GET /api/character/Platinum HTTP/1.1 200 OK`

8. **Close character sheet:**
   - Click the red "X CLOSE" button or click outside modal
   - Verify modal closes properly

## Expected Results

### API Response
The `/api/character/Platinum` endpoint should return HTTP 200 OK with complete character data:

```json
{
  "id": "34d8540c-34e7-4194-8bc8-78a0ae354c96",
  "name": "Kent Jefferies",
  "street_name": "Platinum",
  "archetype": "Street Samurai",
  "attributes": {
    "body": 10,
    "quickness": 15,
    "strength": 14,
    "charisma": 4,
    "intelligence": 12,
    "willpower": 9
  },
  "skills": [
    {
      "skill_name": "Athletics",
      "rating": 6,
      "specialization": "7 dice with Enhanced Articulation"
    },
    {
      "skill_name": "Cars",
      "rating": 2,
      "specialization": null
    }
  ],
  "gear": [...],
  ...
}
```

### Character Sheet Display
All sections should display without errors:
- ✅ Basic Information
- ✅ Attributes
- ✅ Dice Pools
- ✅ Skills (with ratings)
- ✅ Gear

## Related Files
- `game-server.py` - Main server file with the fix
- `tests/test-character-sheet-loading.py` - Automated test script
- `schema.sql` - Database schema v2 (authoritative)
- `www/app.js` - Frontend JavaScript for character selection
- `www/character-sheet-renderer.js` - Character sheet rendering

## Schema Migration Notes
This fix is part of the v1 to v2 schema migration. The v2 schema uses:
- `current_rating` instead of `rating` for skills
- `base_rating` for the base skill level
- `current_rating` reflects the skill level including modifiers

## Future Considerations
- All database queries should use v2 schema column names
- Check for other instances of old column names in the codebase
- Consider adding schema version validation on startup
