from pydantic import BaseModel


class StackSetting(BaseModel):
    cfn_stack_id: str | None = None
