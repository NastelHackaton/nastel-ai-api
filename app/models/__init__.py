from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..extensions import db

class TaskType(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"TaskType('{self.name}')"
