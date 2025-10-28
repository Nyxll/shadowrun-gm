#!/usr/bin/env python3
"""
Comprehensive Test Runner for New Features
Runs all test suites for bug fixes and enhancements
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules directly
import importlib.util
import sys

def load_test_module(filepath):
    """Load a test module from filepath"""
    spec = importlib.util.spec_from_file_location("test_module", filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules["test_module"] = module
    spec.loader.exec_module(module)
    return module

# Load test modules
test_dir = os.path.dirname(os.path.abspath(__file__))
char_sheet_module = load_test_module(os.path.join(test_dir, "test-character-sheet.py"))
char_removal_module = load_test_module(os.path.join(test_dir, "test-character-removal.py"))
loading_states_module = load_test_module(os.path.join(test_dir, "test-loading-states.py"))

run_character_sheet_tests = char_sheet_module.run_all_tests
run_character_removal_tests = char_removal_module.run_all_tests
run_loading_state_tests = loading_states_module.run_all_tests


async def main():
    """Run all test suites"""
    print("=" * 70)
    print("SHADOWRUN GM - COMPREHENSIVE TEST SUITE")
    print("Testing Bug Fixes and New Features")
    print("=" * 70)
    print()
    
    results = {}
    
    # Run character sheet tests
    print("\n" + "=" * 70)
    print("SUITE 1: CHARACTER SHEET VIEWING")
    print("=" * 70)
    results['character_sheet'] = await run_character_sheet_tests()
    
    # Run character removal tests
    print("\n" + "=" * 70)
    print("SUITE 2: CHARACTER REMOVAL")
    print("=" * 70)
    results['character_removal'] = await run_character_removal_tests()
    
    # Run loading state tests
    print("\n" + "=" * 70)
    print("SUITE 3: LOADING STATES")
    print("=" * 70)
    results['loading_states'] = await run_loading_state_tests()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    total_suites = len(results)
    passed_suites = sum(1 for result in results.values() if result)
    failed_suites = total_suites - passed_suites
    
    print(f"\nTest Suites:")
    for suite_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {suite_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_suites}/{total_suites} suites passed")
    
    if failed_suites > 0:
        print(f"\n⚠ {failed_suites} suite(s) failed - check output above for details")
        print("Screenshots saved for failed tests")
    else:
        print("\n✓ All test suites passed!")
    
    print("=" * 70)
    
    return all(results.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
