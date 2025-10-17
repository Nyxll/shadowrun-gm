# Dice Rolling API Test Cases

This document contains comprehensive test cases for all 14 dice rolling tools in the Shadowrun Dice Rolling API.

## 1. roll_dice

**Purpose:** Roll dice using standard notation

### Test Case 1.1: Basic 2d6 Roll
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "2d6"
  },
  "expected": {
    "rolls": "array of 2 numbers between 1-6",
    "sum": "sum of rolls",
    "modifier": 0,
    "total": "sum + modifier"
  }
}
```

### Test Case 1.2: Roll with Positive Modifier
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "1d20+5"
  },
  "expected": {
    "rolls": "array of 1 number between 1-20",
    "sum": "value of roll",
    "modifier": 5,
    "total": "sum + 5"
  }
}
```

### Test Case 1.3: Roll with Negative Modifier
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "3d8-2"
  },
  "expected": {
    "rolls": "array of 3 numbers between 1-8",
    "sum": "sum of rolls",
    "modifier": -2,
    "total": "sum - 2"
  }
}
```

### Test Case 1.4: Single Die Roll
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "1d100"
  },
  "expected": {
    "rolls": "array of 1 number between 1-100",
    "sum": "value of roll",
    "modifier": 0,
    "total": "sum"
  }
}
```

### Test Case 1.5: Multiple Dice No Modifier
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "4d6"
  },
  "expected": {
    "rolls": "array of 4 numbers between 1-6",
    "sum": "sum of all rolls",
    "modifier": 0,
    "total": "sum"
  }
}
```

### Test Case 1.6: Exploding Dice
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "3d6!"
  },
  "expected": {
    "rolls": "array of 3+ numbers (can exceed 6 with explosions)",
    "sum": "sum of all rolls including explosions",
    "modifier": 0,
    "total": "sum",
    "exploding": true,
    "note": "When a die rolls max value, it explodes (rolls again and adds)"
  }
}
```

### Test Case 1.7: Exploding Dice with Modifier
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "2d6!+10"
  },
  "expected": {
    "rolls": "array of 2+ numbers (with explosions)",
    "sum": "sum of all rolls",
    "modifier": 10,
    "total": "sum + 10",
    "exploding": true
  }
}
```

### Test Case 1.8: Boundary - Minimum Dice (1d4)
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "1d4"
  },
  "expected": {
    "rolls": "array of 1 number between 1-4",
    "sum": "value between 1-4",
    "modifier": 0,
    "total": "sum"
  }
}
```

### Test Case 1.9: Boundary - Large Dice Pool
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "20d6"
  },
  "expected": {
    "rolls": "array of 20 numbers between 1-6",
    "sum": "sum of all 20 rolls (20-120)",
    "modifier": 0,
    "total": "sum"
  }
}
```

### Test Case 1.10: Negative - Invalid Notation (Missing Dice)
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "d6"
  },
  "expected": {
    "error": "Invalid notation format",
    "note": "Should require number before 'd'"
  }
}
```

### Test Case 1.11: Negative - Invalid Notation (Zero Dice)
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "0d6"
  },
  "expected": {
    "error": "Invalid dice count",
    "note": "Must have at least 1 die"
  }
}
```

### Test Case 1.12: Negative - Invalid Notation (Zero Sides)
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "2d0"
  },
  "expected": {
    "error": "Invalid die size",
    "note": "Die must have at least 1 side"
  }
}
```

### Test Case 1.13: Exploding Mechanic Verification - Single Explosion
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "1d6!"
  },
  "expected": {
    "rolls": "array with at least 1 number",
    "validation": {
      "if_max_rolled": "If any roll equals 6, verify array length > 1 (explosion occurred)",
      "explosion_value": "If explosion occurred, verify the exploded value > 6",
      "example": "Roll of [6, 4] means 6 exploded into 4, total value = 10"
    },
    "note": "When a 6 is rolled, it should explode and add another roll"
  }
}
```

### Test Case 1.14: Exploding Mechanic Verification - Multiple Explosions
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "5d6!"
  },
  "expected": {
    "rolls": "array with at least 5 numbers (more if explosions occur)",
    "validation": {
      "count_check": "If rolls array length > 5, explosions occurred",
      "chain_explosions": "A 6 can explode into another 6, creating chains",
      "example": "Roll of [6, 6, 3] = 15 (first 6 exploded into another 6, which exploded into 3)"
    },
    "note": "Each 6 should trigger another roll, potentially creating chains"
  }
}
```

### Test Case 1.15: Exploding Mechanic Verification - Non-Exploding Control
```json
{
  "tool": "roll_dice",
  "input": {
    "notation": "5d6"
  },
  "expected": {
    "rolls": "array with exactly 5 numbers (no more, no less)",
    "validation": {
      "count_check": "rolls.length === 5 (no explosions)",
      "max_value": "all individual rolls <= 6",
      "comparison": "Compare with 5d6! to verify explosion difference"
    },
    "note": "Without !, dice should NEVER explode even when rolling 6"
  }
}
```

---

## 2. roll_multiple_dice

**Purpose:** Roll multiple different dice at once

### Test Case 2.1: Two Different Dice Types
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["2d6", "1d20"]
  },
  "expected": {
    "results": [
      {
        "notation": "2d6",
        "rolls": "array of 2 numbers between 1-6",
        "total": "sum of 2d6"
      },
      {
        "notation": "1d20",
        "rolls": "array of 1 number between 1-20",
        "total": "value of 1d20"
      }
    ]
  }
}
```

### Test Case 2.2: Three Dice with Modifiers
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["2d6+3", "1d20-1", "3d8"]
  },
  "expected": {
    "results": "array of 3 roll results with correct modifiers applied"
  }
}
```

### Test Case 2.3: Same Dice Multiple Times
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["1d6", "1d6", "1d6"]
  },
  "expected": {
    "results": "array of 3 separate 1d6 rolls (different values)"
  }
}
```

### Test Case 2.4: Mixed Die Sizes
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["1d4", "1d6", "1d8", "1d10", "1d12", "1d20"]
  },
  "expected": {
    "results": "array of 6 results, each with appropriate die range"
  }
}
```

### Test Case 2.5: Large Modifier Values
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["1d6+10", "2d8-5"]
  },
  "expected": {
    "results": "array of 2 results with large modifiers correctly applied"
  }
}
```

### Test Case 2.6: Exploding Dice in Multiple Rolls
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["3d6!", "2d8!", "1d20"]
  },
  "expected": {
    "results": "array of 3 results, first two with explosions, last without"
  }
}
```

### Test Case 2.7: Boundary - Empty Array
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": []
  },
  "expected": {
    "error": "No dice notations provided",
    "note": "Array must contain at least one notation"
  }
}
```

### Test Case 2.8: Negative - Invalid Notation in Array
```json
{
  "tool": "roll_multiple_dice",
  "input": {
    "notations": ["2d6", "invalid", "1d20"]
  },
  "expected": {
    "error": "Invalid notation at index 1",
    "note": "Should validate each notation"
  }
}
```

---

## 3. roll_with_advantage

**Purpose:** Roll twice and take the higher result (D&D 5e)

### Test Case 3.1: Basic d20 Advantage
```json
{
  "tool": "roll_with_advantage",
  "input": {
    "notation": "1d20"
  },
  "expected": {
    "roll1": "number between 1-20",
    "roll2": "number between 1-20",
    "result": "max(roll1, roll2)",
    "advantage": true
  }
}
```

### Test Case 3.2: Advantage with Modifier
```json
{
  "tool": "roll_with_advantage",
  "input": {
    "notation": "1d20+5"
  },
  "expected": {
    "roll1": "number between 1-20",
    "roll2": "number between 1-20",
    "result": "max(roll1, roll2) + 5"
  }
}
```

### Test Case 3.3: Advantage on d6
```json
{
  "tool": "roll_with_advantage",
  "input": {
    "notation": "1d6"
  },
  "expected": {
    "roll1": "number between 1-6",
    "roll2": "number between 1-6",
    "result": "max(roll1, roll2)"
  }
}
```

### Test Case 3.4: Advantage with Negative Modifier
```json
{
  "tool": "roll_with_advantage",
  "input": {
    "notation": "1d20-2"
  },
  "expected": {
    "roll1": "number between 1-20",
    "roll2": "number between 1-20",
    "result": "max(roll1, roll2) - 2"
  }
}
```

### Test Case 3.5: Advantage on d100
```json
{
  "tool": "roll_with_advantage",
  "input": {
    "notation": "1d100"
  },
  "expected": {
    "roll1": "number between 1-100",
    "roll2": "number between 1-100",
    "result": "max(roll1, roll2)"
  }
}
```

---

## 4. roll_with_disadvantage

**Purpose:** Roll twice and take the lower result (D&D 5e)

### Test Case 4.1: Basic d20 Disadvantage
```json
{
  "tool": "roll_with_disadvantage",
  "input": {
    "notation": "1d20"
  },
  "expected": {
    "roll1": "number between 1-20",
    "roll2": "number between 1-20",
    "result": "min(roll1, roll2)",
    "disadvantage": true
  }
}
```

### Test Case 4.2: Disadvantage with Modifier
```json
{
  "tool": "roll_with_disadvantage",
  "input": {
    "notation": "1d20+3"
  },
  "expected": {
    "roll1": "number between 1-20",
    "roll2": "number between 1-20",
    "result": "min(roll1, roll2) + 3"
  }
}
```

### Test Case 4.3: Disadvantage on d8
```json
{
  "tool": "roll_with_disadvantage",
  "input": {
    "notation": "1d8"
  },
  "expected": {
    "roll1": "number between 1-8",
    "roll2": "number between 1-8",
    "result": "min(roll1, roll2)"
  }
}
```

### Test Case 4.4: Disadvantage with Negative Modifier
```json
{
  "tool": "roll_with_disadvantage",
  "input": {
    "notation": "1d20-1"
  },
  "expected": {
    "roll1": "number between 1-20",
    "roll2": "number between 1-20",
    "result": "min(roll1, roll2) - 1"
  }
}
```

### Test Case 4.5: Disadvantage on d12
```json
{
  "tool": "roll_with_disadvantage",
  "input": {
    "notation": "1d12"
  },
  "expected": {
    "roll1": "number between 1-12",
    "roll2": "number between 1-12",
    "result": "min(roll1, roll2)"
  }
}
```

---

## 5. roll_with_target_number

**Purpose:** Count successes against a target number (Shadowrun-style)

### Test Case 5.1: Basic Success Count (TN 5)
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "6d6",
    "target_number": 5
  },
  "expected": {
    "rolls": "array of 6 numbers between 1-6",
    "target_number": 5,
    "successes": "count of rolls >= 5",
    "failures": "array of rolls < 5"
  }
}
```

### Test Case 5.2: Exploding Dice (TN 4)
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "4d6!",
    "target_number": 4
  },
  "expected": {
    "rolls": "array with possible values > 6 (exploding)",
    "target_number": 4,
    "successes": "count of rolls >= 4",
    "exploding": true
  }
}
```

### Test Case 5.3: Low Target Number (TN 2)
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "8d6!",
    "target_number": 2
  },
  "expected": {
    "rolls": "array of 8+ numbers (with explosions)",
    "target_number": 2,
    "successes": "high count (most rolls succeed)",
    "failures": "array of 1s only"
  }
}
```

### Test Case 5.4: High Target Number (TN 6)
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "10d6!",
    "target_number": 6
  },
  "expected": {
    "rolls": "array of 10+ numbers",
    "target_number": 6,
    "successes": "count of rolls >= 6 (including explosions)",
    "failures": "array of rolls 1-5"
  }
}
```

### Test Case 5.5: Rule of One (All 1s)
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "3d6",
    "target_number": 5
  },
  "expected_if_all_ones": {
    "rolls": "[1, 1, 1]",
    "successes": 0,
    "all_ones": true,
    "critical_failure": true
  }
}
```

### Test Case 5.6: Exploding Mechanic Verification - Success Counting
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "6d6!",
    "target_number": 5
  },
  "expected": {
    "rolls": "array of 6+ numbers (explosions increase array size)",
    "validation": {
      "explosion_check": "If any roll value > 6, explosion occurred",
      "success_counting": "Exploded values (e.g., 12) count as 1 success if >= TN",
      "example": "Roll of [12, 5, 4, 3, 2, 1] = 2 successes (12 and 5 both >= 5)"
    },
    "note": "Exploded dice values count as single successes, not multiple"
  }
}
```

### Test Case 5.7: Exploding vs Non-Exploding Comparison
```json
{
  "tool": "roll_with_target_number",
  "input": {
    "notation": "10d6",
    "target_number": 6
  },
  "expected": {
    "rolls": "array of exactly 10 numbers, all <= 6",
    "validation": {
      "no_explosions": "Without !, max roll value is 6",
      "success_count": "Only natural 6s count as successes",
      "comparison": "Compare with 10d6! to see explosion benefit"
    },
    "note": "Non-exploding dice have lower success potential at high TNs"
  }
}
```

---

## 6. roll_opposed

**Purpose:** Opposed roll between two sets of dice

### Test Case 6.1: Basic Opposed Roll
```json
{
  "tool": "roll_opposed",
  "input": {
    "notation1": "6d6!",
    "target_number1": 5,
    "notation2": "4d6!",
    "target_number2": 4
  },
  "expected": {
    "side1": {
      "rolls": "array of 6+ numbers",
      "successes": "count >= 5"
    },
    "side2": {
      "rolls": "array of 4+ numbers",
      "successes": "count >= 4"
    },
    "net_successes": "side1.successes - side2.successes",
    "winner": "side with more successes"
  }
}
```

### Test Case 6.2: Attacker vs Defender (Easy TN)
```json
{
  "tool": "roll_opposed",
  "input": {
    "notation1": "8d6!",
    "target_number1": 3,
    "notation2": "5d6!",
    "target_number2": 5
  },
  "expected": {
    "side1": "likely high successes (easy TN)",
    "side2": "likely lower successes (hard TN)",
    "net_successes": "positive or negative",
    "winner": "determined by net successes"
  }
}
```

### Test Case 6.3: Equal Dice Pools
```json
{
  "tool": "roll_opposed",
  "input": {
    "notation1": "6d6!",
    "target_number1": 4,
    "notation2": "6d6!",
    "target_number2": 4
  },
  "expected": {
    "side1": "successes count",
    "side2": "successes count",
    "net_successes": "close to 0 (equal pools)",
    "winner": "either side or tie"
  }
}
```

### Test Case 6.4: Large vs Small Pool
```json
{
  "tool": "roll_opposed",
  "input": {
    "notation1": "12d6!",
    "target_number1": 5,
    "notation2": "3d6!",
    "target_number2": 4
  },
  "expected": {
    "side1": "high success count",
    "side2": "low success count",
    "net_successes": "likely positive",
    "winner": "likely side1"
  }
}
```

### Test Case 6.5: Different Target Numbers
```json
{
  "tool": "roll_opposed",
  "input": {
    "notation1": "5d6!",
    "target_number1": 2,
    "notation2": "5d6!",
    "target_number2": 6
  },
  "expected": {
    "side1": "very high successes (TN 2)",
    "side2": "low successes (TN 6)",
    "net_successes": "large positive",
    "winner": "side1"
  }
}
```

---

## 7. roll_initiative

**Purpose:** Roll initiative (Shadowrun-style, never exploding)

### Test Case 7.1: Basic Initiative (2d6+10)
```json
{
  "tool": "roll_initiative",
  "input": {
    "notation": "2d6+10"
  },
  "expected": {
    "notation": "2d6+10",
    "rolls": "array of 2 numbers between 1-6",
    "modifier": 10,
    "initiative": "sum of rolls + 10",
    "phases": "array of 5 initiative values (init, init-10, init-20, init-30, init-40)"
  }
}
```

### Test Case 7.2: High Initiative (3d6+15)
```json
{
  "tool": "roll_initiative",
  "input": {
    "notation": "3d6+15"
  },
  "expected": {
    "notation": "3d6+15",
    "rolls": "array of 3 numbers between 1-6",
    "modifier": 15,
    "initiative": "sum of rolls + 15 (18-33)",
    "phases": "5 phases starting from high initiative"
  }
}
```

### Test Case 7.3: Low Initiative (1d6+5)
```json
{
  "tool": "roll_initiative",
  "input": {
    "notation": "1d6+5"
  },
  "expected": {
    "notation": "1d6+5",
    "rolls": "array of 1 number between 1-6",
    "modifier": 5,
    "initiative": "roll + 5 (6-11)",
    "phases": "5 phases, some may be negative"
  }
}
```

### Test Case 7.4: Initiative with ! (Should NOT Explode)
```json
{
  "tool": "roll_initiative",
  "input": {
    "notation": "2d6!+10"
  },
  "expected": {
    "notation": "2d6!+10",
    "rolls": "array of 2 numbers between 1-6 (NO explosions)",
    "modifier": 10,
    "initiative": "sum + 10",
    "note": "Initiative dice never explode even with ! notation"
  }
}
```

### Test Case 7.5: Zero Modifier Initiative
```json
{
  "tool": "roll_initiative",
  "input": {
    "notation": "2d6"
  },
  "expected": {
    "notation": "2d6",
    "rolls": "array of 2 numbers between 1-6",
    "modifier": 0,
    "initiative": "sum of rolls (2-12)",
    "phases": "5 phases from initiative score"
  }
}
```

---

## 8. track_initiative

**Purpose:** Track initiative for multiple characters with phase breakdown

### Test Case 8.1: Two Characters
```json
{
  "tool": "track_initiative",
  "input": {
    "characters": [
      {"name": "Samurai", "notation": "2d6+10"},
      {"name": "Mage", "notation": "1d6+8"}
    ]
  },
  "expected": {
    "characters": "array of 2 with initiative scores",
    "initiative_order": "sorted by initiative (highest first)",
    "phases": "breakdown showing who acts in each phase",
    "tie_breaking": "higher modifier wins ties"
  }
}
```

### Test Case 8.2: Four Characters with Ties
```json
{
  "tool": "track_initiative",
  "input": {
    "characters": [
      {"name": "Street Samurai", "notation": "3d6+12"},
      {"name": "Decker", "notation": "2d6+9"},
      {"name": "Shaman", "notation": "1d6+7"},
      {"name": "Rigger", "notation": "2d6+10"}
    ]
  },
  "expected": {
    "characters": "array of 4 with initiatives",
    "initiative_order": "sorted, ties broken by modifier",
    "phases": "complete phase breakdown for all characters"
  }
}
```

### Test Case 8.3: Single Character
```json
{
  "tool": "track_initiative",
  "input": {
    "characters": [
      {"name": "Solo Runner", "notation": "2d6+11"}
    ]
  },
  "expected": {
    "characters": "array of 1",
    "initiative_order": "single character",
    "phases": "5 phases for solo character"
  }
}
```

### Test Case 8.4: Large Group (6 Characters)
```json
{
  "tool": "track_initiative",
  "input": {
    "characters": [
      {"name": "PC1", "notation": "2d6+10"},
      {"name": "PC2", "notation": "2d6+9"},
      {"name": "NPC1", "notation": "1d6+8"},
      {"name": "NPC2", "notation": "2d6+7"},
      {"name": "NPC3", "notation": "1d6+6"},
      {"name": "NPC4", "notation": "2d6+8"}
    ]
  },
  "expected": {
    "characters": "array of 6",
    "initiative_order": "all 6 sorted correctly",
    "phases": "complete breakdown for all"
  }
}
```

### Test Case 8.5: Mixed Initiative Dice
```json
{
  "tool": "track_initiative",
  "input": {
    "characters": [
      {"name": "Wired Samurai", "notation": "4d6+15"},
      {"name": "Normal Human", "notation": "1d6+5"},
      {"name": "Boosted Runner", "notation": "3d6+12"}
    ]
  },
  "expected": {
    "characters": "array of 3 with varied dice",
    "initiative_order": "sorted by total initiative",
    "phases": "wired samurai acts most often"
  }
}
```

---

## 9. roll_with_pools

**Purpose:** Roll with dice pools tracking each pool separately

### Test Case 9.1: Skill + Combat Pool
```json
{
  "tool": "roll_with_pools",
  "input": {
    "pools": [
      {"name": "Firearms Skill", "notation": "6d6!"},
      {"name": "Combat Pool", "notation": "4d6!"}
    ],
    "target_number": 5
  },
  "expected": {
    "pools": [
      {
        "name": "Firearms Skill",
        "rolls": "array of 6+ numbers",
        "successes": "count >= 5",
        "failures": "array of rolls < 5"
      },
      {
        "name": "Combat Pool",
        "rolls": "array of 4+ numbers",
        "successes": "count >= 5",
        "failures": "array of rolls < 5"
      }
    ],
    "total_successes": "sum of all pool successes"
  }
}
```

### Test Case 9.2: Three Pools (Skill + Combat + Karma)
```json
{
  "tool": "roll_with_pools",
  "input": {
    "pools": [
      {"name": "Sorcery", "notation": "8d6!"},
      {"name": "Spell Pool", "notation": "5d6!"},
      {"name": "Karma Pool", "notation": "2d6!"}
    ],
    "target_number": 4
  },
  "expected": {
    "pools": "array of 3 with separate tracking",
    "total_successes": "sum of all successes",
    "summary": "breakdown by pool name"
  }
}
```

### Test Case 9.3: Single Pool
```json
{
  "tool": "roll_with_pools",
  "input": {
    "pools": [
      {"name": "Unarmed Combat", "notation": "7d6!"}
    ],
    "target_number": 4
  },
  "expected": {
    "pools": "array of 1",
    "total_successes": "successes from single pool"
  }
}
```

### Test Case 9.4: Low Target Number (TN 2)
```json
{
  "tool": "roll_with_pools",
  "input": {
    "pools": [
      {"name": "Pistols", "notation": "8d6!"},
      {"name": "Combat Pool", "notation": "5d6!"},
      {"name": "Smartlink", "notation": "2d6!"}
    ],
    "target_number": 2
  },
  "expected": {
    "pools": "array of 3",
    "total_successes": "very high (easy TN)",
    "failures": "mostly 1s only"
  }
}
```

### Test Case 9.5: High Target Number (TN 6)
```json
{
  "tool": "roll_with_pools",
  "input": {
    "pools": [
      {"name": "Stealth", "notation": "5d6!"},
      {"name": "Task Pool", "notation": "3d6!"}
    ],
    "target_number": 6
  },
  "expected": {
    "pools": "array of 2",
    "total_successes": "lower count (hard TN)",
    "failures": "many rolls 1-5"
  }
}
```

---

## 10. roll_opposed_pools

**Purpose:** Opposed roll with dice pools (combat, stealth, social, etc.)

### Test Case 10.1: Combat Attack vs Defense
```json
{
  "tool": "roll_opposed_pools",
  "input": {
    "side1_pools": [
      {"name": "Firearms", "notation": "8d6!"},
      {"name": "Combat Pool", "notation": "5d6!"}
    ],
    "side1_target_number": 4,
    "side2_pools": [
      {"name": "Body", "notation": "6d6!"},
      {"name": "Combat Pool", "notation": "4d6!"}
    ],
    "side2_target_number": 5,
    "side1_label": "Attacker",
    "side2_label": "Defender"
  },
  "expected": {
    "side1": {
      "pools": "array of 2 with tracking",
      "total_successes": "combined successes"
    },
    "side2": {
      "pools": "array of 2 with tracking",
      "total_successes": "combined successes"
    },
    "net_successes": "difference",
    "winner": "side with more successes",
    "dodge_check": "if defender's Combat Pool alone > attacker total"
  }
}
```

### Test Case 10.2: Stealth vs Perception
```json
{
  "tool": "roll_opposed_pools",
  "input": {
    "side1_pools": [
      {"name": "Stealth", "notation": "6d6!"},
      {"name": "Task Pool", "notation": "3d6!"}
    ],
    "side1_target_number": 4,
    "side2_pools": [
      {"name": "Perception", "notation": "5d6!"}
    ],
    "side2_target_number": 5,
    "side1_label": "Sneaker",
    "side2_label": "Guard"
  },
  "expected": {
    "side1": "stealth attempt with pools",
    "side2": "perception check",
    "net_successes": "determines if spotted",
    "winner": "higher successes wins"
  }
}
```

### Test Case 10.3: Social Test (Negotiation)
```json
{
  "tool": "roll_opposed_pools",
  "input": {
    "side1_pools": [
      {"name": "Negotiation", "notation": "7d6!"},
      {"name": "Karma Pool", "notation": "2d6!"}
    ],
    "side1_target_number": 4,
    "side2_pools": [
      {"name": "Willpower", "notation": "6d6!"}
    ],
    "side2_target_number": 4,
    "side1_label": "Face",
    "side2_label": "Mr. Johnson"
  },
  "expected": {
    "side1": "negotiation with karma boost",
    "side2": "willpower resistance",
    "net_successes": "negotiation outcome"
  }
}
```

### Test Case 10.4: Spell Resistance
```json
{
  "tool": "roll_opposed_pools",
  "input": {
    "side1_pools": [
      {"name": "Sorcery", "notation": "9d6!"},
      {"name": "Spell Pool", "notation": "6d6!"}
    ],
    "side1_target_number": 5,
    "side2_pools": [
      {"name": "Willpower", "notation": "5d6!"},
      {"name": "Spell Defense", "notation": "3d6!"}
    ],
    "side2_target_number": 4,
    "side1_label": "Mage",
    "side2_label": "Target"
  },
  "expected": {
    "side1": "spell casting pools",
    "side2": "resistance pools",
    "net_successes": "spell effect strength"
  }
}
```

### Test Case 10.5: Hacking Attempt
```json
{
  "tool": "roll_opposed_pools",
  "input": {
    "side1_pools": [
      {"name": "Computer", "notation": "8d6!"},
      {"name": "Hacking Pool", "notation": "5d6!"}
    ],
    "side1_target_number": 6,
    "side2_pools": [
      {"name": "IC Rating", "notation": "6d6!"}
    ],
    "side2_target_number": 4,
    "side1_label": "Decker",
    "side2_label": "System IC"
  },
  "expected": {
    "side1": "hacking attempt",
    "side2": "IC defense",
    "net_successes": "hack success level"
  }
}
```

---

## 11. reroll_failures

**Purpose:** Re-roll failed dice using Karma Pool (escalating cost)

### Test Case 11.1: First Re-roll (1 Karma)
```json
{
  "tool": "reroll_failures",
  "input": {
    "failed_dice": [3, 2, 1],
    "target_number": 5,
    "sides": 6,
    "exploding": true,
    "reroll_iteration": 1
  },
  "expected": {
    "original_failures": "[3, 2, 1]",
    "rerolls": "array of 3 new rolls",
    "new_successes": "count of rerolls >= 5",
    "remaining_failures": "rerolls < 5",
    "karma_cost": 1,
    "iteration": 1
  }
}
```

### Test Case 11.2: Second Re-roll (2 Karma)
```json
{
  "tool": "reroll_failures",
  "input": {
    "failed_dice": [2, 1],
    "target_number": 5,
    "sides": 6,
    "exploding": true,
    "reroll_iteration": 2
  },
  "expected": {
    "original_failures": "[2, 1]",
    "rerolls": "array of 2 new rolls",
    "new_successes": "count >= 5",
    "karma_cost": 2,
    "iteration": 2,
    "note": "Cost escalates with each iteration"
  }
}
```

### Test Case 11.3: Third Re-roll (3 Karma)
```json
{
  "tool": "reroll_failures",
  "input": {
    "failed_dice": [1],
    "target_number": 4,
    "sides": 6,
    "exploding": true,
    "reroll_iteration": 3
  },
  "expected": {
    "original_failures": "[1]",
    "rerolls": "array of 1 new roll",
    "new_successes": "count >= 4",
    "karma_cost": 3,
    "iteration": 3
  }
}
```

### Test Case 11.4: Non-Exploding Re-roll
```json
{
  "tool": "reroll_failures",
  "input": {
    "failed_dice": [3, 2],
    "target_number": 4,
    "sides": 6,
    "exploding": false,
    "reroll_iteration": 1
  },
  "expected": {
    "original_failures": "[3, 2]",
    "rerolls": "array of 2 numbers between 1-6 (no explosions)",
    "new_successes": "count >= 4",
    "karma_cost": 1,
    "exploding": false
  }
}
```

### Test Case 11.5: Many Failures Re-roll
```json
{
  "tool": "reroll_failures",
  "input": {
    "failed_dice": [3, 3, 2, 2, 1, 1],
    "target_number": 5,
    "sides": 6,
    "exploding": true,
    "reroll_iteration": 1
  },
  "expected": {
    "original_failures": "[3, 3, 2, 2, 1, 1]",
    "rerolls": "array of 6 new rolls",
    "new_successes": "count >= 5",
    "remaining_failures": "still failed rolls",
    "karma_cost": 1
  }
}
```

---

## 12. avoid_disaster

**Purpose:** Avoid critical failure (Rule of One) by spending 1 Karma

### Test Case 12.1: Basic Disaster Avoidance
```json
{
  "tool": "avoid_disaster",
  "input": {
    "roll_result": {
      "rolls": [1, 1, 1],
      "successes": 0,
      "all_ones": true
    }
  },
  "expected": {
    "original_result": "all ones",
    "karma_cost": 1,
    "new_result": "simple failure (not critical)",
    "all_ones": false,
    "note": "Cannot re-roll after using this"
  }
}
```

### Test Case 12.2: Disaster with Many Dice
```json
{
  "tool": "avoid_disaster",
  "input": {
    "roll_result": {
      "rolls": [1, 1, 1, 1, 1],
      "successes": 0,
      "all_ones": true
    }
  },
  "expected": {
    "original_result": "5 ones (critical failure)",
    "karma_cost": 1,
    "new_result": "converted to simple failure",
    "disaster_avoided": true
  }
}
```

### Test Case 12.3: Small Pool Disaster
```json
{
  "tool": "avoid_disaster",
  "input": {
    "roll_result": {
      "rolls": [1, 1],
      "successes": 0,
      "all_ones": true
    }
  },
  "expected": {
    "original_result": "2 ones",
    "karma_cost": 1,
    "new_result": "simple failure",
    "disaster_avoided": true
  }
}
```

### Test Case 12.4: Single Die Disaster
```json
{
  "tool": "avoid_disaster",
  "input": {
    "roll_result": {
      "rolls": [1],
      "successes": 0,
      "all_ones": true
    }
  },
  "expected": {
    "original_result": "single 1",
    "karma_cost": 1,
    "new_result": "simple failure",
    "note": "Even single die can be disaster"
  }
}
```

### Test Case 12.5: Large Pool Disaster
```json
{
  "tool": "avoid_disaster",
  "input": {
    "roll_result": {
      "rolls": [1, 1, 1, 1, 1, 1, 1, 1],
      "successes": 0,
      "all_ones": true
    }
  },
  "expected": {
    "original_result": "8 ones (severe critical)",
    "karma_cost": 1,
    "new_result": "converted to simple failure",
    "disaster_avoided": true
  }
}
```

---

## 13. buy_karma_dice

**Purpose:** Buy additional dice using Karma Pool (1 Karma per die)

### Test Case 13.1: Buy 2 Karma Dice
```json
{
  "tool": "buy_karma_dice",
  "input": {
    "karma_dice_count": 2,
    "target_number": 5,
    "sides": 6,
    "exploding": true,
    "max_allowed": null
  },
  "expected": {
    "karma_dice_count": 2,
    "rolls": "array of 2+ numbers (with explosions)",
    "successes": "count >= 5",
    "failures": "rolls < 5",
    "karma_cost": 2
  }
}
```

### Test Case 13.2: Buy Maximum Allowed (Skill Level)
```json
{
  "tool": "buy_karma_dice",
  "input": {
    "karma_dice_count": 6,
    "target_number": 4,
    "sides": 6,
    "exploding": true,
    "max_allowed": 6
  },
  "expected": {
    "karma_dice_count": 6,
    "rolls": "array of 6+ numbers",
    "successes": "count >= 4",
    "karma_cost": 6,
    "note": "At maximum allowed"
  }
}
```

### Test Case 13.3: Buy Single Karma Die
```json
{
  "tool": "buy_karma_dice",
  "input": {
    "karma_dice_count": 1,
    "target_number": 5,
    "sides": 6,
    "exploding": true,
    "max_allowed": null
  },
  "expected": {
    "karma_dice_count": 1,
    "rolls": "array of 1+ numbers",
    "successes": "count >= 5",
    "karma_cost": 1
  }
}
```

### Test Case 13.4: Buy Non-Exploding Karma Dice
```json
{
  "tool": "buy_karma_dice",
  "input": {
    "karma_dice_count": 3,
    "target_number": 4,
    "sides": 6,
    "exploding": false,
    "max_allowed": null
  },
  "expected": {
    "karma_dice_count": 3,
    "rolls": "array of 3 numbers between 1-6 (no explosions)",
    "successes": "count >= 4",
    "karma_cost": 3,
    "exploding": false
  }
}
```

### Test Case 13.5: Buy Karma Dice with Low TN
```json
{
  "tool": "buy_karma_dice",
  "input": {
    "karma_dice_count": 4,
    "target_number": 2,
    "sides": 6,
    "exploding": true,
    "max_allowed": null
  },
  "expected": {
    "karma_dice_count": 4,
    "rolls": "array of 4+ numbers",
    "successes": "high count (easy TN)",
    "karma_cost": 4
  }
}
```

---

## 14. buy_successes

**Purpose:** Buy raw successes using Karma Pool (1 Karma per success, PERMANENT)

### Test Case 14.1: Buy 1 Success (Minimum)
```json
{
  "tool": "buy_successes",
  "input": {
    "current_successes": 1,
    "successes_to_buy": 1
  },
  "expected": {
    "original_successes": 1,
    "bought_successes": 1,
    "total_successes": 2,
    "karma_cost": 1,
    "permanent_cost": true,
    "warning": "This Karma does NOT refresh"
  }
}
```

### Test Case 14.2: Buy Multiple Successes
```json
{
  "tool": "buy_successes",
  "input": {
    "current_successes": 3,
    "successes_to_buy": 2
  },
  "expected": {
    "original_successes": 3,
    "bought_successes": 2,
    "total_successes": 5,
    "karma_cost": 2,
    "permanent_cost": true
  }
}
```

### Test Case 14.3: Buy Many Successes (Expensive)
```json
{
  "tool": "buy_successes",
  "input": {
    "current_successes": 2,
    "successes_to_buy": 5
  },
  "expected": {
    "original_successes": 2,
    "bought_successes": 5,
    "total_successes": 7,
    "karma_cost": 5,
    "permanent_cost": true,
    "warning": "Very expensive - 5 permanent Karma"
  }
}
```

### Test Case 14.4: Buy Success with High Base
```json
{
  "tool": "buy_successes",
  "input": {
    "current_successes": 8,
    "successes_to_buy": 1
  },
  "expected": {
    "original_successes": 8,
    "bought_successes": 1,
    "total_successes": 9,
    "karma_cost": 1,
    "permanent_cost": true
  }
}
```

### Test Case 14.5: Error Case - No Natural Successes
```json
{
  "tool": "buy_successes",
  "input": {
    "current_successes": 0,
    "successes_to_buy": 1
  },
  "expected": {
    "error": "Cannot buy successes without at least 1 natural success",
    "requirement": "Must have current_successes >= 1"
  }
}
```

---

## Test Execution Notes

### General Testing Guidelines

1. **Random Nature**: Many tests involve random dice rolls, so exact values will vary. Focus on:
   - Correct ranges (e.g., d6 produces 1-6)
   - Correct counts (e.g., 2d6 produces 2 numbers)
   - Correct logic (e.g., advantage takes higher value)

2. **Exploding Dice**: When testing with `!` notation:
   - Values can exceed die maximum
   - Multiple explosions possible
   - Verify explosion logic works correctly

3. **Target Numbers**: Test various TNs:
   - Very easy (TN 2): Most rolls succeed
   - Medium (TN 4-5): Balanced
   - Hard (TN 6): Only max rolls + explosions succeed

4. **Edge Cases**: Always test:
   - Minimum values (1 die, TN 2, etc.)
   - Maximum values (many dice, TN 6, etc.)
   - Boundary conditions
   - Error conditions

5. **Karma Pool**: Remember:
   - Reroll costs escalate (1, 2, 3 Karma)
   - Avoid disaster costs 1 Karma
   - Buy dice costs 1 Karma per die
   - Buy successes costs 1 Karma per success (PERMANENT)

### API Testing

To test via API:
```bash
# GET request example
curl "https://shadowrun2.com/dice/api.php?action=roll&notation=2d6"

# POST request example
curl -X POST "https://shadowrun2.com/dice/api.php" \
  -H "Content-Type: application/json" \
  -d '{"action":"roll_opposed_pools","side1":{"pools":[{"name":"Skill","notation":"6d6!"}],"target_number":5},"side2":{"pools":[{"name":"Defense","notation":"4d6!"}],"target_number":4}}'
```

### MCP Testing

To test via MCP tools, use the tool names directly with the specified input parameters.

---

## 15. Skill Web Defaulting

**Purpose:** Calculate target number modifiers when defaulting on skills using the Shadowrun Skill Web

**Resources Used:**
- `skillweb://prompt` - Instructions for calculating defaulting modifiers
- `skillweb://graph` - The complete skill web graph structure

**Calculation Rules:**
- Each dot (connection point) on the path adds +2 to the target number
- Always use the shortest path between nodes
- Nodes prefixed with `dot_` are connection points
- Named nodes are actual skills/attributes (e.g., "Firearms", "QUICKNESS")

### Test Case 15.1: Intelligence to Demolitions
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "INTELLIGENCE",
    "to": "Demolitions"
  },
  "expected": {
    "path": "INTELLIGENCE → dot_m1 → dot_m2 → dot_m3 → Demolitions",
    "dots_traversed": ["dot_m1", "dot_m2", "dot_m3"],
    "dot_count": 3,
    "modifier": "+6",
    "calculation": "3 dots × +2 = +6"
  }
}
```

### Test Case 15.2: Intelligence to Magical Theory
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "INTELLIGENCE",
    "to": "Magical Theory"
  },
  "expected": {
    "path": "INTELLIGENCE → dot_m1 → dot_m4 → dot_m5 → dot_m11 → dot_m12 → Magical Theory",
    "dots_traversed": ["dot_m1", "dot_m4", "dot_m5", "dot_m11", "dot_m12"],
    "dot_count": 5,
    "modifier": "+10",
    "calculation": "5 dots × +2 = +10"
  }
}
```

### Test Case 15.3: Willpower to Military Theory
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "WILLPOWER",
    "to": "Military Theory"
  },
  "expected": {
    "path": "WILLPOWER → dot_m6 → dot_m7 → dot_m8 → dot_m38 → dot_m16 → Military Theory",
    "dots_traversed": ["dot_m6", "dot_m7", "dot_m8", "dot_m38", "dot_m16"],
    "dot_count": 5,
    "modifier": "+10",
    "calculation": "5 dots × +2 = +10"
  }
}
```

### Test Case 15.4: Magical Theory to Military Theory
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Magical Theory",
    "to": "Military Theory"
  },
  "expected": {
    "path": "Magical Theory → dot_m12 → dot_m11 → dot_m7 → dot_m8 → dot_m38 → dot_m16 → Military Theory",
    "dots_traversed": ["dot_m12", "dot_m11", "dot_m7", "dot_m8", "dot_m38", "dot_m16"],
    "dot_count": 6,
    "modifier": "+12",
    "calculation": "6 dots × +2 = +12"
  }
}
```

### Test Case 15.5: Psychology to Sociology
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Psychology",
    "to": "Sociology"
  },
  "expected": {
    "path": "Psychology → dot_m8 → dot_m37 → Sociology",
    "dots_traversed": ["dot_m8", "dot_m37"],
    "dot_count": 2,
    "modifier": "+4",
    "calculation": "2 dots × +2 = +4",
    "note": "Alternative path exists: Psychology → dot_m17 → Sociology (1 dot, +2), but BFS found this path first"
  }
}
```

### Test Case 15.6: QUICKNESS to Stealth
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "QUICKNESS",
    "to": "Stealth"
  },
  "expected": {
    "path": "QUICKNESS → dot_p2 → dot_p3 → Stealth",
    "dots_traversed": ["dot_p2", "dot_p3"],
    "dot_count": 2,
    "modifier": "+4",
    "calculation": "2 dots × +2 = +4"
  }
}
```

### Test Case 15.7: Bike (Motorcycle) to Vector Thrust (Aircraft)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Bike",
    "to": "Vector Thrust"
  },
  "expected": {
    "path": "Bike → dot_g8 → dot_g2 → dot_g1 → dot_g4 → dot_g10 → Vector Thrust",
    "dots_traversed": ["dot_g8", "dot_g2", "dot_g1", "dot_g4", "dot_g10"],
    "dot_count": 5,
    "modifier": "+10",
    "calculation": "5 dots × +2 = +10",
    "note": "Bike is a ground vehicle, Vector Thrust is an aircraft - very different skills"
  }
}
```

### Test Case 15.8: Sociology to Negotiation
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Sociology",
    "to": "Negotiation"
  },
  "expected": {
    "path": "Sociology → dot_m18 → dot_m17 → dot_m34 → dot_m35 → dot_m36 → Negotiation",
    "dots_traversed": ["dot_m18", "dot_m17", "dot_m34", "dot_m35", "dot_m36"],
    "dot_count": 5,
    "modifier": "+10",
    "calculation": "5 dots × +2 = +10"
  }
}
```

### Test Case 15.9: Direct Connection (No Dots)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "dot_p1",
    "to": "Athletics"
  },
  "expected": {
    "path": "dot_p1 → Athletics",
    "dots_traversed": [],
    "dot_count": 0,
    "modifier": "+0",
    "calculation": "0 dots × +2 = +0",
    "note": "Direct connection with cost 0 means no modifier"
  }
}
```

### Test Case 15.10: Same Skill (No Defaulting Needed)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Firearms",
    "to": "Firearms"
  },
  "expected": {
    "path": "Firearms (same skill)",
    "dots_traversed": [],
    "dot_count": 0,
    "modifier": "+0",
    "calculation": "No defaulting needed - character has the skill",
    "note": "When from and to are the same, no defaulting occurs"
  }
}
```

### Test Case 15.11: WILLPOWER to Vector Thrust (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "WILLPOWER",
    "to": "Vector Thrust"
  },
  "expected": {
    "path": "No path exists",
    "reason": "Mental attribute cannot default to vehicle skill",
    "modifier": "N/A - defaulting not possible",
    "note": "Some skills are too unrelated to default between"
  }
}
```

### Test Case 15.12: Computer Theory to Demolitions (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Computer Theory",
    "to": "Demolitions"
  },
  "expected": {
    "path": "No path exists",
    "reason": "Technical skill cannot default to combat skill",
    "modifier": "N/A - defaulting not possible",
    "note": "Graph intentionally separates unrelated skill categories"
  }
}
```

### Test Case 15.13: Sorcery to Car (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Sorcery",
    "to": "Car"
  },
  "expected": {
    "path": "No path exists",
    "reason": "Magic skill cannot default to vehicle skill",
    "modifier": "N/A - defaulting not possible",
    "note": "Magic and vehicle skills are completely separate branches"
  }
}
```

### Test Case 15.14: Firearms to Enchanting (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Firearms",
    "to": "Enchanting"
  },
  "expected": {
    "path": "No path exists",
    "reason": "Combat skill cannot default to magic skill",
    "modifier": "N/A - defaulting not possible",
    "note": "Physical combat and magical skills are separate"
  }
}
```

### Test Case 15.15: Biology to Armed Combat (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Biology",
    "to": "Armed Combat"
  },
  "expected": {
    "path": "No path exists",
    "reason": "Science skill cannot default to combat skill",
    "modifier": "N/A - defaulting not possible",
    "note": "Academic and combat skills don't connect"
  }
}
```

### Test Case 15.16: QUICKNESS to Athletics (Direct Connection)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "QUICKNESS",
    "to": "Athletics"
  },
  "expected": {
    "path": "QUICKNESS → dot_p1 → Athletics",
    "dots_traversed": ["dot_p1"],
    "dot_count": 1,
    "modifier": "+2",
    "calculation": "1 dot × +2 = +2",
    "note": "Very close connection - attribute to related skill"
  }
}
```

### Test Case 15.17: Firearms to Firearms (B/R)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Firearms",
    "to": "Firearms (B/R)"
  },
  "expected": {
    "path": "Firearms → dot_p8 → Firearms (B/R)",
    "dots_traversed": ["dot_p8"],
    "dot_count": 1,
    "modifier": "+2",
    "calculation": "1 dot × +2 = +2",
    "note": "Skill to its Build/Repair variant - very close"
  }
}
```

### Test Case 15.18: Computer to Computer (B/R)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Computer",
    "to": "Computer (B/R)"
  },
  "expected": {
    "path": "Computer → dot_m33 → Computer (B/R)",
    "dots_traversed": ["dot_m33"],
    "dot_count": 1,
    "modifier": "+2",
    "calculation": "1 dot × +2 = +2",
    "note": "Technical skill to B/R variant"
  }
}
```

### Test Case 15.19: Gunnery (B/R) to Projectile (B/R)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Gunnery (B/R)",
    "to": "Projectile (B/R)"
  },
  "expected": {
    "path": "Gunnery (B/R) → dot_p9 → Gunnery → dot_p5 → dot_p4 → dot_p6 → Projectile → dot_p10 → Projectile (B/R)",
    "dots_traversed": ["dot_p9", "dot_p5", "dot_p4", "dot_p6", "dot_p10"],
    "dot_count": 5,
    "modifier": "+10",
    "calculation": "5 dots × +2 = +10",
    "note": "B/R to B/R requires going through base skills"
  }
}
```

### Test Case 15.20: INTELLIGENCE to Car (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "INTELLIGENCE",
    "to": "Car"
  },
  "expected": {
    "path": "No path exists",
    "reason": "No connection between mental skills and vehicle skills in current graph",
    "modifier": "N/A - defaulting not possible",
    "note": "Mental attributes don't connect to REACTION-based vehicle skills"
  }
}
```

### Test Case 15.21: CHARISMA to Computer (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "CHARISMA",
    "to": "Computer"
  },
  "expected": {
    "path": "No path exists",
    "reason": "No connection between social skills and technical skills in current graph",
    "modifier": "N/A - defaulting not possible",
    "note": "Social and technical skill branches are separate"
  }
}
```

### Test Case 15.22: Stealth to Negotiation (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Stealth",
    "to": "Negotiation"
  },
  "expected": {
    "path": "No path exists",
    "reason": "No connection between physical skills and social skills in current graph",
    "modifier": "N/A - defaulting not possible",
    "note": "Physical and social skill branches don't connect"
  }
}
```

### Test Case 15.23: Armed Combat to Unarmed Combat (Street Samurai)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Armed Combat",
    "to": "Unarmed Combat"
  },
  "expected": {
    "path": "Armed Combat → dot_p7 → dot_p13 → Unarmed Combat",
    "dots_traversed": ["dot_p7", "dot_p13"],
    "dot_count": 2,
    "modifier": "+4",
    "calculation": "2 dots × +2 = +4",
    "note": "Related combat skills - reasonable defaulting modifier"
  }
}
```

### Test Case 15.24: Computer to Electronics (Decker)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Computer",
    "to": "Electronics"
  },
  "expected": {
    "path": "Computer → dot_m28 → Electronics",
    "dots_traversed": ["dot_m28"],
    "dot_count": 1,
    "modifier": "+2",
    "calculation": "1 dot × +2 = +2",
    "note": "Very related technical skills - minimal penalty"
  }
}
```

### Test Case 15.25: Sorcery to Magical Theory (Mage)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Sorcery",
    "to": "Magical Theory"
  },
  "expected": {
    "path": "Sorcery → dot_m15 → dot_m13 → Magical Theory",
    "dots_traversed": ["dot_m15", "dot_m13"],
    "dot_count": 2,
    "modifier": "+4",
    "calculation": "2 dots × +2 = +4",
    "note": "Practical magic to theoretical knowledge - close connection"
  }
}
```

### Test Case 15.26: Negotiation to Psychology (Impossible Path)
```json
{
  "test": "skill_web_defaulting",
  "input": {
    "from": "Negotiation",
    "to": "Psychology"
  },
  "expected": {
    "path": "No path exists",
    "reason": "No reverse path from Negotiation back to Psychology in current graph",
    "modifier": "N/A - defaulting not possible",
    "note": "Graph connections are directional - Psychology → Negotiation exists, but not reverse"
  }
}
```

### Skill Web Testing Notes

1. **Path Finding**: The AI should use a shortest-path algorithm (like Dijkstra's or BFS) to find the optimal route through the skill web graph.

2. **Dot Counting**: Only nodes prefixed with `dot_` count toward the modifier. Direct connections between skills/attributes (cost 0) don't add to the modifier.

3. **Graph Structure**: The skill web is stored in `skill-web.json` as a directed graph where:
   - Each node has a `connections` array
   - Each connection has a `destination` and `cost`
   - Cost of 0 = direct connection (no dots)
   - Cost of 2 = one dot between nodes

4. **Practical Application**: When a character attempts to use a skill they don't have:
   - Find the shortest path from a known skill/attribute to the target skill
   - Count the dots on that path
   - Add +2 to the target number for each dot
   - Example: If base TN is 4 and modifier is +6, final TN is 10

5. **Common Defaulting Scenarios**:
   - Attribute to Skill: Usually 2-4 dots (+4 to +8)
   - Related Skills: Usually 1-3 dots (+2 to +6)
   - Unrelated Skills: Can be 5+ dots (+10 or more)
   - Vehicle Skills: Often require going through REACTION attribute

---

## 16. Skill Defaulting Scenarios (With Dice Rolls)

**Purpose:** Real-world skill defaulting scenarios combining skill web pathfinding with actual dice rolling

### Test Case 16.1: Simple Defaulting - QUICKNESS to Stealth

**Scenario:** Platinum (QUICKNESS 10, no Stealth skill) tries to sneak past a guard.

```json
{
  "test": "skill_defaulting_scenario",
  "character": {
    "name": "Platinum",
    "attribute": "QUICKNESS",
    "attribute_value": 10,
    "target_skill": "Stealth",
    "has_skill": false
  },
  "task": {
    "description": "Sneak past guard",
    "base_target_number": 4
  },
  "steps": [
    {
      "step": 1,
      "action": "Calculate defaulting modifier",
      "path": "QUICKNESS → dot_p2 → dot_p3 → Stealth",
      "dots": 2,
      "modifier": "+4",
      "final_tn": 8
    },
    {
      "step": 2,
      "action": "Roll dice",
      "tool": "roll_with_target_number",
      "input": {
        "notation": "10d6!",
        "target_number": 8
      },
      "example_result": {
        "rolls": [11, 9, 9, 5, 4, 3, 2, 2, 1, 1],
        "successes": 3,
        "failures": [5, 4, 3, 2, 2, 1, 1],
        "note": "First die exploded (6+5=11)"
      }
    }
  ],
  "outcome": {
    "successes": 3,
    "result": "Success - Platinum sneaks past with 3 hits"
  }
}
```

### Test Case 16.2: Opposed Defaulting - Stealth vs Perception

**Scenario:** Platinum (QUICKNESS 10, defaulting to Stealth) vs Guard (INTELLIGENCE 4, Perception 6)

```json
{
  "test": "opposed_skill_defaulting",
  "attacker": {
    "name": "Platinum",
    "attribute": "QUICKNESS",
    "attribute_value": 10,
    "target_skill": "Stealth",
    "has_skill": false,
    "defaulting_path": "QUICKNESS → dot_p2 → dot_p3 → Stealth",
    "defaulting_modifier": "+4"
  },
  "defender": {
    "name": "Guard",
    "skill": "Perception",
    "skill_value": 6,
    "has_skill": true,
    "no_defaulting": true
  },
  "task": {
    "description": "Platinum tries to sneak past guard",
    "base_target_number": 4
  },
  "steps": [
    {
      "step": 1,
      "action": "Platinum rolls (defaulting)",
      "tool": "roll_with_target_number",
      "input": {
        "notation": "10d6!",
        "target_number": 8
      },
      "example_result": {
        "rolls": [9, 8, 7, 5, 4, 3, 2, 2, 1, 1],
        "successes": 2,
        "note": "TN 8 due to defaulting penalty"
      }
    },
    {
      "step": 2,
      "action": "Guard rolls Perception",
      "tool": "roll_with_target_number",
      "input": {
        "notation": "6d6!",
        "target_number": 4
      },
      "example_result": {
        "rolls": [6, 5, 4, 3, 2, 1],
        "successes": 3,
        "note": "Guard has the skill, no penalty"
      }
    },
    {
      "step": 3,
      "action": "Compare results",
      "calculation": "Guard successes (3) - Platinum successes (2) = 1",
      "net_successes": 1,
      "winner": "Guard"
    }
  ],
  "outcome": {
    "result": "Guard spots Platinum",
    "note": "Guard's 3 successes beat Platinum's 2 successes by 1"
  }
}
```

### Test Case 16.3: Defaulting with Karma Reroll

**Scenario:** Shadow (INTELLIGENCE 6, defaulting to Computer from Computer Theory 4) hacking a system, uses Karma to reroll failures.

```json
{
  "test": "defaulting_with_karma_reroll",
  "character": {
    "name": "Shadow",
    "known_skill": "Computer Theory",
    "known_skill_value": 4,
    "target_skill": "Computer",
    "has_target_skill": false,
    "karma_pool": 5
  },
  "task": {
    "description": "Hack into corporate database",
    "base_target_number": 5
  },
  "steps": [
    {
      "step": 1,
      "action": "Calculate defaulting modifier",
      "path": "Computer Theory → dot_m32 → dot_m31 → Computer",
      "dots": 2,
      "modifier": "+4",
      "final_tn": 9,
      "note": "Computer Theory to Computer requires going through technical skill dots"
    },
    {
      "step": 2,
      "action": "Initial roll",
      "tool": "roll_with_target_number",
      "input": {
        "notation": "4d6!",
        "target_number": 9
      },
      "example_result": {
        "rolls": [8, 5, 3, 2],
        "successes": 0,
        "failures": [8, 5, 3, 2],
        "note": "No successes - TN 9 is very hard"
      }
    },
    {
      "step": 3,
      "action": "Decide to use Karma reroll",
      "decision": "Reroll all 4 failures (1st reroll = 1 Karma)",
      "karma_cost": 1,
      "remaining_karma": 4
    },
    {
      "step": 4,
      "action": "Karma reroll",
      "tool": "reroll_failures",
      "input": {
        "failed_dice": [8, 5, 3, 2],
        "target_number": 9,
        "sides": 6,
        "exploding": true,
        "reroll_iteration": 1
      },
      "example_result": {
        "rerolls": [12, 7, 4, 3],
        "new_successes": 1,
        "remaining_failures": [7, 4, 3],
        "note": "First die exploded (6+6=12), giving 1 success"
      }
    },
    {
      "step": 5,
      "action": "Decide on second reroll",
      "decision": "Reroll remaining 3 failures (2nd reroll = 2 Karma)",
      "karma_cost": 2,
      "remaining_karma": 2
    },
    {
      "step": 6,
      "action": "Second Karma reroll",
      "tool": "reroll_failures",
      "input": {
        "failed_dice": [7, 4, 3],
        "target_number": 9,
        "sides": 6,
        "exploding": true,
        "reroll_iteration": 2
      },
      "example_result": {
        "rerolls": [10, 5, 2],
        "new_successes": 1,
        "remaining_failures": [5, 2],
        "note": "One die exploded (6+4=10), another success"
      }
    }
  ],
  "outcome": {
    "total_successes": 2,
    "karma_spent": 3,
    "remaining_karma": 2,
    "result": "Success - Shadow hacks in with 2 successes after spending 3 Karma",
    "note": "Defaulting made this very difficult (TN 9), but Karma rerolls saved the day"
  }
}
```

### Test Case 16.4: Combat Defaulting - Armed to Unarmed

**Scenario:** Razor (STRENGTH 7, Armed Combat 6, no Unarmed Combat) gets disarmed and must fight hand-to-hand.

```json
{
  "test": "combat_defaulting_scenario",
  "character": {
    "name": "Razor",
    "known_skill": "Armed Combat",
    "known_skill_value": 6,
    "target_skill": "Unarmed Combat",
    "has_target_skill": false,
    "combat_pool": 8
  },
  "task": {
    "description": "Punch opponent after being disarmed",
    "base_target_number": 4
  },
  "steps": [
    {
      "step": 1,
      "action": "Calculate defaulting modifier",
      "path": "Armed Combat → dot_p7 → dot_p13 → Unarmed Combat",
      "dots": 2,
      "modifier": "+4",
      "final_tn": 8
    },
    {
      "step": 2,
      "action": "Allocate Combat Pool",
      "decision": "Use 4 dice from Combat Pool to boost attack",
      "total_dice": "6 (skill) + 4 (Combat Pool) = 10 dice"
    },
    {
      "step": 3,
      "action": "Roll attack with pools",
      "tool": "roll_with_pools",
      "input": {
        "pools": [
          {"name": "Armed Combat (defaulting)", "notation": "6d6!"},
          {"name": "Combat Pool", "notation": "4d6!"}
        ],
        "target_number": 8
      },
      "example_result": {
        "pools": [
          {
            "name": "Armed Combat (defaulting)",
            "rolls": [9, 8, 6, 5, 3, 2],
            "successes": 2
          },
          {
            "name": "Combat Pool",
            "rolls": [11, 7, 4, 3],
            "successes": 1
          }
        ],
        "total_successes": 3
      }
    }
  ],
  "outcome": {
    "successes": 3,
    "result": "Solid hit - 3 successes despite defaulting penalty",
    "note": "Combat Pool helped compensate for the +4 defaulting penalty"
  }
}
```

### Test Case 16.5: Attribute-Only Defaulting - INTELLIGENCE to Demolitions

**Scenario:** Nova (INTELLIGENCE 8, no relevant skills) tries to defuse a bomb using only raw intelligence.

```json
{
  "test": "attribute_only_defaulting",
  "character": {
    "name": "Nova",
    "attribute": "INTELLIGENCE",
    "attribute_value": 8,
    "target_skill": "Demolitions",
    "has_skill": false,
    "karma_pool": 6
  },
  "task": {
    "description": "Defuse bomb with no training",
    "base_target_number": 4,
    "critical": true
  },
  "steps": [
    {
      "step": 1,
      "action": "Calculate defaulting modifier",
      "path": "INTELLIGENCE → dot_m1 → dot_m2 → dot_m3 → Demolitions",
      "dots": 3,
      "modifier": "+6",
      "final_tn": 10,
      "note": "Very difficult - attribute to unrelated skill"
    },
    {
      "step": 2,
      "action": "Buy Karma dice",
      "decision": "Buy 3 Karma dice to boost chances",
      "tool": "buy_karma_dice",
      "input": {
        "karma_dice_count": 3,
        "target_number": 10,
        "sides": 6,
        "exploding": true
      },
      "karma_cost": 3,
      "example_result": {
        "rolls": [12, 8, 5],
        "successes": 2,
        "note": "2 successes from Karma dice"
      }
    },
    {
      "step": 3,
      "action": "Roll INTELLIGENCE",
      "tool": "roll_with_target_number",
      "input": {
        "notation": "8d6!",
        "target_number": 10
      },
      "example_result": {
        "rolls": [11, 9, 7, 6, 5, 4, 3, 2],
        "successes": 1,
        "note": "Only 1 success from attribute dice"
      }
    },
    {
      "step": 4,
      "action": "Combine results",
      "calculation": "Karma dice (2) + Attribute (1) = 3 total successes"
    }
  ],
  "outcome": {
    "total_successes": 3,
    "karma_spent": 3,
    "result": "Success - Nova defuses the bomb with 3 successes",
    "note": "Without Karma dice, would have only had 1 success. Defaulting from attribute alone is very difficult (TN 10)."
  }
}
```

### Test Case 16.6: Impossible Defaulting Attempt

**Scenario:** Trying to default from a magic skill to a vehicle skill (should fail).

```json
{
  "test": "impossible_defaulting",
  "character": {
    "name": "Mystic",
    "known_skill": "Sorcery",
    "known_skill_value": 8,
    "target_skill": "Car",
    "has_target_skill": false
  },
  "task": {
    "description": "Try to drive a car using magic knowledge",
    "base_target_number": 4
  },
  "steps": [
    {
      "step": 1,
      "action": "Check skill web for path",
      "path": "No path exists",
      "reason": "Magic skills and vehicle skills are completely separate branches",
      "result": "Cannot default"
    }
  ],
  "outcome": {
    "result": "FAILURE - Cannot attempt",
    "note": "Some skills are too unrelated to default between. Character must use REACTION attribute instead, or cannot attempt the task."
  }
}
```

### Skill Defaulting Scenario Notes

1. **Defaulting Penalties Stack Up:**
   - 1-2 dots: +2 to +4 (manageable)
   - 3-4 dots: +6 to +8 (difficult)
   - 5+ dots: +10+ (very difficult)

2. **Karma Can Help:**
   - Buy Karma dice before rolling (1 Karma per die)
   - Reroll failures after rolling (escalating cost: 1, 2, 3 Karma)
   - Buy successes if you have at least 1 natural success (permanent Karma cost)

3. **Combat Pool Usage:**
   - Can allocate Combat Pool dice to defaulted combat skills
   - Helps compensate for defaulting penalties
   - Must split pool between offense and defense

4. **Opposed Tests:**
   - Defender with actual skill has advantage over defaulting attacker
   - Net successes determine outcome

- Tool name
- Input parameters
- Expected output structure
- Special notes where applicable

The tests cover:
- Basic functionality
- Edge cases
- Error conditions
- Shadowrun-specific mechanics
- Karma Pool usage
- Various difficulty levels
- Different pool combinations
- Skill web pathfinding and defaulting calculations
