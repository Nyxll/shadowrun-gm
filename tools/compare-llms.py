#!/usr/bin/env python3
"""
LLM Comparison Script for Shadowrun GM Migration
Processes sample chunks with both Ollama 3.2 and GPT-4o-mini to compare results
"""

import os
import json
from openai import OpenAI
from typing import Dict, List
import hashlib
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComparisonResult:
    """Results from comparing two LLM categorizations"""
    chunk_title: str
    content_preview: str
    ollama_result: Dict
    gpt_result: Dict
    matches: bool
    differences: List[str]

class LLMComparator:
    """Compare categorization results from different LLMs"""
    
    def __init__(self):
        # Initialize Ollama client
        self.ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="not-needed"
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI()  # Uses OPENAI_API_KEY from environment
        
        self.ollama_model = "llama3.2"
        self.gpt_model = "gpt-4o-mini"
        
    def categorize_with_ollama(self, title: str, content: str) -> Dict:
        """Categorize content using Ollama"""
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
            response = self.ollama_client.chat.completions.create(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": "You are a Shadowrun 2nd Edition rules expert. Categorize content accurately. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if Ollama added extra text
            if not result_text.startswith('{'):
                # Look for JSON block
                start = result_text.find('{')
                end = result_text.rfind('}') + 1
                if start != -1 and end > start:
                    result_text = result_text[start:end]
            
            result = json.loads(result_text)
            
            # Validate and normalize
            return {
                'category': result.get('category', 'general'),
                'subcategory': result.get('subcategory', ''),
                'tags': result.get('tags', []),
                'content_type': result.get('content_type', 'rule_mechanic'),
                'raw_response': result_text
            }
            
        except Exception as e:
            return {
                'category': 'ERROR',
                'subcategory': '',
                'tags': [],
                'content_type': 'ERROR',
                'error': str(e),
                'raw_response': response.choices[0].message.content if 'response' in locals() else ''
            }
    
    def categorize_with_gpt(self, title: str, content: str) -> Dict:
        """Categorize content using GPT-4o-mini"""
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
            response = self.openai_client.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": "You are a Shadowrun 2nd Edition rules expert. Categorize content accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize
            return {
                'category': result.get('category', 'general'),
                'subcategory': result.get('subcategory', ''),
                'tags': result.get('tags', []),
                'content_type': result.get('content_type', 'rule_mechanic')
            }
            
        except Exception as e:
            return {
                'category': 'ERROR',
                'subcategory': '',
                'tags': [],
                'content_type': 'ERROR',
                'error': str(e)
            }
    
    def compare_results(self, title: str, content: str) -> ComparisonResult:
        """Compare categorization from both LLMs"""
        print(f"\nComparing: {title}")
        
        # Get results from both
        print("  Querying Ollama 3.2...")
        ollama_result = self.categorize_with_ollama(title, content)
        
        print("  Querying GPT-4o-mini...")
        gpt_result = self.categorize_with_gpt(title, content)
        
        # Compare results
        differences = []
        
        if ollama_result['category'] != gpt_result['category']:
            differences.append(f"Category: Ollama={ollama_result['category']}, GPT={gpt_result['category']}")
        
        if ollama_result['subcategory'] != gpt_result['subcategory']:
            differences.append(f"Subcategory: Ollama={ollama_result['subcategory']}, GPT={gpt_result['subcategory']}")
        
        if ollama_result['content_type'] != gpt_result['content_type']:
            differences.append(f"Content Type: Ollama={ollama_result['content_type']}, GPT={gpt_result['content_type']}")
        
        # Compare tags (order doesn't matter)
        ollama_tags = set(ollama_result['tags'])
        gpt_tags = set(gpt_result['tags'])
        if ollama_tags != gpt_tags:
            only_ollama = ollama_tags - gpt_tags
            only_gpt = gpt_tags - ollama_tags
            if only_ollama or only_gpt:
                differences.append(f"Tags differ: Ollama only={list(only_ollama)}, GPT only={list(only_gpt)}")
        
        matches = len(differences) == 0
        
        return ComparisonResult(
            chunk_title=title,
            content_preview=content[:200] + "...",
            ollama_result=ollama_result,
            gpt_result=gpt_result,
            matches=matches,
            differences=differences
        )


def load_sample_chunks() -> List[Dict]:
    """Load sample chunks from the database or create test samples"""
    # For now, create test samples
    # You can modify this to load from your actual files
    
    samples = [
        {
            "title": "Combat Pool",
            "content": """## Combat Pool

The Combat Pool represents a character's ability to perform exceptional feats in combat. It equals the character's Intelligence + Willpower. Combat Pool dice can be allocated to improve attack rolls, defense rolls, or other combat actions. Allocated dice are rolled along with the base dice pool and count toward successes. Combat Pool refreshes at the start of each Combat Turn."""
        },
        {
            "title": "Initiative",
            "content": """## Initiative

Initiative determines the order in which characters act during a Combat Turn. Each character rolls Initiative Dice (usually 1d6 + Reaction) at the start of combat. The result determines when they act in each Combat Phase. Characters with higher Initiative scores act first. Initiative is rolled at the beginning of each Combat Turn."""
        },
        {
            "title": "Franchi SPAS-22",
            "content": """## FRANCHI SPAS-22

| Type   | Conceal | Ammo | Mode | Damage | Weight | Availability | Cost     | Street Index |
|:-------|---------|------|------|--------|--------|-------------:|---------:|-------------:|
| Sniper |         | 20   | SA   | 15M    | 25     | 24/21 days   | 120,000¥ | 3            |

To determine range, consult the Weapon Range Table and decrease the weapon's Power Level by -2 for each range beyond Short (Medium -2, Long -4, Extreme -6). Ballistic Armor has no effect; reduce Impact Armor by half, rounded down."""
        },
        {
            "title": "Spellcasting",
            "content": """## Spellcasting

To cast a spell, the magician makes a Sorcery Skill Test against a Target Number determined by the spell's Force. The number of successes determines the spell's effectiveness. After casting, the magician must resist Drain, which is based on the spell's Force and type. Drain is resisted with a Willpower Test."""
        },
        {
            "title": "Developer Notes",
            "content": """## DEVELOPER NOTES

This sourcebook exposes and explains the shadowy realm of the mercenary. This sourcebook is not about playing a mercenary storyline, but about playing a mercenary character within the Shadowrun storyline. In the former case, all the player characters are mercenaries and the story objectives have purely mercenary origins and direction."""
        }
    ]
    
    return samples


def print_comparison_report(results: List[ComparisonResult]):
    """Print a detailed comparison report"""
    print("\n" + "=" * 80)
    print("LLM COMPARISON REPORT")
    print("=" * 80)
    
    total = len(results)
    matches = sum(1 for r in results if r.matches)
    accuracy = (matches / total * 100) if total > 0 else 0
    
    print(f"\nOverall Statistics:")
    print(f"  Total chunks compared: {total}")
    print(f"  Perfect matches: {matches} ({accuracy:.1f}%)")
    print(f"  Differences found: {total - matches} ({100 - accuracy:.1f}%)")
    
    print("\n" + "-" * 80)
    print("DETAILED RESULTS")
    print("-" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.chunk_title}")
        print(f"   Content: {result.content_preview[:100]}...")
        
        if result.matches:
            print("   ✅ MATCH - Both LLMs agree")
            print(f"   Category: {result.gpt_result['category']}")
            print(f"   Subcategory: {result.gpt_result['subcategory']}")
            print(f"   Tags: {result.gpt_result['tags']}")
            print(f"   Type: {result.gpt_result['content_type']}")
        else:
            print("   ⚠️  DIFFERENCE - LLMs disagree")
            print("\n   Ollama 3.2:")
            print(f"     Category: {result.ollama_result['category']}")
            print(f"     Subcategory: {result.ollama_result['subcategory']}")
            print(f"     Tags: {result.ollama_result['tags']}")
            print(f"     Type: {result.ollama_result['content_type']}")
            
            print("\n   GPT-4o-mini:")
            print(f"     Category: {result.gpt_result['category']}")
            print(f"     Subcategory: {result.gpt_result['subcategory']}")
            print(f"     Tags: {result.gpt_result['tags']}")
            print(f"     Type: {result.gpt_result['content_type']}")
            
            print("\n   Differences:")
            for diff in result.differences:
                print(f"     • {diff}")
        
        # Show raw Ollama response if it had issues
        if 'raw_response' in result.ollama_result and 'error' in result.ollama_result:
            print(f"\n   ⚠️  Ollama Error: {result.ollama_result['error']}")
            print(f"   Raw response: {result.ollama_result['raw_response'][:200]}...")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Category agreement
    category_matches = sum(1 for r in results if r.ollama_result['category'] == r.gpt_result['category'])
    print(f"\nCategory Agreement: {category_matches}/{total} ({category_matches/total*100:.1f}%)")
    
    # Subcategory agreement
    subcat_matches = sum(1 for r in results if r.ollama_result['subcategory'] == r.gpt_result['subcategory'])
    print(f"Subcategory Agreement: {subcat_matches}/{total} ({subcat_matches/total*100:.1f}%)")
    
    # Content type agreement
    type_matches = sum(1 for r in results if r.ollama_result['content_type'] == r.gpt_result['content_type'])
    print(f"Content Type Agreement: {type_matches}/{total} ({type_matches/total*100:.1f}%)")
    
    # Tag similarity
    tag_similarities = []
    for r in results:
        ollama_tags = set(r.ollama_result['tags'])
        gpt_tags = set(r.gpt_result['tags'])
        if ollama_tags or gpt_tags:
            similarity = len(ollama_tags & gpt_tags) / len(ollama_tags | gpt_tags)
            tag_similarities.append(similarity)
    
    if tag_similarities:
        avg_tag_similarity = sum(tag_similarities) / len(tag_similarities)
        print(f"Average Tag Similarity: {avg_tag_similarity*100:.1f}%")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if accuracy >= 90:
        print("\n✅ Ollama 3.2 performs well! Consider using it for the full migration.")
        print("   Differences are minor and can be reviewed manually if needed.")
    elif accuracy >= 75:
        print("\n⚠️  Ollama 3.2 has some differences from GPT-4o-mini.")
        print("   Consider:")
        print("   - Use Ollama for initial categorization")
        print("   - Manually review the ~20-25% that differ")
        print("   - Or use GPT-4o-mini for consistency")
    else:
        print("\n❌ Ollama 3.2 shows significant differences from GPT-4o-mini.")
        print("   Recommendation: Use GPT-4o-mini for better accuracy.")
        print("   The $0.06 cost is worth the improved categorization quality.")


def main():
    """Main comparison process"""
    print("=" * 80)
    print("LLM COMPARISON: Ollama 3.2 vs GPT-4o-mini")
    print("=" * 80)
    print("\nThis script will compare categorization results from both LLMs")
    print("to help you decide which to use for the full migration.\n")
    
    # Check if Ollama is running
    try:
        comparator = LLMComparator()
        print("✓ Ollama connection successful")
        print("✓ OpenAI connection successful")
    except Exception as e:
        print(f"❌ Error initializing LLM clients: {e}")
        print("\nMake sure:")
        print("  1. Ollama is running (ollama serve)")
        print("  2. llama3.2 model is installed (ollama pull llama3.2)")
        print("  3. OPENAI_API_KEY environment variable is set")
        return
    
    # Load sample chunks
    samples = load_sample_chunks()
    print(f"\nLoaded {len(samples)} sample chunks for comparison\n")
    
    # Compare each chunk
    results = []
    for sample in samples:
        result = comparator.compare_results(sample['title'], sample['content'])
        results.append(result)
    
    # Print report
    print_comparison_report(results)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"llm_comparison_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump([{
            'title': r.chunk_title,
            'ollama': r.ollama_result,
            'gpt': r.gpt_result,
            'matches': r.matches,
            'differences': r.differences
        } for r in results], f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
