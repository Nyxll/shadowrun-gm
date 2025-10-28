# xAI Export Parser - User Guide

## Quick Start

Run this command to process all your xAI exports:

```bash
node tools/process-xai-batch.js
```

## What It Does

The parser will:
1. ✅ Find all 893 UUID folders in `D:/projects/xAI/prod-mc-asset-server`
2. ✅ Process them in batches of 50 (safe, won't freeze)
3. ✅ Show a progress bar for each batch
4. ✅ Save progress after each batch (resumable if interrupted)
5. ✅ Extract character sheets, campaigns, session logs, etc.

## Output Files

All files are saved to `parsed-xai-data/`:

- **`xai-parsed-all.json`** - Complete parsed data with full content
- **`xai-summary.json`** - Summary with character list and statistics
- **`progress.json`** - Progress tracking (for resuming)

## Features

### Progress Tracking
- Shows progress bar: `[████████████░░░░] 75% (38/50)`
- Saves after each batch
- Can resume if interrupted: `node tools/process-xai-batch.js 5` (starts at batch 5)

### Content Detection
Automatically categorizes content as:
- `character_sheet` - Character sheets with stats, skills, spells
- `campaign_data` - Campaign information and plots
- `session_log` - Session logs and karma awards
- `npc_data` - NPC information
- `location_data` - Location descriptions
- `unknown` - Uncategorized content

### Character Extraction
For character sheets, extracts:
- Character name
- Street name
- Race
- Full content for later detailed parsing

## Batch Processing

**Default:** 50 items per batch
- Safe for large datasets
- Won't freeze or crash
- Progress saved incrementally

**To change batch size:** Edit `BATCH_SIZE` in `tools/process-xai-batch.js`

## Resume Processing

If interrupted, the parser remembers what it processed:

```bash
# Resume from where it left off
node tools/process-xai-batch.js

# Or start from specific batch
node tools/process-xai-batch.js 10
```

## Expected Results

Based on test run:
- **893 folders** to process
- **~18 batches** (at 50 per batch)
- **Processing time:** ~2-5 minutes total
- **Output size:** ~50-100 MB (depends on content)

## Troubleshooting

### No output visible
- The progress bar uses special characters that may not display in all terminals
- Check the output files directly in `parsed-xai-data/`
- Files are saved after each batch, so you can monitor progress

### Script seems frozen
- It's probably processing - check if files are being updated
- Each batch takes 10-30 seconds depending on file sizes
- The progress bar updates in real-time

### Want to start over
Delete these files:
```bash
del parsed-xai-data\progress.json
del parsed-xai-data\xai-parsed-all.json
```

Then run again: `node tools/process-xai-batch.js`

## What's Next

After parsing completes:

1. **Review the summary:**
   ```bash
   type parsed-xai-data\xai-summary.json
   ```

2. **Check character list:**
   The summary includes all extracted characters with names and races

3. **Import to database:**
   Use the parsed data to import characters into the Shadowrun GM database

4. **Create training data:**
   Extract excellent narratives and rules explanations for LLM training

## Example Output

```
🔄 xAI Batch Processor

Found 893 folders with content

Processing 893 remaining folders in batches of 50

Batch 1/18:
Processing [████████████████████████████████████████] 100% (50/50)
✓ Batch 1 saved

Batch 2/18:
Processing [████████████████████████████████████████] 100% (50/50)
✓ Batch 2 saved

...

============================================================
✅ Processing Complete!
   Total items: 893
   Characters: 45
   Errors: 0

📁 Output files:
   C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\parsed-xai-data\xai-parsed-all.json
   C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\parsed-xai-data\xai-summary.json
```

## Technical Details

- **Language:** Node.js (ES Modules)
- **Dependencies:** None (uses built-in fs/path)
- **Memory:** Processes in batches to avoid memory issues
- **Error Handling:** Continues on errors, logs them separately
- **Resume:** Tracks processed UUIDs to avoid duplicates

## Support

If you encounter issues:
1. Check `parsed-xai-data/progress.json` to see what was processed
2. Look for error entries in the output JSON
3. Try processing a smaller batch size
4. Check that the xAI directory is accessible
