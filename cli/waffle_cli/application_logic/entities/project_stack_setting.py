from pydantic import BaseModel


class ProjectStackSetting(BaseModel):
    stack_id: str
    template_name: str
