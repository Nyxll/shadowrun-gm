# Shadowrun GM System Architecture

Complete architecture documentation for the Shadowrun 2nd Edition GM Assistant system.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Claude AI                                │
│                    (via Cline/MCP Protocol)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MCP Server (Node.js)                           │
│                   server-unified.js                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Intent Classification & Query Routing                    │   │
│  │ - Pattern matching                                        │   │
│  │ - Keyword analysis                                        │   │
│  │ - LLM fallback (GPT-4o-mini)                             │   │
│  │ - Clarification engine                                    │   │
│  │ - Learning engine                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Data Source Routing                                      │   │
│  │ - Structured tables (spells, powers, totems, gear)       │   │
│  │ - Text chunks (rules, lore)                              │   │
│  │ - Hybrid search (vector + keyword)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Tool Proxies                                             │   │
│  │ - Dice rolling → PHP API                                 │   │
│  │ - Combat modifiers → PHP API                             │   │
│  │ - Character management → PostgreSQL                      │   │
│  │ - Campaign management → PostgreSQL                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────┬───────────────────────┬─────────────────────────┘
                │                       │
                ▼                       ▼
┌───────────────────────────┐  ┌──────────────────────────────────┐
│   PHP API                 │  │   PostgreSQL Database            │
│   shadowrun2.com/dice     │  │   (Supabase Local)               │
│                           │  │                                  │
│ ┌───────────────────────┐ │  │ ┌──────────────────────────────┐ │
│ │ DiceRoller.php        │ │  │ │ Structured Tables:           │ │
│ │ - All dice mechanics  │ │  │ │ - spells                     │ │
│ │ - Shadowrun rules     │ │  │ │ - powers                     │ │
│ │ - Karma pool          │ │  │ │ - totems                     │ │
│ │ - Initiative          │ │  │ │ - gear                       │ │
│ └───────────────────────┘ │  │ │ - campaigns                  │ │
│                           │  │ │ - house_rules                │ │
│ ┌───────────────────────┐ │  │ │ - sr_characters              │ │
│ │ CombatModifiers.php   │ │  │ └──────────────────────────────┘ │
│ │ - Ranged combat TN    │ │  │                                  │
│ │ - Melee combat TN     │ │  │ ┌──────────────────────────────┐ │
│ │ - SR2-specific rules  │ │  │ │ Text Chunks:                 │ │
│ │ - Modifier breakdown  │ │  │ │ - rules_content              │ │
│ └───────────────────────┘ │  │ │   (with vector embeddings)   │ │
│                           │  │ └──────────────────────────────┘ │
│ ┌───────────────────────┐ │  │                                  │
│ │ api.php               │ │  │ ┌──────────────────────────────┐ │
│ │ - Unified endpoint    │ │  │ │ Analytics:                   │ │
│ │ - Error handling      │ │  │ │ - query_logs                 │ │
│ │ - Logging             │ │  │ │ - clarification_feedback     │ │
│ └───────────────────────┘ │  │ └──────────────────────────────┘ │
└───────────────────────────┘  └──────────────────────────────────┘
```

## Component Responsibilities

### 1. MCP Server (Node.js)
**File:** `server-unified.js`

**Responsibilities:**
- Expose tools to Claude via MCP protocol
- Route queries to appropriate data sources
- Manage database connections
- Proxy dice rolling and combat calculations to PHP API
- Handle character and campaign management
- Provide intent classification and query routing

**Key Features:**
- **Intent Classification**: Multi-stage (pattern → keyword → LLM)
- **Hybrid Search**: Combines vector similarity + keyword search
- **Query Logging**: Tracks all queries for analytics
- **Clarification Engine**: Learns from user feedback
- **Learning Engine**: Improves classification over time

**Tools Provided:**
1. `query_shadowrun` - Unified query for rules/gear/lore
2. `roll_dice` - Basic dice rolling
3. `roll_with_target_number` - Shadowrun-style success counting
4. `roll_opposed` - Opposed tests
5. `roll_initiative` - Initiative tracking
6. `roll_with_pools` - Dice pool management
7. `roll_opposed_pools` - Opposed tests with pools
8. `reroll_failures` - Karma pool re-rolls
9. `avoid_disaster` - Rule of One mitigation
10. `buy_karma_dice` - Purchase additional dice
11. `buy_successes` - Purchase raw successes
12. `lookup_gear` - Search gear database
13. `compare_gear` - Compare equipment
14. `get_gear_details` - Detailed gear info
15. `manage_campaigns` - Campaign CRUD
16. `manage_house_rules` - House rule management
17. `create_character` - Character creation
18. `get_character` - Retrieve character
19. `update_character` - Update character
20. `calculate_ranged_combat_tn` - Ranged combat modifiers
21. `calculate_melee_combat_tn` - Melee combat modifiers
22. `explain_combat_modifiers` - Modifier reference
23. `list_light_levels` - Light level reference

### 2. PHP API (Remote Web Service)
**URL:** `https://shadowrun2.com/dice/api.php`

**Responsibilities:**
- All Shadowrun game mechanics
- Dice rolling with exploding dice
- Combat modifier calculations
- Stateless, pure functions
- Can be called by MCP server OR directly by web clients

**Why Remote PHP API?**
- Centralized game mechanics hosted on web server
- Single source of truth for Shadowrun rules
- Can serve both MCP server and web applications
- Easier to test and maintain game logic
- No database dependency for calculations
- Always available, no local setup required

**API Endpoints:**
- Dice Rolling: 13 endpoints
- Combat Modifiers: 5 endpoints
- Full documentation: https://shadowrun2.com/dice/README.md

### 3. PostgreSQL Database
**Connection:** Supabase Local (Docker)

**Schema Categories:**

#### Structured Game Data
- `spells` - Spell database with stats
- `powers` - Adept/critter powers
- `totems` - Shamanic totems
- `gear` - Equipment with full stats

#### Text Content
- `rules_content` - Rules, lore, mechanics (with vector embeddings)

#### Campaign Management
- `campaigns` - Campaign tracking
- `house_rules` - Custom rule modifications
- `sr_characters` - Character sheets
- `character_skills` - Character skills
- `character_spells` - Character spells
- `character_powers` - Character powers
- `character_gear` - Character equipment
- `character_contacts` - Character contacts
- `character_history` - Change audit trail
- `character_modifiers` - Active modifiers

#### Analytics
- `query_logs` - Query tracking and analytics
- `clarification_feedback` - Learning data

## Data Flow Examples

### Example 1: Dice Roll
```
Claude: "Roll 6d6 exploding dice against TN 5"
  ↓
MCP Server: Receives roll_with_target_number tool call
  ↓
MCP Server: Calls PHP API via axios
  POST https://shadowrun2.com/dice/api.php
  {action: "roll_tn", notation: "6d6!", tn: 5}
  ↓
PHP API: DiceRoller::rollWithTargetNumber()
  - Rolls dice
  - Handles exploding dice
  - Counts successes
  ↓
PHP API: Returns JSON result
  ↓
MCP Server: Formats and returns to Claude
  ↓
Claude: Presents result to user
```

### Example 2: Combat Modifier Calculation
```
Claude: "Calculate TN for shooting at prone target at short range with smartlink"
  ↓
MCP Server: Receives calculate_ranged_combat_tn tool call
  ↓
MCP Server: Calls PHP API via axios
  POST https://shadowrun2.com/dice/api.php
  {
    action: "calculate_ranged_tn",
    weapon: {smartlink: true},
    range: "short",
    attacker: {hasSmartlink: true},
    defender: {prone: true}
  }
  ↓
PHP API: CombatModifiers::calculateRangedTN()
  - Base TN from range: 4
  - Smartlink: -2
  - Prone at short range (SR2): -2
  - Final TN: 2 (minimum 2)
  ↓
PHP API: Returns detailed breakdown
  ↓
MCP Server: Formats and returns to Claude
  ↓
Claude: Explains modifiers to user
```

### Example 3: Rules Query
```
Claude: "How does spell drain work?"
  ↓
MCP Server: Receives query_shadowrun tool call
  ↓
MCP Server: Intent classification
  - Pattern matching: No match
  - Keyword analysis: "spell", "drain" → magic category
  - LLM classification: intent="rules", data_sources=["chunks"]
  ↓
MCP Server: Hybrid search on rules_content
  - Generate embedding for query
  - Vector search (pgvector)
  - Keyword search (PostgreSQL FTS)
  - Reciprocal Rank Fusion to combine results
  ↓
PostgreSQL: Returns top matching chunks
  ↓
MCP Server: Formats results with context
  ↓
Claude: Presents explanation to user
```

### Example 4: Gear Lookup
```
Claude: "Show me the Ares Predator stats"
  ↓
MCP Server: Receives query_shadowrun tool call
  ↓
MCP Server: Intent classification
  - Pattern matching: Detects "Ares Predator" (known item)
  - Classification: intent="lookup", tables=["gear"]
  ↓
MCP Server: Query gear table
  SELECT * FROM gear WHERE name ILIKE '%Ares Predator%'
  ↓
PostgreSQL: Returns gear record with stats
  ↓
MCP Server: Formats with damage, ammo, mode, etc.
  ↓
Claude: Presents formatted stats to user
```

## Configuration

### Environment Variables (.env)
```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=postgres

# OpenAI (for embeddings and classification)
OPENAI_API_KEY=your_key_here

# PHP API (optional override)
COMBAT_API_URL=https://shadowrun2.com/dice/api.php
```

### MCP Configuration
**File:** `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "shadowrun-gm": {
      "command": "node",
      "args": [
        "c:\\Users\\Rick\\Documents\\Cline\\MCP\\shadowrun-gm\\server-unified.js"
      ]
    }
  }
}
```

## Key Design Decisions

### Why MCP Server Proxies PHP API?

**Advantages:**
1. **Separation of Concerns**: Game mechanics in PHP, data/AI in Node.js
2. **Reusability**: PHP API can serve web clients directly
3. **Single Source of Truth**: All Shadowrun rules in one place
4. **Easier Testing**: Pure functions in PHP are easier to test
5. **Stateless**: PHP API has no database dependency
6. **Flexibility**: Can swap implementations without changing MCP interface

### Why Not Direct PHP API Access?

Claude/Cline cannot call HTTP APIs directly - they need MCP tools. The MCP server acts as the bridge.

### Why Hybrid Search?

Combines strengths of both approaches:
- **Vector Search**: Semantic understanding, finds conceptually similar content
- **Keyword Search**: Exact matches, technical terms, specific names
- **RRF Fusion**: Best of both worlds

### Why Intent Classification?

Routes queries to optimal data sources:
- **Structured tables**: Fast, precise stats for spells/gear/powers
- **Text chunks**: Detailed explanations, rules, lore
- **Hybrid**: Both stats and context

## Undocumented Features

Based on the code review, here are features that need documentation:

### 1. Intent Classification System
- Multi-stage classification (pattern → keyword → LLM)
- Automatic data source routing
- Clarification engine for ambiguous queries
- Learning engine that improves over time

### 2. Hybrid Search
- Vector similarity search using pgvector
- Full-text search using PostgreSQL
- Reciprocal Rank Fusion for result combination
- Automatic fallback if vector search fails

### 3. Query Analytics
- All queries logged to `query_logs` table
- Tracks execution time, result count, errors
- Classification data stored for analysis
- Can identify content gaps and improve system

### 4. Character Management
- Complete character CRUD operations
- Automatic karma cost calculation
- House rule integration
- Change audit trail
- Modifier tracking

### 5. Campaign & House Rules
- Campaign-specific or global house rules
- Priority-based rule application
- Mechanical effect tracking
- Active/inactive toggle

### 6. Clarification & Learning
- Learns from user feedback
- Improves classification accuracy
- Stores successful query patterns
- Adapts to user preferences

## Testing

See `tests/README.md` for complete test documentation.

**Test Coverage:**
- ✅ Dice rolling (all 13 tools)
- ✅ Gear operations (lookup, compare, details)
- ✅ Intent classification
- ✅ Hybrid search
- ✅ Clarification learning
- 🔄 Combat modifiers (in progress)
- 🔄 Character management (planned)

## Documentation Files

- `README.md` - Project overview and setup
- `ARCHITECTURE.md` - This file
- `tests/README.md` - Test suite documentation
- `SR2-VS-SR3-COMBAT-MODIFIER-COMPARISON.md` - Rule differences
- PHP API Documentation: https://shadowrun2.com/dice/README.md

## External Services

### PHP API Service
- **URL:** https://shadowrun2.com/dice/api.php
- **Documentation:** https://shadowrun2.com/dice/README.md
- **Purpose:** Centralized Shadowrun 2nd Edition game mechanics
- **Endpoints:** Dice rolling, combat modifiers, initiative tracking
- **Access:** Public API, no authentication required
- **Response Format:** JSON

The MCP server treats the PHP API as a remote service and has no knowledge of its internal implementation or file structure.
