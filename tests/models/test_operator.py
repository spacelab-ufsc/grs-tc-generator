# tests/models/test_operator.py
"""
Test suite for Operator model and database operations.

This module contains comprehensive tests for the Operator model, including:
- Database connection tests
- CRUD operations
- Data validation
- Business logic
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from app.models.operator import Operator
from app.database.factories.database_manager import DatabaseManager


class TestOperator:
    """Test suite for Operator model and database operations."""
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
        # Initialize test database
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.db = DatabaseManager.get_session()

    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests complete."""
        cls.db.close()

    def setup_method(self):
        """Run before each test method."""
        # Start a new transaction
        self.transaction = self.db.begin_nested()
        # Create test data
        self.test_operator = Operator(**self.TEST_OPERATOR)
        self.db.add(self.test_operator)
        self.db.flush()

    def teardown_method(self):
        """Run after each test"""
        # Rollback the transaction
        self.transaction.rollback()

    # Test 1:
    def test_database_connection(self):
        """Test database connection is working."""
        result = self.db.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Simple query test failed"
        print("\n✓ Database connection test passed")

    # Test 2:
    def test_operators_table(self):
        """Verify operators table exists and is accessible."""
        result = self.db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'operators')"
        ))
        assert result.scalar() is True, "Operators table does not exist"
        print("\n✓ Operator Table ok")

    # Test 3:
    def test_create_operator(self):
        """Test creating a new operator."""
        new_operator = Operator(
            username="new_user",
            email="new@example.com",
            full_name="New User",
            password="testpass123",
            role="operator"
        )
        self.db.add(new_operator)
        self.db.flush()

        assert new_operator.id is not None
        assert new_operator.created_at is not None

        # Verify the record was inserted
        inserted = self.db.get(Operator, new_operator.id)
        assert inserted is not None, "Failed to insert test operator"
        assert inserted.username == new_operator.username
        assert inserted.email == new_operator.email
        assert inserted.full_name == new_operator.full_name
        assert inserted.role == new_operator.role
        assert inserted.status == "active"
        assert isinstance(inserted.created_at, datetime)
        assert isinstance(inserted.last_login, datetime)

        print("\n✓  New Operator created successfully")

    # Test 4:
    def test_get_all_operators(self):
        """Test data retrieval (limited to 5)."""
        operators = self.db.query(Operator).limit(5).all()
        print("\n")
        for operator in operators:
            print(f"Found operator: {operator.username} ({operator.email})")

        print("\n✓  Operators retrieval all test passed")

    # Test 5:
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

    # Test 9:
    def test_password_hashing(self):
        """Test password hashing and verification"""
        operator = Operator(
            username="testuser2",
            email="test2@example.com",
            full_name="Test User 2",
            password="securepassword123",
            role="operator"
        )

        # Check password is hashed
        assert operator.password_hash is not None
        assert operator.password_hash != "securepassword123"

        # Verify password
        assert operator.verify_password("securepassword123") is True
        assert operator.verify_password("wrongpassword") is False

        print("\n✓  Password Hashing test passed")

    # Test 10:
    def test_required_fields(self):
        """Test that required fields cannot be null"""
        operator = Operator()  # Missing required fields
        self.db.add(operator)

        with pytest.raises(IntegrityError):
            self.db.commit()

        self.db.rollback()

    # Test 11:
    @pytest.mark.parametrize("field", ["username", "email", "password_hash", "role"])
    def test_required_fields_parametrize(self, field):
        """Test that required fields cannot be null."""
        # Create a copy of test data and remove the field being tested
        data = self.TEST_OPERATOR.copy()
        data[field] = None

        operator = Operator(**data)
        self.db.add(operator)

        with pytest.raises(IntegrityError):
            self.db.commit()
            self.db.rollback()

    # Additional Test: Test Role Validation
    def test_role_validation(self):
        """Test that role must be one of the allowed values."""
        with pytest.raises(IntegrityError):
            operator = Operator(
                username="invalid_role",
                email="invalid@example.com",
                full_name="Invalid Role",
                password="test123",
                role="invalid_role"
            )
            self.db.add(operator)
            self.db.flush()