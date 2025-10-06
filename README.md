# Shadowrun GM MCP Server

An MCP (Model Context Protocol) server that provides AI assistants with access to Shadowrun 2nd Edition rules, gear information, and game mechanics through a local Supabase/PostgreSQL database.

## Features

### Phase 1: Rules System (Current)
- **query_rules**: Search for game rules using natural language queries
- **explain_mechanic**: Get comprehensive explanations of specific game mechanics
- **list_rule_categories**: Browse available rule categories and subcategories

### Future Phases
- **Phase 2**: Gear and equipment database with detailed stats
- **Phase 3**: Character management and tracking
- **Phase 4**: Setting lore and world information

## Prerequisites

- Node.js 18+ 
- PostgreSQL database (via Supabase local setup)
- Docker (for running local Supabase)

## Installation

1. **Clone or navigate to the project directory:**
```bash
cd c:\Users\Rick\Documents\Cline\MCP\shadowrun-gm
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up the database:**

First, ensure your local Supabase instance is running:
```bash
cd D:\projects\local-ai-packaged
docker-compose up -d
```

Then create the database schema:
```bash
# Connect to PostgreSQL
psql -h localhost -p 5432 -U postgres -d postgres

# Run the schema file
\i c:/Users/Rick/Documents/Cline/MCP/shadowrun-gm/schema.sql
```

Or use a GUI tool like pgAdmin to execute the `schema.sql` file.

4. **Configure environment variables:**

The `.env` file is already configured with your local Supabase credentials. Verify the settings:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=daf562f1a5bccb27ff6a7de5c0b5Wq
POSTGRES_DB=postgres
```

## Configuration for Cline

Add this server to your Cline MCP settings file:

**Windows:** `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "shadowrun-gm": {
      "command": "node",
      "args": [
        "c:\\Users\\Rick\\Documents\\Cline\\MCP\\shadowrun-gm\\server.js"
      ]
    }
  }
}
```

After adding, restart VS Code or reload the Cline extension.

## Usage

Once configured, you can use the tools in Cline:

### Query Rules
```
Ask Cline: "Use the shadowrun-gm server to explain how initiative works"
```

This will use the `query_rules` tool to search for initiative-related rules.

### Explain Mechanics
```
Ask Cline: "Use shadowrun-gm to explain combat pool mechanics"
```

This will use the `explain_mechanic` tool to provide a comprehensive explanation.

### Browse Categories
```
Ask Cline: "List all available rule categories in shadowrun-gm"
```

This will use the `list_rule_categories` tool to show what's available.

## Database Schema

### rules_content Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| title | TEXT | Rule title/heading |
| content | TEXT | Full rule text |
| rule_category | TEXT | Main category (combat, magic, matrix, etc.) |
| subcategory | TEXT | Subcategory for organization |
| source_file | TEXT | Original source file name |
| source_book | TEXT | Source book reference |
| tags | TEXT[] | Searchable tags |
| embedding | vector(1536) | Vector embedding for semantic search |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |

### Indexes
- Vector similarity search (ivfflat)
- Full-text search (GIN)
- Category and subcategory indexes
- Tag search (GIN)

## Data Migration

To populate the database with your existing RAG data:

1. Export your current vector store data
2. Transform it into the `rules_content` schema
3. Generate embeddings using OpenAI's text-embedding-3-small model
4. Insert into the database

A migration script will be provided in a future update.

## Development

### Testing the Server

Test the database connection:
```bash
npm start
```

You should see:
```
Database connection successful
Shadowrun GM MCP Server running on stdio
```

### Adding New Tools

Edit `server.js` and add new tool definitions in the `ListToolsRequestSchema` handler and implement them in the `CallToolRequestSchema` handler.

### Database Queries

The server uses PostgreSQL full-text search for now. Once embeddings are populated, it will use vector similarity search for more accurate semantic matching.

## Troubleshooting

### Database Connection Issues

1. Verify Supabase is running:
```bash
docker ps
```

2. Test PostgreSQL connection:
```bash
psql -h localhost -p 5432 -U postgres -d postgres
```

3. Check the `.env` file has correct credentials

### MCP Server Not Appearing in Cline

1. Verify the path in `cline_mcp_settings.json` is correct
2. Restart VS Code
3. Check Cline's MCP server logs for errors

### No Results from Queries

The database may be empty. You need to populate it with rule data first. See the Data Migration section.

## Architecture

```
┌─────────────────┐
│     Cline       │
│   (AI Agent)    │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  shadowrun-gm   │
│   MCP Server    │
└────────┬────────┘
         │ PostgreSQL
         │
┌────────▼────────┐
│   Supabase      │
│   (Local)       │
│  - rules_content│
│  - gear (future)│
│  - characters   │
└─────────────────┘
```

## License

ISC

## Contributing

This is a personal project for managing Shadowrun 2nd Edition game data. Feel free to adapt it for your own use.
