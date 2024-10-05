from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from qdrant_client import AsyncQdrantClient

db = SQLAlchemy()
migrate = Migrate()
qdrant_client = AsyncQdrantClient(host="localhost", port=6333, grpc_port=6334, prefer_grpc=True)

