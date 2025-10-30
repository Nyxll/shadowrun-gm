# Orchestrator Reference v2.0 - game-server.py

**Updated:** 2025-10-28  
**Version:** 2.0 - Comprehensive CRUD Integration

This document describes the FastAPI orchestrator with all 70 MCP operations integrated.

## Overview

The `game-server.py` is a FastAPI-based WebSocket server that:
- Manages live game sessions with conversation history
- Integrates Grok AI for natural language GM responses
- Provides **70 MCP tools** for complete character and campaign management
- Uses clean CRUD API architecture via `MCPOperations` and `ComprehensiveCRUD`
- Implements structured logging with trace IDs for debugging
- Optimizes AI payloads (50% token reduction)

## Architecture

```
┌─────────────┐         WebSocket          ┌──────────────────┐
│   Web UI    │ ◄─────────────────────────► │  game-server.py  │
│ (www/)      │                             │   (FastAPI)      │
└─────────────┘                             └──────────────────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                                    │                │                │
                                    ▼                ▼                ▼
                            ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
                            │   Grok AI    │ │  MCP Tools  │ │  PostgreSQL  │
                            │  (x.ai API)  │ │  (70 ops)   │ │   Database   │
                            └──────────────┘ └─────────────┘ └──────────────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                                    │                │                │
                                    ▼                ▼                ▼
                            ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
                            │MCPOperations │ │Comprehensive│ │ AI Payload   │
                            │   (lib/)     │ │   CRUD      │ │  Optimizer   │
                            └──────────────┘ └─────────────┘ └──────────────┘
```

## MCP Operations - Complete List (70 Total)

### Phase 1: Core Operations (20)

**Character & Skills:**
1. `get_character` - Full character sheet
2. `get_character_skill` - Specific skill rating
3. `get_skills` - All character skills
4. `add_skill` - Add new skill
5. `improve_skill` - Increase skill rating
6. `add_specialization` - Add skill specialization
7. `remove_skill` - Remove skill

**Dice & Combat:**
8. `calculate_dice_pool` - Calculate dice pool
9. `calculate_target_number` - Determine TN
10. `roll_dice` - Roll with exploding 6s
11. `calculate_ranged_attack` - Complete ranged attack

**Magic:**
12. `cast_spell` - Spellcasting with drain
13. `get_spells` - All character spells
14. `add_spell` - Learn new spell
15. `update_spell` - Modify spell details
16. `remove_spell` - Forget spell

**Resources:**
17. `add_karma` - Award karma
18. `spend_karma` - Spend karma (validated)
19. `update_karma_pool` - Modify karma pool
20. `set_karma` - Set karma values (correction)
21. `add_nuyen` - Add money
22. `spend_nuyen` - Spend money (validated)

**Gear:**
23. `get_gear` - Get character gear
24. `add_gear` - Add gear item
25. `update_gear_quantity` - Modify quantity
26. `remove_gear` - Remove gear

### Phase 2: Augmentations & Equipment (10)

**Cyberware:**
27. `get_cyberware` - All cyberware
28. `add_cyberware` - Install cyberware
29. `update_cyberware` - Modify cyberware
30. `remove_cyberware` - Remove cyberware

**Bioware:**
31. `get_bioware` - All bioware
32. `add_bioware` - Install bioware
33. `remove_bioware` - Remove bioware

**Vehicles:**
34. `get_vehicles` - All vehicles
35. `add_vehicle` - Add vehicle
36. `update_vehicle` - Modify vehicle
37. `remove_vehicle` - Remove vehicle

**Cyberdecks:**
38. `get_cyberdecks` - All cyberdecks
39. `add_cyberdeck` - Add cyberdeck

### Phase 3: Social & Magical (10)

**Contacts:**
40. `get_contacts` - All contacts
41. `add_contact` - Add contact
42. `update_contact_loyalty` - Modify loyalty

**Spirits:**
43. `get_spirits` - All bound spirits
44. `add_spirit` - Bind spirit
45. `update_spirit_services` - Modify services

**Foci:**
46. `get_foci` - All magical foci
47. `add_focus` - Add focus

**Powers:**
48. `get_powers` - All adept powers
49. `add_power` - Add power
50. `update_power_level` - Modify power level

**Edges/Flaws:**
51. `get_edges_flaws` - All edges/flaws
52. `add_edge_flaw` - Add edge or flaw

**Relationships:**
53. `get_relationships` - All relationships
54. `add_relationship` - Add relationship

### Phase 4: Game State Management (10)

**Active Effects:**
55. `get_active_effects` - All active effects
56. `add_active_effect` - Add buff/debuff
57. `update_effect_duration` - Modify duration
58. `remove_active_effect` - Remove effect

**Modifiers:**
59. `get_modifiers` - All modifiers
60. `add_modifier` - Add modifier
61. `update_modifier` - Modify modifier
62. `remove_modifier` - Remove modifier

### Phase 5: Campaign Management (10)

**House Rules:**
63. `get_house_rules` - All house rules
64. `add_house_rule` - Add house rule
65. `toggle_house_rule` - Enable/disable rule

**NPCs:**
66. `get_campaign_npcs` - All campaign NPCs
67. `add_campaign_npc` - Add NPC
68. `update_campaign_npc` - Modify NPC

**Audit:**
69. `get_audit_log` - View audit log

### Phase 6: Character Management (10)

**Character CRUD:**
70. `create_character` - Create new character
71. `update_character_info` - Update bio info
72. `delete_character` - Delete character
73. `update_attribute` - Modify attribute
74. `update_derived_stats` - Update derived stats

## Key Components

### 1. MCPClient Class

Thin wrapper that delegates all operations to `MCPOperations`:

```python
class MCPClient:
    def __init__(self):
        self.ops = MCPOperations()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        # Routes to appropriate MCPOperations method
        if tool_name == "get_character":
            return await self.ops.get_character(arguments.get('character_name'))
        # ... 69 more routes
```

### 2. MCPOperations Layer (lib/mcp_operations.py)

Business logic layer that:
- Handles character UUID lookups
- Validates inputs
- Calls ComprehensiveCRUD methods
- Formats responses for AI consumption
- Logs all operations

### 3. ComprehensiveCRUD Layer (lib/comprehensive_crud.py)

Database access layer that:
- Executes all SQL operations
- Handles transactions
- Manages audit logging
- Converts database types (UUID, Decimal)
- Ensures data integrity

### 4. AI Payload Optimizer (lib/ai_payload_optimizer.py)

Optimizes tool results for AI:
- Removes audit fields (created_at, updated_at, etc.)
- Removes null values
- Reduces payload size by ~50%
- Preserves essential data

```python
def optimize_tool_result(result):
    """Remove audit fields and nulls to reduce token usage"""
    # Saves ~50% tokens while preserving game data
```

### 5. Session Management

**GameSession Class:**
```python
class GameSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict] = []  # Last 20 messages
        self.active_characters: List[str] = []
        self.created_at = datetime.now()
```

**SessionManager Class:**
- Creates and retrieves sessions
- Registers WebSocket connections
- Maps session IDs to WebSocket instances

### 6. Grok AI Integration

**Model:** `grok-4-fast-non-reasoning` (optimized for speed)

**Function Calling:**
- 70 tool definitions in OpenAI format
- Automatic parameter extraction
- Streaming responses
- Tool result interpretation

**System Context:**
```python
messages = [
    {"role": "system", "content": "You are a Shadowrun 2nd Edition GM assistant with access to character data and game mechanics."},
    *[{"role": m["role"], "content": m["content"]} for m in session.conversation_history]
]
```

## WebSocket Protocol

### Message Types

#### Client → Server

**Chat Message:**
```json
{
  "type": "chat",
  "message": "I want to improve my Firearms skill to rating 6"
}
```

**Add Character:**
```json
{
  "type": "add_character",
  "character": "Platinum"
}
```

#### Server → Client

**Narrative (Streaming):**
```json
{
  "type": "narrative",
  "content": "You spend 12 karma to improve your Firearms skill..."
}
```

**Tool Call:**
```json
{
  "type": "tool_call",
  "tool": "improve_skill",
  "arguments": {
    "character_name": "Platinum",
    "skill_name": "Firearms",
    "new_rating": 6,
    "reason": "Character advancement"
  }
}
```

**Tool Result:**
```json
{
  "type": "tool_result",
  "tool": "improve_skill",
  "result": {
    "success": true,
    "skill_name": "Firearms",
    "old_rating": 5,
    "new_rating": 6,
    "karma_spent": 12
  }
}
```

**Telemetry (Debug Window):**
```json
{
  "type": "telemetry",
  "event": "tool_execution_complete",
  "data": {
    "tool": "improve_skill",
    "duration_ms": 45.2,
    "success": true,
    "payload_reduction": "52.3%"
  },
  "timestamp": "2025-10-28T21:30:00-04:00"
}
```

## REST API Endpoints

### GET /api/characters

List all characters with optimized payload.

**Response:**
```json
{
  "characters": [
    {
      "id": "uuid",
      "street_name": "Platinum",
      "given_name": "Sarah Chen",
      "archetype": "Street Samurai",
      "metatype": "Human"
    }
  ]
}
```

### GET /api/character/{character_name}

Get complete character sheet (optimized for UI).

**Headers:**
- `X-Trace-ID` - Trace ID for debugging

## Logging & Telemetry

### Structured Logging

**Three Log Files:**
1. `logs/shadowrun-gm.log` - All operations
2. `logs/shadowrun-gm-errors.log` - Errors only
3. Console - Simplified output

**Log Format:**
```
2025-10-28 21:30:00 | INFO | [Trace: abc-123] | improve_skill: Platinum Firearms 5→6
```

### Telemetry Events

**Tracked Events:**
- `message_received` - User message
- `grok_api_call_start` - AI request start
- `grok_streaming_start` - Streaming begins
- `grok_tool_request` - Tools requested
- `tool_execution_start` - Tool execution begins
- `tool_execution_complete` - Tool done (with duration)
- `request_complete` - Full request done

**Benefits:**
- Performance monitoring
- Debugging tool calls
- Token usage tracking
- Error diagnosis

## Configuration

### Environment Variables

```bash
# Database
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=postgres

# Grok AI
XAI_API_KEY=your_xai_api_key
OPENAI_API_KEY=your_openai_key  # For compatibility
```

### Server Configuration

**Host:** `0.0.0.0`  
**Port:** `8001`  
**Workers:** 1 (development), 4 (production)

## Running the Server

### Development

```bash
python game-server.py
```

### Production

```bash
uvicorn game-server:app --host 0.0.0.0 --port 8001 --workers 4
```

## Data Flow Example

### Improving a Skill

```
1. User: "I want to improve my Firearms skill to 6"
   ↓
2. Grok AI: Analyzes request, calls improve_skill tool
   ↓
3. MCPClient: Routes to MCPOperations.improve_skill()
   ↓
4. MCPOperations: 
   - Looks up character UUID
   - Validates new rating
   - Calls ComprehensiveCRUD.improve_skill()
   ↓
5. ComprehensiveCRUD:
   - Executes SQL UPDATE
   - Logs to audit table
   - Returns result
   ↓
6. AI Payload Optimizer: Removes audit fields, nulls
   ↓
7. Grok AI: Interprets result, generates narrative
   ↓
8. Client: "You spend 12 karma to improve Firearms to rating 6"
```

## Performance Optimizations

### 1. Payload Optimization
- Removes audit fields (created_at, updated_at, etc.)
- Removes null values
- **Result:** ~50% token reduction

### 2. Conversation History Limit
- Keeps last 20 messages only
- Prevents token overflow
- Maintains context

### 3. Streaming Responses
- Real-time text display
- Lower perceived latency
- Better UX

### 4. UUID-Based Lookups
- Fast character lookups
- Handles name changes
- Supports street names and given names

## Error Handling

### Structured Errors

All errors include:
- Error code
- Error type
- Message
- Trace ID
- Timestamp
- Details (when applicable)

**Example:**
```json
{
  "error": {
    "code": 2001,
    "type": "CHARACTER_NOT_FOUND",
    "message": "Character 'InvalidName' not found",
    "trace_id": "abc-123-def-456",
    "timestamp": "2025-10-28T21:30:00-04:00",
    "details": {
      "available_characters": ["Platinum", "Block", "Manticore", "Oak"]
    }
  }
}
```

##
