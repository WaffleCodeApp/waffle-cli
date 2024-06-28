from argparse import ArgumentParser
from typing import Any
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.alerts import generate_alerts_stack_json
from ..templates.api import generate_api_stack_json
from ..templates.authentication import generate_auth_stack_json
from ..templates.cdn_cicd import generate_cdn_cicd_stack_json
from ..templates.cfn_cicd import generate_cfn_cicd_stack_json
from ..templates.db import generate_db_stack_json
from ..templates.deployment import generate_deployment_stack_json
from ..templates.ecs_cicd import generate_ecs_cicd_stack_json
from ..templates.github import generate_github_stack_json
from ..templates.vpc import generate_vpc_stack_json
from .command_type import Command


class GenerateTemplates(Command):
    name = "generate_templates"
    description = "Creates templates and stores them locally"

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def execute(
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        gateways.local_files.store_file("alerts.json", generate_alerts_stack_json())
        gateways.local_files.store_file("api.json", generate_api_stack_json())
        gateways.local_files.store_file(
            "auth_userpool.json", generate_auth_stack_json()
        )
        gateways.local_files.store_file("cicd-cdn.json", generate_cdn_cicd_stack_json())
        gateways.local_files.store_file("cicd-cfn.json", generate_cfn_cicd_stack_json())
        gateways.local_files.store_file("db.json", generate_db_stack_json())
        gateways.local_files.store_file(
            "deployment.json", generate_deployment_stack_json()
        )
        gateways.local_files.store_file("cicd-ecs.json", generate_ecs_cicd_stack_json())
        gateways.local_files.store_file("github.json", generate_github_stack_json())
        gateways.local_files.store_file("vpc.json", generate_vpc_stack_json())
