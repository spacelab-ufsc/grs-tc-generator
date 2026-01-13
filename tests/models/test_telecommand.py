# tests/models/test_telecommand.py
"""
Test suite for Telecommand model.

This file is divided into two parts to respect separation of concerns:
1. TestTelecommandBehavior: Tests the business logic and object behavior (Unit-like).
2. TestTelecommandPersistence: Tests the database schema constraints and mapping (Integration).
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.models.telecommand import Telecommand
from app.models.satellite import Satellite
from app.models.operator import Operator
from app.database.factories.database_manager import DatabaseManager


class TestTelecommandBehavior:
    """
    Focuses on the logic contained within the Telecommand class methods.
    These tests verify the behavior of the object itself, independent of database constraints.
    """

    def test_update_status_logic(self):
        """Test the update_status method logic and timestamp setting."""
        telecommand = Telecommand(status="pending")
        
        # 1. Update to 'sent'
        telecommand.update_status("sent", "Sending command")
        assert telecommand.status == "sent"
        assert telecommand.status_message == "Sending command"
        assert telecommand.sent_at is not None
        # Ensure timezone awareness
        assert telecommand.sent_at.tzinfo is not None 

        # 2. Update to 'confirmed'
        telecommand.update_status("confirmed", "Success")
        assert telecommand.status == "confirmed"
        assert telecommand.confirmed_at is not None
        assert telecommand.confirmed_at.tzinfo is not None
        
        # Logic check: sent_at should be before or equal to confirmed_at
        assert telecommand.sent_at <= telecommand.confirmed_at

    def test_to_dict_format(self):
        """Test the dictionary representation of the telecommand."""
        now = datetime.now(timezone.utc)
        telecommand = Telecommand(
            id=1,
            satellite_id=10,
            operator_id=5,
            command_type="PING",
            parameters={"timeout": 1000},
            status="pending",
            created_at=now,
            priority=5,
            metadata_={"source": "test"}
        )
        
        data = telecommand.to_dict()
        
        assert data['id'] == 1
        assert data['command_type'] == "PING"
        assert data['parameters'] == {"timeout": 1000}
        assert data['created_at'] == now.isoformat()
        assert data['metadata'] == {"source": "test"}

    def test_repr_format(self):
        """Test the string representation."""
        telecommand = Telecommand(id=123, command_type="RESET", status="queued")
        assert str(telecommand) == '<Telecommand 123: RESET (queued)>'


class TestTelecommandPersistence:
    """
    Focuses on the Database Schema and SQLAlchemy Mapping.
    These tests verify that the database constraints (Foreign Keys, Check Constraints) 
    are correctly configured and enforced by the database.
    """

    @classmethod
    def setup_class(cls):
        # Ensure we are using a fresh database state
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.db = DatabaseManager.get_session()
        
        # If using SQLite, we must enable foreign keys manually for each connection
        if 'sqlite' in str(cls.db.bind.url):
            cls.db.execute(text("PRAGMA foreign_keys=ON"))

    @classmethod
    def teardown_class(cls):
        cls.db.close()

    def setup_method(self):
        # Start a nested transaction (SAVEPOINT)
        self.transaction = self.db.begin_nested()
        
        # Create dependencies (Satellite and Operator)
        self.satellite = Satellite(
            name="Telecommand Test Sat",
            code="TCS-001",
            status="active"
        )
        self.operator = Operator(
            username="tc_operator",
            email="tc@example.com",
            full_name="TC Operator",
            password="password",
            role="operator"
        )
        self.db.add(self.satellite)
        self.db.add(self.operator)
        self.db.flush()

        self.TEST_TC_DATA = {
            "satellite": self.satellite,
            "operator": self.operator,
            "command_type": "TEST_CMD",
            "parameters": {"p1": 1},
            "priority": 5
        }

    def teardown_method(self):
        # Rollback the nested transaction
        self.transaction.rollback()
        # Expunge all objects to ensure clean state for next test
        self.db.expire_all()

    def test_persistence_happy_path(self):
        """Test that a valid telecommand can be saved and retrieved."""
        tc = Telecommand(**self.TEST_TC_DATA)
        self.db.add(tc)
        self.db.flush()

        assert tc.id is not None
        assert tc.status == "pending" # Default value
        assert tc.created_at is not None
        assert tc.satellite_id == self.satellite.id
        assert tc.operator_id == self.operator.id

    def test_foreign_key_satellite(self):
        """Test that telecommand requires a valid satellite."""
        # Try to create with invalid satellite_id
        tc = Telecommand(
            satellite_id=99999, # Non-existent ID
            operator_id=self.operator.id,
            command_type="FAIL",
            priority=5
        )
        self.db.add(tc)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_foreign_key_operator(self):
        """Test that telecommand requires a valid operator."""
        # Try to create with invalid operator_id
        tc = Telecommand(
            satellite_id=self.satellite.id,
            operator_id=99999, # Non-existent ID
            command_type="FAIL",
            priority=5
        )
        self.db.add(tc)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_check_constraint_status(self):
        """Test the CheckConstraint for valid status."""
        data = self.TEST_TC_DATA.copy()
        data['status'] = 'invalid_status'
        
        tc = Telecommand(**data)
        self.db.add(tc)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_check_constraint_priority(self):
        """Test the CheckConstraint for valid priority (1-10)."""
        # Test lower bound
        tc_low = Telecommand(**self.TEST_TC_DATA)
        tc_low.priority = 0
        self.db.add(tc_low)
        
        with pytest.raises(IntegrityError):
            self.db.flush()
        
        # IMPORTANT: Rollback the failed flush to clean the session
        self.db.rollback()
        
        # Start a new nested transaction for the next part of the test
        self.transaction = self.db.begin_nested()
        
        # Re-add dependencies because rollback removed them from session
        self.db.add(self.satellite)
        self.db.add(self.operator)
        self.db.flush()

        # Test upper bound
        tc_high = Telecommand(**self.TEST_TC_DATA)
        tc_high.priority = 11
        self.db.add(tc_high)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_cascade_delete_satellite(self):
        """Test that deleting a satellite deletes its telecommands (CASCADE)."""
        tc = Telecommand(**self.TEST_TC_DATA)
        self.db.add(tc)
        self.db.flush()
        tc_id = tc.id

        # Delete the satellite
        self.db.delete(self.satellite)
        self.db.flush()
        
        # Force session to clear cache and reload from DB
        self.db.expire_all()

        # Verify telecommand is gone
        deleted_tc = self.db.get(Telecommand, tc_id)
        assert deleted_tc is None

    def test_set_default_admin_delete_operator(self):
        """
        Test that deleting an operator reassigns telecommands to Admin (ID 1).
        This tests ON DELETE SET DEFAULT.
        """
        # 1. Ensure Admin (ID 1) exists
        admin = self.db.get(Operator, 1)
        if not admin:
            admin = Operator(
                id=1,
                username="admin",
                email="admin@spacelab.com",
                full_name="System Admin",
                password="admin",
                role="admin"
            )
            self.db.merge(admin)
            self.db.flush()

        # 2. Create a telecommand with a regular operator
        tc = Telecommand(**self.TEST_TC_DATA)
        self.db.add(tc)
        self.db.flush()
        
        tc_id = tc.id
        
        # 3. Delete the regular operator
        self.db.delete(self.operator)
        self.db.flush()
        
        # 4. Verify telecommand was NOT deleted, but reassigned
        self.db.expire_all() # Force reload from DB
        updated_tc = self.db.get(Telecommand, tc_id)
        
        # NOTE: If this fails with None, it means the DB did CASCADE delete instead of SET DEFAULT
        # or SET DEFAULT is not supported/enabled.
        assert updated_tc is not None, "Telecommand was deleted instead of reassigned"
        assert updated_tc.operator_id == 1, f"Operator ID should be 1, got {updated_tc.operator_id}"