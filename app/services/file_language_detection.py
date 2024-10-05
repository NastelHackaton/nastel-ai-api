import os
import json

def detect_language(file_path: str) -> str:
    file_extension = os.path.splitext(file_path)[1]

    with open("./language_map.json", "r") as language_map_file:
        language_map = json.load(language_map_file)
        language_results = list(map(
                lambda file_args: file_args[0] if file_extension in list(map(
                    lambda i: i, file_args[1].get("extensions", []))) else None, language_map.items()))
        language_results = list(filter(None, language_results))

        if len(language_results) == 0:
            return "unknown"
        else:
            return language_results[0]

