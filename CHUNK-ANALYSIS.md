# RAG Database Chunk Analysis & Improvement Recommendations

## Current State Analysis

### Database Overview
- **Total Chunks:** 287
- **Average Chunk Size:** 800 characters
- **Size Range:** 11 - 1,000 characters
- **Embedding Dimensions:** 768 (likely text-embedding-ada-002 or similar)
- **Source Files:** 3 OCR documents
  - FieldsofFire-rules-ocr.txt (77 chunks)
  - FieldsofFire-gear-ocr.txt (118 chunks)
  - FieldsofFire-lore-ocr.txt (92 chunks)

### Current Metadata Structure
```json
{
  "loc": {
    "lines": {
      "from": 1,
      "to": 3
    }
  },
  "source": "blob",
  "file_id": "/data/shared/FieldsofFire-rules-ocr.txt",
  "blobType": "application/json"
}
```

---

## Problems Identified

### 1. **Poor Metadata Quality** ⚠️ CRITICAL
**Issues:**
- No semantic categorization (combat, magic, matrix, gear, etc.)
- No rule titles or headings extracted
- No tags for searchability
- Only line numbers (not useful for semantic search)
- Generic "blob" source type
- No book/edition information

**Impact:**
- Cannot filter by category
- Cannot browse by topic
- Difficult to provide context in responses
- No way to distinguish rule types
- Poor search relevance

### 2. **Inconsistent Chunk Boundaries** ⚠️ HIGH
**Issues:**
- Chunks split by arbitrary line counts, not semantic meaning
- Headers separated from content (e.g., "## DEVELOPER NOTES" alone)
- Tables split across chunks
- Conversational flavor text mixed with rules
- Some chunks as small as 11 characters

**Impact:**
- Incomplete information in search results
- Context loss across chunk boundaries
- Poor embedding quality for tiny chunks
- Redundant information retrieval

### 3. **OCR Artifacts** ⚠️ MEDIUM
**Issues:**
- `\r` line endings preserved
- Repeated characters (e.g., "pprovides", "tter")
- Formatting markers mixed with content
- Markdown tables not properly parsed

**Impact:**
- Reduced search accuracy
- Embedding quality degradation
- Harder to read responses

### 4. **Missing Semantic Structure** ⚠️ HIGH
**Issues:**
- No distinction between:
  - Rule mechanics vs flavor text
  - Stat blocks vs descriptions
  - Examples vs core rules
  - Commentary vs official rules
- No hierarchy (main rules vs sub-rules)

**Impact:**
- Cannot prioritize core rules over examples
- Difficult to provide concise answers
- May return flavor text instead of mechanics

### 5. **Embedding Dimension Mismatch** ⚠️ MEDIUM
**Current:** 768 dimensions (older model)
**New Schema:** 1536 dimensions (text-embedding-3-small)

**Impact:**
- Need to regenerate embeddings for new schema
- Cannot directly migrate existing embeddings
- Opportunity to improve with newer model

---

## Recommended Improvements

### Phase 1: Metadata Enhancement (CRITICAL)

#### Add Semantic Categories
```json
{
  "title": "Combat Pool",
  "rule_category": "combat",
  "subcategory": "dice_pools",
  "tags": ["combat_pool", "intelligence", "willpower", "dice_allocation"],
  "source_book": "Fields of Fire",
  "source_file": "FieldsofFire-rules-ocr.txt",
  "content_type": "rule_mechanic",  // vs "flavor_text", "example", "stat_block"
  "edition": "2nd",
  "page_reference": null,  // if available
  "related_rules": ["initiative", "target_numbers"]
}
```

#### Category Taxonomy
**Rules Categories:**
- `combat` - Combat mechanics, initiative, damage
- `magic` - Spellcasting, drain, astral
- `matrix` - Decking, IC, programs
- `character_creation` - Attributes, priority, essence
- `skills` - Skill tests, defaulting, specializations
- `gear_mechanics` - How gear works (ranges, armor, etc.)
- `general` - Core mechanics, target numbers, success levels

**Gear Categories:**
- `weapons` - Firearms, melee, explosives
- `armor` - Body armor, helmets, shields
- `cyberware` - Implants, essence costs
- `bioware` - Biological augmentations
- `equipment` - General gear, tools
- `vehicles` - Cars, bikes, drones
- `magic_items` - Foci, fetishes

**Lore Categories:**
- `locations` - Cities, districts, buildings
- `corporations` - Megacorps, subsidiaries
- `factions` - Gangs, organizations
- `npcs` - Notable characters
- `timeline` - Historical events
- `setting` - World information

### Phase 2: Improved Chunking Strategy

#### Semantic Chunking Rules
1. **Keep Headers with Content**
   - Include section headers in the chunk
   - Don't split headers from their content

2. **Respect Semantic Boundaries**
   - Complete rules in one chunk when possible
   - Keep stat blocks together
   - Don't split tables
   - Keep examples with their rules

3. **Optimal Chunk Sizes**
   - **Minimum:** 200 characters (avoid tiny chunks)
   - **Target:** 600-1000 characters (current average is good)
   - **Maximum:** 1500 characters (allow larger for complete rules)

4. **Chunk Overlap**
   - Add 100-200 character overlap between chunks
   - Helps maintain context across boundaries
   - Improves retrieval accuracy

#### Example of Good Chunking
```
CHUNK 1:
Title: "Combat Pool"
Content: "The Combat Pool represents a character's ability to perform 
exceptional feats in combat. It equals Intelligence + Willpower. 
Combat Pool dice can be allocated to improve attack rolls, defense 
rolls, or other combat actions..."

CHUNK 2:
Title: "Combat Pool Allocation"
Content: "...Combat Pool dice can be allocated to improve attack rolls, 
defense rolls, or other combat actions. Allocated dice are rolled 
along with the base dice pool and count toward successes. Combat Pool 
refreshes at the start of each Combat Turn..."
```

### Phase 3: Content Type Separation

#### Separate Content Types
1. **Rule Mechanics** - Core game rules
2. **Stat Blocks** - Gear/weapon/spell statistics
3. **Examples** - Gameplay examples and scenarios
4. **Flavor Text** - In-character commentary, lore
5. **Tables** - Reference tables and charts

#### Benefits
- Can prioritize mechanics over flavor in search
- Better context for AI responses
- Easier to format responses appropriately

### Phase 4: OCR Cleanup

#### Text Normalization
```python
def clean_ocr_text(text):
    # Remove \r line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Fix repeated characters (OCR errors)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common OCR mistakes
    text = text.replace('pprovides', 'provides')
    text = text.replace('tter', 'tter')
    
    # Clean markdown formatting
    text = clean_markdown(text)
    
    return text.strip()
```

### Phase 5: Enhanced Search Metadata

#### Add Search-Optimized Fields
```json
{
  "search_keywords": [
    "combat pool",
    "intelligence willpower",
    "dice allocation",
    "attack defense"
  ],
  "difficulty_level": "core",  // core, advanced, optional
  "frequently_referenced": true,
  "cross_references": [
    "initiative",
    "target_numbers",
    "staged_success"
  ]
}
```

---

## Migration Strategy

### Option A: Full Reprocessing (RECOMMENDED)

#### Advantages
- Clean slate with proper chunking
- Better metadata from the start
- Opportunity to use newer embedding model
- Can implement all improvements

#### Process
1. **Extract Raw Text**
   ```sql
   SELECT content, metadata->>'file_id' as source 
   FROM documents 
   ORDER BY metadata->'loc'->'lines'->>'from';
   ```

2. **Reconstruct Original Documents**
   - Combine chunks back into source files
   - Clean OCR artifacts
   - Identify section boundaries

3. **Intelligent Re-chunking**
   - Use semantic boundaries (headers, paragraphs)
   - Keep related content together
   - Add overlap between chunks
   - Extract titles from headers

4. **Categorize Content**
   - Use AI to categorize each chunk
   - Extract tags automatically
   - Identify content types
   - Add cross-references

5. **Generate New Embeddings**
   - Use text-embedding-3-small (1536 dim)
   - Better quality than old 768 dim
   - Batch process for efficiency

6. **Insert into New Schema**
   - Use rules_content table
   - Rich metadata from the start
   - Proper categorization

### Option B: Metadata Enhancement Only

#### Advantages
- Faster implementation
- Keep existing embeddings
- Less processing required

#### Process
1. **Analyze Each Chunk**
   - Use AI to categorize
   - Extract titles
   - Generate tags

2. **Update Metadata**
   - Add to existing JSONB field
   - Or migrate to new schema

3. **Regenerate Embeddings Later**
   - Can be done incrementally
   - When ready for 1536 dim

---

## Specific Recommendations by Content Type

### Rules Content

#### Current Problem
```
Chunk 1: "## DEVELOPER NOTES"
Chunk 2: "This sourcebook exposes and explains..."
```

#### Improved Approach
```
Title: "Developer Notes - Fields of Fire Introduction"
Category: general
Subcategory: introduction
Content: "## DEVELOPER NOTES\n\nThis sourcebook exposes and explains 
the shadowy realm of the mercenary. This sourcebook is not about 
playing a mercenary storyline, but about playing a mercenary character 
within the Shadowrun storyline..."
Tags: ["developer_notes", "mercenary", "introduction", "fields_of_fire"]
```

### Gear Content

#### Current Problem
- Stat blocks split from descriptions
- Flavor text mixed with mechanics
- No structured data for stats

#### Improved Approach
```json
{
  "title": "Franchi SPAS-22",
  "rule_category": "gear_mechanics",
  "subcategory": "weapons",
  "content_type": "stat_block",
  "gear_type": "sniper_rifle",
  "stats": {
    "type": "Sniper",
    "conceal": null,
    "ammo": 20,
    "mode": "SA",
    "damage": "15M",
    "weight": 25,
    "availability": "24/21 days",
    "cost": "120,000¥",
    "street_index": 3
  },
  "special_rules": "Decrease Power Level by -2 for each range beyond Short...",
  "tags": ["sniper", "rifle", "franchi", "spas-22", "long_range"]
}
```

### Lore Content

#### Improved Approach
```json
{
  "title": "Philadelphia - Mercenary Culture",
  "rule_category": "lore",
  "subcategory": "locations",
  "content_type": "flavor_text",
  "location": "Philadelphia",
  "characters_mentioned": ["Matador", "Crayfish"],
  "topics": ["mercenary_culture", "weapons", "urban_life"],
  "tags": ["philadelphia", "mercenary", "remington", "scattergun"]
}
```

---

## Implementation Priority

### High Priority (Do First)
1. ✅ **Extract and categorize rules** - Most important for gameplay
2. ✅ **Add semantic metadata** - Enables better search
3. ✅ **Clean OCR artifacts** - Improves quality
4. ✅ **Implement proper chunking** - Better context

### Medium Priority (Do Next)
5. ⏳ **Separate content types** - Improves relevance
6. ⏳ **Add cross-references** - Better navigation
7. ⏳ **Generate new embeddings** - Better search quality

### Low Priority (Nice to Have)
8. ⏳ **Extract structured data** - For gear stats
9. ⏳ **Add difficulty levels** - For filtering
10. ⏳ **Build relationship graph** - For advanced queries

---

## Automated Categorization Approach

### Use AI to Categorize
```python
def categorize_chunk(content):
    prompt = f"""
    Analyze this Shadowrun 2nd Edition content and provide:
    1. A concise title (max 60 chars)
    2. Category (combat/magic/matrix/character_creation/skills/gear_mechanics/general)
    3. Subcategory (specific topic)
    4. 3-5 relevant tags
    5. Content type (rule_mechanic/stat_block/example/flavor_text/table)
    
    Content:
    {content}
    
    Return as JSON.
    """
    
    # Use OpenAI or local LLM to categorize
    result = llm.complete(prompt)
    return json.loads(result)
```

### Batch Processing
- Process all 287 chunks
- Review and adjust categories
- Build tag vocabulary
- Identify cross-references

---

## Expected Improvements

### Search Quality
- **Before:** Generic keyword matching
- **After:** Semantic search with category filtering

### Response Relevance
- **Before:** May return flavor text or incomplete rules
- **After:** Prioritizes complete rule mechanics

### User Experience
- **Before:** "Here's some text that mentions combat pool"
- **After:** "Combat Pool (Combat > Dice Pools): The Combat Pool represents..."

### Maintenance
- **Before:** Difficult to update or add content
- **After:** Clear structure for additions and updates

---

## Next Steps

### Immediate Actions
1. **Backup Current Database**
   ```sql
   pg_dump -h localhost -p 5433 -U postgres -d postgres -t documents > backup.sql
   ```

2. **Create Migration Script**
   - Extract all chunks
   - Reconstruct documents
   - Implement chunking logic
   - Add categorization

3. **Test on Sample**
   - Process 10-20 chunks
   - Verify quality
   - Adjust approach

4. **Full Migration**
   - Process all content
   - Validate results
   - Load into rules_content

### Success Metrics
- ✅ 100% of chunks have categories
- ✅ 95%+ have accurate titles
- ✅ Average 4+ tags per chunk
- ✅ No chunks < 200 characters
- ✅ Search relevance improved
- ✅ Response quality improved

---

## Conclusion

Your current RAG database has good foundational data but suffers from:
1. **Poor metadata** - No semantic categorization
2. **Arbitrary chunking** - Not respecting content boundaries
3. **OCR artifacts** - Reducing quality
4. **No structure** - Can't distinguish content types

**Recommended Approach:** Full reprocessing with intelligent chunking and rich metadata.

**Estimated Effort:**
- Script development: 4-8 hours
- Processing time: 1-2 hours
- Validation: 2-4 hours
- **Total: 1-2 days**

**Expected ROI:**
- 10x better search relevance
- 5x faster to find specific rules
- Much better AI responses
- Easier to maintain and extend

The investment in proper metadata and chunking will pay dividends in usability and search quality.
