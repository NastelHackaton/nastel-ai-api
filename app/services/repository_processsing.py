import asyncio
import os
import aiofiles
import json
from typing import List

from qdrant_client.models import Distance, VectorParams

from ..extensions import qdrant_client

class PipelineStage:
    """
        Base class for all pipeline stages. All pipeline stages must inherit from this class"
    """

    async def process(self, file_path: str, file_content: str, metadata: dict):
        raise NotImplementedError("Pipeline stage must implement the `process` method")

class StatGenerationStage(PipelineStage):
    """
        Pipeline stage to generate statistics for a file
    """

    async def process(self, file_path: str, file_content: str, metadata: dict):
        line_count = len(file_content.split("\n"))
        word_count = len(file_content.split())

        metadata.update({"line_count": line_count, "word_count": word_count})

class FileProcessingPipeline:
    """
        Class to process a file through a pipeline of stages
    """

    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages

    async def process_file(self, file_path: str):
        """
        Processes a file by passing it through each stage in the pipeline.
        """

        file_extension = os.path.splitext(file_path)[1]

        with open("./language_map.json", "r") as language_map_file:
            language_map = json.load(language_map_file)
            language_results = list(map(
                    lambda file_args: file_args[0] if file_extension in list(map(
                        lambda i: i, file_args[1].get("extensions", []))) else None, language_map.items()))
            language_results = list(filter(None, language_results))

        metadata = {
            "language": language_results[0] if len(language_results) > 0 else "unknown"
        }

        if metadata["language"] == "unknown":
            return

        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            file_content = await file.read()

            for stage in self.stages:
                await stage.process(file_path, file_content, metadata)

class RepositoryProcessor:
    """
        Class to process a repository through a pipeline
    """

    def __init__(self, repo_path: str, pipeline: FileProcessingPipeline):
        self._pipeline = pipeline
        self._repo_path = repo_path

    async def process(self):
        """
        Processes all relevant files in the repository through the pipeline.
        """

        if not os.path.exists(self._repo_path):
            print(f"Repository path does not exist: {self._repo_path}")
            return

        collection_name = self._repo_path.split("/")[-1]
        collection_name = collection_name.replace(" ", "_").replace('-', '_').lower()

        if not (1 <= len(collection_name) <= 256):
            raise ValueError(f"Collection name '{collection_name}' is invalid. Must be between 1 and 256 characters.")

        try:
            if not await qdrant_client.collection_exists(collection_name):
                print(f"Creating collection: {collection_name}")
                await qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=100, distance=Distance.COSINE),
                )
        except Exception as e:
            print(f"Failed to create collection: {e}")
            raise e

        tasks = []
        for root, _, files in os.walk(self._repo_path, topdown=True):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                tasks.append(
                    self._pipeline.process_file(file_path)
                )

        await asyncio.gather(*tasks)
