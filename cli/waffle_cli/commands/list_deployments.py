from argparse import ArgumentParser
from typing import Any
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from .command_type import Command


class ListDeployments(Command):
    name = "list_deployments"
    description = "List deployment IDs that have settings locally."

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def execute(gateways: Gateways = gateway_implementations, **__: Any) -> None:
        names = gateways.deployment_settings.get_names()
        print("Existing deployment ids:\n\t- " + "\n\t- ".join(names))
