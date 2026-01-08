from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.declarative import declarative_base

from ..database import db

# Use the db.Model if it exists, otherwise create a new declarative base
Base = db.Model if hasattr(db, 'Model') else declarative_base()

class Telecommand(db.Model):
    __tablename__ = 'telecommands'

    id = db.Column(db.Integer, primary_key=True)
    satellite_id = db.Column(
        db.Integer,
        db.ForeignKey('satellites.id', ondelete='CASCADE'),
        nullable=False
    )
    operator_id = db.Column(
        db.Integer,
        db.ForeignKey('operators.id', ondelete='SET NULL'),
        nullable=False
    )
    command_type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(JSONB, nullable=True)
    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False,
    )
    status_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False
    )
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
    confirmed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    priority = db.Column(
        db.Integer,
        default=5,
        nullable=False
    )
    metadata = db.Column(JSONB, nullable=True)

    # Relacionamentos
    satellite = db.relationship('Satellite', back_populates='telecommands')
    operator = db.relationship('Operator', back_populates='telecommands')
    execution_logs = db.relationship('ExecutionLog', back_populates='telecommand', cascade='all, delete-orphan')

    # Adicionando restrições CHECK
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'queued', 'sent', 'confirmed', 'failed')",
            name='valid_status'
        ),
        CheckConstraint(
            "priority BETWEEN 1 AND 10",
            name='valid_priority'
        ),
    )

    def __init__(self, **kwargs):
        super(Telecommand, self).__init__(**kwargs)
        # Garante que o status esteja sempre em minúsculas
        if self.status:
            self.status = self.status.lower()

    def to_dict(self):
        """Converte o objeto para um dicionário."""
        return {
            'id': self.id,
            'satellite_id': self.satellite_id,
            'operator_id': self.operator_id,
            'command_type': self.command_type,
            'parameters': self.parameters,
            'status': self.status,
            'status_message': self.status_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'priority': self.priority,
            'metadata': self.metadata
        }

    def update_status(self, new_status, message=None):
        """Atualiza o status do telecomando."""
        self.status = new_status.lower()
        self.status_message = message

        now = datetime.utcnow()
        if new_status.lower() == 'sent':
            self.sent_at = now
        elif new_status.lower() == 'confirmed':
            self.confirmed_at = now

        return self

    def __repr__(self):
        return f'<Telecommand {self.id}: {self.command_type} ({self.status})>'