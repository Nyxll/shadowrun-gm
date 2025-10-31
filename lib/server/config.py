"""
Configuration and Environment Setup
"""

import os
import json
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Setup logging directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


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


# Initialize Grok client (uses OpenAI-compatible API)
grok = AsyncOpenAI(
    api_key=os.getenv('XAI_API_KEY'),
    base_url="https://api.x.ai/v1"
)
