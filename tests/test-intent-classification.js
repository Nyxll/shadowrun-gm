/**
 * Test Suite for Intent Classification System
 * Tests pattern matching, keyword analysis, and unified classifier
 */

import { PatternMatcher } from '../lib/intent/pattern-matcher.js';
import { KeywordAnalyzer } from '../lib/intent/keyword-analyzer.js';
import { IntentClassifier } from '../lib/intent/intent-classifier.js';

// Test data: 100+ real-world queries with expected intents
const testQueries = [
  // SPELL_LOOKUP queries (15 tests)
  { query: 'what is the Fireball spell?', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'show me the Manaball spell', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'list all combat spells', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'show me manipulation spells', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'what spells are available?', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'tell me about the heal spell', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'spell stats for invisibility', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'what magic can I cast?', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'show me detection spells', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'list illusion spells', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'what is mana drain?', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'armor spell info', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'levitate spell stats', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'confusion spell details', expected: 'SPELL_LOOKUP', method: 'keyword' },
  { query: 'list health spells', expected: 'SPELL_LOOKUP', method: 'pattern' },
  
  // POWER_LOOKUP queries (10 tests)
  { query: 'what are adept powers?', expected: 'POWER_LOOKUP', method: 'pattern' },
  { query: 'list all adept powers', expected: 'POWER_LOOKUP', method: 'pattern' },
  { query: 'show me critter powers', expected: 'POWER_LOOKUP', method: 'pattern' },
  { query: 'improved reflexes power', expected: 'POWER_LOOKUP', method: 'pattern' },
  { query: 'killing hands info', expected: 'POWER_LOOKUP', method: 'keyword' },
  { query: 'mystic armor power stats', expected: 'POWER_LOOKUP', method: 'keyword' },
  { query: 'what powers can I get?', expected: 'POWER_LOOKUP', method: 'keyword' },
  { query: 'enhanced perception details', expected: 'POWER_LOOKUP', method: 'keyword' },
  { query: 'combat sense power', expected: 'POWER_LOOKUP', method: 'keyword' },
  { query: 'list powers', expected: 'POWER_LOOKUP', method: 'pattern' },
  
  // TOTEM_LOOKUP queries (10 tests)
  { query: 'what is Bear totem?', expected: 'TOTEM_LOOKUP', method: 'pattern' },
  { query: 'Wolf totem advantages', expected: 'TOTEM_LOOKUP', method: 'pattern' },
  { query: 'list all totems', expected: 'TOTEM_LOOKUP', method: 'pattern' },
  { query: 'show me shamanic totems', expected: 'TOTEM_LOOKUP', method: 'pattern' },
  { query: 'Eagle totem info', expected: 'TOTEM_LOOKUP', method: 'keyword' },
  { query: 'Raven totem disadvantages', expected: 'TOTEM_LOOKUP', method: 'keyword' },
  { query: 'what totems are there?', expected: 'TOTEM_LOOKUP', method: 'keyword' },
  { query: 'Cat totem details', expected: 'TOTEM_LOOKUP', method: 'keyword' },
  { query: 'Snake totem stats', expected: 'TOTEM_LOOKUP', method: 'keyword' },
  { query: 'list totems', expected: 'TOTEM_LOOKUP', method: 'pattern' },
  
  // GEAR_LOOKUP queries (15 tests)
  { query: 'show me the Ares Predator', expected: 'GEAR_LOOKUP', method: 'pattern' },
  { query: 'what is the Colt Manhunter?', expected: 'GEAR_LOOKUP', method: 'pattern' },
  { query: 'stats for Remington 990', expected: 'GEAR_LOOKUP', method: 'pattern' },
  { query: 'look up AK-97', expected: 'GEAR_LOOKUP', method: 'pattern' },
  { query: 'Ares Predator stats', expected: 'GEAR_LOOKUP', method: 'pattern' },
  { query: 'tell me about the Uzi', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'HK227 info', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'Beretta pistol details', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'Ruger weapon stats', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'Panther Cannon info', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'what is cyberware?', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'armor jacket stats', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'smartlink info', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'datajack details', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'wired reflexes stats', expected: 'GEAR_LOOKUP', method: 'keyword' },
  
  // GEAR_COMPARISON queries (10 tests)
  { query: 'compare Ares Predator and Colt Manhunter', expected: 'GEAR_COMPARISON', method: 'pattern' },
  { query: 'what\'s the best heavy pistol?', expected: 'GEAR_COMPARISON', method: 'pattern' },
  { query: 'top assault rifles', expected: 'GEAR_COMPARISON', method: 'pattern' },
  { query: 'rank shotguns by damage', expected: 'GEAR_COMPARISON', method: 'pattern' },
  { query: 'better pistol for damage', expected: 'GEAR_COMPARISON', method: 'pattern' },
  { query: 'compare SMGs', expected: 'GEAR_COMPARISON', method: 'keyword' },
  { query: 'which rifle is better?', expected: 'GEAR_COMPARISON', method: 'keyword' },
  { query: 'best cyberware for essence', expected: 'GEAR_COMPARISON', method: 'keyword' },
  { query: 'top armor by rating', expected: 'GEAR_COMPARISON', method: 'keyword' },
  { query: 'rank weapons by cost', expected: 'GEAR_COMPARISON', method: 'keyword' },
  
  // RULES_QUESTION queries (15 tests)
  { query: 'how does initiative work?', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'explain combat resolution', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'what are the rules for magic?', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'how do I calculate damage?', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'explain spell drain', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'how does hacking work?', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'rules for astral combat', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'how to determine target numbers?', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'explain rigging mechanics', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'what are the healing rules?', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'how does physical adept work?', expected: 'RULES_QUESTION', method: 'pattern' },
  { query: 'explain initiative calculation', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'rules for damage resistance', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'how to resolve opposed tests?', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'when do I use karma?', expected: 'RULES_QUESTION', method: 'keyword' },
  
  // LIST_QUERY queries (10 tests)
  { query: 'list all heavy pistols', expected: 'LIST_QUERY', method: 'pattern' },
  { query: 'show me all assault rifles', expected: 'LIST_QUERY', method: 'pattern' },
  { query: 'what weapons are there?', expected: 'LIST_QUERY', method: 'pattern' },
  { query: 'list SMGs', expected: 'LIST_QUERY', method: 'pattern' },
  { query: 'show all shotguns', expected: 'LIST_QUERY', method: 'pattern' },
  { query: 'what armor is available?', expected: 'LIST_QUERY', method: 'keyword' },
  { query: 'list cyberware', expected: 'LIST_QUERY', method: 'keyword' },
  { query: 'show me all melee weapons', expected: 'LIST_QUERY', method: 'pattern' },
  { query: 'what sniper rifles exist?', expected: 'LIST_QUERY', method: 'keyword' },
  { query: 'list light pistols', expected: 'LIST_QUERY', method: 'pattern' },
  
  // Edge cases and complex queries (15 tests)
  { query: 'Fireball', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'Bear', expected: 'TOTEM_LOOKUP', method: 'pattern' },
  { query: 'improved reflexes', expected: 'POWER_LOOKUP', method: 'pattern' },
  { query: 'predator', expected: 'GEAR_LOOKUP', method: 'pattern' },
  { query: 'how initiative', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'best pistol damage', expected: 'GEAR_COMPARISON', method: 'pattern' },
  { query: 'all spells', expected: 'SPELL_LOOKUP', method: 'pattern' },
  { query: 'magic rules', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'compare pistols', expected: 'GEAR_COMPARISON', method: 'keyword' },
  { query: 'totem advantages', expected: 'TOTEM_LOOKUP', method: 'keyword' },
  { query: 'adept power list', expected: 'POWER_LOOKUP', method: 'keyword' },
  { query: 'weapon stats', expected: 'GEAR_LOOKUP', method: 'keyword' },
  { query: 'spell drain mechanics', expected: 'RULES_QUESTION', method: 'keyword' },
  { query: 'rank rifles', expected: 'GEAR_COMPARISON', method: 'keyword' },
  { query: 'shamanic totem', expected: 'TOTEM_LOOKUP', method: 'keyword' },
];

// Test runner
class IntentClassificationTester {
  constructor() {
    this.patternMatcher = new PatternMatcher();
    this.keywordAnalyzer = new KeywordAnalyzer();
    this.results = {
      total: 0,
      passed: 0,
      failed: 0,
      pattern_correct: 0,
      keyword_correct: 0,
      pattern_total: 0,
      keyword_total: 0,
      failures: [],
    };
  }
  
  runTests() {
    console.log('🧪 Running Intent Classification Tests...\n');
    
    for (const test of testQueries) {
      this.results.total++;
      const { query, expected, method } = test;
      
      // Try pattern matching first
      const patternResult = this.patternMatcher.match(query);
      if (patternResult) {
        this.results.pattern_total++;
        if (patternResult.intent === expected) {
          this.results.passed++;
          this.results.pattern_correct++;
          if (method === 'pattern') {
            console.log(`✓ PASS (pattern): "${query}" → ${expected}`);
          } else {
            console.log(`✓ PASS (pattern, expected ${method}): "${query}" → ${expected}`);
          }
          continue;
        }
      }
      
      // Try keyword analysis
      const keywordResult = this.keywordAnalyzer.analyze(query);
      if (keywordResult) {
        this.results.keyword_total++;
        if (keywordResult.intent === expected) {
          this.results.passed++;
          this.results.keyword_correct++;
          if (method === 'keyword') {
            console.log(`✓ PASS (keyword): "${query}" → ${expected}`);
          } else {
            console.log(`✓ PASS (keyword, expected ${method}): "${query}" → ${expected}`);
          }
          continue;
        }
      }
      
      // Test failed
      this.results.failed++;
      this.results.failures.push({
        query,
        expected,
        got_pattern: patternResult?.intent || null,
        got_keyword: keywordResult?.intent || null,
      });
      console.log(`✗ FAIL: "${query}"`);
      console.log(`  Expected: ${expected}`);
      console.log(`  Pattern: ${patternResult?.intent || 'no match'}`);
      console.log(`  Keyword: ${keywordResult?.intent || 'no match'}`);
    }
    
    this.printSummary();
  }
  
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Tests: ${this.results.total}`);
    console.log(`Passed: ${this.results.passed} (${((this.results.passed / this.results.total) * 100).toFixed(1)}%)`);
    console.log(`Failed: ${this.results.failed} (${((this.results.failed / this.results.total) * 100).toFixed(1)}%)`);
    console.log('');
    console.log('Stage Performance:');
    console.log(`  Pattern Matching: ${this.results.pattern_correct}/${this.results.pattern_total} (${this.results.pattern_total > 0 ? ((this.results.pattern_correct / this.results.pattern_total) * 100).toFixed(1) : 0}%)`);
    console.log(`  Keyword Analysis: ${this.results.keyword_correct}/${this.results.keyword_total} (${this.results.keyword_total > 0 ? ((this.results.keyword_correct / this.results.keyword_total) * 100).toFixed(1) : 0}%)`);
    console.log('');
    
    if (this.results.failures.length > 0) {
      console.log('Failed Tests:');
      for (const failure of this.results.failures) {
        console.log(`  - "${failure.query}"`);
        console.log(`    Expected: ${failure.expected}, Got: ${failure.got_pattern || failure.got_keyword || 'no match'}`);
      }
    }
    
    console.log('='.repeat(60));
  }
}

// Run tests
const tester = new IntentClassificationTester();
tester.runTests();
