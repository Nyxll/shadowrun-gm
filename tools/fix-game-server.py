#!/usr/bin/env python3
"""
Fix corrupted game-server.py file
Reconstructs the corrupted WebSocket handler section
"""

# Read the corrupted file
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where corruption starts (around line with 'add_character')
corruption_start = content.find("elif message_type == 'add_character':")
if corruption_start == -1:
    print("Could not find corruption point")
    exit(1)

# Find where corruption ends (should be at the HTTP endpoints section)
corruption_end = content.find("@app.get(\"/api/characters\")")
if corruption_end == -1:
    # Try alternate marker
    corruption_end = content.find("# HTTP endpoint")
    if corruption_end == -1:
        print("Could not find end of corruption")
        print("Searching for any @app marker...")
        corruption_end = content.find("@app.")
        if corruption_end == -1:
            print("ERROR: Cannot find any endpoint markers")
            exit(1)

# Extract the good parts
before_corruption = content[:corruption_start]
after_corruption = content[corruption_end:]

# Reconstruct the missing section
fixed_section = """elif message_type == 'add_character':
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


"""

# Reconstruct the file
fixed_content = before_corruption + fixed_section + after_corruption

# Write the fixed file
with open('game-server.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ game-server.py has been fixed!")
print(f"   Removed {corruption_end - corruption_start} bytes of corrupted code")
print(f"   Added {len(fixed_section)} bytes of clean code")
