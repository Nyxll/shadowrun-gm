#!/usr/bin/env python3
"""
Roll Platinum's attack against the rat with combat pool
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.dice_roller import DiceRoller

def main():
    print("=" * 60)
    print("PLATINUM'S ATTACK ROLL")
    print("=" * 60)
    print()
    
    # Target number from previous calculation
    target_number = 15
    
    # Platinum is using 6 combat pool dice
    combat_pool = 6
    
    print(f"Target Number: {target_number}")
    print(f"Combat Pool Dice: {combat_pool}")
    print()
    print("Rolling...")
    print()
    
    # Roll the combat pool dice
    result = DiceRoller.roll_with_target_number(
        pool=combat_pool,
        target_number=target_number,
        sides=6,
        exploding=True  # Rule of 6 applies
    )
    
    print("=" * 60)
    print("DICE RESULTS")
    print("=" * 60)
    print()
    
    # Display individual rolls
    print(f"Dice Rolled: {result.rolls}")
    print()
    
    # Count successes (any die >= TN)
    successes = []
    failures = []
    for roll in result.rolls:
        if roll >= target_number:
            successes.append(roll)
        else:
            failures.append(roll)
    
    print(f"Successes (>= {target_number}): {successes if successes else 'None'}")
    print(f"Failures (< {target_number}): {failures if failures else 'None'}")
    print()
    
    print("=" * 60)
    print(f"TOTAL SUCCESSES: {result.successes}")
    print("=" * 60)
    print()
    
    # Interpret results
    if result.all_ones:
        print("⚠️  CRITICAL GLITCH! All dice came up 1!")
        print("The weapon jams or something goes terribly wrong!")
    elif result.successes == 0:
        print("❌ MISS! The shot goes wide in the darkness.")
        print("The rat scurries away unharmed.")
    elif result.successes == 1:
        print("✓ MARGINAL HIT! One success.")
        print("The shot grazes the rat but may not be enough to stop it.")
    elif result.successes >= 2:
        print(f"✓✓ SOLID HIT! {result.successes} successes!")
        print("The shot connects solidly with the rat.")
        if result.successes >= 3:
            print("Excellent shooting in such difficult conditions!")
    
    print()
    
    # Show exploding 6s if any
    sixes = [i for i, r in enumerate(result.rolls[:combat_pool]) if r == 6]
    if sixes:
        print(f"Rule of 6: {len(sixes)} dice exploded (rolled 6)")
        print(f"Additional rolls: {result.rolls[combat_pool:]}")
        print()

if __name__ == "__main__":
    main()
