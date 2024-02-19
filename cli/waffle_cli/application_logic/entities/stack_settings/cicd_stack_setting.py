from .stack_setting import StackSetting


class CicdStackSetting(StackSetting):
    github_owner: str | None = None
    github_repo: str | None = None
    github_commit: str | None = None
    github_branch: str | None = None

    pipeline_id: str | None = None
