from pydantic import BaseModel


class CicdStackSetting(BaseModel):
    github_owner: str | None = None
    github_repo: str | None = None
    github_commit: str | None = None
    github_branch: str | None = None

    pipeline_id: str | None = None

    def get_stack_id(self):
        return f"cicd|{self.pipeline_id}"
