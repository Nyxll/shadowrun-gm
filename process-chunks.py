#!/usr/bin/env python3
"""
Shadowrun GM Chunk Processing Script
Processes OCR text files and saves chunks to JSON (no database insertion)
"""

import os
import re
import json
from openai import OpenAI
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# OpenAI configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

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

class ShadowrunProcessor:
    """Processes Shadowrun content into chunks"""
    
    def __init__(self):
        self.client = OpenAI()
        self.validator = TextValidator()
        print(f"Using model: {OPENAI_MODEL}")
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean OCR artifacts from text"""
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
        parts = re.split(r'\n(#{1,2})\s+(.+?)(?:\r?\n|$)', text)
        
        if len(parts) == 1:
            sections.append({
                'title': os.path.basename(filename).replace('-ocr.txt', '').replace('-', ' ').title(),
                'content': parts[0].strip()
            })
        else:
            current_content = parts[0].strip()
            if current_content:
                sections.append({'title': 'Introduction', 'content': current_content})
            
            i = 1
            while i < len(parts):
                if i + 2 < len(parts):
                    title = parts[i + 1].strip()
                    content = parts[i + 2].strip()
                    if title and content:
                        sections.append({'title': title, 'content': content})
                    i += 3
                else:
                    break
        
        return sections
    
    def create_chunks(self, section: Dict, min_size: int = 200, max_size: int = 1200) -> List[str]:
        """Create semantic chunks from section content"""
        content = section['content']
        chunks = []
        
        if len(content) <= max_size:
            return [content]
        
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) + 2 > max_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    words = current_chunk.split()
                    overlap_text = ' '.join(words[-20:]) if len(words) > 20 else current_chunk
                    current_chunk = overlap_text + '\n\n' + para
                else:
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
    
    def process_file(self, filepath: str) -> List[Chunk]:
        """Process a single file and return chunks"""
        print(f"\nProcessing: {os.path.basename(filepath)}")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        text = self.clean_ocr_text(text)
        sections = self.extract_sections(text, filepath)
        print(f"  Found {len(sections)} sections")
        
        all_chunks = []
        chunk_index = 0
        
        for section in sections:
            chunk_texts = self.create_chunks(section)
            print(f"  Section '{section['title']}': {len(chunk_texts)} chunks")
            
            for chunk_text in chunk_texts:
                categorization = self.categorize_chunk(section['title'], chunk_text)
                
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


def main():
    """Main processing"""
    print("=" * 60)
    print("Shadowrun GM Chunk Processing")
    print("=" * 60)
    
    files = [
        r"G:\My Drive\Sourcebooks\core-combat-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\core-gamemaster-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\core-gear-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\core-magic-rules-ocr.txt",
        r"G:\My Drive\Sourcebooks\FieldsofFire-rules-ocr.txt"
    ]
    
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print("\n❌ Error: Files not found:")
        for f in missing_files:
            print(f"  - {f}")
        return
    
    processor = ShadowrunProcessor()
    
    all_chunks = []
    for filepath in files:
        chunks = processor.process_file(filepath)
        all_chunks.extend(chunks)
    
    print(f"\n{'=' * 60}")
    print(f"Total chunks processed: {len(all_chunks)}")
    print(f"{'=' * 60}\n")
    
    # Save to JSON
    output_file = "processed-chunks.json"
    print(f"Saving chunks to {output_file}...")
    
    chunks_data = [asdict(chunk) for chunk in all_chunks]
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(all_chunks)} chunks to {output_file}")
    print(f"\nNext step: Run 'python insert-chunks.py' to insert into database")


if __name__ == "__main__":
    main()
