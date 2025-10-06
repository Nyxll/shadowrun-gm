# Shadowrun GM MCP Server - Setup Guide

## Quick Start

The server is now installed and ready to use! Follow these steps to add it to Cline.

## Step 1: Add to Cline MCP Settings

1. Open the Cline MCP settings file:
   - **Windows:** `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
   - Full path: `C:\Users\Rick\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

2. Add the shadowrun-gm server configuration:

```json
{
  "mcpServers": {
    "dice-server": {
      "command": "node",
      "args": [
        "C:\\Users\\Rick\\Documents\\Cline\\MCP\\dice-server\\mcp-server.js"
      ]
    },
    "shadowrun-gm": {
      "command": "node",
      "args": [
        "C:\\Users\\Rick\\Documents\\Cline\\MCP\\shadowrun-gm\\server.js"
      ]
    }
  }
}
```

3. Save the file and restart VS Code (or reload the Cline extension)

## Step 2: Verify Installation

After restarting VS Code, you should see the shadowrun-gm server listed in Cline's MCP servers.

You can test it by asking Cline:
```
"List the available tools from the shadowrun-gm MCP server"
```

## Step 3: Populate the Database

The database is currently empty. You need to populate it with your Shadowrun rules data.

### Option A: Manual Entry (for testing)

You can manually insert test data:

```sql
INSERT INTO rules_content (title, content, rule_category, subcategory, tags) VALUES
(
  'Initiative',
  'Initiative determines the order in which characters act during a Combat Turn. Each character rolls Initiative Dice (usually 1d6 + Reaction) at the start of combat. The result determines when they act in each Combat Phase.',
  'combat',
  'initiative',
  ARRAY['initiative', 'combat', 'reaction', 'combat_turn']
);
```

### Option B: Import from Existing RAG Database

You'll need to:
1. Export your existing vector store data
2. Transform it to match the `rules_content` schema
3. Generate embeddings (optional, for semantic search)
4. Import into PostgreSQL

A migration script will be created in a future update.

## Available Tools

### 1. query_rules
Search for rules using natural language.

**Example:**
```
"Use shadowrun-gm to find rules about initiative"
```

### 2. explain_mechanic
Get comprehensive explanations of game mechanics.

**Example:**
```
"Use shadowrun-gm to explain combat pool mechanics"
```

### 3. list_rule_categories
Browse available rule categories.

**Example:**
```
"Use shadowrun-gm to list all rule categories"
```

## Database Connection

The server connects to your local Supabase instance:
- **Host:** localhost
- **Port:** 5433 (mapped from container's 5432)
- **Database:** postgres
- **User:** postgres

Make sure your Supabase Docker containers are running:
```bash
cd D:\projects\local-ai-packaged
docker-compose up -d
```

## Troubleshooting

### Server won't start
1. Check that Supabase is running: `docker ps`
2. Verify the database connection in `.env`
3. Check for port conflicts on 5433

### No results from queries
The database is empty. You need to populate it with rules data first.

### MCP server not appearing in Cline
1. Verify the path in `cline_mcp_settings.json` is correct
2. Restart VS Code completely
3. Check Cline's output panel for errors

## Next Steps

1. **Populate the database** with your Shadowrun rules
2. **Test the tools** by querying for rules
3. **Add more data** as needed (gear, characters, lore)
4. **Expand functionality** with additional tools

## Future Enhancements

- **Phase 2:** Gear and equipment database
- **Phase 3:** Character management
- **Phase 4:** Setting lore and world information
- **Migration script:** Automated import from existing RAG database
- **Vector search:** Semantic search using embeddings
