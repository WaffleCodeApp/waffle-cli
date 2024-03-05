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
