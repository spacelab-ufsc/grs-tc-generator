from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from ..database_config import DatabaseConfig


class PostgresConfig(DatabaseConfig):
    """PostgreSQL database configuration"""

    def create_engine(self) -> Engine:
        return create_engine(
            self.db_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            **self.kwargs
        )
