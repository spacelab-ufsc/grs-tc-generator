from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
import os

Base = declarative_base()


class DatabaseConfig:
    """Base configuration class for database connections"""

    def __init__(self, db_url: str, **kwargs):
        self.db_url = db_url
        self.engine = None
        self.session_factory = None
        self.kwargs = kwargs

    def create_engine(self):
        """Create and return a database engine"""
        raise NotImplementedError("Subclasses must implement this method")

    def create_session(self):
        """Create and return a new session"""
        if not self.engine:
            self.engine = self.create_engine()

        if not self.session_factory:
            self.session_factory = scoped_session(
                sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            )
            Base.metadata.create_all(bind=self.engine)

        return self.session_factory()
