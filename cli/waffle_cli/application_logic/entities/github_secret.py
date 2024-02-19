from pydantic import BaseModel


class GithubSecret(BaseModel):
    github_access_token: str | None
