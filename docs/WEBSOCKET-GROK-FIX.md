# WebSocket & Logging Fixes - October 31, 2025

## Issues Fixed

### 1. Daily Log Rotation ✅
**Problem**: Logs were using `RotatingFileHandler` (size-based rotation) instead of daily rotation.

**Solution**: Changed to `TimedRotatingFileHandler` in `lib/server/logging_setup.py`:
- Rotates at midnight every day
- Keeps 30 days of logs
- Adds date suffix to rotated files (e.g., `shadowrun-gm.log.2025-10-30`)
- Applied to both main log and error log

**Configuration**:
```python
TimedRotatingFileHandler(
    LOG_DIR / 'shadowrun-gm.log',
    when='midnight',      # Rotate at midnight
    interval=1,           # Every 1 day
    backupCount=30,       # Keep 30 days of logs
    encoding='utf-8'
)
```

### 2. Grok Tool Response Flow ✅
**Problem**: After executing MCP tools, the websocket handler sent tool results to the client but **never sent them back to Grok** for a follow-up response. This caused incomplete conversations where Grok would request tools but never receive the results to formulate a final answer.

**Broken Flow**:
1. User asks question
2. Grok requests tools
3. Tools execute
4. ❌ Results sent to client only
5. ❌ Empty response added to history
6. ❌ "complete" sent without actual answer

**Fixed Flow**:
1. User asks question
2. Grok requests tools
3. Tools execute
4. ✅ Results collected in `tool_messages` array
5. ✅ Assistant message with tool_calls added to conversation
6. ✅ Tool results added to conversation
7. ✅ **Second Grok API call** with tool results
8. ✅ Grok streams final response using tool data
9. ✅ Complete answer added to history

**Key Changes in `lib/server/websocket_handler.py`**:

1. **Collect tool results**:
```python
tool_messages = []
for tool_call in tool_calls:
    # Execute tool...
    tool_messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_name,
        "content": json.dumps(optimized_result)
    })
```

2. **Build complete conversation**:
```python
# Add assistant message with tool calls
messages.append({
    "role": "assistant",
    "content": full_response or None,
    "tool_calls": [...]
})

# Add all tool results
messages.extend(tool_messages)
```

3. **Call Grok again for final response**:
```python
followup_response = await grok.chat.completions.create(
    model="grok-4-fast-non-reasoning",
    messages=messages,  # Now includes tool results!
    stream=True
)

# Stream the final response
full_response = ""
async for chunk in followup_response:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        full_response += content
        await websocket.send_json({
            "type": "narrative",
            "content": content
        })
```

## Testing

To test the fixes:

1. **Log Rotation**:
   - Check `logs/` directory after midnight
   - Should see dated log files: `shadowrun-gm.log.2025-10-30`
   - Current logs in `shadowrun-gm.log`

2. **Grok Tool Flow**:
   - Start game server: `python game-server.py`
   - Open game UI
   - Ask a question that requires character data (e.g., "What are Platinum's stats?")
   - Verify:
     - Tool calls execute (visible in debug window)
     - Grok receives tool results
     - Final response uses the tool data
     - Complete answer appears in chat

## Telemetry Events Added

New telemetry event for tracking the follow-up call:
- `grok_followup_start`: When sending tool results back to Grok
  - Includes `tool_results_count`

## Files Modified

1. `lib/server/logging_setup.py` - Daily log rotation
2. `lib/server/websocket_handler.py` - Grok tool response flow
3. `docs/WEBSOCKET-GROK-FIX.md` - This documentation

## Impact

- **Logging**: Cleaner log management with daily rotation and 30-day retention
- **Grok Integration**: Complete tool-calling workflow with proper responses
- **User Experience**: Grok can now actually use tool data to answer questions
- **Debugging**: Better telemetry for tracking the complete request flow
