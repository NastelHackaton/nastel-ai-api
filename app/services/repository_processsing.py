import asyncio
import os
import aiofiles
import json
from typing import List

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

        print(f"File: {file_path} has {line_count} lines and {word_count} words")

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
            print(f"Skipping file: {file_path} due to unknown language")
            return

        print(f"Processing file: {file_path} with language: {metadata['language']}")

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

        tasks = []
        for root, _, files in os.walk(self._repo_path, topdown=True):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                tasks.append(self._pipeline.process_file(file_path))

        await asyncio.gather(*tasks)
