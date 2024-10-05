import asyncio
import os
import aiofiles
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

from . import file_language_detection, qdrant_utils

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

class EmbeddingGenerationStage(PipelineStage):
    """
        Pipeline stage to generate embeddings for a file
    """

    async def process(self, file_path: str, file_content: str, metadata: dict):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=8191, chunk_overlap=200)

        chunks = text_splitter.split_text(file_content)

        for chunk in chunks:
            response = openai.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )

            embeddings = response.data[0].embedding

            metadata.update({
                "chunk": chunk,
                "embeddings": embeddings
            })

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

        metadata = {
            "language": file_language_detection.detect_language(file_path),
            "file_path": file_path,
        }

        if metadata["language"] == "unknown":
            return

        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            file_content = await file.read()

            for stage in self.stages:
                await stage.process(file_path, file_content, metadata)

        return metadata

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

        await qdrant_utils.create_collection_for_repo(self._repo_path)

        tasks = []
        for root, _, files in os.walk(self._repo_path, topdown=True):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                tasks.append(
                    self._pipeline.process_file(file_path)
                )

        results = await asyncio.gather(*tasks)

        await qdrant_utils.store_embeddings_for_repo(self._repo_path, results)
