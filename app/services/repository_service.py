from flask import Response, jsonify

from .github_repository_extractor import GithubRepositoryExtractor
from .repository_processsing import RepositoryProcessor
from ..schemas import SetupRepository

async def setup(data: SetupRepository) -> tuple[Response, int]:
    """Setup function that triggers the repository download and extraction process."""

    try:
        extractor = GithubRepositoryExtractor(data)
        repo_path = extractor.extract()
    except Exception as e:
        return jsonify({'message': 'Failed to download and extract repository', "error": e}), 400

    try:
        await RepositoryProcessor(repo_path).process()
    except Exception as e:
        return jsonify({'message': 'Failed to process repository', "error": e}), 400

    print(f"Repository downloaded and extracted to: {repo_path}")

    return jsonify({'message': 'Repository downloaded and extracted successfully!'}) , 200

