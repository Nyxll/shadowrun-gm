#!/usr/bin/env python3
"""
Import Historical Campaign and Session Data
Imports campaigns and session logs from parsed xAI exports into PostgreSQL
Links to existing characters without duplicating character data
"""

import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

# PostgreSQL connection from .env
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5434'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}

# Data paths
XAI_PARSED_FILE = 'parsed-xai-data/xai-parsed-all.json'
XAI_SUMMARY_FILE = 'parsed-xai-data/xai-summary.json'

def load_xai_data() -> List[Dict]:
    """Load parsed xAI data"""
    print(f"📂 Loading xAI data from {XAI_PARSED_FILE}...")
    
    campaigns = []
    session_logs = []
    
    try:
        with open(XAI_PARSED_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        # Data structure: {'byType': {...}, 'items': [...], 'errors': [...]}
        items = data.get('items', [])
        
        # Filter for campaigns and session logs
        for item in items:
            content_type = item.get('type', 'unknown')
            if content_type == 'campaign_data':
                campaigns.append(item)
            elif content_type == 'session_log':
                session_logs.append(item)
        
        print(f"✅ Found {len(campaigns)} campaigns and {len(session_logs)} session logs")
        return campaigns, session_logs
        
    except FileNotFoundError:
        print(f"❌ File not found: {XAI_PARSED_FILE}")
        return [], []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return [], []
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return [], []

def extract_campaign_info(item: Dict) -> Optional[Dict]:
    """Extract campaign information from xAI item"""
    content = item.get('content', '')
    
    campaign = {
        'uuid': item.get('uuid'),
        'name': None,
        'description': None,
        'setting_notes': None,
        'gm_name': 'Rick',  # Default GM name
        'status': 'archived',  # Historical data is archived
        'metadata': {}
    }
    
    # Try to extract campaign name from content
    lines = content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and not line.startswith('#'):
            # First non-empty, non-header line is likely the campaign name
            if not campaign['name']:
                campaign['name'] = line[:200]  # Limit to 200 chars
                break
    
    # If no name found, use UUID
    if not campaign['name']:
        campaign['name'] = f"Campaign {item.get('uuid', 'Unknown')[:8]}"
    
    # Store full content as description
    campaign['description'] = content[:1000] if content else None
    
    # Store metadata
    campaign['metadata'] = {
        'source': 'xai_export',
        'uuid': item.get('uuid'),
        'original_type': item.get('type')
    }
    
    return campaign

def extract_session_info(item: Dict) -> Optional[Dict]:
    """Extract session log information from xAI item"""
    content = item.get('content', '')
    
    session = {
        'uuid': item.get('uuid'),
        'campaign_name': None,
        'session_date': None,
        'summary': None,
        'karma_awarded': None,
        'participants': [],
        'events': [],
        'metadata': {}
    }
    
    # Try to extract session info from content
    lines = content.split('\n')
    
    # Look for karma awards
    for line in lines:
        if 'karma' in line.lower():
            # Try to extract karma amount
            import re
            karma_match = re.search(r'(\d+)\s*karma', line, re.I)
            if karma_match:
                session['karma_awarded'] = int(karma_match.group(1))
    
    # Store full content as summary
    session['summary'] = content[:2000] if content else None
    
    # Store metadata
    session['metadata'] = {
        'source': 'xai_export',
        'uuid': item.get('uuid'),
        'original_type': item.get('type')
    }
    
    return session

def get_or_create_campaign(conn, campaign_data: Dict) -> int:
    """Get existing campaign or create new one"""
    cursor = conn.cursor()
    
    try:
        # Check if campaign already exists by name
        cursor.execute(
            "SELECT id FROM campaigns WHERE name = %s",
            (campaign_data['name'],)
        )
        result = cursor.fetchone()
        
        if result:
            print(f"  ℹ️  Campaign already exists: {campaign_data['name']}")
            return result[0]
        
        # Create new campaign
        cursor.execute('''
            INSERT INTO campaigns (
                name, gm_name, description, setting_notes, status,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        ''', (
            campaign_data['name'],
            campaign_data['gm_name'],
            campaign_data['description'],
            campaign_data.get('setting_notes'),
            campaign_data['status'],
            datetime.now(),
            datetime.now()
        ))
        
        campaign_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"  ✅ Created campaign: {campaign_data['name']} (ID: {campaign_id})")
        return campaign_id
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error creating campaign: {e}")
        raise

def create_session_log_table(conn):
    """Create session_logs table if it doesn't exist"""
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_logs (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
                session_date DATE,
                summary TEXT,
                karma_awarded INTEGER,
                participants JSONB DEFAULT '[]',
                events JSONB DEFAULT '[]',
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_logs_campaign 
            ON session_logs(campaign_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_logs_date 
            ON session_logs(session_date)
        ''')
        
        conn.commit()
        print("✅ Session logs table ready")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating session_logs table: {e}")
        raise

def import_session_log(conn, session_data: Dict, campaign_id: int) -> int:
    """Import session log into database"""
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO session_logs (
                campaign_id, session_date, summary, karma_awarded,
                participants, events, metadata,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s
            ) RETURNING id
        ''', (
            campaign_id,
            session_data.get('session_date'),
            session_data.get('summary'),
            session_data.get('karma_awarded'),
            json.dumps(session_data.get('participants', [])),
            json.dumps(session_data.get('events', [])),
            json.dumps(session_data.get('metadata', {})),
            datetime.now(),
            datetime.now()
        ))
        
        session_id = cursor.fetchone()[0]
        conn.commit()
        
        return session_id
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error importing session log: {e}")
        raise

def create_character_campaign_links_table(conn):
    """Create character_campaign_links table if it doesn't exist"""
    cursor = conn.cursor()
    
    try:
        # Drop existing table if it has wrong schema
        cursor.execute('''
            DROP TABLE IF EXISTS character_campaign_links CASCADE
        ''')
        
        # Create with correct schema - character_id is UUID referencing characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_campaign_links (
                id SERIAL PRIMARY KEY,
                character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
                campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
                joined_date DATE,
                left_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT unique_char_campaign UNIQUE(character_id, campaign_id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_char_campaign_links_character 
            ON character_campaign_links(character_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_char_campaign_links_campaign 
            ON character_campaign_links(campaign_id)
        ''')
        
        conn.commit()
        print("✅ Character-campaign links table ready")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating character_campaign_links table: {e}")
        raise

def link_characters_to_campaign(conn, campaign_id: int, character_names: List[str]):
    """Link existing characters to campaign"""
    cursor = conn.cursor()
    
    for char_name in character_names:
        try:
            # Find character by street_name in the characters table (not sr_characters)
            cursor.execute('''
                SELECT id, name, street_name FROM characters 
                WHERE street_name ILIKE %s OR name ILIKE %s
                LIMIT 1
            ''', (f'%{char_name}%', f'%{char_name}%'))
            
            result = cursor.fetchone()
            if not result:
                print(f"  ⚠️  Character not found: {char_name}")
                continue
            
            char_id, char_full_name, street_name = result
            
            # Create link if it doesn't exist
            # Note: character_id is UUID in characters table
            cursor.execute('''
                INSERT INTO character_campaign_links (
                    character_id, campaign_id, is_active, created_at
                ) VALUES (%s::uuid, %s, %s, %s)
                ON CONFLICT (character_id, campaign_id) DO NOTHING
            ''', (str(char_id), campaign_id, True, datetime.now()))
            
            if cursor.rowcount > 0:
                print(f"  ✅ Linked character: {char_full_name} ({street_name})")
            
        except Exception as e:
            print(f"  ❌ Error linking character {char_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    conn.commit()

def main():
    """Main import process"""
    print("🎲 Historical Campaign & Session Import Tool")
    print("="*60)
    print(f"Database: PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("="*60)
    
    # Load xAI data
    campaigns_data, sessions_data = load_xai_data()
    
    if not campaigns_data and not sessions_data:
        print("\n❌ No data to import")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("\n✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        return
    
    # Create tables if needed
    print("\n📋 Setting up tables...")
    create_session_log_table(conn)
    create_character_campaign_links_table(conn)
    
    # Import campaigns
    print(f"\n📁 Importing {len(campaigns_data)} campaigns...")
    campaign_ids = {}
    
    for item in campaigns_data:
        campaign = extract_campaign_info(item)
        if campaign:
            try:
                campaign_id = get_or_create_campaign(conn, campaign)
                campaign_ids[campaign['uuid']] = campaign_id
            except Exception as e:
                print(f"  ❌ Failed to import campaign: {e}")
                continue
    
    # Import session logs
    print(f"\n📝 Importing {len(sessions_data)} session logs...")
    
    for item in sessions_data:
        session = extract_session_info(item)
        if session:
            # Try to link to a campaign (use first campaign for now)
            campaign_id = list(campaign_ids.values())[0] if campaign_ids else None
            
            if not campaign_id:
                print("  ⚠️  No campaign to link session to, skipping")
                continue
            
            try:
                session_id = import_session_log(conn, session, campaign_id)
                print(f"  ✅ Imported session log (ID: {session_id})")
            except Exception as e:
                print(f"  ❌ Failed to import session: {e}")
                continue
    
    # Link known characters to campaigns
    print("\n🔗 Linking characters to campaigns...")
    known_characters = ['Oak', 'Platinum', 'Axel', 'Manticore', 'Block', 'Raven']
    
    for campaign_id in campaign_ids.values():
        link_characters_to_campaign(conn, campaign_id, known_characters)
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"✅ Import Complete!")
    print(f"   Campaigns: {len(campaign_ids)}")
    print(f"   Session Logs: {len(sessions_data)}")
    print("="*60)

if __name__ == '__main__':
    main()
