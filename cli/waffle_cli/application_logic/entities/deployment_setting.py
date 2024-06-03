from pydantic import BaseModel

from .cfn_stack_state import CfnStackState


class DeploymentSetting(BaseModel):
    deployment_id: str
    aws_region: str | None = "us-east-1"

    default_log_retention_days: int = 365
    default_alarms_enabled: bool = True
    default_db_backup_retention: int = 35

    full_domain_name: str | None = None

    ns_list: list[str] | None = None
    template_bucket_name: str | None = None
    generic_certificate_arn: str | None = None

    stacks: list[CfnStackState] = []
