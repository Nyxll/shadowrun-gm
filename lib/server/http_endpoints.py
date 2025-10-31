"""
HTTP Endpoint Handlers for FastAPI
Handles character, spellcasting, and session management endpoints
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Dict

from lib.server.config import convert_db_types
from lib.server.logging_setup import trace_logger
from lib.ai_payload_optimizer import optimize_tool_result


async def list_characters_endpoint(mcp_client):
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


async def get_character_endpoint(character_name: str, mcp_client):
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


async def cast_spell_endpoint(data: dict, mcp_client):
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


async def list_sessions_endpoint(session_manager):
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


async def create_session_endpoint(data: dict, session_manager):
    """Create a new session"""
    from datetime import datetime
    
    session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
    session = session_manager.create_session(session_id)
    return {
        "session_id": session_id,
        "created_at": session.created_at.isoformat()
    }
