#!/usr/bin/env node

/**
 * Test Runner - Executes all test files and aggregates results
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readdir } from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Test results tracking
const results = {
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0,
  tests: [],
};

async function runTest(testFile) {
  return new Promise((resolve) => {
    console.log(`\n${colors.cyan}▶ Running: ${testFile}${colors.reset}`);
    console.log('─'.repeat(80));
    
    const startTime = Date.now();
    const child = spawn('node', [join(__dirname, testFile)], {
      stdio: 'inherit',
      shell: true,
    });
    
    child.on('close', (code) => {
      const duration = Date.now() - startTime;
      const result = {
        file: testFile,
        passed: code === 0,
        duration,
      };
      
      results.tests.push(result);
      results.total++;
      
      if (code === 0) {
        results.passed++;
        console.log(`${colors.green}✓ ${testFile} passed (${duration}ms)${colors.reset}`);
      } else {
        results.failed++;
        console.log(`${colors.red}✗ ${testFile} failed (${duration}ms)${colors.reset}`);
      }
      
      resolve(result);
    });
    
    child.on('error', (error) => {
      console.error(`${colors.red}Error running ${testFile}:${colors.reset}`, error);
      results.failed++;
      results.total++;
      resolve({ file: testFile, passed: false, error: error.message });
    });
  });
}

async function main() {
  console.log(`${colors.blue}╔═══════════════════════════════════════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.blue}║           Shadowrun GM MCP Server - Comprehensive Test Suite             ║${colors.reset}`);
  console.log(`${colors.blue}╚═══════════════════════════════════════════════════════════════════════════╝${colors.reset}`);
  
  const startTime = Date.now();
  
  // Get all test files
  const files = await readdir(__dirname);
  const testFiles = files
    .filter(f => f.startsWith('test-') && f.endsWith('.js'))
    .sort();
  
  if (testFiles.length === 0) {
    console.log(`${colors.yellow}No test files found!${colors.reset}`);
    process.exit(1);
  }
  
  console.log(`\nFound ${testFiles.length} test file(s):\n`);
  testFiles.forEach((f, i) => {
    console.log(`  ${i + 1}. ${f}`);
  });
  
  // Run all tests sequentially
  for (const testFile of testFiles) {
    await runTest(testFile);
  }
  
  const totalDuration = Date.now() - startTime;
  
  // Print summary
  console.log('\n' + '═'.repeat(80));
  console.log(`${colors.blue}TEST SUMMARY${colors.reset}`);
  console.log('═'.repeat(80));
  console.log(`Total Tests:    ${results.total}`);
  console.log(`${colors.green}Passed:         ${results.passed}${colors.reset}`);
  console.log(`${colors.red}Failed:         ${results.failed}${colors.reset}`);
  console.log(`Total Duration: ${totalDuration}ms (${(totalDuration / 1000).toFixed(2)}s)`);
  console.log('═'.repeat(80));
  
  // Print individual test results
  if (results.tests.length > 0) {
    console.log('\nIndividual Test Results:');
    results.tests.forEach((test, i) => {
      const status = test.passed 
        ? `${colors.green}✓ PASS${colors.reset}` 
        : `${colors.red}✗ FAIL${colors.reset}`;
      console.log(`  ${i + 1}. ${status} ${test.file} (${test.duration}ms)`);
    });
  }
  
  // Print failed tests details
  if (results.failed > 0) {
    console.log(`\n${colors.red}Failed Tests:${colors.reset}`);
    results.tests
      .filter(t => !t.passed)
      .forEach(test => {
        console.log(`  - ${test.file}`);
        if (test.error) {
          console.log(`    Error: ${test.error}`);
        }
      });
  }
  
  // Final status
  console.log('\n' + '═'.repeat(80));
  if (results.failed === 0) {
    console.log(`${colors.green}🎉 ALL TESTS PASSED!${colors.reset}`);
    console.log('═'.repeat(80));
    process.exit(0);
  } else {
    console.log(`${colors.red}❌ SOME TESTS FAILED${colors.reset}`);
    console.log('═'.repeat(80));
    process.exit(1);
  }
}

main().catch(error => {
  console.error(`${colors.red}Fatal error:${colors.reset}`, error);
  process.exit(1);
});
