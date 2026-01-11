# app/models/execution_log.py
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.database_config import Base

# Avoid circular imports
if TYPE_CHECKING:
    from .telecommand import Telecommand
    from .operator import Operator

class ExecutionLog(Base):
    __tablename__ = 'execution_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc),
        nullable=False
    )

    # Foreign keys
    telecommand_id: Mapped[int] = mapped_column(
        ForeignKey('telecommands.id', ondelete='CASCADE'),
        nullable=False
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey('operators.id', ondelete='SET NULL'),
        nullable=True
    )

    # Relationships
    telecommand: Mapped["Telecommand"] = relationship(
        "Telecommand",
        back_populates="execution_logs"
    )
    creator: Mapped[Optional["Operator"]] = relationship(
        "Operator",
        back_populates="execution_logs"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution log to a dictionary."""
        return {
            'id': self.id,
            'telecommand_id': self.telecommand_id,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

    @classmethod
    def create_log(
        cls,
        telecommand_id: int,
        status: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None
    ) -> "ExecutionLog":
        """ Helper method to create a new log entry.

           Args:
               telecommand_id: ID of the related telecommand
               status: Status of the execution
               message: Optional status message
               details: Optional additional details
               created_by: Optional ID of the operator who created the log

           Returns:
               Newly created ExecutionLog instance
        """
        return cls(
            telecommand_id=telecommand_id,
            status=status,
            message=message,
            details=details,
            created_by=created_by
        )

    def __repr__(self) -> str:
        return f'<ExecutionLog {self.id}: {self.status} (TC: {self.telecommand_id})>'

