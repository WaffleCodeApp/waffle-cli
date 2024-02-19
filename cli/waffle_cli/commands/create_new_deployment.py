from argparse import ArgumentParser

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import GatewayImplementations
from .command_type import Command


class CreateNewDeployment(Command):
    name = "create_new_deployment"
    description = "Create settings for a deployment"

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "deployment_id",
            help="Deployment ID, like for example prod, dev, test, qa, etc.",
        )

    @staticmethod
    def execute(gateways: Gateways = GatewayImplementations(), **kw: str) -> None:
        deployment_id = kw.get("deployment_id")
        if deployment_id is None:
            raise Exception("deployment_id is None")
        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is not None:
            raise Exception("deployment_id already exists")
        gateways.deployment_settings.create_or_update(
            DeploymentSetting(deployment_id=deployment_id)
        )
