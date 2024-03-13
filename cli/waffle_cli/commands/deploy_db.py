from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.stack_settings.db_stack_setting import DbStackSetting
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.db import generate_db_parameter_list, generate_db_stack_json
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
            # choices=["aurora-postgresql15", "postgres15"]
        )
        parser.add_argument(
            "--instance_class",
            help="AWS database instance class. If db_type is RDS, the default is db.t3.micro. If Aurora then the default is db.t3.medium.",
        )


    @staticmethod
    def execute(
        deployment_id: str | None = None,
        database_id: str | None = None,
        allocated_storage_size: str | None = None,
        db_type: str | None = None,
        family: str | None = None,
        instance_class: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert database_id is not None

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

        db_stack_setting = next((ds for ds in setting.db_stack_settings if ds.database_id == database_id), None)

        if db_stack_setting is None:
            db_stack_setting = DbStackSetting(database_id=database_id)
            setting.db_stack_settings.append(db_stack_setting)
            gateways.deployment_settings.create_or_update(setting)


        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=db_template_url,
            setting=setting,
            parameters=generate_db_parameter_list(
                deployment_id=setting.deployment_id,
                database_id=database_id,
                # TODO: store thes in the stack settings:
                # allocated_storage_size=allocated_storage_size,
            ),
            stack_type=StackType.db,
        )

        db_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)
