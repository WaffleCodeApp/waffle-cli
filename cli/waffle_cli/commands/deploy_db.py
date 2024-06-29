from argparse import ArgumentParser
import re
from typing import Any

from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.db import generate_db_parameter_list, generate_db_stack_json
from ..utils.std_colors import BLUE, NEUTRAL, RED
from .command_type import Command
from .utils.deploy_new_stack import deploy_new_stack


STACK_ID = "waffle-db"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployDb(Command):
    name: str = "deploy_db"
    description: str = (
        "Generate a CFN template for a database and deploy it to the selected deployment. "
        "The stack deploys a PostgreSQL database sd either AWS RDS or AWS Aurora, "
        "with replicas, automated backups and alarms."
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
            "database_id",
            help="A database ID that will represent the database. Backend components will be able "
            "to access the database using this id. Recommended to use a human-understanable name "
            "that explains the purpose, like for example 'engine' or 'customers'.",
        )
        parser.add_argument(
            "--allocated_storage_size",
            help="DB storage size in GB. The default is 6.",
        )
        parser.add_argument(
            "--db_type",
            help="AWS RDS or Aurora. RDS by default.",
            choices=["rds", "aurora"],
        )
        parser.add_argument(
            "--family",
            help="AWS database family. If db_type is RDS, the default is postgres15. In case of Aurora, the default is aurora-postgresql15",
        )
        parser.add_argument(
            "--postgres_engine_version",
            help="PostgreSQL version. For example '15.3'",
        )
        parser.add_argument(
            "--instance_class",
            help="AWS database instance class. If db_type is RDS, the default is db.t3.micro. If Aurora then the default is db.t3.medium.",
        )
        parser.add_argument(
            "--create_replica",
            help="If a read replica has to be created in a different availability zone.",
            choices=["Yes", "No"],
        )
        parser.add_argument(
            "--snapshot_id",
            help="AWS DB snapshot identifier. If the database has to be restored from a backup, specify this identifies the backup.",
        )
        parser.add_argument(
            "--multi_az",
            help="If there shall be instance replicas in different AWS availability zones.",
        )
        parser.add_argument(
            "--log_retention_days",
            help="How many days should logs be kept",
        )

        parser.add_argument(
            "--custom_template_name",
            help="Optional. If there is a custom, already uploaded template for this purpose, specify its name.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        database_id: str | None = None,
        allocated_storage_size: str | None = None,
        db_type: str | None = None,
        family: str | None = None,
        postgres_engine_version: str | None = None,
        instance_class: str | None = None,
        create_replica: str | None = None,
        snapshot_id: str | None = None,
        custom_template_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert database_id is not None

        stack_id = f"{STACK_ID}-{database_id}"

        print("\n\n" + BLUE + "Deploying a PostgreSQL database." + NEUTRAL + "\n\n")

        if allocated_storage_size is None:
            print("\n\n")
            while True:
                allocated_storage_size = input("Specify the DB storage size in GB. ")
                if allocated_storage_size != "" and re.match(
                    "^[0-9]+$", allocated_storage_size
                ):
                    break
                print(RED + "Only numbers are supported." + NEUTRAL)

        if db_type is None:
            print(
                NEUTRAL
                + "\n\n"
                + "Database family. RDS and Aurora support different database families. "
                + "For example if database type is 'rds' then you could use 'postgres15'. "
                + "If database type is 'aurora' then you could use 'aurora-postgresql15'. "
                + "These questions are tailored for PostgreSQL databases. If you want to "
                + "use a different database family, then please do a custom installation instead."
                + "\n\n"
            )
            while True:
                db_type = input("Specify the database type: [rds or aurora]  ")
                if db_type.lower() in ["rds", "aurora"]:
                    break
                print(RED + "Please respond with rds or aurora." + NEUTRAL)

        if family is None:
            print(
                NEUTRAL
                + "\n\n"
                + "Database family: RDS and Aurora support different database families. "
                + "For example if database type is 'rds' then you could use 'postgres15'. "
                + "If database type is 'aurora' then you could use 'aurora-postgresql15'. "
                + "These questions are tailored for PostgreSQL databases. If you want to "
                + "use a different database family, then please do a custom installation instead."
                + "\n\n"
            )
            while True:
                family = input("Please specify the AWS database family. ")
                if family == "":
                    break
                print(RED + "Please specify a database family." + NEUTRAL)

        if postgres_engine_version is None:
            print("\n\n")
            while True:
                postgres_engine_version = input("Specify the AWS database family. ")
                if postgres_engine_version == "":
                    break
                print(RED + "Please specify an engine version." + NEUTRAL)

        if instance_class is None:
            print(
                NEUTRAL
                + "\n\n"
                + "Instance class: RDS and Aurora support different database instances. "
                + "For example if db_type is 'rds' then you could use 'db.t3.micro' as the "
                + "smallest choice. If db_type is 'aurora' then you could use 'db.t3.medium' "
                + "as the minimum."
                + "\n\n"
            )
            while True:
                instance_class = input("Specify the AWS database instance class. ")
                if instance_class == "":
                    break
                print(RED + "Please specify an instance class." + NEUTRAL)

        if create_replica is None and db_type != "aurora":
            print(
                NEUTRAL
                + "\n\n"
                + "Enabling a read replica will create a 2nd instance of the database "
                + "in a different availability zone."
                + "\n\n"
            )
            while True:
                create_replica = input(
                    "Choose if a read replica has to be created: ['Yes' or 'No'] "
                )
                if create_replica.lower() in ["yes", "no"]:
                    break
                print(RED + "Please respond with Yes or No." + NEUTRAL)

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=stack_id,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=generate_db_stack_json,
            parameter_list=generate_db_parameter_list(
                deployment_id=deployment_id,
                database_id=database_id,
                allocated_storage_size=allocated_storage_size,
                db_type=db_type,
                family=family,
                instance_class=instance_class,
                create_replica=create_replica,
                snapshot_id=snapshot_id,
            ),
            stack_type=StackType.db,
            include_in_the_project=True,
        )
