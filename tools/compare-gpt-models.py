#!/usr/bin/env python3
"""
GPT Model Comparison Script
Compares GPT-4o vs GPT-4o-mini for Shadowrun categorization task
"""

import os
import json
from openai import OpenAI
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComparisonResult:
    """Results from comparing two GPT model categorizations"""
    chunk_title: str
    content_preview: str
    gpt4o_result: Dict
    gpt4o_mini_result: Dict
    matches: bool
    differences: List[str]
    gpt4o_cost: float
    gpt4o_mini_cost: float

class GPTComparator:
    """Compare categorization results from GPT-4o and GPT-4o-mini"""
    
    def __init__(self):
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        
        # Pricing per 1M tokens (as of 2024)
        self.gpt4o_input_price = 2.50  # $2.50 per 1M input tokens
        self.gpt4o_output_price = 10.00  # $10.00 per 1M output tokens
        self.gpt4o_mini_input_price = 0.15  # $0.15 per 1M input tokens
        self.gpt4o_mini_output_price = 0.60  # $0.60 per 1M output tokens
        
    def categorize_with_model(self, model: str, title: str, content: str) -> tuple[Dict, int, int]:
        """
        Categorize content using specified GPT model
        Returns: (result_dict, input_tokens, output_tokens)
        """
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
                model=model,
                messages=[
                    {"role": "system", "content": "You are a Shadowrun 2nd Edition rules expert. Categorize content accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Get token usage
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Validate and normalize
            return {
                'category': result.get('category', 'general'),
                'subcategory': result.get('subcategory', ''),
                'tags': result.get('tags', []),
                'content_type': result.get('content_type', 'rule_mechanic')
            }, input_tokens, output_tokens
            
        except Exception as e:
            return {
                'category': 'ERROR',
                'subcategory': '',
                'tags': [],
                'content_type': 'ERROR',
                'error': str(e)
            }, 0, 0
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call"""
        if model == "gpt-4o":
            input_cost = (input_tokens / 1_000_000) * self.gpt4o_input_price
            output_cost = (output_tokens / 1_000_000) * self.gpt4o_output_price
        else:  # gpt-4o-mini
            input_cost = (input_tokens / 1_000_000) * self.gpt4o_mini_input_price
            output_cost = (output_tokens / 1_000_000) * self.gpt4o_mini_output_price
        
        return input_cost + output_cost
    
    def compare_results(self, title: str, content: str) -> ComparisonResult:
        """Compare categorization from both GPT models"""
        print(f"\nComparing: {title}")
        
        # Get results from GPT-4o
        print("  Querying GPT-4o...")
        gpt4o_result, gpt4o_in, gpt4o_out = self.categorize_with_model("gpt-4o", title, content)
        gpt4o_cost = self.calculate_cost("gpt-4o", gpt4o_in, gpt4o_out)
        
        # Get results from GPT-4o-mini
        print("  Querying GPT-4o-mini...")
        gpt4o_mini_result, mini_in, mini_out = self.categorize_with_model("gpt-4o-mini", title, content)
        mini_cost = self.calculate_cost("gpt-4o-mini", mini_in, mini_out)
        
        print(f"  Cost: GPT-4o=${gpt4o_cost:.4f}, GPT-4o-mini=${mini_cost:.4f} (Ratio: {gpt4o_cost/mini_cost:.1f}x)")
        
        # Compare results
        differences = []
        
        if gpt4o_result['category'] != gpt4o_mini_result['category']:
            differences.append(f"Category: GPT-4o={gpt4o_result['category']}, GPT-4o-mini={gpt4o_mini_result['category']}")
        
        if gpt4o_result['subcategory'] != gpt4o_mini_result['subcategory']:
            differences.append(f"Subcategory: GPT-4o={gpt4o_result['subcategory']}, GPT-4o-mini={gpt4o_mini_result['subcategory']}")
        
        if gpt4o_result['content_type'] != gpt4o_mini_result['content_type']:
            differences.append(f"Content Type: GPT-4o={gpt4o_result['content_type']}, GPT-4o-mini={gpt4o_mini_result['content_type']}")
        
        # Compare tags (order doesn't matter)
        gpt4o_tags = set(gpt4o_result['tags'])
        mini_tags = set(gpt4o_mini_result['tags'])
        if gpt4o_tags != mini_tags:
            only_gpt4o = gpt4o_tags - mini_tags
            only_mini = mini_tags - gpt4o_tags
            if only_gpt4o or only_mini:
                differences.append(f"Tags differ: GPT-4o only={list(only_gpt4o)}, Mini only={list(only_mini)}")
        
        matches = len(differences) == 0
        
        return ComparisonResult(
            chunk_title=title,
            content_preview=content[:200] + "...",
            gpt4o_result=gpt4o_result,
            gpt4o_mini_result=gpt4o_mini_result,
            matches=matches,
            differences=differences,
            gpt4o_cost=gpt4o_cost,
            gpt4o_mini_cost=mini_cost
        )


def load_sample_chunks() -> List[Dict]:
    """Load sample chunks for testing"""
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
        },
        {
            "title": "Karma Pool",
            "content": """## Karma Pool

The Karma Pool represents a character's accumulated good fortune and experience. Players can spend Karma Pool dice to re-roll failed dice, buy additional dice for tests, or even buy raw successes (requires at least one natural success). Karma Pool is a limited resource that refreshes slowly, making it a strategic choice when to use it."""
        },
        {
            "title": "Smartgun System",
            "content": """## Smartgun System

A smartgun system links a weapon directly to the user's cybernetic systems, providing a +2 bonus to attack rolls. The system displays ammunition count, range to target, and weapon status directly in the user's field of vision. Requires a smartgun link (cyberware) and a smartgun-equipped weapon. The bonus applies to all attacks made with the linked weapon."""
        },
        {
            "title": "Astral Perception",
            "content": """## Astral Perception

Magically active characters can perceive the astral plane while remaining in the physical world. This allows them to see auras, detect magical activity, and identify other astral beings. Using Astral Perception requires a Simple Action and can be maintained as long as the character concentrates. While perceiving astrally, the character's physical perception is reduced."""
        }
    ]
    
    return samples


def print_comparison_report(results: List[ComparisonResult]):
    """Print a detailed comparison report"""
    print("\n" + "=" * 80)
    print("GPT MODEL COMPARISON REPORT")
    print("GPT-4o vs GPT-4o-mini")
    print("=" * 80)
    
    total = len(results)
    matches = sum(1 for r in results if r.matches)
    accuracy = (matches / total * 100) if total > 0 else 0
    
    total_gpt4o_cost = sum(r.gpt4o_cost for r in results)
    total_mini_cost = sum(r.gpt4o_mini_cost for r in results)
    
    print(f"\nOverall Statistics:")
    print(f"  Total chunks compared: {total}")
    print(f"  Perfect matches: {matches} ({accuracy:.1f}%)")
    print(f"  Differences found: {total - matches} ({100 - accuracy:.1f}%)")
    print(f"\nCost Comparison:")
    print(f"  GPT-4o total: ${total_gpt4o_cost:.4f}")
    print(f"  GPT-4o-mini total: ${total_mini_cost:.4f}")
    print(f"  Cost ratio: {total_gpt4o_cost/total_mini_cost:.1f}x more expensive")
    print(f"  Extra cost for GPT-4o: ${total_gpt4o_cost - total_mini_cost:.4f}")
    
    print("\n" + "-" * 80)
    print("DETAILED RESULTS")
    print("-" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.chunk_title}")
        print(f"   Content: {result.content_preview[:100]}...")
        print(f"   Cost: GPT-4o=${result.gpt4o_cost:.4f}, Mini=${result.gpt4o_mini_cost:.4f}")
        
        if result.matches:
            print("   ✅ MATCH - Both models agree")
            print(f"   Category: {result.gpt4o_mini_result['category']}")
            print(f"   Subcategory: {result.gpt4o_mini_result['subcategory']}")
            print(f"   Tags: {result.gpt4o_mini_result['tags']}")
            print(f"   Type: {result.gpt4o_mini_result['content_type']}")
        else:
            print("   ⚠️  DIFFERENCE - Models disagree")
            print("\n   GPT-4o:")
            print(f"     Category: {result.gpt4o_result['category']}")
            print(f"     Subcategory: {result.gpt4o_result['subcategory']}")
            print(f"     Tags: {result.gpt4o_result['tags']}")
            print(f"     Type: {result.gpt4o_result['content_type']}")
            
            print("\n   GPT-4o-mini:")
            print(f"     Category: {result.gpt4o_mini_result['category']}")
            print(f"     Subcategory: {result.gpt4o_mini_result['subcategory']}")
            print(f"     Tags: {result.gpt4o_mini_result['tags']}")
            print(f"     Type: {result.gpt4o_mini_result['content_type']}")
            
            print("\n   Differences:")
            for diff in result.differences:
                print(f"     • {diff}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Category agreement
    category_matches = sum(1 for r in results if r.gpt4o_result['category'] == r.gpt4o_mini_result['category'])
    print(f"\nCategory Agreement: {category_matches}/{total} ({category_matches/total*100:.1f}%)")
    
    # Subcategory agreement
    subcat_matches = sum(1 for r in results if r.gpt4o_result['subcategory'] == r.gpt4o_mini_result['subcategory'])
    print(f"Subcategory Agreement: {subcat_matches}/{total} ({subcat_matches/total*100:.1f}%)")
    
    # Content type agreement
    type_matches = sum(1 for r in results if r.gpt4o_result['content_type'] == r.gpt4o_mini_result['content_type'])
    print(f"Content Type Agreement: {type_matches}/{total} ({type_matches/total*100:.1f}%)")
    
    # Tag similarity
    tag_similarities = []
    for r in results:
        gpt4o_tags = set(r.gpt4o_result['tags'])
        mini_tags = set(r.gpt4o_mini_result['tags'])
        if gpt4o_tags or mini_tags:
            similarity = len(gpt4o_tags & mini_tags) / len(gpt4o_tags | mini_tags)
            tag_similarities.append(similarity)
    
    if tag_similarities:
        avg_tag_similarity = sum(tag_similarities) / len(tag_similarities)
        print(f"Average Tag Similarity: {avg_tag_similarity*100:.1f}%")
    
    # Extrapolate to full migration (287 chunks)
    print("\n" + "=" * 80)
    print("FULL MIGRATION COST ESTIMATE (287 chunks)")
    print("=" * 80)
    
    avg_gpt4o_cost = total_gpt4o_cost / total
    avg_mini_cost = total_mini_cost / total
    
    full_gpt4o_cost = avg_gpt4o_cost * 287
    full_mini_cost = avg_mini_cost * 287
    
    print(f"\nEstimated costs for 287 chunks:")
    print(f"  GPT-4o: ${full_gpt4o_cost:.2f}")
    print(f"  GPT-4o-mini: ${full_mini_cost:.2f}")
    print(f"  Extra cost for GPT-4o: ${full_gpt4o_cost - full_mini_cost:.2f}")
    print(f"  Cost multiplier: {full_gpt4o_cost/full_mini_cost:.1f}x")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    improvement = 100 - accuracy
    cost_diff = total_gpt4o_cost - total_mini_cost
    
    if accuracy >= 95:
        print("\n✅ GPT-4o-mini is excellent! No need for GPT-4o.")
        print(f"   Both models agree {accuracy:.1f}% of the time.")
        print(f"   Save ${full_gpt4o_cost - full_mini_cost:.2f} by using GPT-4o-mini.")
    elif accuracy >= 85:
        print("\n⚠️  GPT-4o shows minor improvements over GPT-4o-mini.")
        print(f"   Agreement: {accuracy:.1f}%")
        print(f"   Extra cost: ${full_gpt4o_cost - full_mini_cost:.2f}")
        print("\n   Consider:")
        print("   - Use GPT-4o-mini for most chunks (save money)")
        print("   - Manually review the ~10-15% that might differ")
        print("   - Or use GPT-4o if perfect accuracy is critical")
    else:
        print("\n💡 GPT-4o provides better categorization than GPT-4o-mini.")
        print(f"   Agreement: {accuracy:.1f}%")
        print(f"   Extra cost: ${full_gpt4o_cost - full_mini_cost:.2f}")
        print("\n   Decision:")
        print(f"   - Is {improvement:.1f}% better accuracy worth ${full_gpt4o_cost - full_mini_cost:.2f}?")
        print("   - For this one-time migration, probably yes if budget allows")
        print("   - Otherwise, GPT-4o-mini + manual review is still good")


def main():
    """Main comparison process"""
    print("=" * 80)
    print("GPT MODEL COMPARISON: GPT-4o vs GPT-4o-mini")
    print("=" * 80)
    print("\nThis script compares categorization quality and cost between")
    print("GPT-4o and GPT-4o-mini to help you choose the best model.\n")
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nSet it with:")
        print('  $env:OPENAI_API_KEY="sk-your-key-here"')
        return
    
    try:
        comparator = GPTComparator()
        print("✓ OpenAI connection successful\n")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        return
    
    # Load sample chunks
    samples = load_sample_chunks()
    print(f"Loaded {len(samples)} sample chunks for comparison\n")
    print("Note: This will cost approximately $0.02-0.03 in API calls\n")
    
    response = input("Proceed with comparison? (yes/no): ")
    if response.lower() != 'yes':
        print("Comparison cancelled")
        return
    
    # Compare each chunk
    results = []
    for sample in samples:
        result = comparator.compare_results(sample['title'], sample['content'])
        results.append(result)
    
    # Print report
    print_comparison_report(results)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"gpt_comparison_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump([{
            'title': r.chunk_title,
            'gpt4o': r.gpt4o_result,
            'gpt4o_mini': r.gpt4o_mini_result,
            'matches': r.matches,
            'differences': r.differences,
            'gpt4o_cost': r.gpt4o_cost,
            'gpt4o_mini_cost': r.gpt4o_mini_cost
        } for r in results], f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
