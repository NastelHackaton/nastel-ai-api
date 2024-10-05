import os
from git import Repo, GitCommandError

from ..schemas import SetupRepository

class GithubRepositoryExtractor:
    """Class to clone a GitHub repository."""

    def __init__(self, data: SetupRepository):
        self.data = data
        self.base_storage_path = "./storage/repo_files"
        self.repo_path = os.path.join(self.base_storage_path, f"{self.data.owner}_{self.data.repo}")

    def extract(self) -> str:
        """Clone the repository from GitHub and return the storage location."""
        try:
            os.makedirs(self.base_storage_path, exist_ok=True)

            if os.path.exists(self.repo_path):
                print("Repo already exists, skipping cloning.")
                return self.repo_path

            repo_url = f"https://{self.data.owner}:{self.data.github_token}@github.com/{self.data.owner}/{self.data.repo}.git"

            Repo.clone_from(
                repo_url,
                self.repo_path,
                branch=self.data.branch,
                depth=1,
                single_branch=True
            )

            return self.repo_path

        except GitCommandError as e:
            print(f"Failed to clone repo: {e}")
            raise e
        except OSError as e:
            print(f"Error during directory creation: {e}")
            raise e
