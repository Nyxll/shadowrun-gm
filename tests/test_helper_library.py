#!/usr/bin/env python3
"""
Test the helper library modules

This script tests all helper utilities to ensure they work correctly
before we start using them in consolidated tools.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.db_utils import get_db_connection, execute_query, get_character_id, table_exists
from lib.helpers.test_utils import isolated_test_db, create_test_character, create_test_mage
from lib.helpers.logging_utils import setup_logger, log_operation, log_success, log_failure, OperationTimer
from lib.helpers.validation_utils import (
    validate_character_name,
    validate_attribute_value,
    validate_skill_rating,
    validate_essence,
    check_required_fields
)

def test_db_utils():
    """Test database utilities"""
    logger = setup_logger(__name__)
    log_operation(logger, "TEST", "Testing database utilities")
    
    # Test connection
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            assert result[0] == 1
        log_success(logger, "Database connection works")
    except Exception as e:
        log_failure(logger, f"Database connection failed: {e}")
        return False
    
    # Test execute_query
    try:
        result = execute_query("SELECT COUNT(*) FROM characters", fetch='one')
        assert result is not None
        log_success(logger, f"execute_query works (found {result[0]} characters)")
    except Exception as e:
        log_failure(logger, f"execute_query failed: {e}")
        return False
    
    # Test table_exists
    try:
        assert table_exists('characters') == True
        assert table_exists('nonexistent_table') == False
        log_success(logger, "table_exists works")
    except Exception as e:
        log_failure(logger, f"table_exists failed: {e}")
        return False
    
    # Test get_character_id
    try:
        char_id = get_character_id("Platinum")
        if char_id:
            log_success(logger, f"get_character_id works (Platinum ID: {char_id})")
        else:
            log_success(logger, "get_character_id works (Platinum not found)")
    except Exception as e:
        log_failure(logger, f"get_character_id failed: {e}")
        return False
    
    return True

def test_test_utils():
    """Test test isolation utilities"""
    logger = setup_logger(__name__)
    log_operation(logger, "TEST", "Testing test isolation utilities")
    
    # Test isolated_test_db
    try:
        with isolated_test_db() as conn:
            char_id = create_test_character(conn, "Isolation Test")
            assert char_id is not None
            
            # Verify character exists in transaction
            cur = conn.cursor()
            cur.execute("SELECT name FROM characters WHERE id = %s", (char_id,))
            result = cur.fetchone()
            assert result[0] == "Isolation Test"
        
        # Verify character was rolled back
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM characters WHERE name = 'Isolation Test'")
            count = cur.fetchone()[0]
            assert count == 0
        
        log_success(logger, "Transaction isolation works (automatic rollback)")
    except Exception as e:
        log_failure(logger, f"Transaction isolation failed: {e}")
        return False
    
    # Test create_test_mage
    try:
        with isolated_test_db() as conn:
            mage_id = create_test_mage(conn, "Test Mage", magic=6, totem="Oak")
            assert mage_id is not None
            
            cur = conn.cursor()
            cur.execute("SELECT base_magic, totem FROM characters WHERE id = %s", (mage_id,))
            result = cur.fetchone()
            assert result[0] == 6
            assert result[1] == "Oak"
        
        log_success(logger, "create_test_mage works")
    except Exception as e:
        log_failure(logger, f"create_test_mage failed: {e}")
        return False
    
    return True

def test_logging_utils():
    """Test logging utilities"""
    logger = setup_logger(__name__)
    log_operation(logger, "TEST", "Testing logging utilities")
    
    # Test basic logging
    log_success(logger, "Success message test")
    log_failure(logger, "Failure message test (this is expected)")
    
    # Test OperationTimer
    try:
        with OperationTimer(logger, "Test Operation"):
            # Simulate work
            import time
            time.sleep(0.1)
        log_success(logger, "OperationTimer works")
    except Exception as e:
        log_failure(logger, f"OperationTimer failed: {e}")
        return False
    
    return True

def test_validation_utils():
    """Test validation utilities"""
    logger = setup_logger(__name__)
    log_operation(logger, "TEST", "Testing validation utilities")
    
    # Test character name validation
    assert validate_character_name("Platinum") == True
    assert validate_character_name("A") == False
    assert validate_character_name("") == False
    log_success(logger, "validate_character_name works")
    
    # Test attribute validation
    assert validate_attribute_value(6) == True
    assert validate_attribute_value(0) == False
    assert validate_attribute_value(21) == False
    log_success(logger, "validate_attribute_value works")
    
    # Test skill rating validation
    assert validate_skill_rating(6) == True
    assert validate_skill_rating(0) == True  # Untrained
    assert validate_skill_rating(13) == False
    log_success(logger, "validate_skill_rating works")
    
    # Test essence validation
    assert validate_essence(6.0) == True
    assert validate_essence(3.5) == True
    assert validate_essence(6.1) == False
    assert validate_essence(-0.1) == False
    log_success(logger, "validate_essence works")
    
    # Test check_required_fields
    data = {'name': 'Platinum', 'metatype': 'Human'}
    missing = check_required_fields(data, ['name', 'metatype', 'body'])
    assert missing == ['body']
    log_success(logger, "check_required_fields works")
    
    return True

def main():
    """Run all helper library tests"""
    logger = setup_logger(__name__)
    
    print("\n" + "=" * 70)
    print("HELPER LIBRARY TEST SUITE")
    print("=" * 70 + "\n")
    
    tests = [
        ("Database Utilities", test_db_utils),
        ("Test Isolation Utilities", test_test_utils),
        ("Logging Utilities", test_logging_utils),
        ("Validation Utilities", test_validation_utils),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'─' * 70}")
        print(f"Testing: {name}")
        print(f"{'─' * 70}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            log_failure(logger, f"{name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} test suites passed")
    
    if passed == total:
        print("\n✅ All helper library tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test suite(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
