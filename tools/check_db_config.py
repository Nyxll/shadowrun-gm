#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

print(f"Database: {os.getenv('POSTGRES_DB')}")
print(f"Host: {os.getenv('POSTGRES_HOST')}")
print(f"Port: {os.getenv('POSTGRES_PORT')}")
print(f"User: {os.getenv('POSTGRES_USER')}")
