import os

from ..adapters.postgres_adapter import PostgresConfig

from ..adapters.sqlite_adapter import SQLiteConfig
from flask_sqlalchemy.session import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseManager:
    """Database factory class"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._db_config = None
        return cls._instance

    @classmethod
    def init_db(cls, db_type: str = 'postgresql', **kwargs) -> Session:
        """Initialize the database connection"""
        if db_type == 'sqlite':
            db_url = kwargs.pop('db_url', os.getenv('SQLITE_DATABASE_URL', 'sqlite:///app.db'))
            cls._db_config = SQLiteConfig(db_url=db_url, **kwargs)
        elif db_type == 'postgresql_test':
            db_url = kwargs.pop('db_url', os.getenv('PG_DATABASE_URL_TEST'))
            cls._db_config = PostgresConfig(db_url=db_url, **kwargs)
        else:  # Default to PostgreSQL
            db_url = kwargs.pop('db_url', os.getenv('PG_DATABASE_URL'))
            cls._db_config = PostgresConfig(db_url=db_url, **kwargs)

        return cls._db_config.create_session()

    @classmethod
    def get_session(cls) -> Session:
        """Get a new database session"""
        if cls._db_config is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return cls._db_config.create_session()

    @classmethod
    def close_session(cls, session: Session) -> None:
        """Close the database session"""
        if session:
            session.close()
