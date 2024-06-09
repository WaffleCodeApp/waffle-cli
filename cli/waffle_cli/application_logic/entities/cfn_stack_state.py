from pydantic import BaseModel
from .stack_type import StackType


class CfnStackState(BaseModel):
    stack_id: str
    cfn_stack_id: str
    stack_type: StackType
