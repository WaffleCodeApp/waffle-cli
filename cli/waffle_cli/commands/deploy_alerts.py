from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.alerts import (
    generate_alerts_parameter_list,
    generate_alerts_stack_json,
)
from .command_type import Command
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-alerts"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployAlerts(Command):
    name: str = "deploy_alerts"
    description: str = (
        "Generate a CFN template for delivering system-wide alerts, and deploy it to the selected deployment. "
        "This stack includes an SNS Topic, which can be accessed from all stacks deployed with waffle. "
        "CloudWatch Alarms of waffle-created AWS components are sent to this SNS Topic. Besides that "
        "it can be used for delivering system-wide notifications from the backend components too. "
        "Email delivery is added to the stack by default. But in addition to that, it's possible to implement a "
        "custom service that forwards messages to Slack for example."
    )

    @staticmethod
    def arg_parser(
        parser: ArgumentParser, gateways: Gateways = gateway_implementations
    ) -> None:
        parser.add_argument(
            "deployment_id",
            help="An existing deployment ID that you add local credentials for",
            choices=gateways.deployment_settings.get_names(),
        )
        parser.add_argument(
            "--email_list",
            help="Comma separated list of email addresses to deliver system-wide alerts to.",
            required=True,
        )
        parser.add_argument(
            "--custom_template_name",
            help="Optional. If there is a custom, already uploaded template for this purpose, specify its name.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        email_list: str | None = None,
        custom_template_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert email_list is not None

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=generate_alerts_stack_json,
            parameter_list=generate_alerts_parameter_list(
                deployment_id=deployment_id,
                email_notification_list=email_list,
            ),
            stack_type=StackType.alerts,
            include_in_the_project=False,
        )
