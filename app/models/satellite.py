# app/models/satellite.py
from ..database import db
from datetime import datetime
from sqlalchemy import event


class Satellite(db.Model):
    __tablename__ = 'satellites'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    status = db.Column(
        db.String(20),
        default='active',
        nullable=False,
        server_default='active'
    )

    # Relacionamentos
    telecommands = db.relationship('Telecommand', back_populates='satellite')

    __table_args__ = (
        db.CheckConstraint(
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


# Atualiza o timestamp quando o satélite for atualizado
@event.listens_for(Satellite, 'before_update')
def update_updated_at(mapper, connection, target):
    target.updated_at = datetime.utcnow()