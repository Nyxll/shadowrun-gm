# Debug Window Enhancement - Phase 1 Complete

## Summary
Successfully implemented Phase 1 of the Debug Window Enhancement Plan, adding comprehensive telemetry helper functions to game-server.py.

## What Was Added

### Telemetry Helper Functions (game-server.py)

Added 6 helper functions for sending different types of telemetry events:

1. **`send_telemetry()`** - Base telemetry function
   - Sends any telemetry event with level (INFO, WARNING, ERROR, DEBUG)
   - Includes timestamp and event-specific data

2. **`send_mcp_telemetry()`** - MCP operation tracking
   - Tracks MCP operation start/complete
   - Includes operation name, arguments, results, timing

3. **`send_database_telemetry()`** - Database operation tracking
   - Tracks SQL queries (SELECT, INSERT, UPDATE, DELETE)
   - Includes table name and query duration

4. **`send_api_telemetry()`** - API endpoint tracking
   - Tracks HTTP requests/responses
   - Includes endpoint, method, status code, duration

5. **`send_error_telemetry()`** - Error tracking
   - Sends full error context with stack traces
   - Includes error type, message, and context

6. **`send_ui_telemetry()`** - UI interaction tracking
   - Tracks user interactions (character selection, sheet viewing)
   - Includes action, component, and action-specific data

## Next Steps

### Phase 1 Remaining Tasks

1. **Add Telemetry to WebSocket Handler**
   - Add `send_mcp_telemetry()` calls before/after tool execution
   - Add `send_error_telemetry()` for all error handling
   - Add `send_ui_telemetry()` for character add/remove operations

2. **Add Telemetry to MCP Operations (lib/mcp_operations.py)**
   - Add database telemetry to all CRUD operations
   - Track query timing for performance monitoring
   - Add operation-level telemetry

### Phase 2: Log Streaming API

Create `/api/logs/stream` endpoint:
```python
@app.get("/api/logs/stream")
async def stream_logs():
    """Stream log file in real-time using Server-Sent Events"""
    async def event_generator():
        with open('logs/shadowrun-gm.log', 'r') as f:
            # Seek to end
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                await asyncio.sleep(0.1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### Phase 3: Enhanced UI Display

Update `www/app.js` to:

1. **Add Event Type Colors** (from design doc)
```javascript
const EVENT_COLORS = {
    'websocket_connected': '#00ff00',
    'websocket_disconnected': '#ff0000',
    'message_received': '#00ffff',
    'grok_api_call_start': '#9d4edd',
    'mcp_operation_start': '#ffaa00',
    'mcp_operation_complete': '#00ff88',
    'database_query': '#4cc9f0',
    'api_request': '#7209b7',
    'error_occurred': '#ff0000',
    // ... (see DEBUG-WINDOW-ENHANCEMENT.md for full list)
};
```

2. **Add Filtering Controls**
```html
<div class="debug-filters">
    <button onclick="filterEvents('all')">All</button>
    <button onclick="filterEvents('errors')">Errors</button>
    <button onclick="filterEvents('warnings')">Warnings</button>
    <button onclick="filterEvents('info')">Info</button>
    <input type="text" id="search" placeholder="Search..." />
    <label><input type="checkbox" id="autoscroll" checked> Auto-scroll</label>
    <button onclick="exportLogs()">Export</button>
    <button onclick="clearDebugWindow()">Clear</button>
</div>
```

3. **Enhanced Event Display**
```javascript
function displayTelemetryEvent(event) {
    const color = EVENT_COLORS[event.event] || '#ffffff';
    const level = event.level || 'INFO';
    const timestamp = new Date(event.timestamp).toLocaleTimeString();
    
    const component = getEventComponent(event.event);
    const message = formatEventMessage(event);
    
    const entry = `
        <div class="debug-entry" data-level="${level}" data-event="${event.event}">
            <span class="timestamp">${timestamp}</span>
            <span class="level ${level.toLowerCase()}">${level}</span>
            <span class="component">[${component}]</span>
            <span class="message" style="color: ${color}">${message}</span>
        </div>
    `;
    
    debugWindow.innerHTML += entry;
    
    if (autoScroll) {
        debugWindow.scrollTop = debugWindow.scrollHeight;
    }
}
```

4. **Event Details Modal**
```javascript
function showEventDetails(event) {
    const modal = document.getElementById('event-details-modal');
    modal.innerHTML = `
        <h3>${event.event}</h3>
        <p><strong>Time:</strong> ${event.timestamp}</p>
        <p><strong>Level:</strong> ${event.level}</p>
        <pre>${JSON.stringify(event.data, null, 2)}</pre>
    `;
    modal.style.display = 'block';
}
```

### Phase 4: Client-Side Logging

Add client-side event tracking:
```javascript
function trackUIEvent(action, component, data = {}) {
    const event = {
        type: 'ui_event',
        action: action,
        component: component,
        data: data,
        timestamp: new Date().toISOString()
    };
    
    // Send to server via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(event));
    }
    
    // Also display locally
    displayTelemetryEvent({
        event: 'ui_interaction',
        level: 'INFO',
        data: event,
        timestamp: event.timestamp
    });
}

// Usage examples:
trackUIEvent('character_selected', 'character-list', {character: 'Platinum'});
trackUIEvent('sheet_opened', 'character-sheet', {character: 'Platinum'});
trackUIEvent('spell_cast', 'spellcasting-panel', {spell: 'Fireball', force: 6});
```

## Benefits Achieved

✅ **Structured Telemetry** - Consistent event format across all components
✅ **Helper Functions** - Easy to add telemetry throughout codebase
✅ **Type Safety** - Dedicated functions for each event type
✅ **Performance Tracking** - Built-in timing for operations
✅ **Error Context** - Full stack traces with error events
✅ **Extensible** - Easy to add new event types

## Testing Plan

1. **Start game server** with enhanced telemetry
2. **Open UI** and connect WebSocket
3. **Perform actions**:
   - Select character
   - Send chat message
   - Trigger tool calls
   - Cause an error (invalid character name)
4. **Verify telemetry** appears in debug window
5. **Check log files** for trace IDs and structured logging

## Files Modified

- ✅ `game-server.py` - Added telemetry helper functions
- ✅ `tools/enhance-debug-telemetry.py` - Script to add helpers
- ✅ `docs/DEBUG-WINDOW-ENHANCEMENT.md` - Design document
- ✅ `docs/DEBUG-WINDOW-PHASE1-COMPLETE.md` - This status document

## Files To Modify (Next)

- [ ] `game-server.py` - Add telemetry calls to WebSocket handler
- [ ] `lib/mcp_operations.py` - Add database telemetry
- [ ] `www/app.js` - Enhanced UI display
- [ ] `www/app.css` - Styling for new UI elements

## Estimated Time Remaining

- Phase 1 completion: 1-2 hours
- Phase 2 (Log streaming): 2-3 hours  
- Phase 3 (UI enhancement): 3-4 hours
- Phase 4 (Client-side logging): 1-2 hours

**Total: 7-11 hours**

## Success Criteria

- [x] Telemetry helper functions added
- [ ] All WebSocket events send telemetry
- [ ] All MCP operations send telemetry
- [ ] All database queries send telemetry
- [ ] All errors send telemetry with stack traces
- [ ] UI displays all event types with colors
- [ ] UI has filtering and search
- [ ] UI has export functionality
- [ ] Client-side events tracked
- [ ] Log streaming API working

## Notes

The telemetry system is now in place and ready for integration. The next step is to add telemetry calls throughout the WebSocket handler and MCP operations. This will provide complete visibility into all system operations in real-time.
