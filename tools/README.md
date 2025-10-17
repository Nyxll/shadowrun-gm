# Shadowrun GM Tools

This directory contains utility and diagnostic scripts for the Shadowrun GM MCP server. These are development and testing tools, not part of the core MCP server functionality.

## Database Inspection Tools

### Content Verification
- **check-barrett.py** - Verify Barrett rifle is in database after rechunking
- **check-gear-chunks.py** - Verify gear items are properly separated into individual chunks
- **show-gear-examples.py** - Display example gear chunks with full content
- **check-content-types.py** - Check content type distribution
- **check-content-types-final.py** - Final content type validation
- **verify-database.py** - General database verification

### Schema & Structure
- **check-schema.py** - Verify database schema
- **check-tables.py** - Check database tables and structure
- **list-all-files.py** - List all files in the processed directory

### Duplicate Detection
- **check-duplicates.py** - Find duplicate chunks in database
- **show-duplicate-examples.py** - Show examples of duplicate content
- **remove-duplicates.py** - Remove duplicate chunks (use with caution)

## Testing Tools

### Server Testing
- **test-connection.js** - Test database connection
- **test-db-connection.js** - Alternative database connection test
- **test-unified-server.js** - Test the unified MCP server
- **test-enhanced-server.js** - Test enhanced server features

## AI Model Comparison

- **compare-gpt-models.py** - Compare different GPT models for categorization
- **compare-llms.py** - Compare various LLM models

## Usage

Most Python scripts can be run directly from the shadowrun-gm directory:

```bash
cd shadowrun-gm
python tools/check-barrett.py
python tools/show-gear-examples.py
```

Node.js scripts:

```bash
cd shadowrun-gm
node tools/test-unified-server.js
```

## Note

These tools are for development and debugging. The core MCP server files remain in the parent directory:
- `server-unified.js` - Main MCP server
- `rechunk-all.py` - Rechunking script
- `process-chunks.py` - Chunk processing
- etc.
