# Training Files Analysis

## Current Training Files

### In Root Directory:
1. **training-processor.js** - Node.js version (interactive training processor)
2. **training-processor.py** - Python version (same functionality, more features)
3. **import-training-data.js** - Imports training data
4. **parse-training-data.js** - Parses training data
5. **fix-training-trigger.sql** - SQL fix for training triggers

### In tools/ Directory:
1. **training-processor.py** - Duplicate of root version
2. **import-training-corpus.py** - Imports training corpus
3. **analyze-gm-patterns.py** - Analyzes GM response patterns (KEEP - needed for upcoming training)

### Parse/Process Files (XAI/Roleplay):
- **parse-roleplay-logs.js** - Parses roleplay logs
- **parse-xai-exports.js** - Parses XAI exports
- **process-roleplay-chunked.js** - Processes roleplay in chunks
- **process-xai-batch.js** - Batch processes XAI data
- **process-xai-with-logging.js** - XAI processing with logging
- **run-xai-parser.bat** - Batch file to run XAI parser
- **sample-xai-parse.js** - Sample XAI parsing

## Recommendations

### Files to KEEP:
1. **analyze-gm-patterns.py** - User confirmed needed for upcoming training
2. **training-processor.py** (root) - More feature-complete Python version
3. **parse-roleplay-logs.js** - Needed for processing roleplay logs
4. **process-roleplay-chunked.js** - Needed for roleplay processing

### Files to CONSOLIDATE:
1. **training-processor.js** + **tools/training-processor.py** → Keep root **training-processor.py** only
   - Python version has more features (AI prompt integration, better UX)
   - Archive both JS version and tools/ duplicate

2. **import-training-data.js** + **import-training-corpus.py** → Merge into single Python script
   - Consolidate into **import-training-data.py** in root

3. **parse-training-data.js** → Archive (one-time use, already parsed)

4. XAI parsers → Keep only if actively used for training data
   - **parse-xai-exports.js** - KEEP if XAI data is part of training
   - **process-xai-batch.js** - KEEP if XAI data is part of training
   - **process-xai-with-logging.js** - Archive (duplicate of batch)
   - **sample-xai-parse.js** - Archive (sample/test file)
   - **run-xai-parser.bat** - KEEP if XAI parsing is active

### Files to ARCHIVE:
1. **training-processor.js** - Superseded by Python version
2. **tools/training-processor.py** - Duplicate of root version
3. **parse-training-data.js** - One-time use
4. **fix-training-trigger.sql** - One-time fix
5. **import-training-corpus.py** - Merge with import-training-data
6. **process-xai-with-logging.js** - Duplicate functionality
7. **sample-xai-parse.js** - Sample/test file

## Proposed Final Structure

### Root Directory:
```
training-processor.py          # Main training processor (Python)
import-training-data.py        # Consolidated import script
analyze-gm-patterns.py         # Pattern analysis (move from tools/)
parse-roleplay-logs.js         # Roleplay log parser
process-roleplay-chunked.js    # Roleplay processor
parse-xai-exports.js           # XAI parser (if needed)
process-xai-batch.js           # XAI batch processor (if needed)
run-xai-parser.bat            # XAI runner (if needed)
```

### tools/ Directory:
```
(Remove all training files - consolidated to root)
```

## Questions for User:

1. **Are you still using XAI data for training?**
   - If YES: Keep parse-xai-exports.js, process-xai-batch.js, run-xai-parser.bat
   - If NO: Archive all XAI-related files

2. **Should analyze-gm-patterns.py move to root?**
   - It's training-related and you said it's needed soon
   - Makes sense to keep with other training files

3. **Merge import scripts?**
   - Combine import-training-data.js + import-training-corpus.py → import-training-data.py
