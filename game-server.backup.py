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
    
    # Custom formatter that handles missing trace_id
    class TraceIDFormatter(logging.Formatter):
        def format(self, record):
            if not hasattr(record, 'trace_id'):
                record.trace_id = 'no-trace'
            return super().format(record)
    
    detailed_formatter = TraceIDFormatter(
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




async def send_telemetry(websocket: WebSocket, event: str, data: dict = None, level: str = "INFO"):
    """
    Helper function to send telemetry events to the UI
    
    Args:
        websocket: WebSocket connection
        event: Event type (e.g., 'database_query', 'mcp_operation_start')
        data: Event-specific data
        level: Log level (INFO, WARNING, ERROR, DEBUG)
    """
    await websocket.send_json({
        "type": "telemetry",
        "event": event,
        "level": level,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })


async def send_mcp_telemetry(websocket: WebSocket, operation: str, phase: str, data: dict = None):
    """
    Send MCP operation telemetry
    
    Args:
        operation: Operation name (e.g., 'get_character', 'cast_spell')
        phase: 'start' or 'complete'
        data: Operation-specific data (arguments, results, timing)
    """
    event = f"mcp_operation_{phase}"
    telemetry_data = {"operation": operation}
    if data:
        telemetry_data.update(data)
    
    await send_telemetry(websocket, event, telemetry_data)


async def send_database_telemetry(websocket: WebSocket, query_type: str, table: str = None, duration_ms: float = None):
    """
    Send database operation telemetry
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Query duration in milliseconds
    """
    data = {"query_type": query_type}
    if table:
        data["table"] = table
    if duration_ms is not None:
        data["duration_ms"] = round(duration_ms, 2)
    
    await send_telemetry(websocket, "database_query", data)


async def send_api_telemetry(websocket: WebSocket, endpoint: str, method: str, status_code: int = None, duration_ms: float = None):
    """
    Send API operation telemetry
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    data = {
        "endpoint": endpoint,
        "method": method
    }
    if status_code:
        data["status_code"] = status_code
    if duration_ms is not None:
        data["duration_ms"] = round(duration_ms, 2)
    
    event = "api_request" if status_code is None else "api_response"
    await send_telemetry(websocket, event, data)


async def send_error_telemetry(websocket: WebSocket, error: Exception, context: str = None):
    """
    Send error telemetry with full context
    
    Args:
        error: Exception object
        context: Additional context about where the error occurred
    """
    import traceback
    
    data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc()
    }
    if context:
        data["context"] = context
    
    await send_telemetry(websocket, "error_occurred", data, level="ERROR")


async def send_ui_telemetry(websocket: WebSocket, action: str, component: str = None, data: dict = None):
    """
    Send UI interaction telemetry
    
    Args:
        action: UI action (e.g., 'character_selected', 'sheet_opened')
        component: UI component name
        data: Action-specific data
    """
    telemetry_data = {"action": action}
    if component:
        telemetry_data["component"] = component
    if data:
        telemetry_data.update(data)
    
    await send_telemetry(websocket, "ui_interaction", telemetry_data)


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
        
        elif tool_name == "add_karma":
            return await self.ops.add_karma(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "spend_karma":
            return await self.ops.spend_karma(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_karma_pool":
            return await self.ops.update_karma_pool(
                arguments.get('character_name'),
                arguments.get('new_pool'),
                arguments.get('reason')
            )
        
        elif tool_name == "set_karma":
            return await self.ops.set_karma(
                arguments.get('character_name'),
                arguments.get('total'),
                arguments.get('available'),
                arguments.get('reason')
            )
        
        elif tool_name == "add_nuyen":
            return await self.ops.add_nuyen(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "spend_nuyen":
            return await self.ops.spend_nuyen(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_skills":
            return await self.ops.get_skills(arguments.get('character_name'))
        
        elif tool_name == "add_skill":
            return await self.ops.add_skill(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('base_rating'),
                arguments.get('specialization'),
                arguments.get('skill_type'),
                arguments.get('reason')
            )
        
        elif tool_name == "improve_skill":
            return await self.ops.improve_skill(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('new_rating'),
                arguments.get('reason')
            )
        
        elif tool_name == "add_specialization":
            return await self.ops.add_specialization(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('specialization'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_skill":
            return await self.ops.remove_skill(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_spells":
            return await self.ops.get_spells(arguments.get('character_name'))
        
        elif tool_name == "add_spell":
            return await self.ops.add_spell(
                arguments.get('character_name'),
                arguments.get('spell_name'),
                arguments.get('learned_force'),
                arguments.get('spell_category'),
                arguments.get('spell_type', 'mana'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_spell":
            return await self.ops.update_spell(
                arguments.get('character_name'),
                arguments.get('spell_name'),
                arguments.get('learned_force'),
                arguments.get('spell_category'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_spell":
            return await self.ops.remove_spell(
                arguments.get('character_name'),
                arguments.get('spell_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_gear":
            return await self.ops.get_gear(
                arguments.get('character_name'),
                arguments.get('gear_type')
            )
        
        elif tool_name == "add_gear":
            return await self.ops.add_gear(
                arguments.get('character_name'),
                arguments.get('gear_name'),
                arguments.get('gear_type', 'equipment'),
                arguments.get('quantity', 1),
                arguments.get('reason')
            )
        
        elif tool_name == "update_gear_quantity":
            return await self.ops.update_gear_quantity(
                arguments.get('character_name'),
                arguments.get('gear_name'),
                arguments.get('quantity'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_gear":
            return await self.ops.remove_gear(
                arguments.get('character_name'),
                arguments.get('gear_name'),
                arguments.get('reason')
            )
        
        # ========== PHASE 2: AUGMENTATIONS & EQUIPMENT ==========
        
        elif tool_name == "get_cyberware":
            return await self.ops.get_cyberware(arguments.get('character_name'))
        
        elif tool_name == "get_bioware":
            return await self.ops.get_bioware(arguments.get('character_name'))
        
        elif tool_name == "add_cyberware":
            return await self.ops.add_cyberware(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('essence_cost', 0),
                arguments.get('target_name'),
                arguments.get('modifier_value', 0),
                arguments.get('modifier_data'),
                arguments.get('reason')
            )
        
        elif tool_name == "add_bioware":
            return await self.ops.add_bioware(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('essence_cost', 0),
                arguments.get('target_name'),
                arguments.get('modifier_value', 0),
                arguments.get('modifier_data'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_cyberware":
            return await self.ops.update_cyberware(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_cyberware":
            return await self.ops.remove_cyberware(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_bioware":
            return await self.ops.remove_bioware(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_vehicles":
            return await self.ops.get_vehicles(arguments.get('character_name'))
        
        elif tool_name == "add_vehicle":
            return await self.ops.add_vehicle(
                arguments.get('character_name'),
                arguments.get('vehicle_name'),
                arguments.get('vehicle_type'),
                arguments.get('handling'),
                arguments.get('speed'),
                arguments.get('body'),
                arguments.get('armor'),
                arguments.get('signature'),
                arguments.get('pilot'),
                arguments.get('modifications'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_vehicle":
            return await self.ops.update_vehicle(
                arguments.get('character_name'),
                arguments.get('vehicle_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_vehicle":
            return await self.ops.remove_vehicle(
                arguments.get('character_name'),
                arguments.get('vehicle_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_cyberdecks":
            return await self.ops.get_cyberdecks(arguments.get('character_name'))
        
        elif tool_name == "add_cyberdeck":
            return await self.ops.add_cyberdeck(
                arguments.get('character_name'),
                arguments.get('deck_name'),
                arguments.get('mpcp'),
                arguments.get('hardening'),
                arguments.get('memory'),
                arguments.get('storage'),
                arguments.get('io_speed'),
                arguments.get('response_increase'),
                arguments.get('persona_programs'),
                arguments.get('utilities'),
                arguments.get('ai_companions'),
                arguments.get('reason')
            )
        
        # ========== PHASE 3: SOCIAL & MAGICAL ==========
        
        elif tool_name == "get_contacts":
            return await self.ops.get_contacts(arguments.get('character_name'))
        
        elif tool_name == "add_contact":
            return await self.ops.add_contact(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('archetype'),
                arguments.get('loyalty', 1),
                arguments.get('connection', 1),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_contact_loyalty":
            return await self.ops.update_contact_loyalty(
                arguments.get('character_name'),
                arguments.get('contact_name'),
                arguments.get('loyalty'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_spirits":
            return await self.ops.get_spirits(arguments.get('character_name'))
        
        elif tool_name == "add_spirit":
            return await self.ops.add_spirit(
                arguments.get('character_name'),
                arguments.get('spirit_name'),
                arguments.get('spirit_type'),
                arguments.get('force', 1),
                arguments.get('services', 1),
                arguments.get('special_abilities'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_spirit_services":
            return await self.ops.update_spirit_services(
                arguments.get('character_name'),
                arguments.get('spirit_name'),
                arguments.get('services'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_foci":
            return await self.ops.get_foci(arguments.get('character_name'))
        
        elif tool_name == "add_focus":
            return await self.ops.add_focus(
                arguments.get('character_name'),
                arguments.get('focus_name'),
                arguments.get('focus_type'),
                arguments.get('force'),
                arguments.get('spell_category'),
                arguments.get('specific_spell'),
                arguments.get('bonus_dice', 0),
                arguments.get('tn_modifier', 0),
                arguments.get('bonded', True),
                arguments.get('karma_cost'),
                arguments.get('description'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_powers":
            return await self.ops.get_powers(arguments.get('character_name'))
        
        elif tool_name == "add_power":
            return await self.ops.add_power(
                arguments.get('character_name'),
                arguments.get('power_name'),
                arguments.get('level', 1),
                arguments.get('cost', 0),
                arguments.get('reason')
            )
        
        elif tool_name == "update_power_level":
            return await self.ops.update_power_level(
                arguments.get('character_name'),
                arguments.get('power_name'),
                arguments.get('new_level'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_edges_flaws":
            return await self.ops.get_edges_flaws(arguments.get('character_name'))
        
        elif tool_name == "add_edge_flaw":
            return await self.ops.add_edge_flaw(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('type'),
                arguments.get('description'),
                arguments.get('cost'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_relationships":
            return await self.ops.get_relationships(arguments.get('character_name'))
        
        elif tool_name == "add_relationship":
            return await self.ops.add_relationship(
                arguments.get('character_name'),
                arguments.get('relationship_type'),
                arguments.get('relationship_name'),
                arguments.get('data'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        # ========== PHASE 4: GAME STATE MANAGEMENT ==========
        
        elif tool_name == "get_active_effects":
            return await self.ops.get_active_effects(arguments.get('character_name'))
        
        elif tool_name == "add_active_effect":
            return await self.ops.add_active_effect(
                arguments.get('character_name'),
                arguments.get('effect_name'),
                arguments.get('effect_type'),
                arguments.get('duration'),
                arguments.get('modifier_value'),
                arguments.get('target_attribute'),
                arguments.get('description'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_effect_duration":
            return await self.ops.update_effect_duration(
                arguments.get('character_name'),
                arguments.get('effect_name'),
                arguments.get('new_duration'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_active_effect":
            return await self.ops.remove_active_effect(
                arguments.get('character_name'),
                arguments.get('effect_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_modifiers":
            return await self.ops.get_modifiers(
                arguments.get('character_name'),
                arguments.get('modifier_type')
            )
        
        elif tool_name == "add_modifier":
            return await self.ops.add_modifier(
                arguments.get('character_name'),
                arguments.get('modifier_name'),
                arguments.get('modifier_type'),
                arguments.get('target_name'),
                arguments.get('modifier_value', 0),
                arguments.get('modifier_data'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_modifier":
            return await self.ops.update_modifier(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_modifier":
            return await self.ops.remove_modifier(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('reason')
            )
        
        # ========== PHASE 5: CAMPAIGN MANAGEMENT ==========
        
        elif tool_name == "get_house_rules":
            return await self.ops.get_house_rules()
        
        elif tool_name == "add_house_rule":
            return await self.ops.add_house_rule(
                arguments.get('rule_name'),
                arguments.get('rule_type'),
                arguments.get('description'),
                arguments.get('mechanical_effect'),
                arguments.get('is_active', True),
                arguments.get('reason')
            )
        
        elif tool_name == "toggle_house_rule":
            return await self.ops.toggle_house_rule(
                arguments.get('rule_name'),
                arguments.get('is_active'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_campaign_npcs":
            return await self.ops.get_campaign_npcs()
        
        elif tool_name == "add_campaign_npc":
            return await self.ops.add_campaign_npc(
                arguments.get('npc_name'),
                arguments.get('npc_type'),
                arguments.get('role'),
                arguments.get('stats'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_campaign_npc":
            return await self.ops.update_campaign_npc(
                arguments.get('npc_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_audit_log":
            return await self.ops.get_audit_log(
                arguments.get('character_name'),
                arguments.get('limit', 100)
            )
        
        # ========== PHASE 6: CHARACTER MANAGEMENT ==========
        
        elif tool_name == "create_character":
            return await self.ops.create_character(
                arguments.get('street_name'),
                arguments.get('given_name'),
                arguments.get('archetype'),
                arguments.get('metatype', 'Human'),
                arguments.get('attributes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_character_info":
            return await self.ops.update_character_info(
                arguments.get('character_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "delete_character":
            return await self.ops.delete_character(
                arguments.get('character_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_attribute":
            return await self.ops.update_attribute(
                arguments.get('character_name'),
                arguments.get('attribute_name'),
                arguments.get('new_value'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_derived_stats":
            return await self.ops.update_derived_stats(
                arguments.get('character_name'),
                arguments.get('updates'),
                arguments.get('reason')
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
        },
        {
            "type": "function",
            "function": {
                "name": "add_karma",
                "description": "Add karma to a character's total and available pool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of karma to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for karma award (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spend_karma",
                "description": "Spend karma from a character's available pool (with validation)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of karma to spend"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for karma expenditure (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_karma_pool",
                "description": "Update a character's karma pool (for in-game spending)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "new_pool": {
                            "type": "integer",
                            "description": "New karma pool value"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for change (optional)"
                        }
                    },
                    "required": ["character_name", "new_pool"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_karma",
                "description": "Set both total and available karma (for error correction)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "total": {
                            "type": "integer",
                            "description": "Total karma earned"
                        },
                        "available": {
                            "type": "integer",
                            "description": "Available karma to spend"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for correction (optional)"
                        }
                    },
                    "required": ["character_name", "total", "available"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_nuyen",
                "description": "Add nuyen to a character's account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of nuyen to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for payment (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spend_nuyen",
                "description": "Spend nuyen from a character's account (with validation)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of nuyen to spend"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for expenditure (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_skills",
                "description": "Get all skills for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_skill",
                "description": "Add a new skill to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to add"
                        },
                        "base_rating": {
                            "type": "integer",
                            "description": "Base rating for the skill (1-10)"
                        },
                        "specialization": {
                            "type": "string",
                            "description": "Optional specialization"
                        },
                        "skill_type": {
                            "type": "string",
                            "description": "Type of skill (e.g., 'active', 'knowledge')"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding the skill"
                        }
                    },
                    "required": ["character_name", "skill_name", "base_rating"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "improve_skill",
                "description": "Improve a character's skill rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to improve"
                        },
                        "new_rating": {
                            "type": "integer",
                            "description": "New rating for the skill"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for improvement"
                        }
                    },
                    "required": ["character_name", "skill_name", "new_rating"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_specialization",
                "description": "Add a specialization to a character's skill",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill"
                        },
                        "specialization": {
                            "type": "string",
                            "description": "Specialization to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding specialization"
                        }
                    },
                    "required": ["character_name", "skill_name", "specialization"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_skill",
                "description": "Remove a skill from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "skill_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_spells",
                "description": "Get all spells for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_spell",
                "description": "Add a new spell to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell"
                        },
                        "learned_force": {
                            "type": "integer",
                            "description": "Force at which the spell was learned"
                        },
                        "spell_category": {
                            "type": "string",
                            "description": "Category of spell (e.g., 'Combat', 'Detection')"
                        },
                        "spell_type": {
                            "type": "string",
                            "description": "Type of spell ('mana' or 'physical')"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding spell"
                        }
                    },
                    "required": ["character_name", "spell_name", "learned_force"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_spell",
                "description": "Update spell details for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell to update"
                        },
                        "learned_force": {
                            "type": "integer",
                            "description": "New learned force"
                        },
                        "spell_category": {
                            "type": "string",
                            "description": "New spell category"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "spell_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_spell",
                "description": "Remove a spell from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "spell_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_gear",
                "description": "Get gear for a character, optionally filtered by type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_type": {
                            "type": "string",
                            "description": "Optional gear type filter (e.g., 'weapon', 'armor')"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_gear",
                "description": "Add gear to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_name": {
                            "type": "string",
                            "description": "Name of the gear"
                        },
                        "gear_type": {
                            "type": "string",
                            "description": "Type of gear"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding gear"
                        }
                    },
                    "required": ["character_name", "gear_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_gear_quantity",
                "description": "Update the quantity of a gear item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_name": {
                            "type": "string",
                            "description": "Name of the gear"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "New quantity"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "gear_name", "quantity"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_gear",
                "description": "Remove gear from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_name": {
                            "type": "string",
                            "description": "Name of the gear to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "gear_name"]
                }
            }
        },
        # ========== PHASE 2: AUGMENTATIONS & EQUIPMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_cyberware",
                "description": "Get all cyberware for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_bioware",
                "description": "Get all bioware for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_cyberware",
                "description": "Add cyberware to a character with essence cost and modifiers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the cyberware"
                        },
                        "essence_cost": {
                            "type": "number",
                            "description": "Essence cost of the cyberware"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Attribute or skill this modifies (optional)"
                        },
                        "modifier_value": {
                            "type": "integer",
                            "description": "Modifier value (e.g., +2 for skill bonus)"
                        },
                        "modifier_data": {
                            "type": "object",
                            "description": "Additional modifier data (special abilities, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding cyberware"
                        }
                    },
                    "required": ["character_name", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_bioware",
                "description": "Add bioware to a character with essence cost and modifiers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the bioware"
                        },
                        "essence_cost": {
                            "type": "number",
                            "description": "Essence cost of the bioware"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Attribute or skill this modifies (optional)"
                        },
                        "modifier_value": {
                            "type": "integer",
                            "description": "Modifier value (e.g., +1 for attribute bonus)"
                        },
                        "modifier_data": {
                            "type": "object",
                            "description": "Additional modifier data"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding bioware"
                        }
                    },
                    "required": ["character_name", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_cyberware",
                "description": "Update cyberware properties",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the cyberware modifier"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (essence_cost, modifier_value, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "modifier_id", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_cyberware",
                "description": "Remove cyberware from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the cyberware modifier to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "modifier_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_bioware",
                "description": "Remove bioware from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the bioware modifier to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "modifier_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_vehicles",
                "description": "Get all vehicles owned by a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_vehicle",
                "description": "Add a vehicle to a character's inventory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "vehicle_name": {
                            "type": "string",
                            "description": "Name of the vehicle"
                        },
                        "vehicle_type": {
                            "type": "string",
                            "description": "Type of vehicle (car, bike, drone, etc.)"
                        },
                        "handling": {
                            "type": "integer",
                            "description": "Handling rating"
                        },
                        "speed": {
                            "type": "integer",
                            "description": "Speed rating"
                        },
                        "body": {
                            "type": "integer",
                            "description": "Body rating"
                        },
                        "armor": {
                            "type": "integer",
                            "description": "Armor rating"
                        },
                        "signature": {
                            "type": "integer",
                            "description": "Signature rating"
                        },
                        "pilot": {
                            "type": "integer",
                            "description": "Pilot rating (for drones)"
                        },
                        "modifications": {
                            "type": "object",
                            "description": "Vehicle modifications"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding vehicle"
                        }
                    },
                    "required": ["character_name", "vehicle_name", "vehicle_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_vehicle",
                "description": "Update vehicle properties",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "vehicle_name": {
                            "type": "string",
                            "description": "Name of the vehicle to update"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (handling, speed, armor, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "vehicle_name", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_vehicle",
                "description": "Remove a vehicle from a character's inventory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "vehicle_name": {
                            "type": "string",
                            "description": "Name of the vehicle to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "vehicle_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_cyberdecks",
                "description": "Get all cyberdecks owned by a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_cyberdeck",
                "description": "Add a cyberdeck to a character with full stats",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "deck_name": {
                            "type": "string",
                            "description": "Name of the cyberdeck"
                        },
                        "mpcp": {
                            "type": "integer",
                            "description": "MPCP rating"
                        },
                        "hardening": {
                            "type": "integer",
                            "description": "Hardening rating"
                        },
                        "memory": {
                            "type": "integer",
                            "description": "Memory in MP"
                        },
                        "storage": {
                            "type": "integer",
                            "description": "Storage in MP"
                        },
                        "io_speed": {
                            "type": "integer",
                            "description": "I/O speed"
                        },
                        "response_increase": {
                            "type": "integer",
                            "description": "Response increase"
                        },
                        "persona_programs": {
                            "type": "array",
                            "description": "List of persona programs"
                        },
                        "utilities": {
                            "type": "array",
                            "description": "List of utility programs"
                        },
                        "ai_companions": {
                            "type": "array",
                            "description": "List of AI companions"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding cyberdeck"
                        }
                    },
                    "required": ["character_name", "deck_name"]
                }
            }
        },
        # ========== PHASE 3: SOCIAL & MAGICAL ==========
        {
            "type": "function",
            "function": {
                "name": "get_contacts",
                "description": "Get all contacts for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_contact",
                "description": "Add a contact to a character's network",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the contact"
                        },
                        "archetype": {
                            "type": "string",
                            "description": "Contact's archetype/profession"
                        },
                        "loyalty": {
                            "type": "integer",
                            "description": "Loyalty rating (1-6)"
                        },
                        "connection": {
                            "type": "integer",
                            "description": "Connection rating (1-6)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the contact"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding contact"
                        }
                    },
                    "required": ["character_name", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_contact_loyalty",
                "description": "Update a contact's loyalty rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "contact_name": {
                            "type": "string",
                            "description": "Name of the contact"
                        },
                        "loyalty": {
                            "type": "integer",
                            "description": "New loyalty rating (1-6)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for loyalty change"
                        }
                    },
                    "required": ["character_name", "contact_name", "loyalty"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_spirits",
                "description": "Get all spirits bound to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_spirit",
                "description": "Add a bound spirit to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spirit_name": {
                            "type": "string",
                            "description": "Name of the spirit"
                        },
                        "spirit_type": {
                            "type": "string",
                            "description": "Type of spirit (e.g., 'City', 'Nature', 'Elemental')"
                        },
                        "force": {
                            "type": "integer",
                            "description": "Force rating of the spirit"
                        },
                        "services": {
                            "type": "integer",
                            "description": "Number of services owed"
                        },
                        "special_abilities": {
                            "type": "array",
                            "description": "List of special abilities"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the spirit"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding spirit"
                        }
                    },
                    "required": ["character_name", "spirit_name", "spirit_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_spirit_services",
                "description": "Update the number of services a spirit owes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spirit_name": {
                            "type": "string",
                            "description": "Name of the spirit"
                        },
                        "services": {
                            "type": "integer",
                            "description": "New number of services"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "spirit_name", "services"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_foci",
                "description": "Get all magical foci owned by a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_focus",
                "description": "Add a magical focus to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "focus_name": {
                            "type": "string",
                            "description": "Name of the focus"
                        },
                        "focus_type": {
                            "type": "string",
                            "description": "Type of focus (e.g., 'Spell', 'Power', 'Weapon')"
                        },
                        "force": {
                            "type": "integer",
                            "description": "Force rating of the focus"
                        },
                        "spell_category": {
                            "type": "string",
                            "description": "Spell category if spell focus"
                        },
                        "specific_spell": {
                            "type": "string",
                            "description": "Specific spell if spell focus"
                        },
                        "bonus_dice": {
                            "type": "integer",
                            "description": "Bonus dice provided"
                        },
                        "tn_modifier": {
                            "type": "integer",
                            "description": "Target number modifier"
                        },
                        "bonded": {
                            "type": "boolean",
                            "description": "Whether the focus is bonded"
                        },
                        "karma_cost": {
                            "type": "integer",
                            "description": "Karma cost to bond"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the focus"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding focus"
                        }
                    },
                    "required": ["character_name", "focus_name", "focus_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_powers",
                "description": "Get all adept powers for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_power",
                "description": "Add an adept power to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "power_name": {
                            "type": "string",
                            "description": "Name of the power"
                        },
                        "level": {
                            "type": "integer",
                            "description": "Level of the power"
                        },
                        "cost": {
                            "type": "number",
                            "description": "Power point cost"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding power"
                        }
                    },
                    "required": ["character_name", "power_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_power_level",
                "description": "Update the level of an adept power",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "power_name": {
                            "type": "string",
                            "description": "Name of the power"
                        },
                        "new_level": {
                            "type": "integer",
                            "description": "New level for the power"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for level change"
                        }
                    },
                    "required": ["character_name", "power_name", "new_level"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_edges_flaws",
                "description": "Get all edges and flaws for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_edge_flaw",
                "description": "Add an edge or flaw to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the edge or flaw"
                        },
                        "type": {
                            "type": "string",
                            "description": "Type: 'edge' or 'flaw'"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the edge/flaw"
                        },
                        "cost": {
                            "type": "integer",
                            "description": "Point cost (positive for edges, negative for flaws)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding"
                        }
                    },
                    "required": ["character_name", "name", "type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_relationships",
                "description": "Get all relationships for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_relationship",
                "description": "Add a relationship to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "relationship_type": {
                            "type": "string",
                            "description": "Type of relationship (e.g., 'ally', 'enemy', 'family')"
                        },
                        "relationship_name": {
                            "type": "string",
                            "description": "Name of the related person/entity"
                        },
                        "data": {
                            "type": "object",
                            "description": "Additional relationship data"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the relationship"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding relationship"
                        }
                    },
                    "required": ["character_name", "relationship_type", "relationship_name"]
                }
            }
        },
        # ========== PHASE 4: GAME STATE MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_active_effects",
                "description": "Get all active effects on a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"}
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_active_effect",
                "description": "Add an active effect to a character (buffs, debuffs, conditions)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "effect_name": {"type": "string", "description": "Name of the effect"},
                        "effect_type": {"type": "string", "description": "Type of effect"},
                        "duration": {"type": "integer", "description": "Duration in turns/minutes"},
                        "modifier_value": {"type": "integer", "description": "Modifier value"},
                        "target_attribute": {"type": "string", "description": "Attribute affected"},
                        "description": {"type": "string", "description": "Effect description"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["character_name", "effect_name", "effect_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_effect_duration",
                "description": "Update the duration of an active effect",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "effect_name": {"type": "string", "description": "Name of the effect"},
                        "new_duration": {"type": "integer", "description": "New duration value"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "effect_name", "new_duration"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_active_effect",
                "description": "Remove an active effect from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "effect_name": {"type": "string", "description": "Name of the effect to remove"},
                        "reason": {"type": "string", "description": "Reason for removal"}
                    },
                    "required": ["character_name", "effect_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_modifiers",
                "description": "Get all modifiers for a character, optionally filtered by type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_type": {"type": "string", "description": "Optional filter by type"}
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_modifier",
                "description": "Add a generic modifier to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_name": {"type": "string", "description": "Name of the modifier"},
                        "modifier_type": {"type": "string", "description": "Type of modifier"},
                        "target_name": {"type": "string", "description": "What this modifies"},
                        "modifier_value": {"type": "integer", "description": "Modifier value"},
                        "modifier_data": {"type": "object", "description": "Additional data"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["character_name", "modifier_name", "modifier_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_modifier",
                "description": "Update a modifier's properties",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_id": {"type": "string", "description": "UUID of the modifier"},
                        "updates": {"type": "object", "description": "Fields to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "modifier_id", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_modifier",
                "description": "Remove a modifier from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_id": {"type": "string", "description": "UUID of the modifier to remove"},
                        "reason": {"type": "string", "description": "Reason for removal"}
                    },
                    "required": ["character_name", "modifier_id"]
                }
            }
        },
        # ========== PHASE 5: CAMPAIGN MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_house_rules",
                "description": "Get all house rules for the campaign",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_house_rule",
                "description": "Add a house rule to the campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule_name": {"type": "string", "description": "Name of the house rule"},
                        "rule_type": {"type": "string", "description": "Type of rule"},
                        "description": {"type": "string", "description": "Description of the rule"},
                        "mechanical_effect": {"type": "string", "description": "Mechanical effect"},
                        "is_active": {"type": "boolean", "description": "Whether active"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["rule_name", "rule_type", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "toggle_house_rule",
                "description": "Toggle a house rule on or off",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule_name": {"type": "string", "description": "Name of the house rule"},
                        "is_active": {"type": "boolean", "description": "New active status"},
                        "reason": {"type": "string", "description": "Reason for toggle"}
                    },
                    "required": ["rule_name", "is_active"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_campaign_npcs",
                "description": "Get all campaign NPCs",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_campaign_npc",
                "description": "Add an NPC to the campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "npc_name": {"type": "string", "description": "Name of the NPC"},
                        "npc_type": {"type": "string", "description": "Type of NPC"},
                        "role": {"type": "string", "description": "Role in campaign"},
                        "stats": {"type": "object", "description": "NPC stats"},
                        "notes": {"type": "string", "description": "Notes about NPC"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["npc_name", "npc_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_campaign_npc",
                "description": "Update campaign NPC information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "npc_name": {"type": "string", "description": "Name of the NPC"},
                        "updates": {"type": "object", "description": "Fields to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["npc_name", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_audit_log",
                "description": "Get audit log entries for a character or campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character name (optional)"},
                        "limit": {"type": "integer", "description": "Max entries to return"}
                    },
                    "required": []
                }
            }
        },
        # ========== PHASE 6: CHARACTER MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "create_character",
                "description": "Create a new character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "street_name": {"type": "string", "description": "Character's street name"},
                        "given_name": {"type": "string", "description": "Character's given name"},
                        "archetype": {"type": "string", "description": "Character archetype"},
                        "metatype": {"type": "string", "description": "Metatype"},
                        "attributes": {"type": "object", "description": "Starting attributes"},
                        "reason": {"type": "string", "description": "Reason for creation"}
                    },
                    "required": ["street_name", "archetype"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_character_info",
                "description": "Update character biographical information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "updates": {"type": "object", "description": "Fields to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_character",
                "description": "Delete a character from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "reason": {"type": "string", "description": "Reason for deletion"}
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_attribute",
                "description": "Update a character's attribute value",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "attribute_name": {"type": "string", "description": "Name of the attribute"},
                        "new_value": {"type": "integer", "description": "New attribute value"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "attribute_name", "new_value"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_derived_stats",
                "description": "Update character's derived statistics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "updates": {"type": "object", "description": "Derived stats to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "updates"]
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
                    await send_telemetry(websocket, "grok_tool_request", {
                        "tools_requested": [tc.function.name for tc in tool_calls],
                        "tool_count": len(tool_calls)
                    })
                    
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
                            
                            # Re-raise to handle in outer try/catch
                            raise
                        
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


# HTTP endpoint to list all characters
@app.get("/api/characters")
async def list_characters_endpoint():
    """List all available characters"""
    try:
        # Use MCP operations to get all characters
        characters = await mcp_client.ops.list_characters()
        
        # Convert UUIDs and Decimals to JSON-serializable types
        characters = convert_db_types(characters)
        
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


# ========== SPELLCASTING UI ENDPOINTS ==========

@app.post("/api/cast_spell")
async def cast_spell_endpoint(data: dict):
    """Cast a spell via HTTP"""
    try:
        caster_name = data.get('caster_name')
        spell_name = data.get('spell_name')
        force = data.get('force')
        target_name = data.get('target_name')
        spell_pool_dice = data.get('spell_pool_dice', 0)
        drain_pool_dice = data.get('drain_pool_dice', 0)
        
        result = await mcp_client.call_tool("cast_spell", {
            "caster_name": caster_name,
            "spell_name": spell_name,
            "force": force,
            "target_name": target_name,
            "spell_pool_dice": spell_pool_dice,
            "drain_pool_dice": drain_pool_dice
        })
        
        result = convert_db_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        trace_logger.error(f"Error casting spell: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sustained_spells/{character_name}")
async def get_sustained_spells_endpoint(character_name: str):
    """Get sustained spells for a character"""
    try:
        from lib.spellcasting import SpellcastingEngine
        engine = SpellcastingEngine()
        
        sustained_spells = await engine.get_sustained_spells(character_name)
        penalty = await engine.calculate_sustaining_penalty(character_name)
        
        result = {
            "sustained_spells": sustained_spells,
            "sustaining_penalty": penalty
        }
        
        result = convert_db_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        trace_logger.error(f"Error getting sustained spells: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/drop_spell")
async def drop_spell_endpoint(data: dict):
    """Drop a sustained spell"""
    try:
        character_name = data.get('character_name')
        spell_name = data.get('spell_name')
        
        from lib.spellcasting import SpellcastingEngine
        engine = SpellcastingEngine()
        
        success = await engine.drop_sustained_spell(character_name, spell_name)
        
        if success:
            # Get updated sustained spells
            sustained_spells = await engine.get_sustained_spells(character_name)
            penalty = await engine.calculate_sustaining_penalty(character_name)
            
            result = {
                "success": True,
                "message": f"Dropped {spell_name}",
                "sustained_spells": sustained_spells,
                "sustaining_penalty": penalty
            }
        else:
            result = {
                "success": False,
                "message": f"Spell {spell_name} not found"
            }
        
        result = convert_db_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        trace_logger.error(f"Error dropping spell: {str(e)}")
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
