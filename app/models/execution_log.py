# app/models/execution_log.py
from ..database import db
from datetime import datetime


class ExecutionLog(db.Model):
    __tablename__ = 'execution_logs'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    # Chaves estrangeiras
    telecommand_id = db.Column(
        db.Integer,
        db.ForeignKey('telecommands.id', ondelete='CASCADE'),
        nullable=False
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('operators.id', ondelete='SET NULL'),
        nullable=True
    )

    # Relacionamentos
    telecommand = db.relationship('Telecommand', back_populates='execution_logs')
    creator = db.relationship('Operator', back_populates='execution_logs')

    def to_dict(self):
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
    def create_log(cls, telecommand_id, status, message=None, details=None, created_by=None):
        """Método auxiliar para criar um novo log"""
        log = cls(
            telecommand_id=telecommand_id,
            status=status,
            message=message,
            details=details,
            created_by=created_by
        )
        db.session.add(log)
        return log

    def __repr__(self):
        return f'<ExecutionLog {self.id}: {self.status} (TC: {self.telecommand_id})>'