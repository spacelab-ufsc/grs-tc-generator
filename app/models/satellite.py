# app/models/satellite.py
from ..database.database_config import Base
from datetime import datetime
from typing import List
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import event


class Satellite(Base):
    __tablename__ = 'satellites'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    status: Mapped[str] = mapped_column(
        String(20),
        default='active',
        nullable=False,
        server_default='active'
    )

    # Relationships (temporarily disabled for testing)
    #telecommands: Mapped[List["Telecommand"]] = relationship(back_populates='satellite')

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'maintenance')",
            name='valid_satellite_status'
        ),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Satellite {self.code}: {self.name}>'


# Update the timestamp when the satellite is updated.
@event.listens_for(Satellite, 'before_update')
def update_updated_at(mapper, connection, target):
    target.updated_at = datetime.utcnow()