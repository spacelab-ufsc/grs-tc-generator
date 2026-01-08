# app/models/operator.py
from ..database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Operator(db.Model):
    __tablename__ = 'operators'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        default='operator',
        nullable=False,
        server_default='operator'
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    last_login = db.Column(db.DateTime(timezone=True))
    status = db.Column(
        db.String(20),
        default='active',
        nullable=False,
        server_default='active'
    )

    # Relacionamentos
    telecommands = db.relationship('Telecommand', back_populates='operator')
    execution_logs = db.relationship('ExecutionLog', back_populates='creator')

    __table_args__ = (
        db.CheckConstraint(
            "role IN ('admin', 'operator', 'viewer')",
            name='valid_operator_role'
        ),
        db.CheckConstraint(
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