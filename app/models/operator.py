# app/models/operator.py
from datetime import datetime
from typing import List, Dict, Optional
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from ..database.database_config import Base

# Avoid circular imports
if TYPE_CHECKING:
    from .telecommand import Telecommand
    from .execution_log import ExecutionLog


class Operator(Base):
    __tablename__ = 'operators'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default='operator',
        nullable=False,
        server_default='operator'
    )
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_login: Mapped[datetime] = mapped_column(insert_default=func.now())
    status: Mapped[str] = mapped_column(
        String(20),
        default='active',
        nullable=False,
        server_default='active'
    )

    # Relationships
    telecommands: Mapped[List["Telecommand"]] = relationship(
        "Telecommand",
        back_populates="operator",
        cascade="all, delete-orphan"
    )
    execution_logs: Mapped[List["ExecutionLog"]] = relationship(
        "ExecutionLog",
        back_populates="creator"
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'operator', 'viewer')",
            name='valid_operator_role'
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name='valid_operator_status'
        ),
    )

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    def __repr__(self):
        return f'<Operator {self.username} ({self.role})>'