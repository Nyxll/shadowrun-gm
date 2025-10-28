#!/usr/bin/env python3
"""
Check which totems have opposed categories (negative dice modifiers)
Usage: 
  python check-totem-opposed.py           # Show all totems with opposed categories
  python check-totem-opposed.py Oak       # Show specific totem details
  python check-totem-opposed.py Oak Bear  # Show multiple specific totems
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def main():
    """Check totems with opposed categories"""
    
    # Check if specific totem names were provided
    specific_totems = sys.argv[1:] if len(sys.argv) > 1 else None
    
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        cursor_factory=RealDictCursor
    )
    
    try:
        cursor = conn.cursor()
        
        # Get totems based on arguments
        if specific_totems:
            # Get specific totems (whether they have opposed categories or not)
            placeholders = ','.join(['%s'] * len(specific_totems))
            cursor.execute(f"""
                SELECT 
                    totem_name,
                    favored_categories,
                    opposed_categories,
                    bonus_dice,
                    penalty_dice,
                    spirit_type
                FROM totems
                WHERE totem_name = ANY(%s)
                ORDER BY totem_name
            """, (specific_totems,))
            
            totems_with_opposed = cursor.fetchall()
            
            print(f"\n{'='*80}")
            print(f"TOTEM DETAILS: {', '.join(specific_totems)}")
            print(f"{'='*80}\n")
            
            if not totems_with_opposed:
                print(f"❌ No totems found matching: {', '.join(specific_totems)}")
                print("\nAvailable totems:")
                cursor.execute("SELECT totem_name FROM totems ORDER BY totem_name")
                all_totems = cursor.fetchall()
                for t in all_totems[:10]:  # Show first 10
                    print(f"  - {t['totem_name']}")
                if len(all_totems) > 10:
                    print(f"  ... and {len(all_totems) - 10} more")
                return
            
            for totem in totems_with_opposed:
                print(f"📋 {totem['totem_name']}")
                print(f"   Favored: {', '.join(totem['favored_categories']) if totem['favored_categories'] else 'None'}")
                print(f"   Opposed: {', '.join(totem['opposed_categories']) if totem['opposed_categories'] else 'None'}")
                print(f"   Bonus: +{totem['bonus_dice']} dice | Penalty: {totem['penalty_dice']} dice")
                print(f"   Spirit: {totem['spirit_type']}")
                print()
            
            # Also check if any characters have these totems
            print(f"\n{'='*80}")
            print(f"CHARACTERS WITH THESE TOTEMS")
            print(f"{'='*80}\n")
            
            cursor.execute("""
                SELECT name, totem, current_magic
                FROM characters
                WHERE totem = ANY(%s)
                ORDER BY name
            """, (specific_totems,))
            
            chars = cursor.fetchall()
            if chars:
                for char in chars:
                    print(f"  • {char['name']}: {char['totem']} (Magic {char['current_magic']})")
            else:
                print(f"  No characters found with totems: {', '.join(specific_totems)}")
            print()
            
            return
        
        # Original behavior: Get all totems with opposed categories
        cursor.execute("""
            SELECT 
                totem_name,
                favored_categories,
                opposed_categories,
                bonus_dice,
                penalty_dice,
                spirit_type
            FROM totems
            WHERE opposed_categories IS NOT NULL
            ORDER BY totem_name
        """)
        
        totems_with_opposed = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"TOTEMS WITH OPPOSED CATEGORIES (Negative Dice Modifiers)")
        print(f"{'='*80}\n")
        
        if not totems_with_opposed:
            print("❌ No totems found with opposed categories!")
            print("This means the opposed_categories column is NULL for all totems.")
        else:
            print(f"✓ Found {len(totems_with_opposed)} totems with opposed categories:\n")
            
            for totem in totems_with_opposed:
                print(f"📋 {totem['totem_name']}")
                print(f"   Favored: {', '.join(totem['favored_categories']) if totem['favored_categories'] else 'None'}")
                print(f"   Opposed: {', '.join(totem['opposed_categories'])}")
                print(f"   Bonus: +{totem['bonus_dice']} dice | Penalty: {totem['penalty_dice']} dice")
                print(f"   Spirit: {totem['spirit_type']}")
                print()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM totems")
        total = cursor.fetchone()['total']
        
        print(f"{'='*80}")
        print(f"Summary: {len(totems_with_opposed)} of {total} totems have opposed categories")
        print(f"{'='*80}\n")
        
        # Show examples of how penalties work
        if totems_with_opposed:
            print("Example Mechanics:")
            print("-" * 80)
            example = totems_with_opposed[0]
            print(f"\n{example['totem_name']} shaman casting spells:")
            
            if example['favored_categories']:
                fav = example['favored_categories'][0]
                print(f"  • {fav} spell: Gets +{example['bonus_dice']} dice bonus")
            
            if example['opposed_categories']:
                opp = example['opposed_categories'][0]
                print(f"  • {opp} spell: Gets {example['penalty_dice']} dice penalty")
            
            print(f"\nExample: Sorcery 6 + Magic Pool 3 = 9 dice base")
            if example['favored_categories']:
                print(f"  Favored spell: 9 + {example['bonus_dice']} = {9 + example['bonus_dice']} dice")
            if example['opposed_categories']:
                print(f"  Opposed spell: 9 + ({example['penalty_dice']}) = {9 + example['penalty_dice']} dice")
            print()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
