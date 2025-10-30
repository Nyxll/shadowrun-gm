# Project Configuration Reference

## CRITICAL SETTINGS - READ FIRST

### Server Configuration
- **Port**: 8001 (NOT 8000!)
- **Base URL**: http://localhost:8001
- **WebSocket**: ws://localhost:8001/game

### Test Characters - use street names not character name
- **Platinum**: Has extensive cyberware/bioware - USE FOR TESTING
- **Oak**: Mage character
- **Leviathan**: Shaman character
- **Axel**: Rigger character
- **Manticore**: Decker character

### Database
- **Host**: From .env POSTGRES_HOST
- **Port**: From .env POSTGRES_PORT  
- **Database**: From .env POSTGRES_DB
- **Always use .env for credentials**

### File Naming Conventions
- Python scripts: `snake_case.py`
- Test files: `test-kebab-case.py` in `/tests` or `/tools`
- Documentation: `CAPS-WITH-DASHES.md` in `/docs`

### Code Patterns
- Reuse existing tools.  only write new files when there is new functionality


#### Python Database Connection
```python
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)
```

#### API Testing Pattern
```python
import requests
import json

# ALWAYS use port 8001!
response = requests.get('http://localhost:8001/api/character/Platinum')
data = response.json()
```

### Common Mistakes to Avoid
1. ❌ Using port 8000 instead of 8001
2. ❌ Testing with Kent instead of Platinum for cyberware
3. ❌ Hardcoding database credentials
4. ❌ Creating duplicate tools instead of checking /tools first
5. ❌ Not checking .clinerules before starting
6. ❌ user proper powershell syntax and escape * asterix and bracket

### Before Making Changes
1. Check if tool already exists in `/tools`
2. Verify port is 8001
3. Use Platinum for cyberware/bioware testing
4. Load .env for all database operations
5. Read .clinerules for project-specific rules

### Key Schema Facts
- **Primary Schema**: `schema.sql` (v3.0) is authoritative
- **Cyberware/Bioware**: Stored in `character_modifiers` table
- **JSONB Fields**: Used for flexible data (abilities, conditions, metadata)
- **House Rules**: Separate table for custom/homebrew content

### API Structure
- Character endpoint: `/api/character/{name}`
- Returns grouped cyberware/bioware arrays
- Each item has: `name`, `effects[]`, `essence_cost` or `body_index_cost`

### Frontend
- Renderer: `www/character-sheet-renderer.js`
- App: `www/app.js`
- Styles: `www/character-sheet.css`, `www/themes.css`
