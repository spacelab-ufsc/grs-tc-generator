# tests/db_test.py
import unittest
import os
from datetime import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your database manager
from app.database.factories.database_manager import DatabaseManager
from app.database.database_config import Base


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        db_url = os.getenv('PG_DATABASE_URL_TEST')
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.session = DatabaseManager.get_session()

    def test_operator_retrieval(self):
        """Test that operators can be retrieved from the database."""
        with self.session as session:
            result = session.execute(text("""
                                          SELECT username, email, role
                                          FROM operators
                                          WHERE username = 'admin'
                                          """))
            operator = result.fetchone()

            self.assertIsNotNone(operator, "Admin operator should exist")
            self.assertEqual(operator.email, 'admin@tcgenerator.com')
            self.assertEqual(operator.role, 'admin')

    def test_satellite_retrieval(self):
        """Test that satellites can be retrieved from the database."""
        with self.session as session:
            result = session.execute(text("""
                                          SELECT name, code, status
                                          FROM satellites
                                          WHERE code = 'SAT-001'
                                          """))
            satellite = result.fetchone()

            self.assertIsNotNone(satellite, "Satellite SAT-001 should exist")
            self.assertEqual(satellite.name, 'FloripaSat-1')
            self.assertEqual(satellite.status, 'active')

    def test_telecommand_operations(self):
        """Test basic telecommand operations."""
        with self.session as session:
            # Test inserting a new telecommand
            result = session.execute(text("""
                                          INSERT INTO telecommands
                                              (satellite_id, operator_id, command_type, parameters, status, priority)
                                          VALUES (1, 1, 'TEST_CMD', '{"test": "data"}', 'pending', 5) RETURNING id
                                          """))
            telecommand_id = result.scalar()
            session.commit()

            self.assertIsNotNone(telecommand_id, "Should return a new telecommand ID")

            # Verify the telecommand was inserted
            result = session.execute(text("""
                                          SELECT command_type, status
                                          FROM telecommands
                                          WHERE id = :id
                                          """), {'id': telecommand_id})

            telecommand = result.fetchone()
            self.assertEqual(telecommand.command_type, 'TEST_CMD')
            self.assertEqual(telecommand.status, 'pending')

            # Clean up
            session.execute(text("DELETE FROM telecommands WHERE id = :id"), {'id': telecommand_id})
            session.commit()

    def test_execution_log_operations(self):
        """Test execution log operations."""
        with self.session as session:
            # First, ensure we have a telecommand to log against
            result = session.execute(text("""
                                          SELECT id
                                          FROM telecommands
                                          ORDER BY id LIMIT 1
                                          """))
            telecommand = result.fetchone()

            if not telecommand:
                self.fail("No telecommand found to test execution logs")
                return

            telecommand_id = telecommand[0]

            # Test inserting a log
            result = session.execute(text("""
                                          INSERT INTO execution_logs
                                              (telecommand_id, status, message, details, created_by)
                                          VALUES (:telecommand_id, 'success', 'Test execution', '{"test": true}',
                                                  1) RETURNING id
                                          """), {'telecommand_id': telecommand_id})

            log_id = result.scalar()
            session.commit()

            self.assertIsNotNone(log_id, "Should return a new log ID")

            # Verify the log was inserted
            result = session.execute(text("""
                                          SELECT status, message
                                          FROM execution_logs
                                          WHERE id = :id
                                          """), {'id': log_id})

            log = result.fetchone()
            self.assertEqual(log.status, 'success')
            self.assertEqual(log.message, 'Test execution')

    def test_command_stats_function(self):
        """Test the get_satellite_command_stats function."""
        with self.session as session:
            result = session.execute(text("""
                                          SELECT *
                                          FROM get_satellite_command_stats(30)
                                          WHERE satellite_id = 1
                                          """))

            stats = result.fetchone()

            # At least one satellite should have stats
            self.assertIsNotNone(stats, "Should return stats for satellite 1")

            # Verify the structure of the returned data
            self.assertTrue(hasattr(stats, 'satellite_id'))
            self.assertTrue(hasattr(stats, 'satellite_name'))
            self.assertTrue(hasattr(stats, 'total_commands'))
            self.assertTrue(isinstance(stats.total_commands, int))

    @classmethod
    def tearDownClass(cls):
        """Clean up database connection."""
        if cls.session:
            cls.session.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)