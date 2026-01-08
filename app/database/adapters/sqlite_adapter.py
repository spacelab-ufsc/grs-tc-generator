from sqlalchemy import create_engine
from ..database_config import DatabaseConfig


class SQLiteConfig(DatabaseConfig):
    """SQLite database configuration"""

    def create_engine(self):
        return create_engine(
            self.db_url,
            connect_args={"check_same_thread": False} if ":memory:" in self.db_url or "sqlite" in self.db_url else {},
            **self.kwargs
        )
