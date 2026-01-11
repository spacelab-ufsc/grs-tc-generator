# tests/models/test_satellite.py
"""
Test suite for Satellite model.

This file is divided into two parts to respect separation of concerns:
1. TestSatelliteBehavior: Tests the business logic and object behavior (Unit-like).
2. TestSatellitePersistence: Tests the database schema constraints and mapping (Integration).
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, select

from app.models.satellite import Satellite
from app.database.factories.database_manager import DatabaseManager


class TestSatelliteBehavior:
    """
    Focuses on the logic contained within the Satellite class methods.
    These tests verify the behavior of the object itself, independent of database constraints.
    """

    def test_to_dict_format(self):
        """Test the dictionary representation of the satellite."""
        now = datetime.now(timezone.utc)
        satellite = Satellite(
            id=1,
            name="Test Satellite",
            code="TS-001",
            description="Test Description",
            status="active",
            created_at=now,
            updated_at=now
        )
        
        data = satellite.to_dict()
        
        assert data['id'] == 1
        assert data['name'] == "Test Satellite"
        assert data['code'] == "TS-001"
        assert data['status'] == "active"
        assert data['created_at'] == now.isoformat()

    def test_repr_format(self):
        """Test the string representation."""
        satellite = Satellite(code="TS-001", name="Test Sat")
        assert str(satellite) == '<Satellite TS-001: Test Sat>'


class TestSatellitePersistence:
    """
    Focuses on the Database Schema and SQLAlchemy Mapping.
    These tests verify that the database constraints (Unique, Not Null, Check) 
    are correctly configured and enforced by the database.
    """

    TEST_SATELLITE_DATA = {
        "name": "Persistence Test Satellite",
        "code": "PTS-001",
        "description": "Test satellite for persistence testing",
        "status": "active"
    }

    @classmethod
    def setup_class(cls):
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.db = DatabaseManager.get_session()

    @classmethod
    def teardown_class(cls):
        cls.db.close()

    def setup_method(self):
        self.transaction = self.db.begin_nested()

    def teardown_method(self):
        self.transaction.rollback()

    def test_persistence_happy_path(self):
        """Test that a valid satellite can be saved and retrieved."""
        satellite = Satellite(**self.TEST_SATELLITE_DATA)
        self.db.add(satellite)
        self.db.flush()

        assert satellite.id is not None
        assert satellite.created_at is not None
        assert satellite.updated_at is not None
        assert satellite.status == "active"

    def test_constraint_unique_code(self):
        """Test that the database enforces unique satellite codes."""
        # Create first satellite
        sat1 = Satellite(**self.TEST_SATELLITE_DATA)
        self.db.add(sat1)
        self.db.flush()

        # Create second satellite with same code
        sat2 = Satellite(**self.TEST_SATELLITE_DATA)
        sat2.name = "Different Name" # Change name to isolate code error
        
        self.db.add(sat2)
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_constraint_required_fields(self):
        """Test that nullable=False fields are enforced."""
        # Missing code, name, etc.
        satellite = Satellite(description="Just Description") 
        self.db.add(satellite)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_check_constraint_status(self):
        """Test the CheckConstraint for valid status."""
        data = self.TEST_SATELLITE_DATA.copy()
        data['status'] = 'exploded' # Invalid status
        
        satellite = Satellite(**data)
        self.db.add(satellite)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_automatic_timestamp_update(self):
        """Test that updated_at is automatically updated on modification."""
        satellite = Satellite(**self.TEST_SATELLITE_DATA)
        self.db.add(satellite)
        self.db.flush()
        
        original_updated_at = satellite.updated_at
        
        # Modify the satellite
        satellite.name = "Updated Name"
        self.db.flush()
        
        # Verify updated_at changed
        # Note: In fast tests, we might need to ensure time passed, 
        # but usually DB precision is enough
        assert satellite.updated_at > original_updated_at
