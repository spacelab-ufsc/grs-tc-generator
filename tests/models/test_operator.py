# tests/models/test_operator.py
"""
Test suite for Operator model.

This file is divided into two parts to respect separation of concerns:
1. TestOperatorBehavior: Tests the business logic and object behavior (Unit-like).
2. TestOperatorPersistence: Tests the database schema constraints and mapping (Integration).
"""
import json
from zoneinfo import ZoneInfo

import pytest
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, select

from app.models.operator import Operator
from app.database.factories.database_manager import DatabaseManager


class TestOperatorBehavior:
    """
    Focuses on the logic contained within the Operator class methods.
    These tests verify the behavior of the object itself, independent of database constraints.
    """
    
    def test_password_hashing_logic(self):
        """Test that the password property handles hashing correctly."""
        operator = Operator(password="secret123")

        # Logic: Password should be hashed, not plain text
        assert operator.password_hash is not None
        assert operator.password_hash != "secret123"
        
        # Logic: Verify method should work
        assert operator.verify_password("secret123") is True
        assert operator.verify_password("wrong") is False

    def test_password_is_not_readable(self):
        """Test that password attribute cannot be read directly."""
        operator = Operator(password="secret")
        with pytest.raises(AttributeError, match="password is not a readable attribute"):
            _ = operator.password

    def test_to_dict_format(self):
        """Test the dictionary representation of the operator."""
        now = datetime.now(UTC)
        operator = Operator(
            id=1,
            username="test",
            email="test@test.com",
            full_name="Test",
            role="operator",
            status="active",
            created_at=now,
            last_login=now
        )
        
        data = operator.to_dict()
        
        assert data['username'] == "test"
        assert data['role'] == "operator"
        assert 'password_hash' not in data  # Security check
        print(data.get("created_at"))
        if data.get("created_at"):
            br_tz = ZoneInfo("America/Sao_Paulo")
            dt_utc = datetime.fromisoformat(data["created_at"])
            data["created_at"] = dt_utc.astimezone(br_tz).strftime("%d/%m/%Y %H:%M:%S")
            dt_utc = datetime.fromisoformat(data["last_login"])
            data["last_login"] = dt_utc.astimezone(br_tz).strftime("%d/%m/%Y %H:%M:%S")
        print(f"\nDictionary: ")
        print(json.dumps(data, indent=4, default=str))

    def test_to_dict_with_sensitive_data(self):
        """Test to_dict with include_sensitive flag."""
        operator = Operator(password="secret")
        data = operator.to_dict(include_sensitive=True)
        assert 'password_hash' in data

    def test_repr_format(self):
        """Test the string representation."""
        operator = Operator(username="user1", role="admin")
        assert str(operator) == '<Operator user1 (admin)>'


class TestOperatorPersistence:
    """
    Focuses on the Database Schema and SQLAlchemy Mapping.
    These tests verify that the database constraints (Unique, Not Null, Check) 
    are correctly configured and enforced by the database.
    """

    TEST_OPERATOR_DATA = {
        "username": "db_user",
        "email": "db@example.com",
        "full_name": "DB User",
        "password": "password123",
        "role": "operator"
    }

    # Test Data
    TEST_OPERATOR = {
        "username": "test_user",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepassword123",
        "role": "operator"
    }

    @classmethod
    def setup_class(cls):
        """Setup once before all tests."""
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.db = DatabaseManager.get_session()

    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests complete."""
        cls.db.close()

    def setup_method(self):
        """Run before each test method."""
        self.transaction = self.db.begin_nested()
        # Create test data
        self.test_operator = Operator(**self.TEST_OPERATOR)
        self.db.add(self.test_operator)
        self.db.flush()

    def teardown_method(self):
        """Run after each test"""
        self.transaction.rollback()

    def test_persistence_happy_path(self):
        """Test that a valid operator can be saved and retrieved."""
        operator = Operator(**self.TEST_OPERATOR_DATA)
        self.db.add(operator)
        self.db.flush()

        assert operator.id is not None
        # Verify default values applied by DB/SQLAlchemy
        assert operator.status == 'active'
        assert operator.created_at is not None

    def test_constraint_unique_username(self):
        """Test that the database enforces unique usernames."""
        # Create first user
        op1 = Operator(**self.TEST_OPERATOR_DATA)
        self.db.add(op1)
        self.db.flush()

        # Create second user with same username
        op2 = Operator(**self.TEST_OPERATOR_DATA)
        op2.email = "different@example.com" # Change email to isolate username error
        
        self.db.add(op2)
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_constraint_unique_email(self):
        """Test that the database enforces unique emails."""
        op1 = Operator(**self.TEST_OPERATOR_DATA)
        self.db.add(op1)
        self.db.flush()

        op2 = Operator(**self.TEST_OPERATOR_DATA)
        op2.username = "different_user" # Change username to isolate email error
        
        self.db.add(op2)
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_constraint_required_fields(self):
        """Test that nullable=False fields are enforced."""
        # Missing username, email, etc.
        operator = Operator(full_name="Just Name") 
        self.db.add(operator)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_check_constraint_role(self):
        """Test the CheckConstraint for valid roles."""
        data = self.TEST_OPERATOR_DATA.copy()
        data['role'] = 'super_hacker' # Invalid role
        
        operator = Operator(**data)
        self.db.add(operator)
        
        with pytest.raises(IntegrityError):
            self.db.flush()

    def test_check_constraint_status(self):
        """Test the CheckConstraint for valid status."""
        data = self.TEST_OPERATOR_DATA.copy()
        data['status'] = 'deleted' # Invalid status (assuming 'deleted' is not in the allowed list)
        
        operator = Operator(**data)
        self.db.add(operator)
        
        with pytest.raises(IntegrityError):
            self.db.flush()


    def test_get_all_operators(self):
        """Test data retrieval (limited to 5)."""
        operators = self.db.query(Operator).limit(5).all()
        print("\n")
        for operator in operators:
            print(f"Found operator: {operator.username} ({operator.email})")

        print("\n✓  Operators retrieval all test passed")

    def test_get_operator_by_id(self):
        """Test retrieving operator by ID."""
        operator = self.db.get(Operator, self.test_operator.id)
        assert operator is not None
        assert operator.username == self.TEST_OPERATOR["username"]
        print("\n✓  Operator retrieval by ID test passed")

    # Test 6:
    def test_get_operator_by_username(self):
        """Test retrieving operator by username."""
        operators = self.db.execute(
            select(Operator).where(Operator.username == self.test_operator.username)
        ).scalar_one_or_none()

        assert operators is not None
        assert operators.username == self.test_operator.username

        print("\n✓  Operator retrieval by username test passed")

    # Test 7:
    def test_update_operator(self):
        """Verify we can update operator information."""
        self.test_operator.full_name = "Updated Name"
        self.test_operator.role = "admin"
        self.db.flush()

        updated = self.db.get(Operator, self.test_operator.id)
        assert updated is not None
        assert updated.full_name == "Updated Name"
        assert updated.role == "admin"

        print("\n✓   Operator Update test passed")

    # Test 8:
    def test_delete_operator(self):
        """Verify we can delete an operator."""
        operator_id = self.test_operator.id
        self.db.delete(self.test_operator)
        self.db.flush()
        deleted = self.db.get(Operator, operator_id)
        assert deleted is None

        print("\n✓  Operator Delete test passed")
