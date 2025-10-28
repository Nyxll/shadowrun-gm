#!/usr/bin/env python3
"""
Interactive Training Processor - Python Version

Dual-mode operation:
  - Interactive menu for guided workflow
  - Direct command-line for automation

Usage:
  python tools/training-processor.py                    # Interactive menu
  python tools/training-processor.py --op=classify      # Direct operation
  python tools/training-processor.py --op=path/to/op.json  # Custom operation
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Any

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5434'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}

class TrainingProcessor:
    """Main training processor class"""
    
    def __init__(self):
        self.conn = None
        self.operations_dir = 'train/operations'
        self.prompts_dir = 'train/prompts'
        self.ensure_operations_dir()
    
    def ensure_operations_dir(self):
        """Create operations directory if it doesn't exist"""
        os.makedirs(self.operations_dir, exist_ok=True)
        os.makedirs('train/custom', exist_ok=True)
        os.makedirs(self.prompts_dir, exist_ok=True)
    
    def load_prompt(self, prompt_name: str, **variables) -> str:
        """Load and populate prompt template"""
        prompt_path = os.path.join(self.prompts_dir, f'{prompt_name}.txt')
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Replace variables
            prompt = template.format(**variables)
            return prompt
            
        except FileNotFoundError:
            print(f"⚠️  Prompt template not found: {prompt_path}")
            return f"[Prompt template '{prompt_name}' not found]"
        except KeyError as e:
            print(f"⚠️  Missing variable in prompt: {e}")
            return template
    
    def get_training_examples(self, intent: str, limit: int = 3) -> str:
        """Get similar training examples from corpus"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT text, category
                FROM training_corpus
                WHERE category ILIKE %s
                ORDER BY RANDOM()
                LIMIT %s
            """, (f'%{intent}%', limit))
            
            examples = cursor.fetchall()
            cursor.close()
            
            if not examples:
                return "[No similar examples found in training corpus]"
            
            result = []
            for i, ex in enumerate(examples, 1):
                result.append(f"Example {i} ({ex['category']}):\n{ex['text']}\n")
            
            return '\n'.join(result)
            
        except Exception as e:
            cursor.close()
            return f"[Error fetching examples: {e}]"
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            print("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            print("\n✅ Disconnected from database")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get training statistics"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN gm_response IS NOT NULL THEN 1 ELSE 0 END) as processed,
                SUM(CASE WHEN gm_response IS NULL THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN intent = expected_intent THEN 1 ELSE 0 END) as correct,
                SUM(CASE WHEN intent != expected_intent AND intent IS NOT NULL THEN 1 ELSE 0 END) as incorrect
            FROM query_logs
            WHERE is_training_data = TRUE
        """)
        
        stats = cursor.fetchone()
        cursor.close()
        
        # Calculate accuracy
        if stats['processed'] > 0:
            stats['accuracy'] = (stats['correct'] / stats['processed']) * 100
        else:
            stats['accuracy'] = 0
        
        return dict(stats)
    
    def show_stats(self):
        """Display training statistics"""
        stats = self.get_stats()
        
        print("\n" + "="*80)
        print("TRAINING STATISTICS")
        print("="*80)
        print(f"Total Queries:     {stats['total']:5}")
        print(f"Processed:         {stats['processed']:5} ({stats['processed']/stats['total']*100:.1f}%)")
        print(f"Pending:           {stats['pending']:5}")
        print(f"Correct:           {stats['correct']:5}")
        print(f"Incorrect:         {stats['incorrect']:5}")
        print(f"Accuracy:          {stats['accuracy']:.1f}%")
        print("="*80)
    
    def get_next_query(self) -> Optional[Dict]:
        """Get next unprocessed training query"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, query_text, expected_intent
            FROM query_logs
            WHERE is_training_data = TRUE
              AND gm_response IS NULL
            ORDER BY id
            LIMIT 1
        """)
        
        query = cursor.fetchone()
        cursor.close()
        
        return dict(query) if query else None
    
    def classify_query(self, query_text: str) -> Dict[str, Any]:
        """
        Classify a query using intent classifier
        TODO: Integrate with actual intent classifier
        For now, returns mock classification
        """
        # This would integrate with lib/intent/intent-classifier.js equivalent
        # For now, return mock data
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'method': 'manual'
        }
    
    def save_response(self, query_id: int, classification: Dict, gm_response: str, dice_rolls: List[Dict]):
        """Save training response to database"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE query_logs
                SET 
                    intent = %s,
                    confidence = %s,
                    classification_method = %s,
                    classification = %s,
                    gm_response = %s,
                    dice_rolls = %s
                WHERE id = %s
            """, (
                classification['intent'],
                classification['confidence'],
                classification['method'],
                json.dumps(classification),
                gm_response,
                json.dumps(dice_rolls),
                query_id
            ))
            
            self.conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error saving response: {e}")
            cursor.close()
            return False
    
    def get_corpus_count(self) -> int:
        """Get count of training corpus examples"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM training_corpus")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except:
            cursor.close()
            return 0
    
    def generate_ai_response(self, query_text: str, intent: str, expected_intent: str) -> str:
        """
        Generate AI GM response to the query using prompt template
        """
        # Get training examples
        training_examples = self.get_training_examples(intent)
        
        # Load system context
        system_context = self.load_prompt(
            'system-context',
            corpus_count=self.get_corpus_count()
        )
        
        # Load and populate prompt
        prompt = self.load_prompt(
            'gm-response',
            system_context=system_context,
            query_text=query_text,
            intent=intent,
            expected_intent=expected_intent,
            training_examples=training_examples
        )
        
        # Show prompt to user
        print("\n" + "="*80)
        print("PROMPT THAT WILL BE SENT TO AI:")
        print("="*80)
        print(prompt)
        print("="*80)
        
        # Ask if user wants to send to AI
        send_to_ai = input("\nSend this prompt to AI? (y/n/skip): ").strip().lower()
        
        if send_to_ai == 'skip':
            return None
        elif send_to_ai == 'y':
            # TODO: Actually call AI API here
            # For now, return template response
            return f"[AI would generate response here based on the prompt above]\n\nThis is a placeholder. When AI integration is complete, this will be the actual AI-generated response matching your GM style."
        else:
            # User declined, return None to skip
            return None
    
    def process_query_interactive(self, query: Dict) -> bool:
        """Process a single query interactively"""
        print("\n" + "="*80)
        print(f"QUERY #{query['id']}")
        print("="*80)
        print(f"\nPlayer Query: \"{query['query_text']}\"")
        print(f"\nExpected Intent: {query['expected_intent']}")
        
        # Classify
        print("\nClassifying...")
        classification = self.classify_query(query['query_text'])
        
        print(f"\nDetected Intent: {classification['intent']}")
        print(f"Confidence: {classification['confidence']*100:.1f}%")
        print(f"Method: {classification['method']}")
        
        is_correct = classification['intent'] == query['expected_intent']
        print(f"\n{'✓ CORRECT' if is_correct else '✗ INCORRECT'} Classification")
        
        # Generate AI response
        print("\n" + "-"*80)
        print("AI-GENERATED GM RESPONSE:")
        print("-"*80)
        
        ai_response = self.generate_ai_response(
            query['query_text'], 
            classification['intent'],
            query['expected_intent']
        )
        
        # If user skipped prompt, skip this query
        if ai_response is None:
            print("\nSkipping this query...")
            return False
        
        print(f"\n{ai_response}")
        
        # Let user confirm or edit
        print("\n" + "-"*80)
        print("Options:")
        print("  1. Accept AI response (press Enter)")
        print("  2. Edit response (type 'edit')")
        print("  3. Write new response (type 'new')")
        print("  4. Skip this query (type 'skip')")
        print("-"*80)
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'skip':
            print("\nSkipping this query...")
            return False
        elif choice == 'edit':
            print("\nEdit the AI response below (press Ctrl+D or Ctrl+Z when done):")
            print("Current response:")
            print(ai_response)
            print("\nEnter your edited version:")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            gm_response = '\n'.join(lines).strip()
            if not gm_response:
                gm_response = ai_response
        elif choice == 'new':
            print("\nEnter your GM response (press Ctrl+D or Ctrl+Z when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            gm_response = '\n'.join(lines).strip()
            if not gm_response:
                print("\nNo response entered, skipping...")
                return False
        else:
            # Accept AI response
            gm_response = ai_response
        
        # Get dice rolls
        print("\n" + "-"*80)
        print("DICE ROLLS:")
        print("-"*80)
        
        needs_dice = input("\nDoes this query require dice rolls? (y/n): ").lower()
        dice_rolls = []
        
        if needs_dice == 'y':
            while True:
                print("\nEnter dice roll details:")
                
                roll_type = input("  Type (attack/defense/skill/resistance/initiative): ")
                skill = input("  Skill/Attribute name: ")
                notation = input("  Notation (e.g., '6d6!' or '[Unarmed]d6!'): ")
                target_number = input("  Target Number (or press Enter if none): ")
                reason = input("  Reason/Description: ")
                
                dice_rolls.append({
                    'type': roll_type,
                    'skill': skill,
                    'notation': notation,
                    'targetNumber': target_number if target_number else None,
                    'modifiers': [],
                    'reason': reason
                })
                
                add_another = input("\nAdd another dice roll? (y/n): ").lower()
                if add_another != 'y':
                    break
        
        # Show summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"\nQuery: \"{query['query_text'][:60]}...\"")
        print(f"Expected: {query['expected_intent']}")
        print(f"Detected: {classification['intent']} ({'CORRECT' if is_correct else 'INCORRECT'})")
        print(f"\nGM Response:\n{gm_response}")
        
        if dice_rolls:
            print(f"\nDice Rolls: {len(dice_rolls)} roll(s)")
            for i, roll in enumerate(dice_rolls, 1):
                print(f"  {i}. {roll['type']}: {roll['skill']} ({roll['notation']})")
        
        # Confirm save
        confirm = input("\nSave this response? (y/n): ").lower()
        
        if confirm == 'y':
            if self.save_response(query['id'], classification, gm_response, dice_rolls):
                print("\n✅ Saved successfully!")
                return True
            else:
                print("\n❌ Failed to save")
                return False
        else:
            print("\nNot saved. Moving to next query...")
            return False
    
    def run_interactive(self):
        """Run interactive menu mode"""
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║         SHADOWRUN GM - TRAINING PROCESSOR (Python)            ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        
        self.show_stats()
        
        print("\nCommands:")
        print("  - Press Enter to process next query")
        print("  - Type 'stats' to show progress")
        print("  - Type 'quit' to exit")
        
        while True:
            command = input("\n> ").strip().lower()
            
            if command == 'quit':
                break
            
            if command == 'stats':
                self.show_stats()
                continue
            
            # Get next query
            query = self.get_next_query()
            
            if not query:
                print("\n🎉 All training queries have been processed!")
                self.show_stats()
                break
            
            # Process query
            self.process_query_interactive(query)
            
            # Show updated stats
            self.show_stats()
        
        print("\n✅ Training session complete!")
    
    def run_operation(self, operation_name: str):
        """Run a specific operation"""
        # TODO: Load and execute operation from JSON
        print(f"\n🚀 Running operation: {operation_name}")
        print("(Operation system not yet implemented)")
        
        # For now, just run interactive mode
        self.run_interactive()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Shadowrun GM Training Processor')
    parser.add_argument('--op', type=str, help='Operation to run (name or path to JSON)')
    
    args = parser.parse_args()
    
    processor = TrainingProcessor()
    
    if not processor.connect():
        sys.exit(1)
    
    try:
        if args.op:
            # Direct operation mode
            processor.run_operation(args.op)
        else:
            # Interactive menu mode
            processor.run_interactive()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.disconnect()

if __name__ == '__main__':
    main()
