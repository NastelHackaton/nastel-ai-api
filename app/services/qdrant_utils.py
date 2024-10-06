from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List
from qdrant_client import AsyncQdrantClient
import uuid

def get_qdrant_client():
    qdrant_client = AsyncQdrantClient(host="localhost", port=6333, grpc_port=6334, prefer_grpc=True)
    return qdrant_client

def make_collection_name(repo_path: str) -> str:
    collection_name = repo_path.split("/")[-1]
    collection_name = collection_name.replace(" ", "_").replace('-', '_').lower()

    if not (1 <= len(collection_name) <= 256):
        raise ValueError(f"Collection name '{collection_name}' is invalid. Must be between 1 and 256 characters.")

    return collection_name

async def create_collection_for_repo(repo_path: str) -> None:
    """
    Creates a collection in Qdrant for a repository.
    """

    qdrant_client = get_qdrant_client()

    try:
        collection_name = make_collection_name(repo_path)

        collection_exists = await qdrant_client.collection_exists(collection_name)

        print(f"Collection exists: {collection_exists}")

        if not collection_exists:
            print(f"Creating collection: {collection_name}")
            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
    except Exception as e:
        print(f"Failed to create collection: {e}")
        raise e

    await qdrant_client.close()

async def store_embeddings_for_repo(repo_path: str, metadatas: List[dict]) -> None:
    """
    Stores embeddings for a repository in Qdrant.
    """
    qdrant_client = get_qdrant_client()

    collection_name = make_collection_name(repo_path)

    if not metadatas:
        return

    points = []

    for metadata in metadatas:
        if metadata is None:
            continue

        payload = {
            "file_path": metadata["file_path"],
            "language": metadata["language"],
            "chunk": metadata["chunk"],
            "line_count": metadata["line_count"],
            "word_count": metadata["word_count"],
        }

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=metadata["embeddings"],
            payload=payload
        )

        points.append(point)

    if points:
        try:
            await qdrant_client.upsert(collection_name=collection_name, points=points, wait=True)
        except Exception as e:
            print(f"Error storing embeddings: {e}")

    await qdrant_client.close()
