from flask import Response, jsonify
import requests
from requests.auth import HTTPBasicAuth
import zipfile
import os
import shutil

from ..schemas import SetupRepository

def download_and_extract_repo(data: SetupRepository) -> bool:
    """Download and extract the repository from GitHub."""

    owner = data.owner
    repo = data.repo
    branch = data.branch
    token = data.github_token

    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
        response = requests.get(url, auth=HTTPBasicAuth(owner, token), stream=True)

        if response.status_code != 200:
            print(f"Failed to download repo. Status code: {response.status_code}")
            return False

        zip_file_path = f"./storage/repo_files/{owner}_{repo}.zip"
        extract_path = f"./storage/repo_files/{owner}_{repo}"

        os.makedirs(extract_path, exist_ok=True)

        with open(zip_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        extracted_folders = os.listdir(extract_path)
        if len(extracted_folders) == 1 and os.path.isdir(os.path.join(extract_path, extracted_folders[0])):
            inner_folder_path = os.path.join(extract_path, extracted_folders[0])
            for file in os.listdir(inner_folder_path):
                shutil.move(os.path.join(inner_folder_path, file), extract_path)

            os.rmdir(inner_folder_path)

        return True
    except Exception as e:
        print(f"Error during download and extraction: {e}")
        return False


def setup(data: SetupRepository) -> tuple[Response, int]:
    """Setup function that triggers the repository download and extraction process."""
    success = download_and_extract_repo(data)

    if not success:
        return jsonify({'message': 'Failed to download and extract repository'}), 400

    return jsonify({'message': 'Repository downloaded and extracted successfully!'}) , 200


