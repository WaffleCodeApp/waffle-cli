from pydantic import BaseModel

from .project_stack_setting import ProjectStackSetting


class ProjectSetting(BaseModel):
    stacks: list[ProjectStackSetting] = []
