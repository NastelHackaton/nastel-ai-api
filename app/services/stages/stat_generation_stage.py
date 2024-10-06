from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

from . import PipelineStage

class Task(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    prompt: str

class CodeReport(BaseModel):
    documentation_score: int = Field(..., ge=0, le=100)
    bugs_score: int = Field(..., ge=0, le=100)
    security_score: int = Field(..., ge=0, le=100)
    performance_score: int = Field(..., ge=0, le=100)
    tasks: List[Task]

class StatGenerationStage(PipelineStage):
    """
    Pipeline stage to generate statistics for a file
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        self.prompt = ChatPromptTemplate.from_template(
            """
            Generate a report for this file {file_path}:

            {content}

            The report should include the following statistics:

            - A score from 0 to 100 indicating the percentage of documentation in the file.
            - A score from 0 to 100 indicating the presence of potential bugs in the file.
            - A score from 0 to 100 indicating the presence of potential security vulnerabilities in the file.
            - A score from 0 to 100 indicating the presence of potential performance issues in the file.

            Also include a list of up to 5 tasks that can be performed to improve each of the above scores.
            The tasks should include the title, description, priority and a prompt that a llm can use to start working on the task.

            Ensure that the tasks are specific to the code provided and not generic. Focus on actionable improvements based on the actual content of the file.

            If the file does not contain code, return only a text containing "This file does not contain code".

            The response should be a JSON object with the following structure:

            {{
                "documentation_score": 80,
                "bugs_score": 60,
                "security_score": 40,
                "performance_score": 20,
                "tasks": [
                    {{
                        "title": "Improve Documentation",
                        "description": "Add comments to explain the purpose of each function and variable in the code.",
                        "category": "documentation",
                        "priority": "high",
                        "prompt": "Write comments to explain the purpose of each function and variable in the code."
                    }},
                    {{
                        "title": "Fix Bugs",
                        "description": "Identify and fix any bugs in the code.",
                        "category": "bugs",
                        "priority": "high",
                        "prompt": "Identify and fix any bugs in the code."
                    }},
                    {{
                        "title": "Improve Security",
                        "description": "Identify and fix any security vulnerabilities in the code.",
                        "category": "security",
                        "priority": "high",
                        "prompt": "Identify and fix any security vulnerabilities in the code."
                    }},
                    {{
                        "title": "Optimize Performance",
                        "description": "Identify and fix any performance issues in the code.",
                        "category": "performance",
                        "priority": "high",
                        "prompt": "Identify and fix any performance issues in the code."
                    }}
                ]
            }}
            """
        )
        self.chain = self.prompt | self.llm | JsonOutputParser()

    async def process(self, file_path: str, file_content: str, metadata: dict):
        line_count = len(file_content.splitlines())
        word_count = len(file_content.split())

        metadata.update({"line_count": line_count, "word_count": word_count})

        try:
            result = await self.chain.ainvoke({
                "file_path": file_path,
                "content": file_content
            })

            if "This file does not contain code" in result:
                metadata.update({
                    "scores": {
                        "documentation": 0,
                        "bugs": 0,
                        "security": 0,
                        "performance": 0
                    },
                    "tasks": []
                })
                return

            report = CodeReport(**result)

            metadata.update({
                "scores": {
                    "documentation": report.documentation_score,
                    "bugs": report.bugs_score,
                    "security": report.security_score,
                    "performance": report.performance_score
                },
                "tasks": [task.model_dump() for task in report.tasks]
            })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
