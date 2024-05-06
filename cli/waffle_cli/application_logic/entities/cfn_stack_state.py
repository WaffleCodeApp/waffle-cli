from pydantic import BaseModel


class CfnStackState(BaseModel):
    stack_id: str | None = None
    cfn_stack_id: str | None = None
