from typing import Callable

from ...application_logic.entities.cfn_stack_state import CfnStackState
from ...application_logic.entities.deployment_setting import DeploymentSetting
from ...application_logic.entities.deployment_state import DeploymentState
from ...application_logic.entities.stack_type import StackType
from ...application_logic.gateway_interfaces import Gateways
from ...gateways import gateway_implementations
from ...utils.std_colors import NEUTRAL, RED, YELLOW


def deploy_new_stack(
    deployment_id: str,
    stack_id: str,
    template_name: str,
    generate_stack_json: Callable[[], str] | None,
    parameter_list: list[dict[str, str]],
    stack_type: StackType,
    include_in_the_project: bool = False,
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

    deployment_state: DeploymentState = gateways.deployment_states.get(
        deployment_id
    ) or DeploymentState(deployment_id=deployment_id)

    if deployment_setting.aws_region is None:
        print(
            RED
            + "AWS region setting not found. Please make sure to run create_deployment_settings first."
            + NEUTRAL
        )
        raise Exception("AWS region is None")

    if deployment_state.template_bucket_name is None:
        print(
            RED
            + "Template bucket name setting not found. Please make sure to run configure_deployment_domain first."
            + NEUTRAL
        )
        raise Exception("template_bucket_name is None")

    if stack_id in [stack.stack_id for stack in deployment_state.stacks]:
        print(
            RED
            + "The deployment settings show that this stack already has been deployed. "
            + "If you want to update it, use the 'update_api' command instead."
            + NEUTRAL
        )
        raise Exception("stack is already deployed in the selected deployment")

    gateways.deployment_template_bucket.create_bucket_if_not_exist(
        deployment_id,
        deployment_state.template_bucket_name,
        deployment_setting.aws_region,
    )

    template_url: str = ""
    if generate_stack_json is not None:
        template_url = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=deployment_state.template_bucket_name,
            aws_region=deployment_setting.aws_region,
            key=template_name,
            content=generate_stack_json(),
        )
    else:
        template_url = (
            gateways.deployment_template_bucket.get_url_base(
                bucket_name=deployment_state.template_bucket_name
            )
            + f"/{template_name}"  # NOTE: this can be yml or json
        )

    cfn_stack_id = gateways.stacks.create_or_update_stack(
        deployment_setting=deployment_setting,
        template_url=template_url,
        stack_id=stack_id,
        stack_state=None,
        parameters=parameter_list,
    )

    deployment_state.stacks.append(
        CfnStackState(
            stack_id=stack_id,
            cfn_stack_id=cfn_stack_id,
            stack_type=stack_type,
        )
    )
    gateways.deployment_states.create_or_update(deployment_state)

    print(
        YELLOW
        + "Deploying the CloudFormation template may take a few minutes.\n\n"
        + NEUTRAL
    )
