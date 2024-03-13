from pydantic import BaseModel
from .deployment_type import DeploymentType
from .stack_settings.vpc_stack_setting import VpcStackSetting
from .stack_settings.auth_stack_setting import AuthStackSetting
from .stack_settings.api_stack_setting import ApiStackSetting
from .stack_settings.alerts_stack_setting import AlertsStackSetting
from .stack_settings.deployment_stack_setting import DeploymentStackSetting
from .stack_settings.github_stack_setting import GithubStackSetting
from .stack_settings.cdn_cicd_stack_setting import CdnCicdStackSetting
from .stack_settings.cfn_cicd_stack_setting import CfnCicdStackSetting
from .stack_settings.ecs_cicd_stack_setting import EcsCicdStackSetting
from .stack_settings.db_stack_setting import DbStackSetting


class DeploymentSetting(BaseModel):
    deployment_id: str
    aws_region: str | None = "us-east-1"
    deployment_type: DeploymentType | None = None
    ns_list: list[str] | None = None
    full_domain_name: str | None = None
    template_bucket_name: str | None = None
    generic_certificate_arn: str | None = None

    vpc_stack_setting: VpcStackSetting | None = None
    auth_stack_setting: AuthStackSetting | None = None
    api_stack_setting: ApiStackSetting | None = None
    alerts_stack_setting: AlertsStackSetting | None = None
    github_stack_setting: GithubStackSetting | None = None
    deployment_stack_setting: DeploymentStackSetting | None = None

    cdn_cicd_stack_settings: list[CdnCicdStackSetting] = []
    cfn_cicd_stack_settings: list[CfnCicdStackSetting] = []
    ecs_cicd_stack_settings: list[EcsCicdStackSetting] = []
    db_stack_settings: list[DbStackSetting] = []
