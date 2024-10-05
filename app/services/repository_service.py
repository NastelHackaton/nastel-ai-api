from flask import Response, jsonify

from .github_repository_extractor import GithubRepositoryExtractor
from .repository_processsing import RepositoryProcessor, FileProcessingPipeline, StatGenerationStage
from ..schemas import SetupRepository

async def setup(data: SetupRepository) -> tuple[Response, int]:
    """Setup function that triggers the repository download and extraction process."""

    try:
        extractor = GithubRepositoryExtractor(data)
        repo_path = extractor.extract()
    except Exception as e:
        return jsonify({'message': 'Failed to download and extract repository', "error": e}), 400

    await RepositoryProcessor(
        repo_path,
        FileProcessingPipeline([
            StatGenerationStage()
        ])
    ).process()

    print(f"Repository downloaded and extracted to: {repo_path}")

    return jsonify({'message': 'Repository downloaded and extracted successfully!'}) , 200


