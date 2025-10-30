"""
Helper utilities for Shadowrun GM tools and tests

This package provides reusable utilities for:
- Database connections (db_utils)
- Test isolation (test_utils)
- Logging (logging_utils)
- Validation (validation_utils)
"""

from .db_utils import get_db_connection, execute_query, get_character_id
from .logging_utils import setup_logger, log_operation
from .validation_utils import (
    validate_character_name,
    validate_attribute_value,
    validate_skill_rating,
    validate_essence,
    check_required_fields
)

__all__ = [
    'get_db_connection',
    'execute_query',
    'get_character_id',
    'setup_logger',
    'log_operation',
    'validate_character_name',
    'validate_attribute_value',
    'validate_skill_rating',
    'validate_essence',
    'check_required_fields',
]
