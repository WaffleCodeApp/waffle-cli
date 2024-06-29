from time import sleep
from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
import botocore  # pyright: ignore[reportMissingTypeStubs]
from ..application_logic.entities.cfn_stack_state import CfnStackState
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces.stacks import Stacks
from ..utils.progress_indicator import show_progress


class StacksWithCfn(Stacks):
    def _get_client(self, deployment_id: str, aws_region: str) -> Any:
        return Session(profile_name=deployment_id).client(  # type: ignore
            "cloudformation", region_name=aws_region
        )

    def _get_cfn_func(
        self,
        deployment_id: str,
        aws_region: str,
        stack_state: CfnStackState | None,
    ):
        c = self._get_client(deployment_id, aws_region)
        if stack_state is not None:
            return c.create_stack
        return c.update_stack

    def create_or_update_stack(
        self,
        deployment_setting: DeploymentSetting,
        template_url: str,
        stack_id: str,
        stack_state: CfnStackState | None,
        parameters: list[dict[str, str]],
    ) -> str:
        if deployment_setting.aws_region is None:
            raise Exception("aws_region is not specified")
        f = self._get_cfn_func(
            deployment_setting.deployment_id,
            deployment_setting.aws_region,
            stack_state,
        )
        try:
            response = f(
                StackName=(
                    (stack_state.cfn_stack_id if stack_state is not None else stack_id),
                ),
                TemplateURL=template_url,
                Capabilities=["CAPABILITY_NAMED_IAM"],
                Parameters=parameters,
            )
            return f"{response['StackId']}"
        except botocore.exceptions.ClientError as e:  # type: ignore
            if (
                stack_state is not None
                and e.__str__()  # type: ignore
                == "An error occurred (ValidationError) when calling the UpdateStack operation: No updates are to be performed."
            ):
                return stack_state.cfn_stack_id
            raise e

    def _get_stack_statuses(
        self,
        deployment_id: str,
        aws_region: str,
    ) -> list[tuple[str, str]]:
        stacks: list[tuple[str, str]] = []
        client = self._get_client(deployment_id, aws_region)
        next_token: str | None = None
        while True:
            kw = {}
            if next_token is not None:
                kw["NextToken"] = next_token
            response = client.describe_stacks(**kw)
            if response["Stacks"]:
                stacks.extend(
                    [(s["StackId"], s["StackStatus"]) for s in response["Stacks"]]
                )
            if response["NextToken"] is None:
                break
            next_token = response["NextToken"]
        return stacks

    def wait_for_stacks_to_create_or_update(
        self,
        deployment_id: str,
        aws_region: str,
        cfn_stack_ids: list[str] | None = None,
    ) -> bool:

        i = 0
        show_progress(i, "Checking stack statuses...")
        succeeded: bool = True
        while True:
            i += 1
            stack_statuses = self._get_stack_statuses(
                deployment_id,
                aws_region,
            )

            if cfn_stack_ids is not None:
                stack_statuses = [s for s in stack_statuses if s[0] in cfn_stack_ids]

            if (
                len(
                    [
                        s
                        for s in stack_statuses
                        if s[1] != "CREATE_COMPLETE"
                        and s[1] != "CREATE_FAILED"
                        and s[1] != "ROLLBACK_COMPLETE"
                        and s[1] != "ROLLBACK_FAILED"
                        and s[1] != "UPDATE_COMPLETE"
                        and s[1] != "UPDATE_FAILED"
                        and s[1] != "UPDATE_ROLLBACK_COMPLETE"
                        and s[1] != "UPDATE_ROLLBACK_FAILED"
                    ]
                )
                == 0
            ):
                succeeded = len(
                    [
                        s
                        for s in stack_statuses
                        if s[1] == "CREATE_COMPLETE" or s[1] == "UPDATE_COMPLETE"
                    ]
                ) == len(stack_statuses)
                break
            show_progress(i, "Stack are being created or updated...")
            sleep(10)
        show_progress(i, "Finished creating or updating stacks...")
        return succeeded

    def get_physical_resource_id_from_stack(
        self,
        deployment_id: str,
        aws_region: str,
        cfn_stack_id: str,
        logical_resource_id: str,
    ) -> str:
        client = self._get_client(deployment_id, aws_region)
        response = client.describe_stack_resource(
            StackName=cfn_stack_id, LogicalResourceId=logical_resource_id
        )
        physical_resource_id = response["StackResources"][0]["PhysicalResourceId"]
        return physical_resource_id
