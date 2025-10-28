# Character Data Enrichment Plan

## Overview
This document outlines the strategy for enriching character markdown files with detailed game mechanics data from the database.

## Current Status (v1)

### Completed Enrichment
✅ **Database Enrichment** (via `tools/enrich-from-database.py`)
- 13 edges/flaws enriched with descriptions from `qualities` table
- 4 cyberware items enriched with stats from `gear` table
- Data now stored in database with enhanced descriptions

✅ **v1 Export** (via `tools/export-to-v1-markdown.py`)
- All 6 characters exported to `characters/v1/` directory
- Includes enriched edge/flaw descriptions
- Includes cyberware costs where available
- Clean, structured markdown format

### What's Missing in v1
The current enrichment is limited because:
1. **Simple name matching** - Only finds exact or partial name matches
2. **No semantic search** - Can't find related content by meaning
3. **Limited data sources** - Only uses `qualities` and `gear` tables
4. **No RAG integration** - Doesn't leverage the `rules_content` table with embeddings

## Future Enrichment Strategy (v2+)

### Phase 1: Enhanced Database Enrichment
Use AI/semantic search to enrich data with:

#### 1. Weapon Details
**Source**: `gear` table + `rules_content` RAG
- Full weapon stats (damage, conceal, ammo, modes, recoil)
- Special rules (smartlink bonuses, burst fire, etc.)
- Availability and street index
- Book references

**Example Enhancement**:
```markdown
## Weapons
- **Panther Assault Cannon**
  - Damage: 18D
  - Conceal: N/A
  - Ammo: 15 rounds
  - Mode: SA/BF/FA
  - Recoil: 10
  - **Special**: Requires STR 10 to fire, -2 to target number with gyro-mount
  - **Source**: Street Samurai Catalog, p.XX
```

#### 2. Armor Details
**Source**: `gear` table + `rules_content` RAG
- Ballistic/Impact ratings
- Concealability modifiers
- Special properties (hardened, layering rules)
- Weight and encumbrance

#### 3. Cyberware/Bioware Details
**Source**: `gear` table + `rules_content` RAG
- Full essence costs
- Game effects and bonuses
- Incompatibilities
- Legality and availability
- Book references

**Example Enhancement**:
```markdown
## Cyberware
- **Wired Reflexes 3 (Beta-Grade)** (Essence: 2.40)
  - +3D6 to Initiative
  - +3 to Reaction
  - Incompatible with: Boosted Reflexes, Move-by-Wire
  - **Source**: Shadowrun Core, p.XX
```

#### 4. Edge/Flaw Mechanics
**Source**: `qualities` table + `rules_content` RAG
- Point costs
- Detailed game effects
- Restrictions and requirements
- Examples of use

**Example Enhancement**:
```markdown
## Edges
- **Ambidexterity** (3 points)
  - No penalty for using off-hand
  - Can use two weapons without penalty
  - **Game Effect**: Ignore -2 penalty for off-hand weapon use
  - **Source**: Shadowrun Companion, p.XX
```

#### 5. Skill Descriptions
**Source**: `rules_content` RAG
- Skill category (Active/Knowledge/Language)
- Linked attribute
- Common uses and tests
- Specialization examples

#### 6. Spell Details
**Source**: `spells` table + `rules_content` RAG
- Full spell stats (type, target, duration, drain)
- Detailed effects
- Casting modifiers
- Book references

### Phase 2: AI-Powered Semantic Enrichment

#### Tools Needed
1. **Semantic Search Function**
   - Query `rules_content` table using embeddings
   - Find relevant rules by meaning, not just keywords
   - Return context with book references

2. **LLM Integration**
   - Use OpenAI/Claude to interpret and format data
   - Generate natural language descriptions
   - Cross-reference multiple sources
   - Ensure consistency

#### Enrichment Workflow
```python
def enrich_with_ai(item_name, item_type):
    # 1. Semantic search in rules_content
    relevant_rules = semantic_search(item_name, item_type)
    
    # 2. Query specific tables
    db_data = query_database(item_name, item_type)
    
    # 3. Use LLM to synthesize
    enriched_data = llm_synthesize(
        item_name=item_name,
        db_data=db_data,
        rules=relevant_rules
    )
    
    return enriched_data
```

### Phase 3: Validation & Quality Control

#### Automated Checks
- Verify all stats match source books
- Check for missing required fields
- Validate cross-references
- Ensure consistent formatting

#### Manual Review
- Spot-check enriched data
- Verify game mechanics accuracy
- Check for edge cases
- Update as needed

## Implementation Plan

### Step 1: Create AI Enrichment Script
**File**: `tools/enrich-with-ai.py`
- Integrate with game server's RAG system
- Use semantic search for each item type
- Generate comprehensive descriptions
- Update database with enriched data

### Step 2: Enhanced Export
**File**: `tools/export-to-v2-markdown.py`
- Include all enriched data
- Add book references
- Format for readability
- Include game mechanics summaries

### Step 3: Validation Suite
**File**: `tools/validate-enrichment.py`
- Check data completeness
- Verify stat accuracy
- Generate quality reports
- Flag items needing review

### Step 4: Iterative Improvement
- Run enrichment on all characters
- Review and refine
- Update enrichment rules
- Re-export as v2, v3, etc.

## Data Sources Priority

### High Priority (Immediate Impact)
1. **Weapons** - Critical for combat
2. **Cyberware/Bioware** - Core character mechanics
3. **Edges/Flaws** - Character definition
4. **Armor** - Survival mechanics

### Medium Priority (Enhanced Gameplay)
5. **Skills** - Understanding capabilities
6. **Spells** - For magical characters
7. **Contacts** - Roleplay context
8. **Vehicles** - Transportation details

### Low Priority (Nice to Have)
9. **Background** - Narrative enrichment
10. **Equipment** - Miscellaneous gear
11. **Lifestyle** - Context details

## Success Metrics

### v1 (Current)
- ✅ 13/17 edges/flaws enriched (76%)
- ✅ 4 cyberware items enriched
- ✅ All characters exported

### v2 (Target)
- 🎯 100% edges/flaws with full mechanics
- 🎯 100% cyberware/bioware with stats
- 🎯 100% weapons with complete data
- 🎯 100% armor with ratings
- 🎯 All items with book references

### v3 (Stretch Goal)
- 🎯 AI-generated tactical summaries
- 🎯 Combat optimization suggestions
- 🎯 Character synergy analysis
- 🎯 Automated character sheet validation

## Next Steps

1. **Immediate**: Review v1 exports for accuracy
2. **Short-term**: Develop AI enrichment script
3. **Medium-term**: Run full enrichment pipeline
4. **Long-term**: Automate continuous enrichment

## Notes

- Keep original markdown files unchanged
- Version all enriched exports (v1, v2, v3...)
- Document all enrichment decisions
- Maintain traceability to source books
- Use database as single source of truth
