from pydantic import BaseModel


class DeploymentSetting(BaseModel):
    deployment_id: str
    aws_region: str | None = "us-east-1"

    default_log_retention_days: int = 365
    default_alarms_enabled: bool = True
    default_db_backup_retention: int = 35
    default_require_manual_cicd_approval: bool = False

    full_domain_name: str | None = None
