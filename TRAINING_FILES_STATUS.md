# Training Files - Current Status

**Last Updated:** 2025-01-11

## Active Training Files (Root Directory)

### Core Training Tools:
1. **analyze-gm-patterns.py** - GM response pattern analysis
   - Moved from tools/ to root (training-related)
   - Use: Analyze GM response patterns for training refinement

### Status: Training Processing Files Missing
⚠️ **IMPORTANT:** The following files listed in the original analysis were NOT found in the root directory:
- training-processor.py
- parse-roleplay-logs.js
- process-roleplay-chunked.js
- parse-xai-exports.js
- process-xai-batch.js
- run-xai-parser.bat

**These files may be:**
1. Already archived/deleted in a previous cleanup
2. Located in a different directory (check `train/` or `tools/`)
3. Never existed in root (analysis may have been based on planned structure)

## Archived Files

See: `archive/training-files/2025-01-11/`

### What Was Archived:
- **training-processor.js** - Superseded by Python version
- **tools/training-processor.py** - Duplicate of root version
- **parse-training-data.js** - One-time use, already processed
- **fix-training-trigger.sql** - One-time fix, already applied
- **import-training-data.js** - To be replaced by Python version
- **import-training-corpus.py** - To be merged into consolidated import script

## Next Steps

### TODO: Create Consolidated Import Script
Create `import-training-data.py` in root that consolidates:
- Functionality from archived `import-training-data.js`
- Functionality from archived `import-training-corpus.py`
- Use Python with psycopg2 and python-dotenv
- Follow project standards from .clinerules

### Training Workflow:
1. **Parse Data:**
   - Roleplay: Use `parse-roleplay-logs.js` → `process-roleplay-chunked.js`
   - XAI: Use `parse-xai-exports.js` → `process-xai-batch.js`

2. **Import Data:**
   - Use consolidated `import-training-data.py` (to be created)

3. **Process Training:**
   - Use `training-processor.py` for interactive processing
   - Use `analyze-gm-patterns.py` for pattern analysis

4. **Refine:**
   - Analyze patterns
   - Adjust training data
   - Re-process as needed

## File Locations

```
shadowrun-gm/
├── training-processor.py          # Main processor
├── analyze-gm-patterns.py         # Pattern analysis
├── parse-roleplay-logs.js         # Roleplay parser
├── process-roleplay-chunked.js    # Roleplay processor
├── parse-xai-exports.js           # XAI parser
├── process-xai-batch.js           # XAI batch processor
├── run-xai-parser.bat            # XAI runner
└── archive/
    └── training-files/
        └── 2025-01-11/            # Archived duplicates
