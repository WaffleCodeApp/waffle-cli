from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]
from .parameters import Parameters
from .conditions import Conditions
from .db_subnet_group import DbSubnetGroup
from .secret import Secret
from .db_kms_key import DbKmsKey
from .monitoring_role import MonitoringRole
from .db_parameter_group import DbParameterGroup
from .aurora_cluster import AuroraCluster
from .rds_instances import RdsInstances
from .alarms import Alarms
from .outputs import Outputs


def generate_db_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    db_subnet_group = DbSubnetGroup(t, params, conditions)
    secret = Secret(t, params)
    db_kms_key = DbKmsKey(t)
    monitoring_role = MonitoringRole(t, conditions)
    db_parameter_group = DbParameterGroup(t, params, conditions)
    aurora_cluster = AuroraCluster(
        t,
        params,
        conditions,
        secret,
        db_subnet_group,
        db_kms_key,
        db_parameter_group,
        monitoring_role,
    )
    rds_instances = RdsInstances(
        t,
        params,
        conditions,
        db_parameter_group,
        secret,
        db_subnet_group,
        db_kms_key,
        monitoring_role,
    )
    Alarms(t, params, conditions, aurora_cluster, rds_instances, db_parameter_group)
    Outputs(t, params, secret)

    return t.to_json()

def generate_db_parameter_list(
    deployment_id: str,
    database_id: str,
    allocated_storage_size: str | None = None,
    db_type: str | None = None,
    family: str | None = None,
    postgres_engine_version: str | None = None,
    instance_class: str | None = None,
    create_replica: str | None = None,
    snapshot_id: str | None = None,
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
        {
            "ParameterKey": "DatabaseId",
            "ParameterValue": database_id,
        },
        {
            "ParameterKey": "AllocatedStorageSize",
            "ParameterValue": allocated_storage_size or "",
        },
        {
            "ParameterKey": "Family",
            "ParameterValue": family or "",
        },
        {
            "ParameterKey": "PostgresEngineVersion",
            "ParameterValue": postgres_engine_version or "",
        },
        {
            "ParameterKey": "InstanceClass",
            "ParameterValue": instance_class or "",
        },
        {
            "ParameterKey": "SnaphotId",
            "ParameterValue": snapshot_id or "",
        },
        {
            "ParameterKey": "CreateReplica",
            "ParameterValue": create_replica or "",
        },
        {
            "ParameterKey": "DBType",
            "ParameterValue": db_type or "",
        }
    ]
 