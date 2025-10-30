# UI Spellcasting Integration Plan

## Goal
Add interactive spellcasting interface to the character sheet with full Playwright testing.

## Components to Add

### 1. Enhanced Spell Display
- Show spell list with "Cast" buttons
- Display sustained spells separately
- Show sustaining penalty
- Add "Drop Spell" buttons for sustained spells

### 2. Cast Spell Modal
- Force selection (for variable-force spells)
- Target selection (self/other character)
- Cast button
- Display drain results
- Show success/failure

### 3. Sustained Spells Section
- List of currently sustained spells
- Show force and target
- Drop spell buttons
- Display total penalty (-2 per spell)

### 4. Backend Integration
- Add spellcasting endpoints to game-server.py
- Integrate with SpellcastingEngine
- Return drain results and create modifiers

## Implementation Steps

1. Add spellcasting endpoints to game-server.py
2. Enhance character-sheet-renderer.js with spell UI
3. Add spell modal HTML/CSS
4. Create Playwright test suite
5. Test end-to-end workflow

## Playwright Test Cases

1. **Load Character Sheet**: Verify spell list displays
2. **Cast Spell**: Click cast button, select force, verify drain
3. **Sustained Spell**: Verify spell appears in sustained list
4. **Sustaining Penalty**: Verify penalty displays correctly
5. **Drop Spell**: Click drop, verify spell removed
6. **Multiple Spells**: Cast 2 spells, verify -4 penalty
7. **Variable Force**: Test casting at different forces

## UI Mockup

```
┌─ Magic & Spellcasting ────────────────────────┐
│ Totem: Oak                                     │
│                                                │
│ Sustained Spells (Penalty: -4 dice)           │
│ ┌────────────────────────────────────────┐   │
│ │ Armor (Force 6) on Oak        [Drop]   │   │
│ │ Increase Strength (Force 4)   [Drop]   │   │
│ └────────────────────────────────────────┘   │
│                                                │
│ Health Spells                                  │
│ ┌────────────────────────────────────────┐   │
│ │ Heal (Force 6)                [Cast]   │   │
│ │   Type: Mana • Target: Touch            │   │
│ │   Drain: (Force ÷ 2)M                   │   │
│ └────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

## Files to Modify

1. `game-server.py` - Add spellcasting endpoints
2. `www/character-sheet-renderer.js` - Enhance renderMagic()
3. `www/character-sheet.css` - Add spell UI styles
4. `tests/test-spellcasting-ui.py` - Playwright tests
