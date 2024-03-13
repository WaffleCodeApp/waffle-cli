from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.stack_settings.alerts_stack_setting import AlertsStackSetting
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.alerts import generate_alerts_parameter_list, generate_alerts_stack_json
from .command_type import Command


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
            help="Only required when run for the first time for a deployment. "
            "Comma separated list of email addresses to deliver system-wide alerts to.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        email_list: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is None:
            raise Exception("setting not found for deployment_id")

        if not setting.template_bucket_name:
            raise Exception("Template bucket name is None")

        if not setting.aws_region:
            raise Exception("AWS region is None")

        if not setting.deployment_type:
            raise Exception("Deployment type is None")

        if setting.alerts_stack_setting is None and email_list is None:
            raise Exception("email_list has to be specified at the first use")

        gateways.deployment_template_bucket.create_bucket_if_not_exist(
            deployment_id, setting.template_bucket_name, setting.aws_region
        )

        alerts_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=setting.template_bucket_name,
            aws_region=setting.aws_region,
            key="alerts-template.json",
            content=generate_alerts_stack_json(),
        )

        if setting.alerts_stack_setting is None:
            assert email_list is not None
            setting.alerts_stack_setting = AlertsStackSetting(
                email_notifications=email_list,
            )

        gateways.deployment_settings.create_or_update(setting)

        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=alerts_template_url,
            setting=setting,
            parameters=generate_alerts_parameter_list(
                deployment_id=setting.deployment_id,
                email_notification_list=setting.alerts_stack_setting.email_notifications,
            ),
            stack_type=StackType.alerts,
        )

        setting.alerts_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)
