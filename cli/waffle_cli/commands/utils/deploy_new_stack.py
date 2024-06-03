from typing import Callable
from application_logic.entities.cfn_stack_state import CfnStackState
from application_logic.entities.deployment_setting import DeploymentSetting
from application_logic.entities.project_setting import ProjectSetting
from application_logic.entities.project_stack_setting import ProjectStackSetting
from ...application_logic.gateway_interfaces import Gateways
from ...gateways import gateway_implementations
from ...utils.std_colors import NEUTRAL, RED, YELLOW


def deploy_new_stack(
    deployment_id: str,
    stack_id: str,
    template_name_default: str,
    generate_stack_json: Callable[[], str],
    parameter_list: list[dict[str, str]],
    gateways: Gateways = gateway_implementations,
):
    deployment_setting: DeploymentSetting | None = gateways.deployment_settings.get(
        deployment_id
    )
    if deployment_setting is None:
        print(
            RED
            + f"Settings for {deployment_id} not found. Please make sure to run create_deployment_settings first."
            + NEUTRAL
        )
        raise Exception("Setting not found for deployment_id")

    if deployment_setting.aws_region is None:
        print(
            RED
            + "AWS region setting not found. Please make sure to run create_deployment_settings first."
            + NEUTRAL
        )
        raise Exception("AWS region is None")

    if deployment_setting.template_bucket_name is None:
        print(
            RED
            + "Template bucket name setting not found. Please make sure to run configure_deployment_domain first."
            + NEUTRAL
        )
        raise Exception("template_bucket_name is None")

    project_setting = gateways.project_settings.get() or ProjectSetting()

    template_name: str = template_name_default
    project_stack: ProjectStackSetting | None = next(
        (stack for stack in project_setting.stacks if stack.stack_id == stack_id),
        None,
    )
    if project_stack:
        template_name = project_stack.template_name
    else:
        project_setting.stacks.append(
            ProjectStackSetting(stack_id=stack_id, template_name=template_name_default)
        )

    gateways.project_settings.create_or_update(project_setting)

    if stack_id in [stack.stack_id for stack in deployment_setting.stacks]:
        print(
            RED
            + "The deployment settings show that this stack already has been deployed. "
            + "If you want to update it, use the 'update_api' command instead."
            + NEUTRAL
        )
        raise Exception("stack is already deployed in the selected deployment")

    gateways.deployment_template_bucket.create_bucket_if_not_exist(
        deployment_id,
        deployment_setting.template_bucket_name,
        deployment_setting.aws_region,
    )

    template_url: str = gateways.deployment_template_bucket.upload_obj(
        deployment_id=deployment_id,
        bucket_name=deployment_setting.template_bucket_name,
        aws_region=deployment_setting.aws_region,
        key=template_name,
        content=generate_stack_json(),
    )

    cfn_stack_id = gateways.stacks.create_or_update_stack(
        deployment_setting=deployment_setting,
        template_url=template_url,
        stack_id=stack_id,
        stack_state=None,
        parameters=parameter_list,
    )

    deployment_setting.stacks.append(
        CfnStackState(
            stack_id=stack_id,
            cfn_stack_id=cfn_stack_id,
        )
    )
    gateways.deployment_settings.create_or_update(deployment_setting)

    print(
        YELLOW
        + "Deploying the CloudFormation template may take a few minutes.\n\n"
        + NEUTRAL
    )
