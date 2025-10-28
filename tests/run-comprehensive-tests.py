#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Runs all tests repeatedly until all pass
"""

import subprocess
import sys
import time
from datetime import datetime

def run_test(test_file, description):
    """Run a single test file and return success status"""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            ['python', test_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        print(f"\n{'✓ PASSED' if success else '✗ FAILED'}: {description}")
        return success
        
    except subprocess.TimeoutExpired:
        print(f"\n✗ TIMEOUT: {description} took longer than 5 minutes")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {description} - {e}")
        return False

def main():
    """Run all tests in sequence"""
    
    tests = [
        # Core CRUD API tests
        ('tests/test-all-crud-operations.py', 'CRUD API Operations (All Characters)'),
        ('tests/test-comprehensive-crud.py', 'Comprehensive CRUD Tests'),
        
        # Schema validation
        ('tests/test-schema-fixes.py', 'Schema Validation'),
        
        # MCP operations
        ('tests/test-game-server-mcp.py', 'MCP Server Operations'),
        
        # UI tests (if Playwright test completes)
        # ('tests/test-character-sheet-ui.py', 'Character Sheet UI (Playwright)'),
        
        # Specific feature tests
        ('tests/test-spell-force-display.py', 'Spell Force Display'),
        ('tests/test-cast-spell-learned-force.py', 'Spell Casting with Learned Force'),
        ('tests/test-spellcasting-mcp.py', 'Spellcasting MCP Tool'),
    ]
    
    iteration = 1
    max_iterations = 10  # Run up to 10 times or until all pass
    
    while iteration <= max_iterations:
        print(f"\n\n{'#'*70}")
        print(f"# TEST ITERATION {iteration}/{max_iterations}")
        print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}\n")
        
        results = {}
        all_passed = True
        
        for test_file, description in tests:
            success = run_test(test_file, description)
            results[description] = success
            if not success:
                all_passed = False
        
        # Print summary
        print(f"\n\n{'='*70}")
        print(f"ITERATION {iteration} SUMMARY")
        print(f"{'='*70}")
        
        passed_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        for description, success in results.items():
            status = '✓ PASS' if success else '✗ FAIL'
            print(f"{status}: {description}")
        
        print(f"\nResults: {passed_count}/{total_count} tests passed")
        print(f"{'='*70}\n")
        
        if all_passed:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
            print(f"Completed in {iteration} iteration(s)")
            return 0
        
        if iteration < max_iterations:
            print(f"\nSome tests failed. Waiting 5 seconds before retry...")
            time.sleep(5)
        
        iteration += 1
    
    print(f"\n⚠ Not all tests passed after {max_iterations} iterations")
    print(f"Please review failures and fix issues manually")
    return 1

if __name__ == "__main__":
    sys.exit(main())
