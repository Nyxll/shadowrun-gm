"""
WebSocket Handler - Live Game Session Management
Handles WebSocket connections for real-time game sessions
"""

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)
trace_logger = logging.getLogger('trace')


def create_websocket_endpoint(app, session_manager, mcp_client, grok, get_mcp_tool_definitions, 
                              send_telemetry, send_mcp_telemetry, send_ui_telemetry, 
                              send_error_telemetry, convert_db_types, optimize_tool_result):
    """
    Create and register the WebSocket endpoint with the FastAPI app
    
    Args:
        app: FastAPI application instance
        session_manager: Session manager instance
        mcp_client: MCP client instance for tool routing
        grok: Grok API client
        get_mcp_tool_definitions: Function to get MCP tool definitions
        send_telemetry: Telemetry helper function
        send_mcp_telemetry: MCP telemetry helper function
        send_ui_telemetry: UI telemetry helper function
        send_error_telemetry: Error telemetry helper function
        convert_db_types: Database type conversion function
        optimize_tool_result: Tool result optimization function
    """
    
    @app.websocket("/game/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        """WebSocket endpoint for real-time game sessions"""
        await websocket.accept()
        
        # Get or create session
        session = session_manager.get_session(session_id)
        if not session:
            session = session_manager.create_session(session_id)
        
        session_manager.register_websocket(session_id, websocket)
        
        trace_logger.info(f"WebSocket connected: {session_id}")
        
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "content": f"Connected to session {session_id}"
        })
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                message_type = data.get('type')
                
                if message_type == 'chat':
                    # Handle chat message
                    message = data.get('message', '')
                    
                    if not message:
                        continue
                    
                    # Track request timing
                    request_start = datetime.now()
                    
                    # Send telemetry: message received
                    await websocket.send_json({
                        "type": "telemetry",
                        "event": "message_received",
                        "data": {"message_length": len(message)},
                        "timestamp": request_start.isoformat()
                    })
                    
                    # Add user message to history
                    session.add_message("user", message)
                    
                    # Log user query to database for learning
                    try:
                        import psycopg2
                        import os
                        from dotenv import load_dotenv
                        load_dotenv()
                        
                        conn = psycopg2.connect(
                            host=os.getenv('POSTGRES_HOST'),
                            port=os.getenv('POSTGRES_PORT'),
                            user=os.getenv('POSTGRES_USER'),
                            password=os.getenv('POSTGRES_PASSWORD'),
                            dbname=os.getenv('POSTGRES_DB')
                        )
                        cur = conn.cursor()
                        
                        # Log to query_logs table
                        cur.execute("""
                            INSERT INTO query_logs (
                                timestamp, query_text, session_id, 
                                intent, classification
                            ) VALUES (
                                NOW(), %s, %s, %s, %s
                            )
                        """, (
                            message,
                            session_id,
                            'websocket_chat',  # Intent
                            '{"source": "websocket", "model": "grok-4-fast-non-reasoning"}'  # Classification
                        ))
                        
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        trace_logger.info(f"Logged user query to database: {message[:50]}...")
                    except Exception as log_error:
                        trace_logger.error(f"Failed to log query to database: {str(log_error)}")
                    
                    # Prepare messages for Grok
                    messages = [
                        {"role": "system", "content": "You are a Shadowrun 2nd Edition GM assistant with access to character data and game mechanics."},
                        *[{"role": m["role"], "content": m["content"]} for m in session.conversation_history]
                    ]
                    
                    # Send telemetry: Grok API call start
                    grok_start = datetime.now()
                    await websocket.send_json({
                        "type": "telemetry",
                        "event": "grok_api_call_start",
                        "data": {"message_count": len(messages)},
                        "timestamp": grok_start.isoformat()
                    })
                    
                    # Call Grok with function calling (using fast non-reasoning model)
                    try:
                        response = await grok.chat.completions.create(
                            model="grok-4-fast-non-reasoning",
                            messages=messages,
                            tools=get_mcp_tool_definitions(),
                            tool_choice="auto",
                            stream=True
                        )
                        
                        # Send telemetry: streaming start
                        await websocket.send_json({
                            "type": "telemetry",
                            "event": "grok_streaming_start",
                            "data": {"model": "grok-4-fast-non-reasoning"},
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as grok_error:
                        # Send error to debug window
                        await websocket.send_json({
                            "type": "telemetry",
                            "event": "grok_api_error",
                            "data": {
                                "error": str(grok_error),
                                "model": "grok-4-fast-non-reasoning",
                                "error_type": type(grok_error).__name__
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                        trace_logger.error(f"Grok API error: {str(grok_error)}")
                        await websocket.send_json({
                            "type": "error",
                            "content": f"Grok API Error: {str(grok_error)}"
                        })
                        continue
                    
                    # Stream response
                    full_response = ""
                    tool_calls = []
                    
                    async for chunk in response:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            await websocket.send_json({
                                "type": "narrative",
                                "content": content
                            })
                        
                        if chunk.choices[0].delta.tool_calls:
                            tool_calls.extend(chunk.choices[0].delta.tool_calls)
                    
                    # Handle tool calls
                    if tool_calls:
                        # Send telemetry: tool request
                        await send_telemetry(websocket, "grok_tool_request", {
                            "tools_requested": [tc.function.name for tc in tool_calls],
                            "tool_count": len(tool_calls)
                        })
                        
                        # Collect tool results to send back to Grok
                        tool_messages = []
                        
                        for tool_call in tool_calls:
                            tool_name = tool_call.function.name
                            arguments = json.loads(tool_call.function.arguments)
                            
                            trace_logger.info(f"Tool call: {tool_name} with {arguments}")
                            
                            # Send MCP telemetry: operation start
                            tool_start = datetime.now()
                            await send_mcp_telemetry(websocket, tool_name, "start", {
                                "arguments": arguments
                            })
                            
                            # Send tool_call message for tracking
                            await websocket.send_json({
                                "type": "tool_call",
                                "tool": tool_name,
                                "arguments": arguments
                            })
                            
                            # Execute tool with error handling
                            try:
                                result = await mcp_client.call_tool(tool_name, arguments)
                                result = convert_db_types(result)
                                
                                # Optimize result for AI (remove audit fields, nulls) - saves ~50% tokens
                                optimized_result = optimize_tool_result(result)
                                
                                # Calculate tool execution time
                                tool_end = datetime.now()
                                tool_duration = (tool_end - tool_start).total_seconds() * 1000
                                
                                # Send MCP telemetry: operation complete
                                await send_mcp_telemetry(websocket, tool_name, "complete", {
                                    "duration_ms": round(tool_duration, 2),
                                    "success": True,
                                    "payload_reduction": f"{(1 - len(str(optimized_result)) / len(str(result))) * 100:.1f}%" if result else "0%"
                                })
                                
                                # Add tool result to messages for Grok
                                tool_messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_name,
                                    "content": json.dumps(optimized_result)
                                })
                                
                            except Exception as tool_error:
                                # Send error telemetry
                                await send_error_telemetry(websocket, tool_error, f"MCP tool execution: {tool_name}")
                                
                                # Calculate error time
                                tool_end = datetime.now()
                                tool_duration = (tool_end - tool_start).total_seconds() * 1000
                                
                                # Send failed operation telemetry
                                await send_mcp_telemetry(websocket, tool_name, "complete", {
                                    "duration_ms": round(tool_duration, 2),
                                    "success": False,
                                    "error": str(tool_error)
                                })
                                
                                # Add error result to messages for Grok
                                tool_messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_name,
                                    "content": json.dumps({"error": str(tool_error)})
                                })
                            
                            # Send optimized tool result to client (for display)
                            await websocket.send_json({
                                "type": "tool_result",
                                "tool": tool_name,
                                "result": optimized_result if 'optimized_result' in locals() else {"error": str(tool_error)}
                            })
                        
                        # CRITICAL: Send tool results back to Grok for final response
                        # Add assistant message with tool calls
                        messages.append({
                            "role": "assistant",
                            "content": full_response or None,
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                } for tc in tool_calls
                            ]
                        })
                        
                        # Add all tool results
                        messages.extend(tool_messages)
                        
                        # Send telemetry: Grok follow-up call
                        await websocket.send_json({
                            "type": "telemetry",
                            "event": "grok_followup_start",
                            "data": {"tool_results_count": len(tool_messages)},
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Call Grok again with tool results to get final response
                        try:
                            followup_response = await grok.chat.completions.create(
                                model="grok-4-fast-non-reasoning",
                                messages=messages,
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
                            
                        except Exception as followup_error:
                            trace_logger.error(f"Grok follow-up error: {str(followup_error)}")
                            await websocket.send_json({
                                "type": "error",
                                "content": f"Error getting final response: {str(followup_error)}"
                            })
                    
                    # Add assistant response to history
                    session.add_message("assistant", full_response)
                    
                    # Calculate total request time
                    request_end = datetime.now()
                    total_duration = (request_end - request_start).total_seconds() * 1000
                    
                    # Send telemetry: request complete
                    await websocket.send_json({
                        "type": "telemetry",
                        "event": "request_complete",
                        "data": {
                            "total_duration_ms": round(total_duration, 2),
                            "tool_calls": len(tool_calls),
                            "response_length": len(full_response)
                        },
                        "timestamp": request_end.isoformat()
                    })
                    
                    # Send complete message
                    await websocket.send_json({
                        "type": "complete",
                        "content": "Response complete"
                    })
                
                elif message_type == 'add_character':
                    # Add character to session
                    character_name = data.get('character')
                    session.add_character(character_name)
                    
                    # Send UI telemetry
                    await send_ui_telemetry(websocket, "character_added", "session-manager", {
                        "character": character_name,
                        "total_characters": len(session.active_characters)
                    })
                    
                    await websocket.send_json({
                        "type": "system",
                        "content": f"Added {character_name} to session"
                    })
                    await websocket.send_json({
                        "type": "session_info",
                        "characters": session.active_characters
                    })
                
                elif message_type == 'remove_character':
                    # Remove character from session
                    character_name = data.get('character')
                    if character_name in session.active_characters:
                        session.active_characters.remove(character_name)
                        
                        # Send UI telemetry
                        await send_ui_telemetry(websocket, "character_removed", "session-manager", {
                            "character": character_name,
                            "total_characters": len(session.active_characters)
                        })
                        
                        await websocket.send_json({
                            "type": "system",
                            "content": f"Removed {character_name} from session"
                        })
                        await websocket.send_json({
                            "type": "session_info",
                            "characters": session.active_characters
                        })
                
                elif message_type == 'get_session_info':
                    # Return session info
                    await websocket.send_json({
                        "type": "session_info",
                        "session_id": session_id,
                        "characters": session.active_characters,
                        "message_count": len(session.conversation_history)
                    })
                
        except WebSocketDisconnect:
            trace_logger.info(f"WebSocket disconnected: {session_id}")
            session_manager.unregister_websocket(session_id)
        except Exception as e:
            trace_logger.error(f"WebSocket error: {str(e)}")
            await websocket.close()
            session_manager.unregister_websocket(session_id)
    
    return websocket_endpoint
