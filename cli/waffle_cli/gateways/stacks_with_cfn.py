from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
import botocore  # pyright: ignore[reportMissingTypeStubs]
from application_logic.entities.stack_settings.stack_setting import (
    StackSetting,
)
from application_logic.entities.deployment_setting import DeploymentSetting
from application_logic.entities.stack_type import StackType
from application_logic.gateway_interfaces.stacks import Stacks


class StacksWithCfn(Stacks):
    def _get_client(self, deployment_id: str, aws_region: str) -> Any:
        return Session(profile_name=deployment_id).client(  # type: ignore
            "cloudformation", region_name=aws_region
        )

    def _get_cfn_func(
        self, deployment_id: str, aws_region: str, stack_setting: StackSetting | None
    ):
        c = self._get_client(deployment_id, aws_region)
        if stack_setting and stack_setting.cfn_stack_id is None:
            return c.create_stack
        return c.update_stack

    def create_or_update_stack(
        self,
        template_url: str,
        setting: DeploymentSetting,
        parameters: list[dict[str, str]],
        stack_type: StackType,
        pipeline_name: str | None = None,
    ) -> str:
        if setting.aws_region is None:
            raise Exception("aws_region is not specified")
        f = self._get_cfn_func(
            setting.deployment_id,
            setting.aws_region,
            getattr(setting, f"{stack_type.value}_stack_setting"),
        )
        try:
            default_name = f"waffle-{setting.deployment_id}-{stack_type.value}" + (
                f"-{pipeline_name}" if pipeline_name else ""
            )
            response = f(
                StackName=(
                    getattr(setting, f"{stack_type.value}_stack_setting").cfn_stack_id,
                    default_name,
                ),
                TemplateURL=template_url,
                Capabilities=["CAPABILITY_NAMED_IAM"],
                Parameters=parameters,
            )
            return f"{response['StackId']}"
        except botocore.exceptions.ClientError as e:  # type: ignore
            if (
                getattr(setting, f"{stack_type}_stack_setting").cfn_stack_id
                and e.__str__()  # type: ignore
                == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
            ):
                return getattr(setting, f"{stack_type}_stack_setting").cfn_stack_id
            raise e

    # def create_or_update_api_stack(
    #     self, deployment_id: str, template_url: str, setting: DeploymentSetting
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.api_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.api_stack_id or f"wca-api-{deployment_id}",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 # {
    #                 #     "ParameterKey": "DeploymentType",
    #                 #     "ParameterValue": setting.deployment_type,
    #                 # },
    #                 {
    #                     "ParameterKey": "FullDomainName",
    #                     "ParameterValue": setting.full_domain_name,
    #                 },
    #                 {
    #                     "ParameterKey": "BackendApiHostname",
    #                     "ParameterValue": setting.api_subdomain,
    #                 },
    #                 {
    #                     "ParameterKey": "GenericCertificateArn",
    #                     "ParameterValue": setting.generic_certificate_arn,
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.api_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.api_stack_id
    #         raise e

    # def create_or_update_misc_stack(
    #     self, deployment_id: str, template_url: str, setting: DeploymentSetting
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.misc_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.misc_stack_id or f"wca-misc-{deployment_id}",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 # {
    #                 #     "ParameterKey": "DeploymentType",
    #                 #     "ParameterValue": setting.deployment_type,
    #                 # },
    #                 {
    #                     "ParameterKey": "EmailNotificationList",
    #                     "ParameterValue": setting.email_notifications,
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.misc_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.misc_stack_id
    #         raise e

    # def create_or_update_alerts_cfn_stack(
    #     self,
    #     deployment_id: str,
    #     template_url: str,
    #     setting: DeploymentSetting,
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.alerts_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.alerts_stack_id or f"wca-cfn-{deployment_id}-alerts",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 {
    #                     "ParameterKey": "DeploymentType",
    #                     "ParameterValue": setting.deployment_type,
    #                 },
    #                 {
    #                     "ParameterKey": "PipelineId",
    #                     "ParameterValue": "alerts",
    #                 },
    #                 {
    #                     "ParameterKey": "CICDManualApproval",
    #                     "ParameterValue": (
    #                         "False"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "True"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "GithubOwner",
    #                     "ParameterValue": setting.github_owner,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubRepoName",
    #                     "ParameterValue": setting.github_repo,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubBranch",
    #                     "ParameterValue": setting.github_branch,
    #                 },
    #                 {
    #                     "ParameterKey": "CommitID",
    #                     "ParameterValue": setting.github_commit,
    #                 },
    #                 {
    #                     "ParameterKey": "BuildspecPath",
    #                     "ParameterValue": "alerts/buildspec.yml",
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.alerts_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.alerts_stack_id
    #         raise e

    # def create_or_update_customer_db_stack(
    #     self,
    #     deployment_id: str,
    #     template_url: str,
    #     setting: DeploymentSetting,
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.customer_db_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.customer_db_stack_id
    #             or f"wca-db-{deployment_id}-customer",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 {
    #                     "ParameterKey": "DeploymentType",
    #                     "ParameterValue": setting.deployment_type,
    #                 },
    #                 {
    #                     "ParameterKey": "DatabaseId",
    #                     "ParameterValue": "customer",
    #                 },
    #                 {
    #                     "ParameterKey": "Family",
    #                     "ParameterValue": (
    #                         "postgres15"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "aurora-postgresql15"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "DBType",
    #                     "ParameterValue": (
    #                         "rds"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "aurora"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "InstanceClass",
    #                     "ParameterValue": (
    #                         "db.t3.micro"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "db.t3.medium"
    #                     ),
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.customer_db_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.customer_db_stack_id
    #         raise e

    # def create_or_update_deployer_db_stack(
    #     self,
    #     deployment_id: str,
    #     template_url: str,
    #     setting: DeploymentSetting,
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.deployer_db_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.deployer_db_stack_id
    #             or f"wca-db-{deployment_id}-deployer",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 {
    #                     "ParameterKey": "DeploymentType",
    #                     "ParameterValue": setting.deployment_type,
    #                 },
    #                 {
    #                     "ParameterKey": "DatabaseId",
    #                     "ParameterValue": "deployer",
    #                 },
    #                 {
    #                     "ParameterKey": "Family",
    #                     "ParameterValue": (
    #                         "postgres15"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "aurora-postgresql15"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "DBType",
    #                     "ParameterValue": (
    #                         "rds"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "aurora"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "InstanceClass",
    #                     "ParameterValue": (
    #                         "db.t3.micro"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "db.t3.medium"
    #                     ),
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.deployer_db_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.deployer_db_stack_id
    #         raise e

    # def create_or_update_deployer_ecs_stack(
    #     self,
    #     deployment_id: str,
    #     template_url: str,
    #     setting: DeploymentSetting,
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.deployer_ecs_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.deployer_ecs_stack_id
    #             or f"wca-ecs-{deployment_id}-deployer",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 {
    #                     "ParameterKey": "DeploymentType",
    #                     "ParameterValue": setting.deployment_type,
    #                 },
    #                 {
    #                     "ParameterKey": "PipelineId",
    #                     "ParameterValue": "deployer",
    #                 },
    #                 {
    #                     "ParameterKey": "CICDManualApproval",
    #                     "ParameterValue": (
    #                         "False"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "True"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "InstanceCount",
    #                     "ParameterValue": setting.deployer_instance_count,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubOwner",
    #                     "ParameterValue": setting.github_owner,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubRepoName",
    #                     "ParameterValue": setting.github_repo,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubBranch",
    #                     "ParameterValue": setting.github_branch,
    #                 },
    #                 {
    #                     "ParameterKey": "CommitID",
    #                     "ParameterValue": setting.github_commit,
    #                 },
    #                 {
    #                     "ParameterKey": "BuildspecPath",
    #                     "ParameterValue": "deployer/buildspec.yml",
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.deployer_ecs_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.deployer_ecs_stack_id
    #         raise e

    # def create_or_update_admin_app_cfn_stack(
    #     self,
    #     deployment_id: str,
    #     template_url: str,
    #     setting: DeploymentSetting,
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.admin_app_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.admin_app_stack_id
    #             or f"wca-cfn-{deployment_id}-admin-app",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 {
    #                     "ParameterKey": "DeploymentType",
    #                     "ParameterValue": setting.deployment_type,
    #                 },
    #                 {
    #                     "ParameterKey": "PipelineId",
    #                     "ParameterValue": "admin-app",
    #                 },
    #                 {
    #                     "ParameterKey": "CICDManualApproval",
    #                     "ParameterValue": (
    #                         "False"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "True"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "GithubOwner",
    #                     "ParameterValue": setting.github_owner,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubRepoName",
    #                     "ParameterValue": setting.github_repo,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubBranch",
    #                     "ParameterValue": setting.github_branch,
    #                 },
    #                 {
    #                     "ParameterKey": "CommitID",
    #                     "ParameterValue": setting.github_commit,
    #                 },
    #                 {
    #                     "ParameterKey": "BuildspecPath",
    #                     "ParameterValue": "admin_app/buildspec.yml",
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.admin_app_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.admin_app_stack_id
    #         raise e

    # def create_or_update_admin_web_ui_cdn_stack(
    #     self,
    #     deployment_id: str,
    #     template_url: str,
    #     setting: DeploymentSetting,
    # ) -> str:
    #     f = (
    #         self._get_client(deployment_id=deployment_id).create_stack
    #         if setting.admin_web_ui_stack_id is None
    #         else self._get_client(deployment_id=deployment_id).update_stack
    #     )
    #     try:
    #         response = f(
    #             StackName=setting.admin_web_ui_stack_id
    #             or f"wca-cdn-{deployment_id}-admin-web-ui",
    #             TemplateURL=template_url,
    #             Capabilities=["CAPABILITY_NAMED_IAM"],
    #             Parameters=[
    #                 {
    #                     "ParameterKey": "DeploymentId",
    #                     "ParameterValue": setting.deployment_id,
    #                 },
    #                 {
    #                     "ParameterKey": "DeploymentType",
    #                     "ParameterValue": setting.deployment_type,
    #                 },
    #                 {
    #                     "ParameterKey": "PipelineId",
    #                     "ParameterValue": "admin-web-ui",
    #                 },
    #                 {
    #                     "ParameterKey": "CICDManualApproval",
    #                     "ParameterValue": (
    #                         "False"
    #                         if setting.deployment_type == DeploymentType.DEV
    #                         else "True"
    #                     ),
    #                 },
    #                 {
    #                     "ParameterKey": "FullDomainName",
    #                     "ParameterValue": setting.full_domain_name,
    #                 },
    #                 {
    #                     "ParameterKey": "WebHostname",
    #                     "ParameterValue": "www",
    #                 },
    #                 {
    #                     "ParameterKey": "GenericCertificateArn",
    #                     "ParameterValue": setting.generic_certificate_arn,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubOwner",
    #                     "ParameterValue": setting.github_owner,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubRepoName",
    #                     "ParameterValue": setting.github_repo,
    #                 },
    #                 {
    #                     "ParameterKey": "GithubBranch",
    #                     "ParameterValue": setting.github_branch,
    #                 },
    #                 {
    #                     "ParameterKey": "CommitID",
    #                     "ParameterValue": setting.github_commit,
    #                 },
    #                 {
    #                     "ParameterKey": "BuildspecPath",
    #                     "ParameterValue": "admin-web-ui/buildspec.yml",
    #                 },
    #             ],
    #         )
    #         return f"{response['StackId']}"
    #     except botocore.exceptions.ClientError as e:  # type: ignore
    #         if (
    #             setting.admin_web_ui_stack_id
    #             and e.__str__()  # type: ignore
    #             == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
    #         ):
    #             return setting.admin_web_ui_stack_id
    #         raise e
