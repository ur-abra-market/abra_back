# The tests module

"""
Function tests should be in tests/endpoints/categories/core/test_get_all_categories.py
Endpoints tests should be in tests/endpoints/categories/test_all.py
"""

from core.settings import database_settings

database_settings.RDS_HOSTNAME = "tests_database"
