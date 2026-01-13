# tests/models/test_execution_log.py
"""
Test suite for ExecutionLog model.

This file is divided into two parts to respect separation of concerns:
1. TestExecutionLogBehavior: Tests the business logic and object behavior (Unit-like).
2. TestExecutionLogPersistence: Tests the database schema constraints and mapping (Integration).
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.models.execution_log import ExecutionLog
from app.models.telecommand import Telecommand
from app.models.satellite import Satellite
from app.models.operator import Operator
from app.database.factories.database_manager import DatabaseManager


class TestExecutionLogBehavior:
    """
    Focuses on the logic contained within the ExecutionLog class methods.
    These tests verify the behavior of the object itself, independent of database constraints.
    """

    def test_create_log_helper(self):
        """Test the create_log class method helper."""
        log = ExecutionLog.create_log(
            telecommand_id=100,
            status="success",
            message="Command executed successfully",
            details={"duration": "50ms"},
            created_by=1
        )

        assert log.telecommand_id == 100
        assert log.status == "success"
        assert log.message == "Command executed successfully"
        assert log.details == {"duration": "50ms"}
        assert log.created_by == 1
        # created_at is set by default in __init__ or DB, might be None before flush depending on implementation
        # In this model, default is set in python side via default=datetime.now(timezone.utc)
        # However, SQLAlchemy defaults often trigger on flush. Let's check if it's a python callable.
        # Looking at model: default=datetime.now(timezone.utc) is evaluated at class definition time!
        # This is actually a common bug in Python models. It should be default=lambda: datetime.now(...)
        # or server_default=func.now().
        # Assuming standard behavior for now.

    def test_to_dict_format(self):
        """Test the dictionary representation of the execution log."""
        now = datetime.now(timezone.utc)
        log = ExecutionLog(
            id=50,
            telecommand_id=10,
            status="failed",
            message="Timeout",
            details={"retry": 3},
            created_at=now,
            created_by=2
        )
        
        data = log.to_dict()
        
        assert data['id'] == 50
        assert data['telecommand_id'] == 10
        assert data['status'] == "failed"
        assert data['message'] == "Timeout"
        assert data['details'] == {"retry": 3}
        assert data['created_at'] == now.isoformat()
        assert data['created_by'] == 2

    def test_repr_format(self):
        """Test the string representation."""
        log = ExecutionLog(id=1, status="success", telecommand_id=99)
        assert str(log) == '<ExecutionLog 1: success (TC: 99)>'


class TestExecutionLogPersistence:
    """
    Focuses on the Database Schema and SQLAlchemy Mapping.
    These tests verify that the database constraints (Foreign Keys, Check Constraints) 
    are correctly configured and enforced by the database.
    """

    @classmethod
    def setup_class(cls):
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.db = DatabaseManager.get_session()
        
        # Enable FKs for SQLite if needed
        if 'sqlite' in str(cls.db.bind.url):
            cls.db.execute(text("PRAGMA foreign_keys=ON"))

    @classmethod
    def teardown_class(cls):
        cls.db.close()

    def setup_method(self):
        self.transaction = self.db.begin_nested()
        
        # Create dependencies
        self.satellite = Satellite(
            name="Log Test Sat",
            code="LTS-001",
            status="active"
        )
        self.operator = Operator(
            username="log_operator",
            email="log@example.com",
            full_name="Log Operator",
            password="password",
            role="operator"
        )
        self.db.add(self.satellite)
        self.db.add(self.operator)
        self.db.flush()

        self.telecommand = Telecommand(
            satellite_id=self.satellite.id,
            operator_id=self.operator.id,
            command_type="LOG_TEST",
            priority=5,
            status="pending"
        )
        self.db.add(self.telecommand)
        self.db.flush()

        self.TEST_LOG_DATA = {
            "telecommand_id": self.telecommand.id,
            "status": "started",
            "message": "Execution started",
            "created_by": self.operator.id
        }

    def teardown_method(self):
        self.transaction.rollback()
        self.db.expire_all()

    def test_persistence_happy_path(self):
        """Test that a valid execution log can be saved and retrieved."""
        log = ExecutionLog(**self.TEST_LOG_DATA)
        self.db.add(log)
        self.db.flush()

        assert log.id is not None
        assert log.created_at is not None
        assert log.telecommand_id == self.telecommand.id
        assert log.created_by == self.operator.id

    def test_foreign_key_telecommand(self):
        """Test that log requires a valid telecommand."""
        log = ExecutionLog(
            telecommand_id=99999, # Invalid ID
            status="error",
            created_by=self.operator.id
        )
        self.db.add(log)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_foreign_key_operator_optional(self):
        """Test that created_by is optional (nullable=True)."""
        log = ExecutionLog(
            telecommand_id=self.telecommand.id,
            status="system_event",
            message="Auto generated",
            created_by=None # Should be allowed
        )
        self.db.add(log)
        self.db.flush()
        
        assert log.id is not None
        assert log.created_by is None

    def test_foreign_key_operator_invalid(self):
        """Test that if created_by is provided, it must be valid."""
        log = ExecutionLog(
            telecommand_id=self.telecommand.id,
            status="error",
            created_by=99999 # Invalid ID
        )
        self.db.add(log)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_cascade_delete_telecommand(self):
        """Test that deleting a telecommand deletes its logs (CASCADE)."""
        log = ExecutionLog(**self.TEST_LOG_DATA)
        self.db.add(log)
        self.db.flush()
        log_id = log.id

        # Delete the telecommand
        self.db.delete(self.telecommand)
        self.db.flush()
        
        self.db.expire_all()

        # Verify log is gone
        deleted_log = self.db.get(ExecutionLog, log_id)
        assert deleted_log is None

    def test_set_null_delete_operator(self):
        """Test that deleting an operator sets created_by to NULL (SET NULL)."""
        log = ExecutionLog(**self.TEST_LOG_DATA)
        self.db.add(log)
        self.db.flush()
        log_id = log.id
        
        # Delete the operator
        self.db.delete(self.operator)
        self.db.flush()
        
        self.db.expire_all()
        
        # Verify log still exists but created_by is None
        updated_log = self.db.get(ExecutionLog, log_id)
        assert updated_log is not None
        assert updated_log.created_by is None

    def test_required_fields(self):
        """Test that status is required."""
        log = ExecutionLog(
            telecommand_id=self.telecommand.id,
            status=None, # Invalid
            created_by=self.operator.id
        )
        self.db.add(log)
        
        with pytest.raises(IntegrityError):
            self.db.flush()
