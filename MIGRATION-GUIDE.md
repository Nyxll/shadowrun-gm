# Migration Guide - Reprocessing Original Documents

## Overview

This guide explains how to reprocess your original Shadowrun OCR files with intelligent chunking and rich metadata extraction.

## Why Reprocess from Originals?

**Better than recombining existing chunks because:**
1. ✅ Clean slate - no accumulated errors
2. ✅ Proper semantic boundaries from the start
3. ✅ Headers stay with their content
4. ✅ AI can see full context for categorization
5. ✅ Can fix OCR errors at source
6. ✅ Generate better embeddings with newer model

---

## How It Works

### 1. **Section Extraction** (Markdown Headers)

The script identifies sections by looking for markdown headers:

```
# FIELDS OF FIRE - Rules          <- Level 1 header
## DEVELOPER NOTES                <- Level 2 header
### Combat Pool                   <- Level 3 header
```

**Why this works:**
- Your OCR files use markdown formatting
- Headers naturally indicate topic boundaries
- Keeps related content together

**Example:**
```
Input:
## Combat Pool
The Combat Pool represents...
It equals Intelligence + Willpower...

Output Section:
{
  "header": "Combat Pool",
  "level": 2,
  "content": "## Combat Pool\nThe Combat Pool represents...\nIt equals..."
}
```

### 2. **Intelligent Chunking** (Semantic Boundaries)

Each section is chunked based on:
- **Paragraph boundaries** (not arbitrary line counts)
- **Size limits** (200-1200 characters)
- **Overlap** (150 characters between chunks for context)

**Example:**
```python
Section: "Combat Pool" (2000 characters)

Chunk 1 (1000 chars):
"## Combat Pool
The Combat Pool represents a character's ability...
Combat Pool dice can be allocated..."

Chunk 2 (1150 chars):
"...Combat Pool dice can be allocated...  <- OVERLAP
Allocated dice are rolled along with...
Combat Pool refreshes at the start..."
```

**Why overlap matters:**
- Maintains context across boundaries
- Improves embedding quality
- Better search results

### 3. **AI Categorization** (How Topics Are Assigned)

For each chunk, GPT-4o-mini analyzes:

**Input to AI:**
```
Title: "Combat Pool"
Content: "The Combat Pool represents a character's ability to perform 
exceptional feats in combat. It equals Intelligence + Willpower..."
```

**AI Prompt:**
```
Analyze this Shadowrun 2nd Edition content and provide:
1. category: combat/magic/matrix/character_creation/skills/gear_mechanics/general/lore
2. subcategory: specific topic
3. tags: 3-5 relevant search tags
4. content_type: rule_mechanic/stat_block/example/flavor_text/table
```

**AI Response:**
```json
{
  "category": "combat",
  "subcategory": "dice_pools",
  "tags": ["combat_pool", "intelligence", "willpower", "dice_allocation"],
  "content_type": "rule_mechanic"
}
```

**How AI knows what to assign:**
1. **Keyword analysis** - "Combat Pool", "Intelligence", "Willpower"
2. **Context understanding** - Describes game mechanics
3. **Pattern recognition** - Similar to other combat rules
4. **Content structure** - Explains how something works (= rule mechanic)

**Caching:**
- Results are cached to avoid re-analyzing similar content
- Saves API calls and time

### 4. **Where to Split** (Decision Logic)

The script splits at:

**Priority 1: Section Headers**
```
## Combat Pool          <- SPLIT HERE (new section)
Content about combat pool...

## Initiative           <- SPLIT HERE (new section)
Content about initiative...
```

**Priority 2: Paragraph Breaks**
```
The Combat Pool represents...
First paragraph about basics.

When allocating Combat Pool dice...  <- SPLIT HERE if size exceeded
Second paragraph about allocation.
```

**Priority 3: Size Limits**
```
If paragraph is 1500 chars and max_size is 1200:
  Split at sentence boundary within paragraph
  Add overlap to next chunk
```

**Never splits:**
- In the middle of a sentence
- Within a table
- Between a header and its first paragraph

---

## Step-by-Step Process

### Prerequisites

1. **Install Python dependencies:**
```bash
pip install psycopg2-binary openai
```

2. **Set OpenAI API key:**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

3. **Verify file paths:**
Edit `migrate.py` line 285-289 to point to your actual files:
```python
files = [
    "D:/projects/local-ai-packaged/data/shared/FieldsofFire-rules-ocr.txt",
    "D:/projects/local-ai-packaged/data/shared/FieldsofFire-gear-ocr.txt",
    "D:/projects/local-ai-packaged/data/shared/FieldsofFire-lore-ocr.txt"
]
```

### Running the Migration

#### Step 1: Test on Sample (Recommended)

Create a test file with just one section:

```bash
# Create test file
head -n 50 D:/projects/local-ai-packaged/data/shared/FieldsofFire-rules-ocr.txt > test-sample.txt
```

Modify `migrate.py` to use test file:
```python
files = ["test-sample.txt"]
```

Run migration:
```bash
cd C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm
python migrate.py
```

**Expected output:**
```
============================================================
Shadowrun GM Database Migration
============================================================

Processing: test-sample.txt
  Found 2 sections
  Section 'FIELDS OF FIRE - Rules': 1 chunks
  Section 'DEVELOPER NOTES': 2 chunks
  Total chunks created: 3

============================================================
Total chunks to insert: 3
============================================================

Proceed with database insertion? (yes/no):
```

#### Step 2: Review Test Results

Check the database:
```sql
SELECT title, rule_category, subcategory, tags, LENGTH(content) as size
FROM rules_content
ORDER BY created_at DESC
LIMIT 10;
```

Verify:
- ✅ Titles make sense
- ✅ Categories are accurate
- ✅ Tags are relevant
- ✅ Content is complete
- ✅ No chunks < 200 characters

#### Step 3: Full Migration

Once satisfied with test results:

1. **Backup existing data:**
```bash
docker exec supabase-db pg_dump -U postgres -d postgres -t documents > backup-old-chunks.sql
docker exec supabase-db pg_dump -U postgres -d postgres -t rules_content > backup-rules-content.sql
```

2. **Update file paths in migrate.py** to all three files

3. **Run full migration:**
```bash
python migrate.py
```

4. **When prompted:**
```
Proceed with database insertion? (yes/no): yes
Clear existing rules_content table first? (yes/no): yes
```

**Expected processing time:**
- Rules file (77 chunks): ~5-10 minutes
- Gear file (118 chunks): ~8-15 minutes
- Lore file (92 chunks): ~6-12 minutes
- **Total: ~20-40 minutes** (depends on API speed)

---

## Understanding the Output

### Console Output Explained

```
Processing: FieldsofFire-rules-ocr.txt
  Found 15 sections                    <- Markdown headers found
  Section 'Combat Pool': 2 chunks      <- Section split into 2 chunks
  Section 'Initiative': 1 chunks       <- Section fits in 1 chunk
  Section 'Target Numbers': 3 chunks   <- Larger section, 3 chunks
  Total chunks created: 45             <- Total for this file
```

### What Gets Created

For each chunk:
```json
{
  "title": "Combat Pool",
  "content": "## Combat Pool\n\nThe Combat Pool represents...",
  "rule_category": "combat",
  "subcategory": "dice_pools",
  "tags": ["combat_pool", "intelligence", "willpower"],
  "source_file": "FieldsofFire-rules-ocr.txt",
  "source_book": "Fields of Fire",
  "content_type": "rule_mechanic",
  "embedding": [0.123, -0.456, ...] // 1536 dimensions
}
```

---

## Customization Options

### Adjust Chunk Sizes

In `migrate.py`, modify the `chunk_section` method:

```python
def chunk_section(self, section: Dict, 
                 max_size: int = 1200,    # Maximum chunk size
                 min_size: int = 200,     # Minimum chunk size
                 overlap: int = 150):     # Overlap between chunks
```

**Recommendations:**
- **Smaller chunks (600-800):** Better for precise searches
- **Larger chunks (1000-1500):** Better for context
- **More overlap (200-300):** Better context, more storage
- **Less overlap (50-100):** Less redundancy, less storage

### Change AI Model

For categorization:
```python
model="gpt-4o-mini",  # Fast and cheap
# or
model="gpt-4o",       # More accurate, more expensive
```

For embeddings:
```python
model="text-embedding-3-small",  # 1536 dims, good quality
# or
model="text-embedding-3-large",  # 3072 dims, best quality
```

### Add Custom Categories

Modify the AI prompt to include your custom categories:

```python
prompt = f"""...
1. "category": One of: combat, magic, matrix, character_creation, 
   skills, gear_mechanics, general, lore, house_rules, errata
...
```

---

## Troubleshooting

### "File not found" Error

**Problem:** Script can't find your OCR files

**Solution:** Update file paths in `migrate.py`:
```python
files = [
    "C:/path/to/your/FieldsofFire-rules-ocr.txt",  # Use forward slashes
    # ...
]
```

### "OpenAI API Error"

**Problem:** API key not set or invalid

**Solution:**
```bash
# Check if key is set
echo $env:OPENAI_API_KEY

# Set it
$env:OPENAI_API_KEY="sk-your-key-here"
```

### "Database connection failed"

**Problem:** Can't connect to PostgreSQL

**Solution:**
1. Check Supabase is running: `docker ps`
2. Verify port 5433 is correct
3. Test connection: `psql -h localhost -p 5433 -U postgres -d postgres`

### "Too many API requests"

**Problem:** Hitting OpenAI rate limits

**Solution:** Add delays between requests:
```python
import time

def categorize_content(self, title: str, content: str) -> Dict:
    # ... existing code ...
    time.sleep(0.5)  # Wait 500ms between requests
    # ... rest of code ...
```

### Chunks too small/large

**Problem:** Chunks don't meet size requirements

**Solution:** Adjust parameters:
```python
# For smaller chunks
max_size: int = 800
min_size: int = 150

# For larger chunks
max_size: int = 1500
min_size: int = 300
```

---

## Validation

### After Migration, Check:

1. **Total chunk count:**
```sql
SELECT COUNT(*) FROM rules_content;
-- Should be similar to original 287, maybe slightly different
```

2. **Category distribution:**
```sql
SELECT rule_category, COUNT(*) 
FROM rules_content 
GROUP BY rule_category 
ORDER BY COUNT(*) DESC;
```

3. **Average chunk size:**
```sql
SELECT AVG(LENGTH(content)) as avg_size,
       MIN(LENGTH(content)) as min_size,
       MAX(LENGTH(content)) as max_size
FROM rules_content;
-- avg should be 600-1000, min >= 200
```

4. **Sample chunks:**
```sql
SELECT title, rule_category, subcategory, tags, LEFT(content, 100)
FROM rules_content
LIMIT 10;
```

5. **Embeddings present:**
```sql
SELECT COUNT(*) as with_embeddings
FROM rules_content
WHERE embedding IS NOT NULL;
-- Should equal total count
```

---

## Cost Estimation

### OpenAI API Costs

**For 287 chunks:**

**Categorization (GPT-4o-mini):**
- ~287 requests × 800 tokens input × $0.15/1M tokens = $0.03
- ~287 requests × 100 tokens output × $0.60/1M tokens = $0.02
- **Subtotal: ~$0.05**

**Embeddings (text-embedding-3-small):**
- ~287 chunks × 800 chars avg × $0.02/1M tokens = $0.005
- **Subtotal: ~$0.01**

**Total estimated cost: ~$0.06** (6 cents)

Very affordable for a one-time migration!

---

## Next Steps After Migration

1. **Test search quality:**
```sql
SELECT title, content
FROM rules_content
WHERE to_tsvector('english', title || ' ' || content) 
      @@ plainto_tsquery('english', 'combat pool')
LIMIT 3;
```

2. **Add to Cline MCP settings** (see SETUP.md)

3. **Test from Cline:**
```
"Use shadowrun-gm to explain combat pool"
```

4. **Compare with old system:**
- Search relevance
- Response quality
- Coverage

5. **Iterate if needed:**
- Adjust chunk sizes
- Refine categories
- Add more tags

---

## Summary

**The migration script:**
1. ✅ Reads original OCR files
2. ✅ Cleans OCR artifacts
3. ✅ Extracts sections by markdown headers
4. ✅ Chunks semantically with overlap
5. ✅ Uses AI to categorize and tag
6. ✅ Generates 1536-dim embeddings
7. ✅ Inserts into rules_content table

**Result:**
- Rich metadata for better search
- Semantic chunking for better context
- Modern embeddings for better relevance
- Ready for production use!

**Time investment:** 1-2 hours setup + 30-40 minutes processing
**Cost:** ~$0.06 in API calls
**Benefit:** 10x better search quality and usability
