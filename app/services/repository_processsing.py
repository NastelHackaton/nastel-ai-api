import asyncio
import os
import aiofiles
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

from ..extensions import db
from ..models import Repository, File, Task
from .stages import PipelineStage, StatGenerationStage
from . import file_language_detection, qdrant_utils


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

    def __init__(self, repo_path: str):
        self._repo_path = repo_path

    async def process(self):
        """
        Processes all relevant files in the repository through the pipeline.
        """

        repository = Repository(
            name=os.path.basename(self._repo_path)
        )
        db.session.add(repository)

        db.session.commit()

        pipeline = FileProcessingPipeline([
            StatGenerationStage(),
            EmbeddingGenerationStage()
        ])

        if not os.path.exists(self._repo_path):
            print(f"Repository path does not exist: {self._repo_path}")
            return

        await qdrant_utils.create_collection_for_repo(self._repo_path)

        tasks = []
        for root, _, files in os.walk(self._repo_path, topdown=True):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                tasks.append(pipeline.process_file(file_path))


        results = await asyncio.gather(*tasks)

        await qdrant_utils.store_embeddings_for_repo(self._repo_path, results)

        for result in results:
            if result is None:
                continue

            file = File(
                path=result["file_path"],
                repository_id=repository.id
            )

            db.session.add(file)

            db.session.commit()

            if result["tasks"]:
                for task in result["tasks"]:
                    try:
                        task = Task(
                            title=task["title"],
                            description=task["description"],
                            category=task["category"],
                            priority=task["priority"],
                            prompt=task["prompt"],
                            file_id=file.id
                        )

                        db.session.add(task)
                        db.session.commit()
                    except Exception as e:
                        print("Error while creating a new task", e)



