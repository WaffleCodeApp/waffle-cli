from pydantic import BaseModel

from .cfn_stack_state import CfnStackState


class DeploymentState(BaseModel):
    deployment_id: str
    ns_list: list[str] | None = None
    template_bucket_name: str | None = None
    generic_certificate_arn: str | None = None

    vpc_stack_state: CfnStackState | None = None
    auth_stack_state: CfnStackState | None = None
    api_stack_state: CfnStackState | None = None
    alerts_stack_state: CfnStackState | None = None
    github_stack_state: CfnStackState | None = None
    deployment_stack_state: CfnStackState | None = None

    cdn_cicd_stack_states: list[CfnStackState] = []
    cfn_cicd_stack_states: list[CfnStackState] = []
    ecs_cicd_stack_states: list[CfnStackState] = []
    db_stack_states: list[CfnStackState] = []
