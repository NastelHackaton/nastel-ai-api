from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..extensions import db

class Repository(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Repository('{self.name}')"

class File(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    path = db.Column(db.String(100), nullable=False)
    repository_id = db.Column(UUID(as_uuid=True), db.ForeignKey('repository.id'), nullable=False)

    def __init__(self, path: str, repository_id: UUID):
        self.path = path
        self.repository_id = repository_id

    def __repr__(self):
        return f"File('{self.path}')"

class Task(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    priority = db.Column(db.String(32), nullable=False)
    prompt = db.Column(db.String(1024), nullable=False)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey('file.id'), nullable=False)

    def __init__(self, title: str, description: str, category: str, priority: str, prompt: str, file_id: UUID):
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.prompt = prompt
        self.file_id = file_id

    def __repr__(self):
        return f"Task('{self.title}')"

class FileScore(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey('file.id'), nullable=False)
    scoreKind = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def __init__(self, file_id: UUID, scoreKind: str, score: float):
        self.file_id = file_id
        self.scoreKind = scoreKind
        self.score = score

