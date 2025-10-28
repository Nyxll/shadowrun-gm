#!/usr/bin/env python3
"""
Test script to demonstrate what telemetry events should be sent
"""

# Example telemetry flow for: "cast increase attribute on platinum's charisma at max force"

telemetry_events = [
    {
        "type": "telemetry",
        "event": "message_received",
        "timestamp": "2025-10-25T14:30:00.000Z",
        "data": {
            "message": "cast increase attribute on platinum's charisma at max force",
            "session_id": "session_123",
            "message_length": 60
        }
    },
    {
        "type": "telemetry",
        "event": "grok_api_call_start",
        "timestamp": "2025-10-25T14:30:00.100Z",
        "data": {
            "model": "grok-4",
            "message_count": 3,
            "tools_available": 7,
            "streaming": True
        }
    },
    {
        "type": "telemetry",
        "event": "grok_streaming_start",
        "timestamp": "2025-10-25T14:30:01.250Z",
        "data": {
            "latency_ms": 1150,
            "first_token_received": True
        }
    },
    {
        "type": "telemetry",
        "event": "grok_content_chunk",
        "timestamp": "2025-10-25T14:30:01.300Z",
        "data": {
            "content": "I need to get Platinum's character data first...",
            "chunk_size": 48
        }
    },
    {
        "type": "telemetry",
        "event": "grok_tool_request",
        "timestamp": "2025-10-25T14:30:02.000Z",
        "data": {
            "tools_requested": ["get_character", "cast_spell"],
            "tool_count": 2,
            "reason": "Grok decided to call tools"
        }
    },
    {
        "type": "tool_call",
        "tool": "get_character",
        "arguments": {"character_name": "Platinum"}
    },
    {
        "type": "telemetry",
        "event": "tool_execution_start",
        "timestamp": "2025-10-25T14:30:02.050Z",
        "data": {
            "tool": "get_character",
            "arguments": {"character_name": "Platinum"}
        }
    },
    {
        "type": "telemetry",
        "event": "tool_execution_complete",
        "timestamp": "2025-10-25T14:30:02.100Z",
        "data": {
            "tool": "get_character",
            "duration_ms": 50,
            "success": True,
            "result_size": 1024
        }
    },
    {
        "type": "tool_result",
        "tool": "get_character",
        "result": {"name": "Platinum", "magic": 6, "...": "..."}
    },
    {
        "type": "telemetry",
        "event": "grok_api_call_start",
        "timestamp": "2025-10-25T14:30:02.150Z",
        "data": {
            "model": "grok-4",
            "message_count": 5,
            "reason": "Calling Grok with tool results",
            "tool_results_count": 2
        }
    },
    {
        "type": "telemetry",
        "event": "grok_final_response",
        "timestamp": "2025-10-25T14:30:03.000Z",
        "data": {
            "total_duration_ms": 2900,
            "tokens_used": 450,
            "response_complete": True
        }
    }
]

print("Expected telemetry flow:")
for i, event in enumerate(telemetry_events, 1):
    print(f"\n{i}. {event['event']}")
    if 'data' in event:
        for key, value in event['data'].items():
            print(f"   {key}: {value}")
