#!/usr/bin/env python3
"""
Run all Python test suites for Shadowrun GM
"""

import sys
import asyncio
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_game_server_mcp import MCPTestSuite
from test_ui import UITestSuite


async def main():
    """Run all Python test suites"""
    
    print("\n" + "="*70)
    print("SHADOWRUN GM - COMPLETE PYTHON TEST SUITE")
    print("="*70 + "\n")
    
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    # Run MCP tests
    print("Running Game Server MCP Tests...")
    print("-"*70)
    mcp_suite = MCPTestSuite()
    mcp_success = await mcp_suite.run_all_tests()
    total_passed += mcp_suite.passed
    total_failed += mcp_suite.failed
    total_tests += mcp_suite.tests_run
    
    print("\n" + "="*70 + "\n")
    
    # Run UI tests
    print("Running UI Tests...")
    print("-"*70)
    ui_suite = UITestSuite()
    ui_success = await ui_suite.run_all_tests()
    total_passed += ui_suite.passed
    total_failed += ui_suite.failed
    total_tests += ui_suite.tests_run
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"\nGame Server MCP Tests: {mcp_suite.passed}/{mcp_suite.tests_run} passed")
    print(f"UI Tests: {ui_suite.passed}/{ui_suite.tests_run} passed")
    print(f"\nTOTAL: {total_passed}/{total_tests} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {total_failed} TESTS FAILED")
    
    print("="*70 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
