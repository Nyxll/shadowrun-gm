#!/usr/bin/env python3
"""
Shadowrun 2E Gear Data Loader with Deduplication
Handles loading gear from CSV and DAT files with intelligent merging
"""

import psycopg2
import psycopg2.extras
import csv
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class GearItem:
    """Represents a gear item to be loaded"""
    name: str
    category: str
    subcategory: Optional[str] = None
    base_stats: Dict = None
    modifiers: Dict = None
    requirements: Dict = None
    tags: List[str] = None
    description: Optional[str] = None
    game_notes: Optional[str] = None
    source: Optional[str] = None
    availability: Optional[str] = None
    cost: Optional[int] = None
    street_index: Optional[float] = None
    legality: Optional[str] = None
    
    def __post_init__(self):
        if self.base_stats is None:
            self.base_stats = {}
        if self.modifiers is None:
            self.modifiers = {}
        if self.requirements is None:
            self.requirements = {}
        if self.tags is None:
            self.tags = []


class LoadStats:
    """Track loading statistics"""
    def __init__(self):
        self.inserted = 0
        self.updated = 0
        self.merged = 0
        self.skipped = 0
        self.errors = []
        self.duplicates_found = []
        
    def add_error(self, item_name: str, error: str):
        self.errors.append(f"{item_name}: {error}")
        
    def add_duplicate(self, item_name: str, existing_name: str, similarity: float):
        self.duplicates_found.append({
            'new': item_name,
            'existing': existing_name,
            'similarity': similarity
        })
    
    def generate_report(self) -> str:
        """Generate a human-readable report"""
        report = [
            "=" * 60,
            "GEAR LOADING REPORT",
            "=" * 60,
            "",
            f"✓ Inserted:  {self.inserted} new items",
            f"↻ Updated:   {self.updated} items (better data quality)",
            f"⊕ Merged:    {self.merged} items (combined stats)",
            f"⊘ Skipped:   {self.skipped} duplicates",
            "",
        ]
        
        if self.duplicates_found:
            report.append("Potential Duplicates Requiring Review:")
            report.append("-" * 60)
            for dup in self.duplicates_found[:10]:  # Show first 10
                report.append(f"  '{dup['new']}' ≈ '{dup['existing']}' ({dup['similarity']:.0%})")
            if len(self.duplicates_found) > 10:
                report.append(f"  ... and {len(self.duplicates_found) - 10} more")
            report.append("")
        
        if self.errors:
            report.append("Errors:")
            report.append("-" * 60)
            for error in self.errors[:10]:  # Show first 10
                report.append(f"  ✗ {error}")
            if len(self.errors) > 10:
                report.append(f"  ... and {len(self.errors) - 10} more")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)


class GearLoader:
    """Main gear loading class with deduplication"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
        self.stats = LoadStats()
        
    def connect(self):
        """Connect to database"""
        self.conn = psycopg2.connect(**self.db_config)
        self.conn.autocommit = False
        logger.info("Connected to database")
        
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        # Remove special characters, convert to lowercase
        normalized = re.sub(r'[^a-z0-9]', '', name.lower())
        return normalized
    
    def find_existing_item(self, name: str, category: str) -> Optional[Dict]:
        """Find existing item by exact name match"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM gear 
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s)) 
                AND category = %s
            """, (name, category))
            return cur.fetchone()
    
    def find_similar_items(self, name: str, category: str, threshold: float = 0.85) -> List[Tuple[Dict, float]]:
        """Find similar items using fuzzy matching"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, category, data_quality
                FROM gear 
                WHERE category = %s
            """, (category,))
            
            existing_items = cur.fetchall()
            
        similar = []
        norm_name = self.normalize_name(name)
        
        for item in existing_items:
            norm_existing = self.normalize_name(item['name'])
            ratio = SequenceMatcher(None, norm_name, norm_existing).ratio()
            
            if ratio >= threshold:
                similar.append((dict(item), ratio))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)
    
    def merge_stats(self, existing: Dict, new: Dict) -> Dict:
        """Merge two stat dictionaries, preferring non-null values"""
        merged = existing.copy()
        
        for key, value in new.items():
            if value is not None and value != '':
                # If existing value is null/empty, use new value
                if key not in merged or merged[key] is None or merged[key] == '':
                    merged[key] = value
                # If both have values, keep existing (higher quality source loaded first)
        
        return merged
    
    def load_item(self, item: GearItem, source_file: str, data_quality: int) -> str:
        """
        Load a single item with deduplication
        Returns: 'inserted', 'updated', 'merged', or 'skipped'
        """
        try:
            # Check for exact match
            existing = self.find_existing_item(item.name, item.category)
            
            if existing:
                return self._handle_existing_item(existing, item, source_file, data_quality)
            
            # Check for similar items (potential duplicates)
            similar = self.find_similar_items(item.name, item.category, threshold=0.85)
            
            if similar:
                # Found similar item - log it but insert anyway
                for similar_item, similarity in similar:
                    if similarity < 1.0:  # Not exact match
                        self.stats.add_duplicate(
                            item.name, 
                            similar_item['name'], 
                            similarity
                        )
                        logger.warning(
                            f"Similar item found: '{item.name}' ≈ '{similar_item['name']}' "
                            f"({similarity:.0%} match)"
                        )
            
            # Insert new item
            return self._insert_item(item, source_file, data_quality)
            
        except Exception as e:
            self.stats.add_error(item.name, str(e))
            logger.error(f"Error loading {item.name}: {e}")
            return 'error'
    
    def _handle_existing_item(self, existing: Dict, new_item: GearItem, 
                             source_file: str, data_quality: int) -> str:
        """Handle case where item already exists"""
        
        existing_quality = existing['data_quality']
        
        if data_quality > existing_quality:
            # New source is better quality - UPDATE
            return self._update_item(existing['id'], new_item, source_file, data_quality, existing)
            
        elif data_quality == existing_quality:
            # Same quality - MERGE stats
            return self._merge_item(existing['id'], new_item, source_file, existing)
            
        else:
            # Existing is better quality - SKIP
            self._log_skip(existing['id'], new_item.name, source_file, 
                          f"Existing data quality ({existing_quality}) > new ({data_quality})")
            self.stats.skipped += 1
            return 'skipped'
    
    def _insert_item(self, item: GearItem, source_file: str, data_quality: int) -> str:
        """Insert new item"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO gear (
                    name, category, subcategory, base_stats, modifiers, requirements,
                    tags, description, game_notes, source, availability, cost,
                    street_index, legality, data_source, source_file, loaded_from, data_quality
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """, (
                item.name, item.category, item.subcategory,
                json.dumps(item.base_stats), json.dumps(item.modifiers), 
                json.dumps(item.requirements),
                item.tags, item.description, item.game_notes, item.source,
                item.availability, item.cost, item.street_index, item.legality,
                'csv' if source_file.endswith('.csv') else 'dat',
                source_file, [source_file], data_quality
            ))
            
            gear_id = cur.fetchone()[0]
            
            # Log to history
            cur.execute("""
                INSERT INTO gear_load_history (
                    gear_id, action, source_file, item_name, item_category, 
                    new_data, reason
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                gear_id, 'insert', source_file, item.name, item.category,
                json.dumps(asdict(item)), 'New item'
            ))
            
        self.conn.commit()
        self.stats.inserted += 1
        logger.info(f"✓ Inserted: {item.name} (quality={data_quality})")
        return 'inserted'
    
    def _update_item(self, gear_id: int, item: GearItem, source_file: str, 
                    data_quality: int, existing: Dict) -> str:
        """Update existing item with better quality data"""
        with self.conn.cursor() as cur:
            # Get current loaded_from array
            loaded_from = existing.get('loaded_from', [])
            if source_file not in loaded_from:
                loaded_from.append(source_file)
            
            cur.execute("""
                UPDATE gear SET
                    subcategory = %s, base_stats = %s, modifiers = %s, requirements = %s,
                    tags = %s, description = %s, game_notes = %s, source = %s,
                    availability = %s, cost = %s, street_index = %s, legality = %s,
                    source_file = %s, loaded_from = %s, data_quality = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (
                item.subcategory, json.dumps(item.base_stats), json.dumps(item.modifiers),
                json.dumps(item.requirements), item.tags, item.description, 
                item.game_notes, item.source, item.availability, item.cost,
                item.street_index, item.legality, source_file, loaded_from, 
                data_quality, gear_id
            ))
            
            # Log to history
            cur.execute("""
                INSERT INTO gear_load_history (
                    gear_id, action, source_file, item_name, item_category,
                    old_data, new_data, reason
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                gear_id, 'update', source_file, item.name, item.category,
                json.dumps(dict(existing)), json.dumps(asdict(item)),
                f'Better quality data ({data_quality} > {existing["data_quality"]})'
            ))
            
        self.conn.commit()
        self.stats.updated += 1
        logger.info(f"↻ Updated: {item.name} (quality {existing['data_quality']} → {data_quality})")
        return 'updated'
    
    def _merge_item(self, gear_id: int, item: GearItem, source_file: str, existing: Dict) -> str:
        """Merge stats from multiple sources of same quality"""
        # Merge JSONB fields
        merged_stats = self.merge_stats(
            existing.get('base_stats', {}), 
            item.base_stats
        )
        merged_modifiers = self.merge_stats(
            existing.get('modifiers', {}), 
            item.modifiers
        )
        merged_requirements = self.merge_stats(
            existing.get('requirements', {}), 
            item.requirements
        )
        
        # Merge tags (union)
        existing_tags = existing.get('tags', []) or []
        merged_tags = list(set(existing_tags + item.tags))
        
        # Keep longer description
        merged_desc = (item.description 
                      if item.description and len(item.description) > len(existing.get('description', '') or '')
                      else existing.get('description'))
        
        # Update loaded_from array
        loaded_from = existing.get('loaded_from', []) or []
        if source_file not in loaded_from:
            loaded_from.append(source_file)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE gear SET
                    base_stats = %s, modifiers = %s, requirements = %s, tags = %s,
                    description = %s, loaded_from = %s, updated_at = NOW()
                WHERE id = %s
            """, (
                json.dumps(merged_stats), json.dumps(merged_modifiers),
                json.dumps(merged_requirements), merged_tags, merged_desc,
                loaded_from, gear_id
            ))
            
            # Log to history
            cur.execute("""
                INSERT INTO gear_load_history (
                    gear_id, action, source_file, item_name, item_category,
                    old_data, new_data, reason
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                gear_id, 'merge', source_file, item.name, item.category,
                json.dumps(dict(existing)), json.dumps(asdict(item)),
                'Merged stats from same quality source'
            ))
            
        self.conn.commit()
        self.stats.merged += 1
        logger.info(f"⊕ Merged: {item.name} from {source_file}")
        return 'merged'
    
    def _log_skip(self, gear_id: int, item_name: str, source_file: str, reason: str):
        """Log skipped item to history"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO gear_load_history (
                    gear_id, action, source_file, item_name, item_category, reason
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (gear_id, 'skip', source_file, item_name, '', reason))
        self.conn.commit()


# Example usage and CSV loader functions
def load_cyberware_csv(loader: GearLoader, csv_path: Path):
    """Load CYBERWARE.csv file"""
    logger.info(f"Loading {csv_path.name}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Parse cyberware stats
                item = GearItem(
                    name=row['Name'].strip(),
                    category='cyberware',
                    subcategory=row.get('Type', '').strip() or None,
                    base_stats={
                        'essence': float(row.get('Essence', 0)) if row.get('Essence') else None,
                        'index': float(row.get('Index', 0)) if row.get('Index') else None,
                        'surgery_time': row.get('Surgery Time', '').strip() or None,
                    },
                    cost=int(row.get('Cost', 0)) if row.get('Cost') else None,
                    availability=row.get('Availability', '').strip() or None,
                    street_index=float(row.get('Street Index', 1.0)) if row.get('Street Index') else None,
                    legality=row.get('Legality', '').strip() or None,
                    description=row.get('Description', '').strip() or None,
                    source=row.get('Source', '').strip() or None,
                )
                
                loader.load_item(item, csv_path.name, data_quality=8)
                
            except Exception as e:
                logger.error(f"Error parsing row: {row.get('Name', 'Unknown')}: {e}")
    
    logger.info(f"Finished loading {csv_path.name}")


def load_totems_csv(loader: GearLoader, csv_path: Path):
    """Load TOTEMS.csv file"""
    logger.info(f"Loading {csv_path.name}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                item = GearItem(
                    name=row['Totem'].strip(),
                    category='totem',
                    description=row.get('Description', '').strip() or None,
                    modifiers={
                        'advantages': row.get('Advantages', '').strip() or None,
                        'disadvantages': row.get('Disadvantages', '').strip() or None,
                    },
                    source=row.get('Source', '').strip() or None,
                )
                
                loader.load_item(item, csv_path.name, data_quality=8)
                
            except Exception as e:
                logger.error(f"Error parsing row: {row.get('Totem', 'Unknown')}: {e}")
    
    logger.info(f"Finished loading {csv_path.name}")


def load_spells_csv(loader: GearLoader, csv_path: Path):
    """Load SPELLS.csv file"""
    logger.info(f"Loading {csv_path.name}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                item = GearItem(
                    name=row['Spell'].strip(),
                    category='spell',
                    subcategory=row.get('Category', '').strip() or None,
                    base_stats={
                        'type': row.get('Type', '').strip() or None,
                        'target': row.get('Target', '').strip() or None,
                        'drain': row.get('Drain', '').strip() or None,
                    },
                    description=row.get('Description', '').strip() or None,
                    source=row.get('Source', '').strip() or None,
                )
                
                loader.load_item(item, csv_path.name, data_quality=8)
                
            except Exception as e:
                logger.error(f"Error parsing row: {row.get('Spell', 'Unknown')}: {e}")
    
    logger.info(f"Finished loading {csv_path.name}")


def load_powers_csv(loader: GearLoader, csv_path: Path):
    """Load POWERS.csv file"""
    logger.info(f"Loading {csv_path.name}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                item = GearItem(
                    name=row['Power'].strip(),
                    category='power',
                    subcategory=row.get('Type', '').strip() or None,
                    base_stats={
                        'cost': float(row.get('Cost', 0)) if row.get('Cost') else None,
                    },
                    description=row.get('Description', '').strip() or None,
                    source=row.get('Source', '').strip() or None,
                )
                
                loader.load_item(item, csv_path.name, data_quality=8)
                
            except Exception as e:
                logger.error(f"Error parsing row: {row.get('Power', 'Unknown')}: {e}")
    
    logger.info(f"Finished loading {csv_path.name}")


def main():
    """Main entry point"""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Database configuration
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'postgres'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', '')
    }
    
    # Data directory
    data_dir = Path('G:/My Drive/SR-ai/DataTables')
    
    # Create loader
    loader = GearLoader(db_config)
    
    try:
        loader.connect()
        
        # Load CSV files (high quality = 8)
        csv_files = {
            'CYBERWARE.csv': load_cyberware_csv,
            'TOTEMS.csv': load_totems_csv,
            'SPELLS.csv': load_spells_csv,
            'POWERS.csv': load_powers_csv,
        }
        
        for filename, load_func in csv_files.items():
            csv_path = data_dir / filename
            if csv_path.exists():
                load_func(loader, csv_path)
            else:
                logger.warning(f"File not found: {csv_path}")
        
        # Generate and display report
        print("\n" + loader.stats.generate_report())
        
        # Save report to file
        report_path = Path(__file__).parent / 'gear_load_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(loader.stats.generate_report())
        logger.info(f"Report saved to {report_path}")
        
    finally:
        loader.disconnect()


if __name__ == '__main__':
    main()
