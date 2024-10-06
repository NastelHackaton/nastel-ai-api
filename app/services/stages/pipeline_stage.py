class PipelineStage:
    """
        Base class for all pipeline stages. All pipeline stages must inherit from this class"
    """

    async def process(self, file_path: str, file_content: str, metadata: dict):
        raise NotImplementedError("Pipeline stage must implement the `process` method")
