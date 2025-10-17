#!/usr/bin/env node

/**
 * Skill Web Defaulting Test Suite
 * Tests the 8 skill web defaulting scenarios from test-cases.md
 */

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Simple BFS pathfinding for skill web
function findShortestPath(graph, start, end) {
  if (start === end) {
    return {
      path: [start],
      dots: [],
      dotCount: 0,
      modifier: 0
    };
  }

  const queue = [[start]];
  const visited = new Set([start]);

  while (queue.length > 0) {
    const path = queue.shift();
    const current = path[path.length - 1];

    if (!graph[current]) continue;

    for (const connection of graph[current].connections) {
      const next = connection.destination;

      if (next === end) {
        const fullPath = [...path, next];
        const dots = fullPath.filter(node => node.startsWith('dot_'));
        return {
          path: fullPath,
          dots: dots,
          dotCount: dots.length,
          modifier: dots.length * 2
        };
      }

      if (!visited.has(next)) {
        visited.add(next);
        queue.push([...path, next]);
      }
    }
  }

  return null; // No path found
}

// Test cases from test-cases.md Section 15
const testCases = [
  {
    name: "Test 15.1: Intelligence to Demolitions",
    from: "INTELLIGENCE",
    to: "Demolitions",
    expected: {
      dotCount: 3,
      modifier: 6
    }
  },
  {
    name: "Test 15.2: Intelligence to Magical Theory",
    from: "INTELLIGENCE",
    to: "Magical Theory",
    expected: {
      dotCount: 5,
      modifier: 10
    }
  },
  {
    name: "Test 15.3: Willpower to Military Theory",
    from: "WILLPOWER",
    to: "Military Theory",
    expected: {
      dotCount: 5,
      modifier: 10
    }
  },
  {
    name: "Test 15.4: Magical Theory to Military Theory",
    from: "Magical Theory",
    to: "Military Theory",
    expected: {
      dotCount: 6,
      modifier: 12
    }
  },
  {
    name: "Test 15.5: Psychology to Sociology",
    from: "Psychology",
    to: "Sociology",
    expected: {
      dotCount: 2,
      modifier: 4
    }
  },
  {
    name: "Test 15.6: QUICKNESS to Stealth",
    from: "QUICKNESS",
    to: "Stealth",
    expected: {
      dotCount: 2,
      modifier: 4
    }
  },
  {
    name: "Test 15.7: Bike to Vector Thrust",
    from: "Bike",
    to: "Vector Thrust",
    expected: {
      dotCount: 5,
      modifier: 10
    }
  },
  {
    name: "Test 15.8: Sociology to Negotiation",
    from: "Sociology",
    to: "Negotiation",
    expected: {
      dotCount: 5,
      modifier: 10
    }
  },
  // Impossible Paths - Skills too unrelated to default
  {
    name: "Test 15.9: WILLPOWER to Vector Thrust (Impossible)",
    from: "WILLPOWER",
    to: "Vector Thrust",
    expected: {
      noPath: true,
      reason: "Mental attribute cannot default to vehicle skill"
    }
  },
  {
    name: "Test 15.10: Computer Theory to Demolitions (Impossible)",
    from: "Computer Theory",
    to: "Demolitions",
    expected: {
      noPath: true,
      reason: "Technical skill cannot default to combat skill"
    }
  },
  {
    name: "Test 15.11: Sorcery to Car (Impossible)",
    from: "Sorcery",
    to: "Car",
    expected: {
      noPath: true,
      reason: "Magic skill cannot default to vehicle skill"
    }
  },
  {
    name: "Test 15.12: Firearms to Enchanting (Impossible)",
    from: "Firearms",
    to: "Enchanting",
    expected: {
      noPath: true,
      reason: "Combat skill cannot default to magic skill"
    }
  },
  {
    name: "Test 15.13: Biology to Armed Combat (Impossible)",
    from: "Biology",
    to: "Armed Combat",
    expected: {
      noPath: true,
      reason: "Science skill cannot default to combat skill"
    }
  },
  // Edge Cases
  {
    name: "Test 15.14: Same Skill (Firearms to Firearms)",
    from: "Firearms",
    to: "Firearms",
    expected: {
      dotCount: 0,
      modifier: 0,
      sameskill: true
    }
  },
  {
    name: "Test 15.15: Direct Connection (QUICKNESS to Athletics)",
    from: "QUICKNESS",
    to: "Athletics",
    expected: {
      dotCount: 1,
      modifier: 2
    }
  },
  // B/R (Build/Repair) Skills
  {
    name: "Test 15.16: Firearms to Firearms (B/R)",
    from: "Firearms",
    to: "Firearms (B/R)",
    expected: {
      dotCount: 1,
      modifier: 2
    }
  },
  {
    name: "Test 15.17: Computer to Computer (B/R)",
    from: "Computer",
    to: "Computer (B/R)",
    expected: {
      dotCount: 1,
      modifier: 2
    }
  },
  {
    name: "Test 15.18: Gunnery (B/R) to Projectile (B/R)",
    from: "Gunnery (B/R)",
    to: "Projectile (B/R)",
    expected: {
      dotCount: 5,
      modifier: 10
    }
  },
  // Cross-Category Paths (Valid but Long)
  {
    name: "Test 15.19: INTELLIGENCE to Car (Impossible)",
    from: "INTELLIGENCE",
    to: "Car",
    expected: {
      noPath: true,
      reason: "No connection between mental skills and vehicle skills in current graph"
    }
  },
  {
    name: "Test 15.20: CHARISMA to Computer (Impossible)",
    from: "CHARISMA",
    to: "Computer",
    expected: {
      noPath: true,
      reason: "No connection between social skills and technical skills in current graph"
    }
  },
  {
    name: "Test 15.21: Stealth to Negotiation (Impossible)",
    from: "Stealth",
    to: "Negotiation",
    expected: {
      noPath: true,
      reason: "No connection between physical skills and social skills in current graph"
    }
  },
  // Real-World Scenarios
  {
    name: "Test 15.22: Armed Combat to Unarmed Combat (Street Samurai)",
    from: "Armed Combat",
    to: "Unarmed Combat",
    expected: {
      dotCount: 2,
      modifier: 4
    }
  },
  {
    name: "Test 15.23: Computer to Electronics (Decker)",
    from: "Computer",
    to: "Electronics",
    expected: {
      dotCount: 1,
      modifier: 2
    }
  },
  {
    name: "Test 15.24: Sorcery to Magical Theory (Mage)",
    from: "Sorcery",
    to: "Magical Theory",
    expected: {
      dotCount: 2,
      modifier: 4
    }
  },
  {
    name: "Test 15.25: Negotiation to Psychology (Face)",
    from: "Negotiation",
    to: "Psychology",
    expected: {
      noPath: true,
      reason: "No reverse path from Negotiation back to Psychology in current graph"
    }
  }
];

async function runTests() {
  console.log('='.repeat(80));
  console.log('SKILL WEB DEFAULTING TEST SUITE');
  console.log('='.repeat(80));
  console.log();

  // Load skill web graph from downloaded file
  const graphPath = join(__dirname, 'skill-web-downloaded.json');
  const graphData = await readFile(graphPath, 'utf-8');
  const graph = JSON.parse(graphData);
  
  console.log('Using skill web graph from: https://shadowrun2.com/dice/skill-web.json');
  console.log();

  let passed = 0;
  let failed = 0;

  for (const test of testCases) {
    console.log(`\n${test.name}`);
    console.log('-'.repeat(80));
    console.log(`From: ${test.from}`);
    console.log(`To: ${test.to}`);

    const result = findShortestPath(graph, test.from, test.to);

    if (!result) {
      if (test.expected.noPath) {
        console.log('✅ PASSED - No path found (as expected)');
        console.log(`Reason: ${test.expected.reason}`);
        passed++;
      } else {
        console.log('❌ FAILED: No path found');
        failed++;
      }
      continue;
    }

    // If we found a path but expected no path
    if (test.expected.noPath) {
      console.log('❌ FAILED: Found unexpected path');
      console.log(`Path: ${result.path.join(' → ')}`);
      console.log(`Expected: No path (${test.expected.reason})`);
      failed++;
      continue;
    }

    console.log(`Path: ${result.path.join(' → ')}`);
    console.log(`Dots traversed: [${result.dots.join(', ')}]`);
    console.log(`Dot count: ${result.dotCount}`);
    console.log(`Modifier: +${result.modifier}`);

    // Verify results based on test type
    let testPassed = false;

    if (test.expected.sameskill) {
      // Same skill test - should have 0 modifier
      testPassed = result.dotCount === 0 && result.modifier === 0;
      if (testPassed) {
        console.log('✅ PASSED - Same skill (no defaulting needed)');
        passed++;
      } else {
        console.log('❌ FAILED - Expected 0 modifier for same skill');
        failed++;
      }
    } else if (test.expected.minModifier !== undefined) {
      // Minimum modifier test - verify path exists and meets minimum
      testPassed = result.modifier >= test.expected.minModifier;
      if (testPassed) {
        console.log(`✅ PASSED - Path found with modifier +${result.modifier} (minimum +${test.expected.minModifier})`);
        passed++;
      } else {
        console.log(`❌ FAILED - Modifier +${result.modifier} is less than minimum +${test.expected.minModifier}`);
        failed++;
      }
    } else {
      // Exact match test
      const dotCountMatch = result.dotCount === test.expected.dotCount;
      const modifierMatch = result.modifier === test.expected.modifier;

      if (dotCountMatch && modifierMatch) {
        console.log('✅ PASSED');
        passed++;
      } else {
        console.log('❌ FAILED');
        if (!dotCountMatch) {
          console.log(`   Expected dot count: ${test.expected.dotCount}, got: ${result.dotCount}`);
        }
        if (!modifierMatch) {
          console.log(`   Expected modifier: +${test.expected.modifier}, got: +${result.modifier}`);
        }
        failed++;
      }
    }
  }

  // Summary
  console.log('\n' + '='.repeat(80));
  console.log('TEST SUMMARY');
  console.log('='.repeat(80));
  console.log(`Total tests: ${testCases.length}`);
  console.log(`Passed: ${passed} ✅`);
  console.log(`Failed: ${failed} ❌`);
  console.log(`Success rate: ${((passed / testCases.length) * 100).toFixed(1)}%`);
  console.log('='.repeat(80));

  process.exit(failed > 0 ? 1 : 0);
}

runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
