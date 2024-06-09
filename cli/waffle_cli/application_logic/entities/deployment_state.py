from pydantic import BaseModel
from .cfn_stack_state import CfnStackState


class DeploymentState(BaseModel):
    deployment_id: str
    template_bucket_name: str | None = None
    generic_certificate_arn: str | None = None
    stacks: list[CfnStackState] = []
