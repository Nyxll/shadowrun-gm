# Orchestrator Reference - game-server.py

This document describes the FastAPI orchestrator that coordinates between the web UI, Grok AI, and MCP tools.

## Overview

The `game-server.py` is a FastAPI-based WebSocket server that:
- Manages live game sessions with conversation history
- Integrates Grok AI for natural language GM responses
- Calls MCP tools for game mechanics (dice rolling, character data, etc.)
- Provides REST API endpoints for character data
- Implements structured logging with trace IDs for debugging

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
                            │  (x.ai API)  │ │ (Internal)  │ │   Database   │
                            └──────────────┘ └─────────────┘ └──────────────┘
```

## Key Components

### 1. Session Management

**GameSession Class**
Manages individual game sessions with:
- Conversation history (last 20 messages)
- Active characters in the session
- Pending actions (for turn-based combat)
- Turn order tracking
- Current scene information

```python
class GameSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict] = []
        self.active_characters: List[str] = []
        self.pending_actions: Dict[str, Any] = {}
        self.turn_order: List[Dict] = []
        self.current_scene: Optional[str] = None
```

**SessionManager Class**
Manages all active sessions:
- Creates and retrieves sessions
- Registers WebSocket connections
- Maps session IDs to WebSocket instances

### 2. MCP Client

**MCPClient Class**
Executes MCP tool calls by directly querying the PostgreSQL database:

**Available Tools:**
- `get_character` - Full character sheet data
- `get_character_skill` - Specific skill rating
- `calculate_dice_pool` - Dice pool calculation
- `calculate_target_number` - TN determination
- `roll_dice` - Dice rolling with exploding 6s
- `calculate_ranged_attack` - Complete ranged attack calculation
- `cast_spell` - Spellcasting with drain calculation

**Database Connection:**
```python
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB', 'postgres')
}
```

### 3. Grok AI Integration

**Configuration:**
```python
grok = AsyncOpenAI(
    api_key=os.getenv('XAI_API_KEY'),
    base_url="https://api.x.ai/v1"
)
```

**Model:** `grok-4` (via OpenAI-compatible API)

**Function Calling:**
The orchestrator provides tool definitions to Grok, enabling it to:
1. Understand when to call tools
2. Extract parameters from natural language
3. Interpret tool results
4. Generate narrative responses

**Streaming:**
Responses are streamed to the client in real-time for better UX.

### 4. Logging System

**Structured Logging with Trace IDs:**
- Every request gets a unique trace ID (UUID)
- Trace IDs propagate through all operations
- Logs include trace ID for distributed tracing
- Three log files:
  - `shadowrun-gm.log` - All application logs
  - `shadowrun-gm-errors.log` - Error logs only
  - Console output - Simplified format

**Log Rotation:**
- 10MB max file size
- 5 backup files retained
- Automatic rotation

**Example Log Entry:**
```
2025-10-24 17:30:00 | INFO     | [Trace: a1b2c3d4-e5f6-7890-abcd-ef1234567890] | GET /api/character/Platinum
```

### 5. Error Handling

**Structured Error Responses:**
```json
{
  "error": {
    "code": 2001,
    "type": "CHARACTER_NOT_FOUND",
    "message": "Character 'InvalidName' not found",
    "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2025-10-24T17:30:00-04:00",
    "details": {
      "available_characters": ["Platinum", "Block", "Manticore"]
    }
  }
}
```

**Error Codes:**
- `2001` - CHARACTER_NOT_FOUND
- `2002` - CHARACTER_LOAD_FAILED
- `2003` - DATABASE_ERROR
- `2004` - INVALID_REQUEST
- `2005` - API_TIMEOUT
- `2006` - API_ERROR
- `9000` - UNKNOWN_ERROR
- `9001` - INTERNAL_ERROR

## WebSocket Protocol

### Connection

**Endpoint:** `ws://localhost:8001/game/{session_id}`

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8001/game/session_123');
```

### Message Types

#### Client → Server

**1. Chat Message**
```json
{
  "type": "chat",
  "message": "I want to shoot the ganger with my Ares Predator"
}
```

**2. Add Character**
```json
{
  "type": "add_character",
  "character": "Platinum"
}
```

**3. Remove Character**
```json
{
  "type": "remove_character",
  "character": "Platinum"
}
```

**4. Get Session Info**
```json
{
  "type": "get_session_info"
}
```

#### Server → Client

**1. System Message**
```json
{
  "type": "system",
  "content": "Connected to session session_123"
}
```

**2. Processing Indicator**
```json
{
  "type": "processing",
  "content": "GM is thinking..."
}
```

**3. Narrative (Streaming)**
```json
{
  "type": "narrative",
  "content": "The ganger dives for cover as you..."
}
```

**4. Tool Execution**
```json
{
  "type": "tool_execution",
  "tools": ["calculate_ranged_attack", "roll_dice"]
}
```

**5. Tool Result**
```json
{
  "type": "tool_result",
  "tool": "calculate_ranged_attack",
  "result": {
    "final_tn": 4,
    "combat_pool": 8,
    "successes": 6
  }
}
```

**6. Complete**
```json
{
  "type": "complete",
  "content": "Response complete"
}
```

**7. Error**
```json
{
  "type": "error",
  "content": "Error: Character not found"
}
```

**8. Session Info**
```json
{
  "type": "session_info",
  "session_id": "session_123",
  "characters": ["Platinum", "Block"],
  "message_count": 15
}
```

## REST API Endpoints

### GET /

Serves the main web interface (`www/index.html`)

### GET /api/characters

List all available characters from the database.

**Response:**
```json
{
  "characters": [
    {
      "id": "uuid-string",
      "name": "Platinum",
      "full_name": "Platinum",
      "character_type": "Player Character",
      "archetype": "Street Samurai"
    }
  ]
}
```

### GET /api/character/{character_name}

Get complete character sheet data.

**Parameters:**
- `character_name` - Name or street name of character

**Response:** Complete character sheet (see MCP-TOOLS-REFERENCE.md for structure)

**Headers:**
- `X-Trace-ID` - Trace ID for debugging

### GET /api/sessions

List all active game sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session_123",
      "characters": ["Platinum", "Block"],
      "message_count": 15,
      "created_at": "2025-10-24T17:00:00-04:00"
    }
  ]
}
```

### POST /api/sessions

Create a new game session.

**Request:**
```json
{
  "session_id": "my_session"
}
```

**Response:**
```json
{
  "session_id": "my_session",
  "created_at": "2025-10-24T17:30:00-04:00"
}
```

## Grok AI Workflow

### 1. User Message Processing

```python
async def process_with_grok(
    session: GameSession,
    user_message: str,
    websocket: WebSocket
) -> str:
```

**Steps:**
1. Add user message to conversation history
2. Build message array with system context
3. Call Grok with tool definitions
4. Stream response to client
5. Execute any tool calls
6. Get final response with tool results
7. Add assistant response to history

### 2. System Context

Loaded from `train/prompts/system-context.txt`:
- GM role and responsibilities
- Available tools and when to use them
- Shadowrun 2nd Edition rules
- How to handle player actions
- Narrative style guidelines

### 3. Tool Calling Flow

```
User: "I shoot the ganger"
  ↓
Grok: [Calls calculate_ranged_attack]
  ↓
Orchestrator: [Executes tool, returns result]
  ↓
Grok: [Interprets result, generates narrative]
  ↓
Client: "You take aim and fire. Roll 8d6 vs TN 4..."
```

## Data Type Handling

### UUID and Decimal Conversion

PostgreSQL returns UUID and Decimal types that aren't JSON-serializable. The orchestrator converts them:

```python
def convert_db_types(obj):
    """Recursively convert UUID and Decimal to JSON-serializable types"""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    # ... recursive handling for dicts and lists
```

### Custom JSON Encoder

```python
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
```

## Configuration

### Environment Variables

Required in `.env` file:

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

### Server Configuration

**Host:** `0.0.0.0` (all interfaces)  
**Port:** `8001`  
**Protocol:** HTTP/WebSocket

## Running the Server

### Development

```bash
python game-server.py
```

### Production

```bash
uvicorn game-server:app --host 0.0.0.0 --port 8001 --workers 4
```

### With Auto-Reload

```bash
uvicorn game-server:app --reload --host 0.0.0.0 --port 8001
```

## Middleware

### TraceIDMiddleware

Handles trace ID propagation:
1. Extracts trace ID from `X-Trace-ID` header
2. Generates new UUID if not present
3. Sets in context variable for logging
4. Adds to response headers
5. Logs request/response with trace ID

## Performance Considerations

### Conversation History Limit

Only the last 20 messages are kept to manage token usage with Grok AI:

```python
if len(self.conversation_history) > 20:
    self.conversation_history = self.conversation_history[-20:]
```

### Database Connection Pooling

Currently uses direct connections. For production, consider:
- Connection pooling with `psycopg_pool`
- Async database operations
- Connection timeout handling

### Streaming Responses

Grok responses are streamed to reduce perceived latency:
- Client sees text as it's generated
- Better user experience
- Lower memory usage

## Error Recovery

### WebSocket Disconnection

```python
except WebSocketDisconnect:
    session_manager.unregister_websocket(session_id)
    print(f"Client disconnected from session {session_id}")
```

### Database Errors

All database operations are wrapped in try/finally blocks to ensure connections are closed:

```python
try:
    cursor.execute(...)
    result = cursor.fetchone()
finally:
    cursor.close()
    conn.close()
```

### API Errors

Grok API errors are caught and returned as structured error responses with trace IDs.

## Testing

### Manual Testing

```bash
# Start server
python game-server.py

# In another terminal, test WebSocket
wscat -c ws://localhost:8001/game/test_session

# Send chat message
{"type": "chat", "message": "Hello GM"}
```

### API Testing

```bash
# List characters
curl http://localhost:8001/api/characters

# Get character
curl http://localhost:8001/api/character/Platinum

# Create session
curl -X POST http://localhost:8001/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test"}'
```

## Future Enhancements

### Planned Features

1. **Persistent Sessions** - Save sessions to database
2. **Combat Tracker** - Initiative and turn management
3. **Dice Pool Management** - Track Combat Pool, Karma Pool usage
4. **Character State** - Track wounds, conditions, active spells
5. **Scene Management** - Save and load scenes
6. **Multi-User Support** - Multiple players per session
7. **Voice Integration** - Text-to-speech for GM narration

### Performance Improvements

1. **Connection Pooling** - Async database pool
2. **Caching** - Redis for character data
3. **Rate Limiting** - Prevent API abuse
4. **Load Balancing** - Multiple server instances

## Troubleshooting

### Common Issues

**1. WebSocket Connection Fails**
- Check server is running on port 8001
- Verify firewall allows WebSocket connections
- Check browser console for errors

**2. Database Connection Errors**
- Verify PostgreSQL is running
- Check `.env` file has correct credentials
- Test connection with `psql`

**3. Grok API Errors**
- Verify `XAI_API_KEY` is set
- Check API quota/limits
- Review error logs with trace ID

**4. Character Not Found**
- Check character name spelling
- Try using street name instead
- List available characters with `/api/characters`

### Debug Mode

Enable detailed logging:

```python
# In
