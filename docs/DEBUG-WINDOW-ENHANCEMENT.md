# Debug Window Enhancement Plan

## Current State
- Debug window only shows telemetry events sent via WebSocket
- Backend has comprehensive logging to files (`logs/shadowrun-gm.log`, `logs/shadowrun-gm-errors.log`)
- Logs include trace IDs, timestamps, and detailed operation info
- No way to view backend logs in real-time from UI

## Goals
1. Show ALL events in debug window:
   - UI events (character selection, sheet viewing, etc.)
   - WebSocket events (connection, messages, etc.)
   - Grok API events (requests, responses, streaming)
   - MCP tool calls (with arguments and results)
   - Database operations (queries, updates, etc.)
   - API endpoint calls (HTTP requests/responses)
   - Error events (with stack traces)

2. Provide log streaming from backend
3. Add filtering and search capabilities
4. Color-code by event type and severity

## Implementation Plan

### Phase 1: Enhanced WebSocket Telemetry
Add more telemetry events to game-server.py:
- `database_query` - When executing SQL
- `mcp_operation_start` - When MCP operation begins
- `mcp_operation_complete` - When MCP operation completes
- `api_request` - HTTP endpoint called
- `api_response` - HTTP endpoint response
- `error_occurred` - Any error with stack trace

### Phase 2: Log Streaming API
Create endpoint `/api/logs/stream` that:
- Tails the log file in real-time
- Sends new log entries via Server-Sent Events (SSE)
- Supports filtering by level, trace ID, component

### Phase 3: Enhanced UI Display
Update app.js to:
- Display all event types with appropriate colors
- Add filtering controls (by type, level, component)
- Add search functionality
- Add "export logs" button
- Show event details on click
- Auto-scroll toggle

### Phase 4: Client-Side Logging
Add client-side event tracking:
- UI interactions (button clicks, form submissions)
- Character sheet operations
- WebSocket state changes
- API call timing

## Event Types & Colors

```javascript
const EVENT_COLORS = {
    // WebSocket Events
    'websocket_connected': '#00ff00',
    'websocket_disconnected': '#ff0000',
    'message_received': '#00ffff',
    'message_sent': '#00aaff',
    
    // Grok AI Events
    'grok_api_call_start': '#9d4edd',
    'grok_streaming_start': '#c77dff',
    'grok_tool_request': '#ff6b35',
    'grok_api_error': '#ff0000',
    
    // MCP/Tool Events
    'tool_execution_start': '#ffd60a',
    'tool_execution_complete': '#06ffa5',
    'mcp_operation_start': '#ffaa00',
    'mcp_operation_complete': '#00ff88',
    
    // Database Events
    'database_query': '#4cc9f0',
    'database_update': '#4895ef',
    'database_error': '#ff006e',
    
    // API Events
    'api_request': '#7209b7',
    'api_response': '#560bad',
    
    // UI Events
    'ui_interaction': '#06ffa5',
    'character_loaded': '#00ff88',
    'sheet_opened': '#00ffaa',
    
    // System Events
    'request_complete': '#06ffa5',
    'error_occurred': '#ff0000',
    'warning': '#ffaa00'
};
```

## Log Entry Format

```json
{
    "timestamp": "2025-10-30T00:00:00.000Z",
    "level": "INFO|ERROR|WARNING|DEBUG",
    "event": "event_type",
    "trace_id": "uuid",
    "component": "websocket|api|mcp|database|ui",
    "message": "Human-readable message",
    "data": {
        // Event-specific data
    }
}
```

## UI Mockup

```
┌─────────────────────────────────────────────────────────┐
│ Debug Window                                      [Clear]│
├─────────────────────────────────────────────────────────┤
│ Filters: [All] [Errors] [Warnings] [Info]              │
│ Search: [________________]  Auto-scroll: [✓]  [Export] │
├─────────────────────────────────────────────────────────┤
│ 00:00:01 | INFO    | [WS] Message received (45 chars)   │
│ 00:00:02 | INFO    | [GROK] API call started            │
│ 00:00:03 | INFO    | [GROK] Tool request: get_character │
│ 00:00:04 | INFO    | [MCP] Operation: get_character     │
│ 00:00:05 | INFO    | [DB] Query: SELECT * FROM chars... │
│ 00:00:06 | SUCCESS | [MCP] Complete (125ms)             │
│ 00:00:07 | SUCCESS | [GROK] Tool complete               │
│ 00:00:08 | INFO    | [WS] Response sent                 │
└─────────────────────────────────────────────────────────┘
```

## Benefits
1. **Complete visibility** into system operations
2. **Real-time debugging** without checking log files
3. **Performance monitoring** with timing data
4. **Error tracking** with full context
5. **User-friendly** color-coded display
6. **Searchable** and filterable logs
7. **Exportable** for bug reports

## Next Steps
1. Implement Phase 1 (enhanced telemetry)
2. Test with existing UI
3. Implement Phase 2 (log streaming)
4. Implement Phase 3 (enhanced UI)
5. Implement Phase 4 (client-side logging)
