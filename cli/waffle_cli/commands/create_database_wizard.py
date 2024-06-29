from argparse import ArgumentParser
import re
from typing import Any

from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import BOLD, NEUTRAL, RED, YELLOW
from .command_type import Command
from .deploy_db import DeployDb


class CreateDatabaseWizard(Command):
    name = "create_database_wizard"
    description = "Step-by-step specify a PostgreSQL database and deploy it into an existing Waffle deployment."

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def execute(gateways: Gateways = gateway_implementations, **__: Any) -> None:
        print(
            NEUTRAL
            + "Waffle is a toolkit to help deploy complete web-applications to secure "
            + "environments in AWS.\n\n"
            + "This tool helps you add a PostgreSQL database to one of your existing "
            + "deployments step-by-step interactively.\n\n"
            + YELLOW
            + "If you want to use custom templates or existing resources, then "
            + "you need to do a custom installation, prease refer to the docs.\n\n"
            + NEUTRAL
        )

        deployment_ids = gateways.deployment_settings.get_names()
        if len(deployment_ids) == 0:
            print(
                RED
                + "Couldn't find any deployments. Please start with creating at "
                + "least one deployment.\n\n"
                + NEUTRAL
                + "You can create a new deployment with the create_deployment_wizard "
                + "command.\n\n"
            )
            return

        print(
            BOLD
            + "To which deployment do you want to install a frontend?\n\n"
            + NEUTRAL
            + "The following deployments were found:\n"
            + "\n".join([f"\t- {d}" for d in deployment_ids])
            + "\n\n"
        )
        deployment_id: str = ""
        while True:
            deployment_id = input(
                "Please choose a deployment from the list above or type done: "
            )
            if deployment_id in deployment_ids:
                break
            else:
                print(
                    RED
                    + "Deployment choice not reconized, please use one of the list above."
                    + NEUTRAL
                )

        print("\n\n" + NEUTRAL)
        print(
            NEUTRAL
            + "Databases created using waffle require an identifier. "
            + "This id can be used for easily accessing the db from "
            + "other services. The id can be a string of your choice "
            + "containing only letters. You'll likely have to use the id in "
            + "your codebase, so it's recommended to use something that "
            + "explains the purpose well, like for example 'engine' or 'customers'."
            + "\n\n"
        )
        while True:
            database_id = input("Please choose an id for this database: ")
            if database_id != "" and re.match("^[a-z,0-9]+$", database_id):
                break
            print(RED + "Only letters and numbers are supported." + NEUTRAL)
        DeployDb.execute(
            deployment_id=deployment_id,
            database_id=database_id,
        )
