#!/usr/bin/env python3
"""
Shadowrun Dice Roller
Implements Shadowrun 2nd Edition dice mechanics including:
- Exploding 6s (Rule of 6)
- Target number success counting
- Opposed rolls
- Initiative tracking
- Karma pool mechanics
"""

import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class DiceRoll:
    """Result of a dice roll"""
    rolls: List[int]
    successes: int
    target_number: int
    pool_size: int
    notation: str
    all_ones: bool = False
    critical_glitch: bool = False


class DiceRoller:
    """Shadowrun dice rolling engine"""
    
    @staticmethod
    def parse_notation(notation: str) -> Tuple[int, int, int, bool]:
        """
        Parse dice notation like "6d6+2" or "4d6!"
        Returns: (count, sides, modifier, exploding)
        """
        notation = notation.strip().lower()
        exploding = notation.endswith('!')
        if exploding:
            notation = notation[:-1]
        
        # Split on 'd'
        parts = notation.split('d')
        if len(parts) != 2:
            raise ValueError(f"Invalid dice notation: {notation}")
        
        count = int(parts[0])
        
        # Check for modifier
        modifier = 0
        sides_part = parts[1]
        if '+' in sides_part:
            sides, mod = sides_part.split('+')
            sides = int(sides)
            modifier = int(mod)
        elif '-' in sides_part:
            sides, mod = sides_part.split('-')
            sides = int(sides)
            modifier = -int(mod)
        else:
            sides = int(sides_part)
        
        return count, sides, modifier, exploding
    
    @staticmethod
    def roll_single_die(sides: int = 6) -> int:
        """Roll a single die"""
        return random.randint(1, sides)
    
    @staticmethod
    def roll_with_target_number(
        pool: int,
        target_number: int,
        sides: int = 6,
        exploding: bool = True
    ) -> DiceRoll:
        """
        Roll dice pool against target number (Shadowrun style)
        
        Args:
            pool: Number of dice to roll
            target_number: Target number for success
            sides: Number of sides on each die (default 6)
            exploding: Whether 6s explode (Rule of 6)
        
        Returns:
            DiceRoll object with results
        """
        rolls = []
        successes = 0
        
        for _ in range(pool):
            roll = DiceRoller.roll_single_die(sides)
            combined_value = roll
            
            # Exploding dice (Rule of 6) - combine into single value
            if exploding:
                while roll == sides:
                    roll = DiceRoller.roll_single_die(sides)
                    combined_value += roll
            
            # Add the combined value (e.g., 6+4=10)
            rolls.append(combined_value)
            
            # Check for success on combined value
            if combined_value >= target_number:
                successes += 1
        
        # Check for all ones (critical glitch)
        all_ones = all(r == 1 for r in rolls)
        
        return DiceRoll(
            rolls=rolls,
            successes=successes,
            target_number=target_number,
            pool_size=pool,
            notation=f"{pool}d{sides}{'!' if exploding else ''}",
            all_ones=all_ones,
            critical_glitch=all_ones and successes == 0
        )
    
    @staticmethod
    def roll_opposed(
        pool1: int,
        tn1: int,
        pool2: int,
        tn2: int,
        sides: int = 6,
        exploding: bool = True
    ) -> Dict[str, Any]:
        """
        Roll opposed test between two sides
        
        Returns:
            Dictionary with both rolls and net successes
        """
        roll1 = DiceRoller.roll_with_target_number(pool1, tn1, sides, exploding)
        roll2 = DiceRoller.roll_with_target_number(pool2, tn2, sides, exploding)
        
        net_successes = roll1.successes - roll2.successes
        
        if net_successes > 0:
            winner = "side1"
        elif net_successes < 0:
            winner = "side2"
        else:
            winner = "tie"
        
        return {
            "side1": {
                "pool": pool1,
                "target_number": tn1,
                "rolls": roll1.rolls,
                "successes": roll1.successes,
                "all_ones": roll1.all_ones
            },
            "side2": {
                "pool": pool2,
                "target_number": tn2,
                "rolls": roll2.rolls,
                "successes": roll2.successes,
                "all_ones": roll2.all_ones
            },
            "net_successes": abs(net_successes),
            "winner": winner
        }
    
    @staticmethod
    def roll_initiative(notation: str) -> Dict[str, Any]:
        """
        Roll initiative (never exploding in Shadowrun)
        
        Args:
            notation: Dice notation like "2d6+10"
        
        Returns:
            Dictionary with initiative score and breakdown
        """
        count, sides, modifier, _ = DiceRoller.parse_notation(notation)
        
        rolls = [DiceRoller.roll_single_die(sides) for _ in range(count)]
        total = sum(rolls) + modifier
        
        # Calculate initiative passes (every 10 points = 1 pass)
        passes = 1 + (total // 10)
        
        return {
            "notation": notation,
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "passes": passes,
            "breakdown": f"{'+'.join(map(str, rolls))} + {modifier} = {total}"
        }
    
    @staticmethod
    def track_initiative(characters: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Track initiative for multiple characters
        
        Args:
            characters: List of dicts with 'name' and 'notation' keys
        
        Returns:
            Dictionary with sorted initiative order and phase breakdown
        """
        results = []
        
        for char in characters:
            name = char.get('name', 'Unknown')
            notation = char.get('notation', '1d6')
            
            init_roll = DiceRoller.roll_initiative(notation)
            results.append({
                "name": name,
                "notation": notation,
                "total": init_roll['total'],
                "passes": init_roll['passes'],
                "rolls": init_roll['rolls'],
                "modifier": init_roll['modifier']
            })
        
        # Sort by initiative total (highest first)
        results.sort(key=lambda x: x['total'], reverse=True)
        
        # Build phase breakdown
        max_passes = max(r['passes'] for r in results)
        phases = []
        
        for phase in range(1, max_passes + 1):
            phase_order = [
                r['name'] for r in results 
                if r['passes'] >= phase
            ]
            phases.append({
                "phase": phase,
                "active_characters": phase_order
            })
        
        return {
            "initiative_order": results,
            "phases": phases,
            "max_passes": max_passes
        }
    
    @staticmethod
    def roll_with_pools(
        pools: List[Dict[str, str]],
        target_number: int,
        sides: int = 6,
        exploding: bool = True
    ) -> Dict[str, Any]:
        """
        Roll multiple dice pools (skill, combat pool, karma pool, etc.)
        
        Args:
            pools: List of dicts with 'name' and 'notation' keys
            target_number: Target number for all pools
            sides: Die sides
            exploding: Whether dice explode
        
        Returns:
            Dictionary with individual pool results and totals
        """
        pool_results = []
        total_successes = 0
        all_rolls = []
        
        for pool_def in pools:
            name = pool_def.get('name', 'Unknown Pool')
            notation = pool_def.get('notation', '0d6')
            
            count, _, modifier, _ = DiceRoller.parse_notation(notation)
            
            if count > 0:
                roll = DiceRoller.roll_with_target_number(
                    count, target_number, sides, exploding
                )
                
                pool_results.append({
                    "name": name,
                    "notation": notation,
                    "rolls": roll.rolls,
                    "successes": roll.successes,
                    "all_ones": roll.all_ones
                })
                
                total_successes += roll.successes
                all_rolls.extend(roll.rolls)
        
        return {
            "pools": pool_results,
            "total_successes": total_successes,
            "target_number": target_number,
            "all_rolls": all_rolls
        }
    
    @staticmethod
    def buy_karma_dice(
        karma_dice_count: int,
        target_number: int,
        sides: int = 6,
        exploding: bool = True,
        max_allowed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Buy karma dice (costs 1 karma per die, max usually = karma pool rating)
        
        Args:
            karma_dice_count: Number of karma dice to buy
            target_number: Target number for successes
            sides: Die sides
            exploding: Whether dice explode
            max_allowed: Maximum karma dice allowed (optional)
        
        Returns:
            Dictionary with karma dice results
        """
        if max_allowed and karma_dice_count > max_allowed:
            return {
                "error": f"Cannot buy {karma_dice_count} karma dice (max: {max_allowed})",
                "karma_cost": 0,
                "successes": 0
            }
        
        roll = DiceRoller.roll_with_target_number(
            karma_dice_count, target_number, sides, exploding
        )
        
        return {
            "karma_dice_bought": karma_dice_count,
            "karma_cost": karma_dice_count,
            "rolls": roll.rolls,
            "successes": roll.successes,
            "target_number": target_number,
            "all_ones": roll.all_ones
        }
    
    @staticmethod
    def buy_successes(
        current_successes: int,
        successes_to_buy: int
    ) -> Dict[str, Any]:
        """
        Buy successes with karma (2 karma per success)
        
        Args:
            current_successes: Current number of successes
            successes_to_buy: Number of successes to buy
        
        Returns:
            Dictionary with new total and karma cost
        """
        karma_cost = successes_to_buy * 2
        new_total = current_successes + successes_to_buy
        
        return {
            "current_successes": current_successes,
            "successes_bought": successes_to_buy,
            "karma_cost": karma_cost,
            "new_total": new_total
        }
    
    @staticmethod
    def reroll_failures(
        failed_dice: List[int],
        target_number: int,
        sides: int = 6,
        exploding: bool = True,
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Reroll failed dice (e.g., with karma or second chance)
        
        Args:
            failed_dice: List of failed die results
            target_number: Target number for success
            sides: Die sides
            exploding: Whether dice explode
            iteration: Which reroll iteration this is
        
        Returns:
            Dictionary with reroll results
        """
        rerolls = []
        new_successes = 0
        still_failed = []
        
        for _ in failed_dice:
            roll = DiceRoller.roll_single_die(sides)
            rerolls.append(roll)
            
            if roll >= target_number:
                new_successes += 1
            else:
                still_failed.append(roll)
            
            # Handle exploding
            if exploding:
                while roll == sides:
                    roll = DiceRoller.roll_single_die(sides)
                    rerolls.append(roll)
                    if roll >= target_number:
                        new_successes += 1
        
        return {
            "reroll_iteration": iteration,
            "dice_rerolled": len(failed_dice),
            "rerolls": rerolls,
            "new_successes": new_successes,
            "still_failed": still_failed,
            "target_number": target_number
        }
    
    @staticmethod
    def avoid_disaster(roll_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avoid critical glitch by spending karma (all 1s rolled)
        
        Args:
            roll_result: Previous roll result with all_ones=True
        
        Returns:
            Dictionary indicating if disaster was avoided
        """
        if not roll_result.get('all_ones', False):
            return {
                "error": "No critical glitch to avoid",
                "karma_cost": 0,
                "disaster_avoided": False
            }
        
        return {
            "disaster_avoided": True,
            "karma_cost": 1,
            "message": "Spent 1 karma to avoid critical glitch"
        }
