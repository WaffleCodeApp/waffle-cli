from pydantic import BaseModel


class CfnStackState(BaseModel):
    stack_id: str
    cfn_stack_id: str
