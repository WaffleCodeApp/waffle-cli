from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.stack_settings.db_stack_setting import DbStackSetting
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.db import generate_db_parameter_list, generate_db_stack_json
from ..utils.std_colors import BLUE, BOLD, GREEN, NEUTRAL, RED
from .command_type import Command


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
            "that explains the purpose, like for example engine or customers.",
        )
        parser.add_argument(
            "--allocated_storage_size",
            help="DB storage size in GB. The default is 6.",
        )
        parser.add_argument(
            "--db_type",
            help="AWS RDS or Aurora. RDS by default.",
            choices=["rds", "aurora"]
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
            help="AWS database instance class. If db_type is RDS, the default is db.t3.micro. If Aurora then the default is db.t3.medium.",
            choices=["Yes", "No"]
        )
        parser.add_argument(
            "--snapshot_id",
            help="AWS DB snapshot identifier. If the database has to be restored from a backup, specify this identifies the backup.",
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
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert database_id is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is None:
            print(RED + f'Settings for {deployment_id} not found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("Setting not found for deployment_id")

        if setting.aws_region is None:
            print(RED + 'AWS region setting not found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("AWS region is None")

        if setting.deployment_type is None:
            print(RED + 'Deployment type setting found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("Deployment type is None")

        if setting.template_bucket_name is None:
            print(RED + "Template bucket name setting not found. Please make sure to run configure_deployment_domain first." + NEUTRAL)
            raise Exception("template_bucket_name is None")

        db_stack_setting = next((ds for ds in setting.db_stack_settings if ds.database_id == database_id), None)

        if db_stack_setting is None:
            db_stack_setting = DbStackSetting(database_id=database_id)
            setting.db_stack_settings.append(db_stack_setting)
            gateways.deployment_settings.create_or_update(setting)

        if db_stack_setting.allocated_storage_size is None and allocated_storage_size is None:
            print(BLUE + BOLD)
            db_stack_setting.allocated_storage_size = input("Please specify the DB storage size in GB. ")
            print(NEUTRAL)
        elif allocated_storage_size is not None:
            db_stack_setting.allocated_storage_size = allocated_storage_size

        if db_stack_setting.db_type is None and db_type is None:
            print(BLUE + BOLD)
            db_stack_setting.db_type = input("Please specify the DB type: AWS RDS or Aurora. 'rds' or 'aurora' accepted ")
            print(NEUTRAL)
            if db_stack_setting.db_type not in ['rds', 'aurora']:
                raise Exception('DB type unknown')
        elif db_type is not None:
            db_stack_setting.db_type = db_type

        if db_stack_setting.family is None and family is None:
            print(BLUE + BOLD)
            db_stack_setting.family = input("Please specify the AWS database family. For example if db_type is 'rds' then you could use 'postgres15'. If db_type is 'aurora' then you could use 'aurora-postgresql15'. ")
            print(NEUTRAL)
        elif family is not None:
            db_stack_setting.family = family

        if db_stack_setting.postgres_engine_version is None and postgres_engine_version is None:
            print(BLUE + BOLD)
            db_stack_setting.postgres_engine_version = input("Please specify the PostgreSQL version. For example '15.3'. ")
            print(NEUTRAL)
        elif postgres_engine_version is not None:
            db_stack_setting.postgres_engine_version = postgres_engine_version

        if db_stack_setting.instance_class is None and instance_class is None:
            print(BLUE + BOLD)
            db_stack_setting.instance_class = input("Please specify the AWS database instance class. For example if db_type is 'rds' then you could use 'db.t3.micro' as the smallest choice. If db_type is 'aurora' then you could use 'db.t3.medium' as the minimum. ")
            print(NEUTRAL)
        elif instance_class is not None:
            db_stack_setting.instance_class = instance_class

        if db_stack_setting.create_replica is None and create_replica is None:
            print(BLUE + BOLD)
            db_stack_setting.create_replica = input("Please specify if a read replica should be created in a different availability zone. 'Yes' or 'No': ")
            print(NEUTRAL)
            if db_stack_setting.create_replica not in ['Yes', 'No']:
                raise Exception('create_replica response unknown')
        elif create_replica is not None:
            db_stack_setting.create_replica = create_replica

        gateways.deployment_settings.create_or_update(setting)

        gateways.deployment_template_bucket.create_bucket_if_not_exist(
            deployment_id, setting.template_bucket_name, setting.aws_region
        )

        db_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=setting.template_bucket_name,
            aws_region=setting.aws_region,
            key="db-template.json",
            content=generate_db_stack_json(),
        )

        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=db_template_url,
            setting=setting,
            parameters=generate_db_parameter_list(
                deployment_id=setting.deployment_id,
                database_id=database_id,
                allocated_storage_size=db_stack_setting.allocated_storage_size,
                db_type=db_stack_setting.db_type,
                family=db_stack_setting.family,
                instance_class=db_stack_setting.instance_class,
                create_replica=create_replica,
                snapshot_id=snapshot_id
            ),
            stack_type=StackType.db,
        )

        db_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)

        print(GREEN + 'Done. The deployment typically takes a few minutes.\n' + NEUTRAL)
