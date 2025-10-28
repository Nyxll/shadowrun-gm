#!/usr/bin/env python3
"""
Check system status - database, environment, and services
"""
import os
import sys
from dotenv import load_dotenv

print("="*70)
print("SHADOWRUN GM SYSTEM STATUS CHECK")
print("="*70)

# Check .env file
print("\n1. Checking .env file...")
if os.path.exists('.env'):
    print("   ✓ .env file exists")
    load_dotenv()
    
    required_vars = [
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password
            if 'PASSWORD' in var:
                print(f"   ✓ {var}=***")
            else:
                print(f"   ✓ {var}={value}")
        else:
            print(f"   ✗ {var} is missing!")
            missing.append(var)
    
    if missing:
        print(f"\n   ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
else:
    print("   ✗ .env file not found!")
    print("   Please create .env file with database credentials")
    sys.exit(1)

# Check database connection
print("\n2. Checking database connection...")
try:
    import psycopg
    from psycopg.rows import dict_row
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row,
        connect_timeout=5
    )
    
    print("   ✓ Database connection successful!")
    
    # Check tables
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = [row['table_name'] for row in cur.fetchall()]
    
    print(f"\n3. Database tables ({len(tables)} found):")
    important_tables = [
        'characters',
        'character_skills',
        'character_modifiers',
        'character_gear',
        'character_edges_flaws',
        'gear',
        'qualities'
    ]
    
    for table in important_tables:
        if table in tables:
            # Count rows
            cur.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cur.fetchone()['count']
            print(f"   ✓ {table}: {count} rows")
        else:
            print(f"   ✗ {table}: MISSING!")
    
    # Check character count
    print("\n4. Characters in database:")
    cur.execute("""
        SELECT name, street_name, archetype
        FROM characters
        ORDER BY name
    """)
    
    characters = cur.fetchall()
    if characters:
        for char in characters:
            name = char['street_name'] or char['name']
            archetype = char['archetype'] or 'Unknown'
            print(f"   • {name} ({archetype})")
    else:
        print("   ✗ No characters found!")
    
    conn.close()
    
except ImportError:
    print("   ✗ psycopg library not installed!")
    print("   Run: pip install psycopg[binary]")
    sys.exit(1)
    
except Exception as e:
    print(f"   ✗ Database connection failed!")
    print(f"   Error: {e}")
    print("\n   Possible issues:")
    print("   - Database server not running")
    print("   - Wrong credentials in .env")
    print("   - Firewall blocking connection")
    print("   - Wrong host/port")
    sys.exit(1)

# Check game server
print("\n5. Checking game server...")
try:
    import requests
    response = requests.get('http://localhost:8001/api/characters', timeout=2)
    if response.status_code == 200:
        print("   ✓ Game server is running on http://localhost:8001")
        data = response.json()
        print(f"   ✓ API responding with {len(data.get('characters', []))} characters")
    else:
        print(f"   ⚠ Game server responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ✗ Game server not running")
    print("   Start with: python game-server.py")
except ImportError:
    print("   ⚠ requests library not installed (optional)")
except Exception as e:
    print(f"   ⚠ Could not check game server: {e}")

print("\n" + "="*70)
print("SYSTEM STATUS CHECK COMPLETE")
print("="*70)
