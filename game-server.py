#!/usr/bin/env python3
"""
Shadowrun GM - Live Game Server
FastAPI server with Grok AI + MCP tools integration
Clean refactored version using MCPOperations
"""

import os
import json
import uuid
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from contextvars import ContextVar
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Scope
import uvicorn
from openai import AsyncOpenAI
from decimal import Decimal

# Import our MCP operations layer
from lib.mcp_operations import MCPOperations
from lib.ai_payload_optimizer import optimize_tool_result

load_dotenv()

# Setup logging directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure structured logging with rotation
def setup_logging():
    """Setup structured logging with trace ID support"""
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | [Trace: %(trace_id)s] | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Main application log (with rotation)
    app_handler = RotatingFileHandler(
        LOG_DIR / 'shadowrun-gm.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    
    # Error log (with rotation)
    error_handler = RotatingFileHandler(
        LOG_DIR / 'shadowrun-gm-errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler (simpler format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Initialize logging
logger = setup_logging()

# Custom log adapter to include trace_id
class TraceIDLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that includes trace_id in log records"""
    
    def process(self, msg, kwargs):
        trace_id = trace_id_var.get(None) or 'no-trace'
        return msg, {**kwargs, 'extra': {'trace_id': trace_id}}

# Create trace-aware logger
trace_logger = TraceIDLoggerAdapter(logger, {})

# Context variable for trace ID (thread-safe)
trace_id_var: ContextVar[str] = ContextVar('trace_id', default=None)


# Custom JSON encoder for UUID and Decimal types
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle UUID and Decimal types"""
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def convert_db_types(obj):
    """Recursively convert UUID and Decimal types to JSON-serializable types"""
    if isinstance(obj, dict):
        return {k: convert_db_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_db_types(item) for item in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Middleware to handle trace ID for distributed tracing"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract trace ID from header or generate new one
        trace_id = request.headers.get('X-Trace-ID') or str(uuid.uuid4())
        
        # Set in context variable for use throughout request
        trace_id_var.set(trace_id)
        
        # Log request with trace ID using structured logger
        trace_logger.info(f"{request.method} {request.url.path}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log response status
            trace_logger.info(f"{request.method} {request.url.path} - {response.status_code}")
            
            # Add trace ID to response headers
            response.headers['X-Trace-ID'] = trace_id
            
            return response
            
        except Exception as e:
            # Log errors with trace ID
            trace_logger.error(f"{request.method} {request.url.path} - Error: {str(e)}")
            raise


# Initialize FastAPI
app = FastAPI(title="Shadowrun GM Server", version="2.0.0")

# Add trace ID middleware
app.add_middleware(TraceIDMiddleware)

# Initialize Grok client (uses OpenAI-compatible API)
grok = AsyncOpenAI(
    api_key=os.getenv('XAI_API_KEY'),
    base_url="https://api.x.ai/v1"
)


class GameSession:
    """Manages a single game session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict] = []
        self.active_characters: List[str] = []
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 20 messages to manage token usage
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def add_character(self, character_name: str):
        """Add character to active session"""
        if character_name not in self.active_characters:
            self.active_characters.append(character_name)


class SessionManager:
    """Manages all game sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.websockets: Dict[str, WebSocket] = {}
    
    def create_session(self, session_id: str) -> GameSession:
        """Create new game session"""
        session = GameSession(session_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def register_websocket(self, session_id: str, websocket: WebSocket):
        """Register websocket for session"""
        self.websockets[session_id] = websocket
    
    def unregister_websocket(self, session_id: str):
        """Unregister websocket"""
        if session_id in self.websockets:
            del self.websockets[session_id]


# Global session manager
session_manager = SessionManager()


class MCPClient:
    """
    Thin wrapper around MCPOperations for backward compatibility
    All actual logic is in lib/mcp_operations.py
    """
    
    def __init__(self):
        self.ops = MCPOperations()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        Delegate tool calls to MCPOperations
        This maintains the same interface as before but uses the clean CRUD API
        """
        
        if tool_name == "get_character_skill":
            return await self.ops.get_character_skill(
                arguments.get('character_name'),
                arguments.get('skill_name')
            )
        
        elif tool_name == "calculate_dice_pool":
            return await self.ops.calculate_dice_pool(
                arguments.get('skill_rating'),
                arguments.get('attribute_rating'),
                arguments.get('modifiers', [])
            )
        
        elif tool_name == "calculate_target_number":
            return await self.ops.calculate_target_number(
                arguments.get('situation'),
                arguments.get('difficulty', 'average')
            )
        
        elif tool_name == "roll_dice":
            return await self.ops.roll_dice(
                arguments.get('pool'),
                arguments.get('target_number')
            )
        
        elif tool_name == "get_character":
            return await self.ops.get_character(arguments.get('character_name'))
        
        elif tool_name == "calculate_ranged_attack":
            return await self.ops.calculate_ranged_attack(
                arguments.get('character_name'),
                arguments.get('weapon_name'),
                arguments.get('target_distance'),
                arguments.get('target_description'),
                arguments.get('environment'),
                arguments.get('combat_pool', 0)
            )
        
        elif tool_name == "cast_spell":
            return await self.ops.cast_spell(
                arguments.get('caster_name'),
                arguments.get('spell_name'),
                arguments.get('force'),
                arguments.get('target_name'),
                arguments.get('spell_pool_dice', 0),
                arguments.get('drain_pool_dice', 0)
            )
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


# Global MCP client
mcp_client = MCPClient()


class NoCacheStaticFiles(StaticFiles):
    """StaticFiles with cache-busting headers"""
    
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        
        # Add cache-busting headers for HTML, JS, CSS files
        if path.endswith(('.html', '.js', '.css')):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response


def get_mcp_tool_definitions() -> List[Dict]:
    """Get MCP tool definitions for Grok function calling"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_character_skill",
                "description": "Get a character's skill rating and associated attribute",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill (e.g., 'Street Etiquette', 'Firearms')"
                        }
                    },
                    "required": ["character_name", "skill_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_dice_pool",
                "description": "Calculate total dice pool from skill, attribute, and modifiers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_rating": {
                            "type": "integer",
                            "description": "Skill rating"
                        },
                        "attribute_rating": {
                            "type": "integer",
                            "description": "Attribute rating"
                        },
                        "modifiers": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of modifier values (e.g., [2, -1])"
                        }
                    },
                    "required": ["skill_rating", "attribute_rating"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_target_number",
                "description": "Calculate target number for a situation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": "Description of the situation"
                        },
                        "difficulty": {
                            "type": "string",
                            "enum": ["trivial", "easy", "average", "difficult", "very_difficult"],
                            "description": "Difficulty level"
                        }
                    },
                    "required": ["situation"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "roll_dice",
                "description": "Roll dice pool against target number (Shadowrun style with exploding 6s)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pool": {
                            "type": "integer",
                            "description": "Number of dice to roll"
                        },
                        "target_number": {
                            "type": "integer",
                            "description": "Target number for successes"
                        }
                    },
                    "required": ["pool", "target_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_character",
                "description": "Get full character data including attributes, skills, and gear",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_ranged_attack",
                "description": "Calculate complete ranged attack including all character cyberware/bioware modifiers, vision enhancements, smartlink bonuses, and roll dice",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character making the attack"
                        },
                        "weapon_name": {
                            "type": "string",
                            "description": "Name of the weapon being used"
                        },
                        "target_distance": {
                            "type": "integer",
                            "description": "Distance to target in meters"
                        },
                        "target_description": {
                            "type": "string",
                            "description": "Description of the target"
                        },
                        "environment": {
                            "type": "string",
                            "description": "Environmental conditions"
                        },
                        "combat_pool": {
                            "type": "integer",
                            "description": "Number of combat pool dice to use"
                        }
                    },
                    "required": ["character_name", "weapon_name", "target_distance", "target_description", "environment"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cast_spell",
                "description": "Cast a spell in Shadowrun 2nd Edition",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "caster_name": {
                            "type": "string",
                            "description": "Name of the character casting the spell"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell being cast"
                        },
                        "force": {
                            "type": "integer",
                            "description": "Force level to cast the spell at"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Name of the target (optional)"
                        },
                        "spell_pool_dice": {
                            "type": "integer",
                            "description": "Number of Magic Pool dice to add to spellcasting"
                        },
                        "drain_pool_dice": {
                            "type": "integer",
                            "description": "Number of Magic Pool dice to add to drain resistance"
                        }
                    },
                    "required": ["caster_name", "spell_name", "force"]
                }
            }
        }
    ]


# WebSocket endpoint for live game sessions
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
                    await websocket.send_json({
                        "type": "telemetry",
                        "event": "grok_tool_request",
                        "data": {
                            "tools_requested": [tc.function.name for tc in tool_calls],
                            "tool_count": len(tool_calls)
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        trace_logger.info(f"Tool call: {tool_name} with {arguments}")
                        
                        # Send telemetry: tool execution start
                        tool_start = datetime.now()
                        await websocket.send_json({
                            "type": "telemetry",
                            "event": "tool_execution_start",
                            "data": {"tool": tool_name, "arguments": arguments},
                            "timestamp": tool_start.isoformat()
                        })
                        
                        # Send tool_call message for tracking
                        await websocket.send_json({
                            "type": "tool_call",
                            "tool": tool_name,
                            "arguments": arguments
                        })
                        
                        # Execute tool
                        result = await mcp_client.call_tool(tool_name, arguments)
                        result = convert_db_types(result)
                        
                        # Optimize result for AI (remove audit fields, nulls) - saves ~50% tokens
                        optimized_result = optimize_tool_result(result)
                        
                        # Calculate tool execution time
                        tool_end = datetime.now()
                        tool_duration = (tool_end - tool_start).total_seconds() * 1000
                        
                        # Send telemetry: tool execution complete
                        await websocket.send_json({
                            "type": "telemetry",
                            "event": "tool_execution_complete",
                            "data": {
                                "tool": tool_name,
                                "duration_ms": round(tool_duration, 2),
                                "success": True,
                                "payload_reduction": f"{(1 - len(str(optimized_result)) / len(str(result))) * 100:.1f}%" if result else "0%"
                            },
                            "timestamp": tool_end.isoformat()
                        })
                        
                        # Send optimized tool result to client (for display)
                        await websocket.send_json({
                            "type": "tool_result",
                            "tool": tool_name,
                            "result": optimized_result
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


# HTTP endpoint to list all characters
@app.get("/api/characters")
async def list_characters_endpoint():
    """List all available characters"""
    try:
        # Use comprehensive_crud to get all characters
        from lib.comprehensive_crud import get_all_characters
        characters = await get_all_characters()
        
        # Optimize for UI (remove audit fields, nulls)
        optimized_characters = optimize_tool_result(characters)
        
        return JSONResponse(content={"characters": optimized_characters})
    except Exception as e:
        trace_logger.error(f"Error listing characters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# HTTP endpoint to get character data
@app.get("/api/character/{character_name}")
async def get_character_endpoint(character_name: str):
    """Get character data via HTTP"""
    try:
        result = await mcp_client.call_tool("get_character", {"character_name": character_name})
        result = convert_db_types(result)
        
        # Optimize for UI (remove audit fields, nulls)
        optimized_result = optimize_tool_result(result)
        
        return JSONResponse(content=optimized_result)
    except Exception as e:
        trace_logger.error(f"Error getting character: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# HTTP endpoint to list sessions
@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    sessions = []
    for session_id, session in session_manager.sessions.items():
        sessions.append({
            "session_id": session_id,
            "characters": session.active_characters,
            "message_count": len(session.conversation_history),
            "created_at": session.created_at.isoformat()
        })
    return {"sessions": sessions}


# HTTP endpoint to create session
@app.post("/api/sessions")
async def create_session(data: dict):
    """Create a new session"""
    session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
    session = session_manager.create_session(session_id)
    return {
        "session_id": session_id,
        "created_at": session.created_at.isoformat()
    }


# Serve static files with cache-busting
app.mount("/", NoCacheStaticFiles(directory="www", html=True), name="www")


if __name__ == "__main__":
    trace_logger.info("Starting Shadowrun GM Server v2.0.0")
    trace_logger.info("Using MCPOperations with comprehensive CRUD API")
    uvicorn.run(app, host="0.0.0.0", port=8001)
