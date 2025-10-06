#!/usr/bin/env python3
"""
Shadowrun GM Database Migration Script
Migrates OCR text files to properly structured database with AI categorization
"""

import os
import re
import json
import hashlib
import psycopg2
from openai import OpenAI
from typing import List, Dict, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file for database config
load_dotenv()

# Configuration from environment variables
# Database config from .env file or environment
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5433')
DB_NAME = os.getenv('POSTGRES_DB', 'postgres')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

# OpenAI configuration - API key must be in system environment
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_EMBED_MODEL = os.getenv('OPENAI_EMBED_MODEL', 'text-embedding-3-small')

@dataclass
class Chunk:
    """Represents a content chunk with metadata"""
    title: str
    content: str
    category: str
    subcategory: str
    tags: List[str]
    content_type: str
    source_file: str
    chunk_index: int

class TextValidator:
    """Validates and cleans text for database insertion"""
    
    @staticmethod
    def has_null_bytes(text: str) -> bool:
        """Check if text contains NULL bytes"""
        return '\x00' in text
    
    @staticmethod
    def has_problematic_chars(text: str) -> Tuple[bool, List[str]]:
        """Check for problematic characters"""
        problems = []
        
        # Check for NULL bytes
        if '\x00' in text:
            problems.append("NULL bytes (\\x00)")
        
        # Check for other control characters (except newlines, tabs, carriage returns)
        control_chars = set()
        for char in text:
            if ord(char) < 32 and char not in '\n\t\r':
                control_chars.add(f"\\x{ord(char):02x}")
        
        if control_chars:
            problems.append(f"Control characters: {', '.join(sorted(control_chars))}")
        
        # Check for invalid UTF-8 sequences
        try:
            text.encode('utf-8')
        except UnicodeEncodeError as e:
            problems.append(f"Invalid UTF-8: {str(e)}")
        
        # Check for extremely long lines (>10000 chars)
        lines = text.split('\n')
        long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 10000]
        if long_lines:
            problems.append(f"Extremely long lines: {long_lines[:5]}")
        
        return len(problems) > 0, problems
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text of problematic characters"""
        # Remove NULL bytes
        text = text.replace('\x00', '')
        
        # Remove other control characters (except newlines, tabs, carriage returns)
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
        
        # Normalize line endings - REMOVE CARRIAGE RETURNS
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Ensure valid UTF-8
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return text

class ShadowrunMigrator:
    """Handles migration of Shadowrun content to database"""
    
    def __init__(self):
        # Initialize OpenAI client - uses OPENAI_API_KEY from environment automatically
        self.client = OpenAI()
        self.validator = TextValidator()
        
        print(f"Using model: {OPENAI_MODEL}")
        print(f"Using embeddings: {OPENAI_EMBED_MODEL}")
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean OCR artifacts from text"""
        # First, use validator to clean problematic characters
        text = self.validator.clean_text(text)
        
        # Fix common OCR errors
        text = text.replace('pprovides', 'provides')
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('–', '-')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def extract_sections(self, text: str, filename: str) -> List[Dict]:
        """Extract sections from text based on headers"""
        sections = []
        
        # Split by markdown headers (## or #)
        parts = re.split(r'\n(#{1,2})\s+(.+?)(?:\r?\n|$)', text)
        
        if len(parts) == 1:
            # No headers found, treat as single section
            sections.append({
                'title': os.path.basename(filename).replace('-ocr.txt', '').replace('-', ' ').title(),
                'content': parts[0].strip()
            })
        else:
            # Process header-based sections
            current_content = parts[0].strip()
            if current_content:
                sections.append({
                    'title': 'Introduction',
                    'content': current_content
                })
            
            i = 1
            while i < len(parts):
                if i + 2 < len(parts):
                    header_level = parts[i]
                    title = parts[i + 1].strip()
                    content = parts[i + 2].strip()
                    
                    if title and content:
                        sections.append({
                            'title': title,
                            'content': content
                        })
                    
                    i += 3
                else:
                    break
        
        return sections
    
    def create_chunks(self, section: Dict, min_size: int = 200, max_size: int = 1200, overlap: int = 100) -> List[str]:
        """Create semantic chunks from section content"""
        content = section['content']
        chunks = []
        
        # If content is small enough, return as single chunk
        if len(content) <= max_size:
            return [content]
        
        # Split by paragraphs
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would exceed max_size
            if len(current_chunk) + len(para) + 2 > max_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    words = current_chunk.split()
                    overlap_text = ' '.join(words[-20:]) if len(words) > 20 else current_chunk
                    current_chunk = overlap_text + '\n\n' + para
                else:
                    # Paragraph itself is too long, split it
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        if len(current_chunk) + len(sent) + 1 > max_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sent
                        else:
                            current_chunk += ' ' + sent if current_chunk else sent
            else:
                current_chunk += '\n\n' + para if current_chunk else para
        
        # Add final chunk
        if current_chunk and len(current_chunk.strip()) >= min_size:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def categorize_chunk(self, title: str, content: str) -> Dict:
        """Use AI to categorize chunk"""
        prompt = f"""Analyze this Shadowrun 2nd Edition content and provide categorization.

Title: {title}

Content:
{content[:800]}...

Provide a JSON response with:
1. "category": One of: combat, magic, matrix, character_creation, skills, gear_mechanics, general, lore
2. "subcategory": Specific topic (e.g., "initiative", "spellcasting", "weapons", "locations")
3. "tags": Array of 3-5 relevant search tags (lowercase, underscore-separated)
4. "content_type": One of: rule_mechanic, stat_block, example, flavor_text, table, introduction

Return ONLY valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a Shadowrun 2nd Edition rules expert. Categorize content accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if model added extra text
            if not result_text.startswith('{'):
                start = result_text.find('{')
                end = result_text.rfind('}') + 1
                if start != -1 and end > start:
                    result_text = result_text[start:end]
            
            result = json.loads(result_text)
            
            return {
                'category': result.get('category', 'general'),
                'subcategory': result.get('subcategory', ''),
                'tags': result.get('tags', []),
                'content_type': result.get('content_type', 'rule_mechanic')
            }
        except Exception as e:
            print(f"  Warning: Categorization failed: {e}")
            return {
                'category': 'general',
                'subcategory': '',
                'tags': [],
                'content_type': 'rule_mechanic'
            }
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = self.client.embeddings.create(
                model=OPENAI_EMBED_MODEL,
                input=text[:8000]  # Limit to 8000 chars
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  Warning: Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def process_file(self, filepath: str) -> List[Chunk]:
        """Process a single file and return chunks"""
        print(f"\nProcessing: {os.path.basename(filepath)}")
        
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Validate text
        has_problems, problems = self.validator.has_problematic_chars(text)
        if has_problems:
            print(f"  ⚠️  Found problematic characters:")
            for problem in problems:
                print(f"     - {problem}")
            print(f"  ✓ Cleaning text...")
            text = self.validator.clean_text(text)
        else:
            print(f"  ✓ No problematic characters found")
        
        # Clean OCR artifacts
        text = self.clean_ocr_text(text)
        
        # Extract sections
        sections = self.extract_sections(text, filepath)
        print(f"  Found {len(sections)} sections")
        
        # Process each section
        all_chunks = []
        chunk_index = 0
        
        for section in sections:
            # Create chunks
            chunk_texts = self.create_chunks(section)
            print(f"  Section '{section['title']}': {len(chunk_texts)} chunks")
            
            for chunk_text in chunk_texts:
                # Categorize
                categorization = self.categorize_chunk(section['title'], chunk_text)
                
                # Create chunk object
                chunk = Chunk(
                    title=section['title'],
                    content=chunk_text,
                    category=categorization['category'],
                    subcategory=categorization['subcategory'],
                    tags=categorization['tags'],
                    content_type=categorization['content_type'],
                    source_file=os.path.basename(filepath),
                    chunk_index=chunk_index
                )
                
                all_chunks.append(chunk)
                chunk_index += 1
        
        print(f"  Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def insert_chunks(self, chunks: List[Chunk]):
        """Insert chunks into database"""
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        try:
            cur = conn.cursor()
            
            for i, chunk in enumerate(chunks, 1):
                # Generate embedding
                embedding = self.generate_embedding(chunk.content)
                
                # Insert into rules_content table
                cur.execute("""
                    INSERT INTO rules_content 
                    (title, content, category, subcategory, tags, source_file, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    chunk.title,
                    chunk.content,
                    chunk.category,
                    chunk.subcategory,
                    chunk.tags,
                    chunk.source_file,
                    embedding
                ))
                
                if i % 10 == 0:
                    print(f"  Inserted {i}/{len(chunks)} chunks...")
            
            conn.commit()
            print(f"  ✓ Successfully inserted {len(chunks)} chunks")
            
            # Validate insertion
            print("\n  Validating insertion...")
            cur.execute("SELECT COUNT(*) FROM rules_content")
            total_count = cur.fetchone()[0]
            print(f"    Total records in database: {total_count}")
            
            # Check by source file
            cur.execute("""
                SELECT source_file, COUNT(*) 
                FROM rules_content 
                GROUP BY source_file 
                ORDER BY source_file
            """)
            file_counts = cur.fetchall()
            print("\n    Records by source file:")
            for source_file, count in file_counts:
                print(f"      {source_file}: {count} chunks")
            
            # Check by category
            cur.execute("""
                SELECT category, COUNT(*) 
                FROM rules_content 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            """)
            category_counts = cur.fetchall()
            print("\n    Records by category:")
            for category, count in category_counts:
                print(f"      {category}: {count} chunks")
            
            # Verify embeddings
            cur.execute("SELECT COUNT(*) FROM rules_content WHERE embedding IS NOT NULL")
            embedding_count = cur.fetchone()[0]
            print(f"\n    Chunks with embeddings: {embedding_count}/{total_count}")
            
            if embedding_count == total_count:
                print("    ✓ All chunks have embeddings")
            else:
                print(f"    ⚠️  Warning: {total_count - embedding_count} chunks missing embeddings")
            
        except Exception as e:
            conn.rollback()
            print(f"  ❌ Error inserting chunks: {e}")
            raise
        finally:
            cur.close()
            conn.close()


def main():
    """Main migration process"""
    print("=" * 60)
    print("Shadowrun GM Database Migration")
    print("=" * 60)
    
    # File paths - Shadowrun sourcebook OCR files
    files = [
        r"G:\My Drive\Sourcebooks\core-combat-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\core-gamemaster-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\core-gear-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\core-magic-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\FieldsofFire-rules-ocr.txt"
    ]
    
    # Check files exist
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print("\n❌ Error: The following files were not found:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPlease update the file paths in migrate.py (lines 395-399)")
        return
    
    # Initialize migrator
    try:
        migrator = ShadowrunMigrator()
    except Exception as e:
        print(f"\n❌ Error initializing migrator: {e}")
        return
    
    # Process all files
    all_chunks = []
    for filepath in files:
        try:
            chunks = migrator.process_file(filepath)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"\n❌ Error processing {filepath}: {e}")
            return
    
    print(f"\n{'=' * 60}")
    print(f"Total chunks to insert: {len(all_chunks)}")
    print(f"{'=' * 60}\n")
    
    print("Proceeding with database insertion...")
    
    # Insert into database
    try:
        migrator.insert_chunks(all_chunks)
        print(f"\n{'=' * 60}")
        print("✓ Migration completed successfully!")
        print(f"{'=' * 60}")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")


if __name__ == "__main__":
    main()
