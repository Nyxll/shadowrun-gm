# UI Spellcasting Implementation Guide

## Status: Backend Complete ✅ | Frontend In Progress

### Completed Work

1. **Backend Endpoints** (game-server.py) ✅
   - `POST /api/cast_spell` - Cast a spell
   - `GET /api/sustained_spells/{character_name}` - Get sustained spells
   - `POST /api/drop_spell` - Drop a sustained spell

2. **SpellcastingEngine** (lib/spellcasting.py) ✅
   - `get_sustained_spells(character_id)` - Returns list of sustained spells
   - `calculate_sustaining_penalty(character_id)` - Returns -2 per spell
   - `drop_sustained_spell(character_id, spell_name)` - Ends sustained spell

### Remaining Work

## Step 1: Enhance character-sheet-renderer.js

The `renderMagic()` method needs to be enhanced to add interactive spell UI.

### Current renderMagic() Location
File: `www/character-sheet-renderer.js`
Method: `renderMagic()` (starts around line 600)

### Required Changes

1. **Add Sustained Spells Section** (at top of magic section)
```javascript
// Add this BEFORE the totem information
if (this.characterData.sustained_spells && this.characterData.sustained_spells.length > 0) {
    const penalty = this.characterData.sustaining_penalty || 0;
    const sustainedItems = this.characterData.sustained_spells.map(spell => `
        <div class="sustained-spell-item">
            <span class="spell-name">${spell.spell_name} (Force ${spell.force})</span>
            <span class="spell-target">on ${spell.target_character_id || 'self'}</span>
            <button class="drop-spell-btn" data-spell="${spell.spell_name}" data-character="${this.characterData.street_name}">
                Drop
            </button>
        </div>
    `).join('\n');
    
    content += `
        <div class="subsection sustained-spells-section">
            <h4>Sustained Spells (Penalty: ${penalty} dice)</h4>
            <div class="sustained-spell-list">${sustainedItems}</div>
        </div>
    `;
}
```

2. **Add Cast Buttons to Spells**
In the spell rendering loop, add cast button:
```javascript
// In the spellItems.map() function, add:
<button class="cast-spell-btn" 
        data-spell="${spell.spell_name}" 
        data-force="${spell.learned_force || 'variable'}"
        data-character="${this.characterData.street_name}">
    Cast
</button>
```

3. **Add Event Listeners** (in constructor or init method)
```javascript
// Add to CharacterSheetRenderer class
attachSpellEventListeners() {
    // Cast spell buttons
    document.querySelectorAll('.cast-spell-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const spellName = e.target.dataset.spell;
            const force = e.target.dataset.force;
            const character = e.target.dataset.character;
            
            await this.castSpell(character, spellName, force);
        });
    });
    
    // Drop spell buttons
    document.querySelectorAll('.drop-spell-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const spellName = e.target.dataset.spell;
            const character = e.target.dataset.character;
            
            await this.dropSpell(character, spellName);
        });
    });
}

async castSpell(character, spellName, force) {
    try {
        // If variable force, prompt user
        if (force === 'variable') {
            force = prompt(`Cast ${spellName} at what Force? (1-12)`);
            if (!force) return;
            force = parseInt(force);
        }
        
        const response = await fetch('/api/cast_spell', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                caster_name: character,
                spell_name: spellName,
                force: force,
                target_name: character  // Default to self
            })
        });
        
        const result = await response.json();
        
        // Show drain results
        alert(`Cast ${spellName} at Force ${force}\n\n${result.summary}`);
        
        // Reload character sheet to show sustained spell
        await this.reloadCharacterSheet(character);
        
    } catch (error) {
        console.error('Error casting spell:', error);
        alert('Error casting spell: ' + error.message);
    }
}

async dropSpell(character, spellName) {
    try {
        const response = await fetch('/api/drop_spell', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                character_name: character,
                spell_name: spellName
            })
        });
        
        const result = await response.json();
        alert(result.message);
        
        // Reload character sheet
        await this.reloadCharacterSheet(character);
        
    } catch (error) {
        console.error('Error dropping spell:', error);
        alert('Error dropping spell: ' + error.message);
    }
}

async reloadCharacterSheet(characterName) {
    // Fetch updated character data
    const response = await fetch(`/api/character/${characterName}`);
    const data = await response.json();
    
    // Re-render
    this.characterData = data;
    const content = this.render(data);
    document.getElementById('character-sheet-content').innerHTML = content;
    
    // Re-attach event listeners
    this.attachSpellEventListeners();
}
```

## Step 2: Add CSS Styles

File: `www/character-sheet.css`

Add these styles:
```css
/* Sustained Spells Section */
.sustained-spells-section {
    background: rgba(0, 255, 0, 0.05);
    border: 1px solid var(--neon-green);
    padding: 1rem;
    margin-bottom: 1rem;
}

.sustained-spell-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.sustained-spell-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-left: 3px solid var(--neon-orange);
}

.sustained-spell-item .spell-name {
    font-weight: bold;
    color: var(--neon-green);
}

.sustained-spell-item .spell-target {
    color: var(--neon-cyan);
    font-size: 0.9rem;
}

/* Spell Action Buttons */
.cast-spell-btn,
.drop-spell-btn {
    background: var(--neon-green);
    color: var(--dark-bg);
    border: none;
    padding: 0.25rem 0.75rem;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 0.9rem;
}

.cast-spell-btn:hover {
    background: var(--neon-cyan);
    box-shadow: 0 0 10px var(--neon-cyan);
}

.drop-spell-btn {
    background: var(--neon-orange);
}

.drop-spell-btn:hover {
    background: #ff6600;
    box-shadow: 0 0 10px var(--neon-orange);
}
```

## Step 3: Update app.js to Load Sustained Spells

File: `www/app.js`

When loading character data, also fetch sustained spells:
```javascript
async function loadCharacterSheet(characterName) {
    try {
        // Fetch character data
        const charResponse = await fetch(`/api/character/${characterName}`);
        const charData = await charResponse.json();
        
        // Fetch sustained spells
        const spellsResponse = await fetch(`/api/sustained_spells/${characterName}`);
        const spellsData = await spellsResponse.json();
        
        // Merge data
        charData.sustained_spells = spellsData.sustained_spells;
        charData.sustaining_penalty = spellsData.sustaining_penalty;
        
        // Render
        const renderer = new CharacterSheetRenderer();
        const content = renderer.render(charData);
        document.getElementById('character-sheet-content').innerHTML = content;
        
        // Attach event listeners
        renderer.attachSpellEventListeners();
        
    } catch (error) {
        console.error('Error loading character:', error);
    }
}
```

## Step 4: Create Playwright Tests

File: `tests/test-spellcasting-ui.py`

```python
#!/usr/bin/env python3
"""
Playwright tests for spellcasting UI
"""
import asyncio
from playwright.async_api import async_playwright

async def test_spellcasting_ui():
    """Test spellcasting UI end-to-end"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to app
        await page.goto('http://localhost:8001')
        
        # Wait for page load
        await page.wait_for_selector('#character-select')
        
        # Select Oak character
        await page.select_option('#character-select', 'Oak')
        
        # Click "View Sheet" button
        await page.click('#view-sheet-button')
        
        # Wait for character sheet modal
        await page.wait_for_selector('.character-sheet-modal')
        
        # Scroll to Magic section
        magic_section = await page.query_selector('text=Magic & Spellcasting')
        await magic_section.scroll_into_view_if_needed()
        
        # Test 1: Cast Armor spell
        print("Test 1: Casting Armor spell...")
        armor_cast_btn = await page.query_selector('[data-spell="Armor"]')
        await armor_cast_btn.click()
        
        # Wait for alert (drain results)
        await page.wait_for_timeout(1000)
        
        # Test 2: Verify sustained spell appears
        print("Test 2: Verifying sustained spell appears...")
        sustained_section = await page.query_selector('.sustained-spells-section')
        assert sustained_section is not None, "Sustained spells section should appear"
        
        # Test 3: Verify penalty displays
        print("Test 3: Verifying sustaining penalty...")
        penalty_text = await page.text_content('.sustained-spells-section h4')
        assert '-2 dice' in penalty_text, "Should show -2 dice penalty"
        
        # Test 4: Drop spell
        print("Test 4: Dropping spell...")
        drop_btn = await page.query_selector('.drop-spell-btn')
        await drop_btn.click()
        
        # Wait for reload
        await page.wait_for_timeout(1000)
        
        # Test 5: Verify spell removed
        print("Test 5: Verifying spell removed...")
        sustained_section = await page.query_selector('.sustained-spells-section')
        assert sustained_section is None, "Sustained spells section should be gone"
        
        print("✅ All tests passed!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_spellcasting_ui())
```

## Step 5: Install Playwright

```bash
pip install playwright
playwright install chromium
```

## Step 6: Run Tests

```bash
# Start game server
python game-server.py

# In another terminal, run tests
python tests/test-spellcasting-ui.py
```

## Expected Test Flow

1. Load character sheet for Oak
2. Click "Cast" on Armor spell
3. See drain results in alert
4. Sustained spell appears in "Sustained Spells" section
5. Penalty shows "-2 dice"
6. Click "Drop" button
7. Spell removed, penalty gone

## Key Integration Points

1. **Character Sheet Renderer**: Displays spells with cast buttons
2. **Sustained Spells Section**: Shows active sustained spells with drop buttons
3. **Backend API**: Handles spell casting and sustained spell management
4. **Event Listeners**: Wire up buttons to API calls
5. **Playwright Tests**: Verify end-to-end functionality

## Next Steps After Implementation

1. Run Playwright tests to verify functionality
2. Test with multiple sustained spells (verify cumulative penalty)
3. Test variable-force spells (should prompt for force)
4. Test casting on other targets (not just self)
5. Document any issues found

## Notes

- The backend is fully functional and tested
- The SpellcastingEngine handles all game logic
- The UI just needs to call the endpoints and display results
- Playwright will verify the entire flow works correctly
