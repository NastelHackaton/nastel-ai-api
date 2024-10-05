from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from qdrant_client import AsyncQdrantClient

db = SQLAlchemy()
migrate = Migrate()

