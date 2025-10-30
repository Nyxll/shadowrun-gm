# Game Server Refactoring Plan

## Problem
The `game-server.py` file is ~2000 lines, making it:
- Slow to read/parse in context
- Hard to maintain
- Difficult to test individual components
- Takes up significant context window space

## Solution: Modular Architecture

Split game-server.py into focused, single-responsibility modules:

```
game-server.py (main entry point - ~200 lines)
├── lib/server/
│   ├── __init__.py
│   ├── config.py              # Configuration & environment
│   ├── logging_setup.py       # Logging configuration
│   ├── middleware.py          # TraceID middleware
│   ├── session_manager.py     # GameSession & SessionManager classes
│   ├── telemetry.py           # All telemetry helper functions
│   ├── websocket_handler.py   # WebSocket endpoint logic
│   ├── http_endpoints.py      # HTTP API endpoints
│   └── tool_definitions.py    # MCP tool definitions (largest file)
```

## File Breakdown

### 1. `game-server.py` (Main Entry - ~200 lines)
**Purpose:** Application entry point and FastAPI setup
```python
- FastAPI app initialization
- Mount static files
- Import and register routes
- Start uvicorn server
```

### 2. `lib/server/config.py` (~50 lines)
**Purpose:** Configuration and environment setup
```python
- Load environment variables
- Define constants (LOG_DIR, etc.)
- Grok client initialization
- CustomJSONEncoder class
- convert_db_types function
```

### 3. `lib/server/logging_setup.py` (~100 lines)
**Purpose:** Logging configuration
```python
- setup_logging() function
- TraceIDFormatter class
- TraceIDLoggerAdapter class
- trace_id_var context variable
- trace_logger initialization
```

### 4. `lib/server/middleware.py` (~50 lines)
**Purpose:** HTTP middleware
```python
- TraceIDMiddleware class
- Request/response logging
- Trace ID propagation
```

### 5. `lib/server/session_manager.py` (~100 lines)
**Purpose:** Session management
```python
- GameSession class
- SessionManager class
- Session CRUD operations
```

### 6. `lib/server/telemetry.py` (~150 lines)
**Purpose:** Telemetry helper functions
```python
- send_telemetry()
- send_mcp_telemetry()
- send_database_telemetry()
- send_api_telemetry()
- send_error_telemetry()
- send_ui_telemetry()
```

### 7. `lib/server/websocket_handler.py` (~300 lines)
**Purpose:** WebSocket endpoint logic
```python
- websocket_endpoint() function
- Message handling (chat, add_character, etc.)
- Grok streaming logic
- Tool call execution
```

### 8. `lib/server/http_endpoints.py` (~150 lines)
**Purpose:** HTTP API endpoints
```python
- list_characters_endpoint()
- get_character_endpoint()
- cast_spell_endpoint()
- get_sustained_spells_endpoint()
- drop_spell_endpoint()
- list_sessions()
- create_session()
```

### 9. `lib/server/tool_definitions.py` (~1000 lines)
**Purpose:** MCP tool definitions
```python
- get_mcp_tool_definitions() function
- All 60+ tool definitions
- Can be further split by phase if needed
```

### 10. `lib/server/mcp_client.py` (~400 lines)
**Purpose:** MCP client wrapper
```python
- MCPClient class
- call_tool() method with all tool routing
- Can be further split by phase if needed
```

## Benefits

### Performance
- **Faster Loading:** Each module loads independently
- **Lazy Imports:** Only load what's needed
- **Parallel Processing:** Modules can be cached separately

### Maintainability
- **Single Responsibility:** Each file has one clear purpose
- **Easier Testing:** Test individual modules in isolation
- **Better Organization:** Related code grouped together
- **Smaller Context:** Each file fits easily in context window

### Development
- **Faster Iteration:** Modify one module without touching others
- **Clear Dependencies:** Import structure shows relationships
- **Easier Debugging:** Smaller files easier to debug
- **Better Collaboration:** Multiple devs can work on different modules

## Context Window Impact

### Before (Current)
- game-server.py: ~2000 lines (~60K tokens)
- Must load entire file to make changes
- Takes up 47% of 128K context window

### After (Refactored)
- Largest file: tool_definitions.py (~1000 lines, ~30K tokens)
- Most files: 50-300 lines (~2-10K tokens each)
- Only load files you're working on
- Typical context usage: 10-20K tokens (8-16%)

## Implementation Steps

### Phase 1: Extract Configuration & Logging
1. Create `lib/server/` directory
2. Move logging setup to `logging_setup.py`
3. Move config to `config.py`
4. Update imports in `game-server.py`
5. Test server starts correctly

### Phase 2: Extract Middleware & Sessions
1. Move TraceIDMiddleware to `middleware.py`
2. Move GameSession/SessionManager to `session_manager.py`
3. Update imports
4. Test WebSocket connections

### Phase 3: Extract Telemetry
1. Move all telemetry functions to `telemetry.py`
2. Update imports in websocket handler
3. Test telemetry events

### Phase 4: Extract WebSocket Handler
1. Move websocket_endpoint to `websocket_handler.py`
2. Import dependencies (telemetry, session_manager, etc.)
3. Test chat and tool calls

### Phase 5: Extract HTTP Endpoints
1. Move all HTTP endpoints to `http_endpoints.py`
2. Create FastAPI router
3. Test all endpoints

### Phase 6: Extract Tool Definitions
1. Move get_mcp_tool_definitions() to `tool_definitions.py`
2. Optionally split by phase (tool_definitions_phase1.py, etc.)
3. Test tool calls

### Phase 7: Extract MCP Client
1. Move MCPClient class to `mcp_client.py`
2. Optionally split call_tool() by phase
3. Test all tool operations

### Phase 8: Final Cleanup
1. Update game-server.py to be minimal entry point
2. Add __init__.py files
3. Update documentation
4. Run full test suite

## File Size Estimates

```
game-server.py              200 lines  (was 2000)
lib/server/config.py         50 lines
lib/server/logging_setup.py 100 lines
lib/server/middleware.py     50 lines
lib/server/session_manager.py 100 lines
lib/server/telemetry.py     150 lines
lib/server/websocket_handler.py 300 lines
lib/server/http_endpoints.py 150 lines
lib/server/tool_definitions.py 1000 lines
lib/server/mcp_client.py    400 lines
-------------------------------------------
Total:                      2500 lines (includes new structure)
```

## Testing Strategy

After each phase:
1. Run `python game-server.py` - should start without errors
2. Test WebSocket connection
3. Test character loading
4. Test tool calls
5. Test telemetry events
6. Run existing test suite

## Rollback Plan

- Keep original `game-server.py` as `game-server.backup.py`
- Each phase is independent
- Can revert individual modules if issues arise
- Git commits after each successful phase

## Success Criteria

- ✅ Server starts and runs correctly
- ✅ All WebSocket functionality works
- ✅ All HTTP endpoints work
- ✅ All tool calls execute correctly
- ✅ Telemetry events display properly
- ✅ No performance degradation
- ✅ All tests pass
- ✅ Each module < 500 lines (except tool_definitions)
- ✅ Context window usage < 20% for typical edits

## Future Enhancements

Once refactored, we can:
1. Add type hints to all modules
2. Create unit tests for each module
3. Add module-level documentation
4. Implement dependency injection
5. Add performance monitoring per module
6. Create module-specific logging
7. Split tool_definitions by phase if needed
8. Add caching layers per module

## Estimated Time

- Phase 1-2: 30 minutes
- Phase 3-4: 30 minutes
- Phase 5-6: 45 minutes
- Phase 7-8: 30 minutes
- Testing: 30 minutes
**Total: ~3 hours**

## Priority

**HIGH** - This refactoring will:
- Make future development 3-5x faster
- Reduce context window usage by 60-80%
- Improve code maintainability significantly
- Enable better testing and debugging
- Allow multiple developers to work simultaneously

## Next Steps

1. Create `lib/server/` directory structure
2. Start with Phase 1 (Configuration & Logging)
3. Test after each phase
4. Document any issues encountered
5. Update this plan as needed

---

**Status:** Ready to implement
**Owner:** Development team
**Timeline:** Can be completed in one session
