from marshmallow import Schema, fields, post_load

class SetupRepository():
    def __init__(self, github_token: str, owner: str, repo: str, branch: str):
        self.github_token = github_token
        self.owner = owner
        self.repo = repo
        self.branch = branch

    def __repr__(self):
        return f"<SetupRepository(github_token={self.github_token}, owner={self.owner}, repo={self.repo}, branch={self.branch})>"

class SetupRepositorySchema(Schema):
    github_token = fields.Str(required=True)
    owner = fields.Str(required=True)
    repo = fields.Str(required=True)
    branch = fields.Str(required=True)

    @post_load()
    def make_setup_repository(self, data, **kwargs):
        return SetupRepository(**data)
