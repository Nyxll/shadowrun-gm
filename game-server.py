#!/usr/bin/env python3
"""
Shadowrun GM - Live Game Server
FastAPI server with Grok AI + MCP tools integration
Clean refactored version using MCPOperations
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Scope
import uvicorn
from decimal import Decimal

# Import our MCP operations layer
from lib.mcp_operations import MCPOperations
from lib.ai_payload_optimizer import optimize_tool_result

# Import refactored server modules
from lib.server.config import grok, convert_db_types, CustomJSONEncoder
from lib.server.logging_setup import trace_logger, trace_id_var
from lib.server.middleware import TraceIDMiddleware
from lib.server.session_manager import SessionManager
from lib.server.telemetry import (
    send_telemetry,
    send_mcp_telemetry,
    send_database_telemetry,
    send_api_telemetry,
    send_error_telemetry,
    send_ui_telemetry
)
from lib.server.http_endpoints import (
    list_characters_endpoint,
    get_character_endpoint,
    cast_spell_endpoint,
    get_sustained_spells_endpoint,
    drop_spell_endpoint,
    list_sessions_endpoint,
    create_session_endpoint
)
from lib.server.tool_definitions import get_mcp_tool_definitions
from lib.server.mcp_client import MCPClient
from lib.server.websocket_handler import create_websocket_endpoint


# Initialize FastAPI
app = FastAPI(title="Shadowrun GM Server", version="2.0.0")

# Add trace ID middleware
app.add_middleware(TraceIDMiddleware)


# Global session manager
session_manager = SessionManager()


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


# Register WebSocket endpoint with all required dependencies
create_websocket_endpoint(
    app, 
    session_manager, 
    mcp_client, 
    grok, 
    get_mcp_tool_definitions,
    send_telemetry,
    send_mcp_telemetry,
    send_ui_telemetry,
    send_error_telemetry,
    convert_db_types,
    optimize_tool_result
)


# HTTP endpoint to list all characters
@app.get("/api/characters")
async def list_characters():
    """List all available characters"""
    return await list_characters_endpoint(mcp_client)


# HTTP endpoint to get character data
@app.get("/api/character/{character_name}")
async def get_character(character_name: str):
    """Get character data via HTTP"""
    return await get_character_endpoint(character_name, mcp_client)


# ========== SPELLCASTING UI ENDPOINTS ==========

@app.post("/api/cast_spell")
async def cast_spell(data: dict):
    """Cast a spell via HTTP"""
    return await cast_spell_endpoint(data, mcp_client)


@app.get("/api/sustained_spells/{character_name}")
async def get_sustained_spells(character_name: str):
    """Get sustained spells for a character"""
    return await get_sustained_spells_endpoint(character_name)


@app.post("/api/drop_spell")
async def drop_spell(data: dict):
    """Drop a sustained spell"""
    return await drop_spell_endpoint(data)


# HTTP endpoint to list sessions
@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    return await list_sessions_endpoint(session_manager)


# HTTP endpoint to create session
@app.post("/api/sessions")
async def create_session(data: dict):
    """Create a new session"""
    return await create_session_endpoint(data, session_manager)


# Serve static files with cache-busting
app.mount("/", NoCacheStaticFiles(directory="www", html=True), name="www")


if __name__ == "__main__":
    trace_logger.info("Starting Shadowrun GM Server v2.0.0")
    trace_logger.info("Using MCPOperations with comprehensive CRUD API")
    uvicorn.run(app, host="0.0.0.0", port=8001)
