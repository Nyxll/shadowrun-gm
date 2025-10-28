# Telemetry Requirements for Shadowrun GM

## Problem Statement

The current debug panel only shows MCP tool calls, but misses critical orchestrator activity:
- When Grok API is called
- What Grok is thinking/deciding  
- When Grok requests tools
- When calling Grok again with results
- Overall request flow timing

## Required Telemetry Events

### 1. Message Received
```json
{
  "type": "telemetry",
  "event": "message_received",
  "data": {
    "message": "user message text",
    "session_id": "session_123",
    "message_length": 60,
    "timestamp_ms": 1234567890
  }
}
```

### 2. Grok API Call Start (Initial)
```json
{
  "type": "telemetry",
  "event": "grok_api_call_start",
  "data": {
    "model": "grok-4",
    "message_count": 3,
    "tools_available": 7,
    "streaming": true,
    "call_number": 1,
    "reason": "Initial user request"
  }
}
```

### 3. Grok Streaming Start
```json
{
  "type": "telemetry",
  "event": "grok_streaming_start",
  "data": {
    "latency_ms": 1150,
    "first_token_received": true
  }
}
```

### 4. Grok Content Chunks (Optional - for debugging)
```json
{
  "type": "telemetry",
  "event": "grok_content_chunk",
  "data": {
    "content": "I need to get Platinum's character data...",
    "chunk_size": 48,
    "total_so_far": 150
  }
}
```

### 5. Grok Tool Request
```json
{
  "type": "telemetry",
  "event": "grok_tool_request",
  "data": {
    "tools_requested": ["get_character", "cast_spell"],
    "tool_count": 2,
    "reason": "Grok decided to call tools"
  }
}
```

### 6. Tool Execution Start
```json
{
  "type": "telemetry",
  "event": "tool_execution_start",
  "data": {
    "tool": "get_character",
    "arguments": {"character_name": "Platinum"},
    "timestamp_ms": 1234567890
  }
}
```

### 7. Tool Execution Complete
```json
{
  "type": "telemetry",
  "event": "tool_execution_complete",
  "data": {
    "tool": "get_character",
    "duration_ms": 50,
    "success": true,
    "result_size_bytes": 1024,
    "error": null
  }
}
```

### 8. Grok API Call Start (With Tool Results)
```json
{
  "type": "telemetry",
  "event": "grok_api_call_start",
  "data": {
    "model": "grok-4",
    "message_count": 5,
    "call_number": 2,
    "reason": "Calling Grok with tool results",
    "tool_results_count": 2
  }
}
```

### 9. Grok Final Response
```json
{
  "type": "telemetry",
  "event": "grok_final_response",
  "data": {
    "total_duration_ms": 2900,
    "response_complete": true,
    "had_tool_calls": true,
    "tool_call_count": 2
  }
}
```

### 10. Request Complete
```json
{
  "type": "telemetry",
  "event": "request_complete",
  "data": {
    "total_duration_ms": 3000,
    "grok_calls": 2,
    "tool_calls": 2,
    "success": true
  }
}
```

## Implementation Plan

### Server Changes (game-server.py)

1. **Add telemetry helper function**
```python
async def send_telemetry(websocket: WebSocket, event: str, data: Dict):
    """Send telemetry event to client"""
    await websocket.send_json({
        "type": "telemetry",
        "event": event,
        "timestamp": datetime.now().isoformat(),
        "data": data
    })
```

2. **Update process_with_grok function**
   - Add telemetry at start
   - Track Grok API call timing
   - Send events for streaming start
   - Track tool requests
   - Send events for second Grok call
   - Send final completion event

3. **Update game_websocket endpoint**
   - Send telemetry when message received
   - Track overall request timing

### Client Changes (www/app.js)

1. **Add telemetry log array**
```javascript
let telemetryLog = [];
```

2. **Handle telemetry messages**
```javascript
case 'telemetry':
    logTelemetry(data.event, data.data);
    break;
```

3. **Update debug panel**
   - Show telemetry events in chronological order
   - Color code by event type
   - Show timing information
   - Expandable details for each event

### UI Display

The debug panel should show something like:

```
Debug: Request Flow
