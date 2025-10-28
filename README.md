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

Create a `.env` file in the project root with your database credentials:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=postgres
```

**Important:** Never commit the `.env` file to version control. It should be listed in `.gitignore`.

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

**Authoritative Schema File:** `schema.sql` (Version 3.0)

The unified schema includes:

### Core Tables
- **characters**: Character data with base/current attributes for karma tracking
- **character_skills**: Skills with base and current ratings
- **character_modifiers**: Permanent modifiers from cyberware, bioware, training, house rules
- **character_active_effects**: Temporary/sustained effects (spells, drugs, wounds)
- **character_gear**: Physical equipment with modifications
- **character_relationships**: Spells, contacts, foci, etc.

### Campaign Management System
- **campaigns**: Campaign state tracking with objectives, complications, and milestones
- **campaign_npcs**: Dynamic NPC tracking with relevance-based filtering
- **house_rules**: Custom campaign rules and homebrew content

**Campaign Features:**
- Fluid narrative state (current situation, location)
- Objective tracking with completion status
- Active complications management
- Milestone recording for major achievements
- Session linking for multi-session campaigns

**NPC Tracking:**
- Relevance levels: current (active in scene), background (present but not active), future (mentioned but not encountered)
- Status management: active/inactive
- Location tracking with partial matching
- Combat stats storage for NPCs that may fight
- Notes field for GM observations

### Key Features
- **Cyberware/Bioware Tracking**: Use `character_modifiers` with `source_type='cyberware'` or `'bioware'`
- **House Rules Support**: Flag custom content with `is_homebrew=true` and link to `house_rules` table
- **Flexible Modifiers**: JSONB `modifier_data` field stores complex effects (smartlink abilities, conditional bonuses, etc.)
- **Special Abilities**: Store in `modifier_data` JSONB for items like Smartlink 2 (grenade bonus, no mag penalty, called shots)

### Character Modifier System

The modifier system provides a flexible, database-driven approach to managing all character enhancements. See [docs/MODIFIER-SYSTEM.md](docs/MODIFIER-SYSTEM.md) for complete documentation.

**Supported Modifier Types:**
- `vision` - Vision enhancements (thermographic, lowLight, magnification, ultrasound)
- `combat` - Combat bonuses/penalties (smartlink, laser sights, spells)
- `skill` - Skill bonuses (reflex recorders, specializations)
- `attribute` - Attribute modifications (cyberware, bioware)
- `initiative` - Initiative modifiers
- `armor` - Armor bonuses

**Vision System Features:**
- Distinguishes natural vs cybernetic vision (different darkness penalties)
- Supports optical magnification (shifts range categories)
- Handles multiple vision types simultaneously
- Fully extensible without code changes

**Example: Smartlink 3**
```sql
INSERT INTO character_modifiers (
  character_id, modifier_type, target_name, modifier_value,
  source, source_type, modifier_data, is_permanent
) VALUES (
  char_id, 'combat', 'ranged_tn', -3,
  'Smartlink 3', 'cyberware',
  '{"rating": 3, "requires_weapon_smartlink": true}'::jsonb,
  true
);
```

**Old Schema Files:** Archived in `schema/archive/` for reference

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

The Shadowrun GM system consists of three integrated components:

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        SHADOWRUN GM SYSTEM                        │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Web UI        │         │   Orchestrator   │         │   MCP Server    │
│   (www/)        │◄───────►│  game-server.py  │◄───────►│ server-unified  │
│                 │ WebSocket│                  │  Calls  │     .js         │
│ - Chat UI       │         │ - Session Mgmt   │         │                 │
│ - Char Sheets   │         │ - Grok AI        │         │ - Dice Rolling  │
│ - Themes        │         │ - Tool Calling   │         │ - Character DB  │
│ - Error Handler │         │ - Trace IDs      │         │ - Game Mechanics│
└─────────────────┘         └──────────────────┘         └─────────────────┘
         │                           │                             │
         │                           │                             │
         └───────────────────────────┼─────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   PostgreSQL    │
                            │    Database     │
                            │                 │
                            │ - Characters    │
                            │ - Skills        │
                            │ - Modifiers     │
                            │ - Gear          │
                            │ - Rules         │
                            └─────────────────┘
```

### Component Details

#### 1. Web UI (www/)
**Purpose:** Browser-based interface for players and GM

**Key Features:**
- Real-time chat with Grok AI GM
- Character selection and management
- Interactive character sheet viewer
- WebSocket streaming for live responses
- 4 theme options (Tron, Matrix, Cyberpunk, Classic)
- Error handling with trace IDs

**Technology:** Vanilla JavaScript, WebSocket, CSS Grid

**Documentation:** [docs/UI-REFERENCE.md](docs/UI-REFERENCE.md)

#### 2. Orchestrator (game-server.py)
**Purpose:** FastAPI server coordinating AI, tools, and database

**Key Features:**
- WebSocket server for real-time communication
- Grok AI integration (x.ai API)
- Function calling to MCP tools
- Session management with conversation history
- Structured logging with trace IDs
- REST API for character data

**Technology:** Python, FastAPI, WebSocket, Grok AI

**Documentation:** [docs/ORCHESTRATOR-REFERENCE.md](docs/ORCHESTRATOR-REFERENCE.md)

#### 3. MCP Server (server-unified.js)
**Purpose:** Tool provider for game mechanics and data access

**Key Features:**
- 7 game-server.py tools (character data, combat, spells)
- 14 dice rolling tools (via shadowrun2.com API)
- 6 campaign management tools (campaigns, NPCs, state tracking)
- Direct PostgreSQL database access
- Character sheet queries with modifiers
- Combat calculations with vision/smartlink
- Spellcasting with drain
- Dynamic NPC tracking with relevance system
- Campaign state management (objectives, complications, milestones)

**Technology:** Node.js, MCP Protocol, PostgreSQL

**Documentation:** [docs/MCP-TOOLS-REFERENCE.md](docs/MCP-TOOLS-REFERENCE.md)

### Data Flow Example

**Player Action: "I shoot the ganger with my Ares Predator"**

```
1. User types in Web UI
   ↓
2. WebSocket sends to Orchestrator with trace ID
   ↓
3. Orchestrator forwards to Grok AI
   ↓
4. Grok decides to call calculate_ranged_attack tool
   ↓
5. Orchestrator calls MCP Server tool
   ↓
6. MCP Server queries PostgreSQL for:
   - Character stats (Quickness, Firearms skill)
   - Cyberware modifiers (Smartlink, vision)
   - Weapon stats (Ares Predator)
   ↓
7. MCP Server calculates:
   - Base TN from range
   - Modifiers (smartlink -2, vision, etc.)
   - Final TN
   - Rolls dice if combat pool specified
   ↓
8. Result returns to Orchestrator
   ↓
9. Grok interprets result, generates narrative
   ↓
10. Orchestrator streams response to Web UI
   ↓
11. User sees: "You take aim. Roll 8d6 vs TN 4..."
```

### Communication Protocols

**Web UI ↔ Orchestrator:**
- Protocol: WebSocket (ws:// or wss://)
- Format: JSON messages
- Types: chat, add_character, narrative, tool_result, etc.

**Orchestrator ↔ Grok AI:**
- Protocol: HTTPS (OpenAI-compatible API)
- Format: JSON with function calling
- Streaming: Server-Sent Events (SSE)

**Orchestrator ↔ MCP Server:**
- Protocol: Direct function calls (internal)
- Format: Python dictionaries
- Database: psycopg3 with PostgreSQL

**MCP Server ↔ Database:**
- Protocol: PostgreSQL wire protocol
- Format: SQL queries
- Connection: Direct with credentials from .env

### Running the Complete System

**1. Start PostgreSQL:**
```bash
cd D:\projects\local-ai-packaged
docker-compose up -d
```

**2. Start Game Server (Orchestrator):**
```bash
cd c:\Users\Rick\Documents\Cline\MCP\shadowrun-gm
python game-server.py
```

**3. Open Web UI:**
```
http://localhost:8001
```

The MCP server is embedded in game-server.py and starts automatically.

### Environment Configuration

Required `.env` file:
```bash
# Database
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5434
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=postgres

# Grok AI
XAI_API_KEY=your_xai_api_key
```

### Port Usage

- **8001** - Game server (HTTP/WebSocket)
- **5434** - PostgreSQL database
- **3000** - Supabase Studio (optional)

### Legacy MCP Server (Cline Integration)

The original `server.js` provides MCP tools for Cline AI assistant:

```
┌─────────────────┐
│     Cline       │
│   (AI Agent)    │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  shadowrun-gm   │
│   server.js     │
└────────┬────────┘
         │ PostgreSQL
         │
┌────────▼────────┐
│   Database      │
│  - rules_content│
│  - characters   │
└─────────────────┘
```

This is separate from the game server and used for development/testing.

## License

ISC

## Contributing

This is a personal project for managing Shadowrun 2nd Edition game data. Feel free to adapt it for your own use.
