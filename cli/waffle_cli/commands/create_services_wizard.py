from argparse import ArgumentParser
import re
from typing import Any

from ..application_logic.entities.project_setting import ProjectSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import BLUE, BOLD, NEUTRAL, RED, YELLOW
from .command_type import Command
from .deploy_cdn import DeployCdn
from .deploy_db import DeployDb


class CreateServicesWizard(Command):
    name = "create_services_wizard"
    description = "Step-by-step specify services and deploy them to the deployments."

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def execute(gateways: Gateways = gateway_implementations, **__: Any) -> None:
        print(
            NEUTRAL
            + "Waffle is a toolkit to help deploy complete web-applications to secure "
            + "environments in AWS.\n\n"
            + "This tool helps you add services to your existing deployments step-by-step interactively "
            + "and deploy it to your deployments.\n\n"
            + YELLOW
            + "If you want to use custom templates or existing resources, then "
            + "you need to do a custom installation, prease refer to the docs.\n\n"
            + NEUTRAL
        )
        while True:
            proceed = input("Do you want to proceed? [Y]/n ")
            if proceed.lower() == "y" or proceed == "":
                break
            elif proceed.lower() == "n":
                return

        print("\n")

        deployment_ids = gateways.deployment_settings.get_names()
        if len(deployment_ids) == 0:
            print(
                RED
                + "Couldn't find any deployments. Please start with creating at "
                + "least one deployment.\n\n"
                + NEUTRAL
                + "You can create a new deployment with the setup_project_wizard "
                + "command.\n\n"
            )
            return

        print(
            NEUTRAL
            + "You can create the following types of services with waffle:\n"
            + "- Frontend with its own CICD pipeline\n"
            + "- Long running (containerized) backend service with its own CICD pipeline and HTTP endpoints\n"
            + "- Database with optional automated backups. Only PostgreSQL is supported yet.\n"
            + "- Any infrastructure as code with its own CICD pipeline\n"
            + "The last one can be used for deploying short-running, rapidly scaling backend services (AWS Lambda).\n\n"
            + NEUTRAL
            + BOLD
            + "This wizard enables you to add any number services of your choice "
            + "and deploy them to your deployments.\n\n"
            + NEUTRAL
        )

        project_setting = gateways.project_settings.get() or ProjectSetting()

        if len(project_setting.stacks) > 0:
            print(
                NEUTRAL
                + "Your project already has the following services added:\n"
                + "\n".join([f"- {s.stack_id}" for s in project_setting.stacks])
                + "\n\n"
            )
        else:
            gateways.project_settings.create_or_update(project_setting)

        while True:
            print(
                BLUE
                + "What type of service do you want to add to your project next?\n"
                + NEUTRAL
                + "[0] Frontend\n"
                + "[1] Backend container\n"
                + "[2] Database (PostgreSQL)\n"
                + "[3] Infrastructure (choose this for deploying Lambda)\n"
                + "[4] I've finished adding services.\n\n"
            )
            resp = input("Please choose a service type: [0-4] ")
            if resp in ["0", "1", "2", "3"]:
                while True:
                    print(
                        BOLD
                        + "To which deployment do you want to install it next?\n\n"
                        + NEUTRAL
                        + "The following deployments were found:\n"
                        + "\n".join([f"\t- {d}" for d in deployment_ids])
                        + f"\n\nRespond to the next question with {BLUE}done{NEUTRAL} if finished deploying this sevrice.\n"
                    )
                    deployment_id: str = ""
                    while True:
                        deployment_id = input(
                            "Please choose a deployment from the list above or type done: "
                        )
                        if deployment_id in deployment_ids or deployment_id == "done":
                            break
                        else:
                            print(
                                RED
                                + "Deployment choice not reconized, please use one of the list above. Or respond with 'done'."
                                + NEUTRAL
                            )
                    if deployment_id == "done":
                        break

                    print("\n\n")
                    # proceed with deployment

                    if resp == "0":
                        print(
                            BOLD + "Adding and deploying a frontend-stack\n\n" + NEUTRAL
                        )
                        pipeline_id = input("Please choose an id for this service: ")
                        if pipeline_id != "" and re.match("^[a-z,0-9]+$", pipeline_id):
                            break
                        print(RED + "Only letters and numbers are supported." + NEUTRAL)
                        DeployCdn.execute(
                            deployment_id=deployment_id, pipeline_id=pipeline_id
                        )
                    elif resp == "1":
                        print(
                            BOLD
                            + "Adding and deploying a backend container\n\n"
                            + NEUTRAL
                        )
                    elif resp == "2":
                        print(
                            BOLD
                            + "Adding and deploying a database\n\n"
                            + NEUTRAL
                            + "Databases created using waffle require an identifier. "
                            + "This id can be used for easily accessing the db from "
                            + "other services. The id can be a string of your choice "
                            + "containing only letters. You'll likely have to use the id in "
                            + "your codebase, so it's recommended to use something that "
                            + "explains the purpose well, like for example 'engine' or 'customers'."
                            + "\n\n"
                        )
                        while True:
                            database_id = input(
                                "Please choose an id for this database: "
                            )
                            if database_id != "" and re.match(
                                "^[a-z,0-9]+$", database_id
                            ):
                                break
                            print(
                                RED
                                + "Only letters and numbers are supported."
                                + NEUTRAL
                            )
                        DeployDb.execute(
                            deployment_id=deployment_id, database_id=database_id
                        )
                    elif resp == "3":
                        print(
                            BOLD
                            + "Adding and deploying a stack of AWS resources\n\n"
                            + NEUTRAL
                        )
            elif resp == "4":
                print(BOLD + "Finished adding new services.\n\n" + NEUTRAL)
                break
            else:
                print(
                    RED
                    + "Could not recognize your answer, please respond with a number between 0-4.\n"
                    + NEUTRAL
                )
