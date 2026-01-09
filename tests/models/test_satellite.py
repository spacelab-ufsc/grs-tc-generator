# tests/models/test_satellite.py
"""
Test suite for Satellite model and database operations.

This module contains comprehensive tests for the Satellite model, including:
- Database operations
- Data validation
- Business logic
- Relationships
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from app.models.satellite import Satellite
from app.database.factories.database_manager import DatabaseManager


class TestSatellite:
    """Test suite for Satellite model and database operations."""

    # Test Data
    TEST_SATELLITE = {
        "name": "Test Satellite",
        "code": "TS-001",
        "description": "Test satellite for unit testing",
        "status": "active"
    }

    @classmethod
    def setup_class(cls):
        """Setup once before all tests."""
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.db: Session = DatabaseManager.get_session()

    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests complete."""
        cls.db.close()

    def setup_method(self):
        """Setup before each test method."""
        self.transaction = self.db.begin_nested()
        # Create test data
        self.test_satellite = Satellite(**self.TEST_SATELLITE)
        self.db.add(self.test_satellite)
        self.db.flush()

    def teardown_method(self):
        """Cleanup after each test method."""
        self.transaction.rollback()

    # Test 1. Database Connection Test
    def test_database_connection(self):
        """Test database connection is working."""
        result = self.db.execute(text("SELECT 1")).scalar()
        assert result == 1, "Database connection failed"
        print("\n✓ Database connection test passed")

    # Test 2. Table Existence Test
    def test_satellite_table_exists(self):
        """Verify satellites table exists."""
        result = self.db.execute(text("""
                                      SELECT EXISTS (SELECT
                                                     FROM information_schema.tables
                                                     WHERE table_schema = 'public'
                                                       AND table_name = 'satellites')
                                      """)).scalar()
        assert result is True, "Satellites table does not exist"
        print("\n✓ Satellite Table ok")

    # Test 3. Test Create (Insert) Operation
    def test_create_satellite(self):
        """Test creating a new satellite."""
        new_satellite = Satellite(
            name="New Test Satellite",
            code="TS-002",
            description="Another test satellite",
            status="active"
        )
        self.db.add(new_satellite)
        self.db.flush()

        assert new_satellite.id is not None
        assert new_satellite.created_at is not None
        assert new_satellite.updated_at is not None
        assert new_satellite.status == "active"

        # Verify the record was inserted
        inserted = self.db.get(Satellite, new_satellite.id)
        assert inserted is not None, "Failed to insert test satellite"
        assert inserted.name == new_satellite.name
        assert inserted.code == new_satellite.code
        assert inserted.description == new_satellite.description

        print("\n✓  New Operator created successfully")

    # Test 4. Test Read (Retrieve) Operation - Get All
    def test_get_all_satellites(self):
        """Test retrieving all satellites."""
        satellites = self.db.query(Satellite).all()
        print("\n")
        for satellite in satellites:
            print(f"Found satellite: {satellite.name} ({satellite.code})")

        assert isinstance(satellites, list)
        if satellites:
            assert all(isinstance(sat, Satellite) for sat in satellites)

        print("\n✓  Satellites retrieval all test passed")

    # Test 5. Test Read (Retrieve) Operation - Get By ID
    def test_get_satellite_by_id(self):
        """Test retrieving satellite by ID."""
        satellite = self.db.get(Satellite, self.test_satellite.id)
        assert satellite is not None
        assert satellite.code == self.TEST_SATELLITE["code"]

        print("\n✓  Satellite retrieval by ID test passed")

    # Test 6. Test Read (Retrieve) Operation - Get By Code
    def test_get_satellite_by_code(self):
        """Test retrieving satellite by code."""
        satellite = self.db.execute(
            select(Satellite).where(Satellite.code == self.test_satellite.code)
        ).scalar_one_or_none()

        assert satellite is not None
        assert satellite.name == self.test_satellite.name

        print("\n✓  Satellite retrieval by code test passed")

    # 7. Test Update Operation
    def test_update_satellite(self):
        """Test updating satellite information."""
        original_updated = self.test_satellite.updated_at
        self.test_satellite.name = "Updated Satellite Name"
        self.test_satellite.status = "maintenance"
        self.db.flush()

        updated = self.db.get(Satellite, self.test_satellite.id)
        assert updated is not None
        assert updated.name == "Updated Satellite Name"
        assert updated.status == "maintenance"
        assert updated.updated_at.timestamp() > original_updated.timestamp() # Verify updated_at was changed

        print("\n✓   Satellite Update test passed")

    # Test 8. Test Delete Operation
    def test_delete_satellite(self):
        """Test deleting a satellite."""
        satellite_id = self.test_satellite.id
        self.db.delete(self.test_satellite)
        self.db.flush()

        deleted = self.db.get(Satellite, satellite_id)
        assert deleted is None

        print("\n✓  Satellite Delete test passed")

    # Test9. Test Status Validation
    def test_status_validation(self):
        """Test that status must be one of the allowed values."""
        with pytest.raises(IntegrityError):
            satellite = Satellite(
                name="Invalid Status",
                code="TS-999",
                status="invalid_status"
            )
            self.db.add(satellite)
            self.db.flush()

    # Test 10. Test Required Fields
    @pytest.mark.parametrize("field", ["name", "code", "status"])
    def test_required_fields(self, field):
        """Test that required fields cannot be null."""
        # Create a copy of test data and remove the field being tested
        data = self.TEST_SATELLITE.copy()
        data[field] = None

        satellite = Satellite(**data)
        self.db.add(satellite)

        with pytest.raises(IntegrityError):
            self.db.flush()
            self.db.rollback()

    # Test 11. Test Code Uniqueness
    def test_code_uniqueness(self):
        """Test that satellite codes must be unique."""
        with pytest.raises(IntegrityError):
            duplicate_satellite = Satellite(
                name="Duplicate Satellite",
                code=self.TEST_SATELLITE["code"],  # Duplicate code
                status="active"
            )
            self.db.add(duplicate_satellite)
            self.db.flush()

    # Test 12. Test Timestamp Updates
    def test_timestamp_updates(self):
        """Test that timestamps are automatically updated."""
        original_updated = self.test_satellite.updated_at
        self.test_satellite.description = "Updated description"
        self.db.flush()

        updated = self.db.get(Satellite, self.test_satellite.id)
        # Compare timestamps properly
        assert updated.updated_at.timestamp() > original_updated.timestamp()