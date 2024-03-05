from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    ImportValue,
    Join,
    rds,
    Ref,
    secretsmanager,
    Template,
)

from .parameters import Parameters
from .conditions import Conditions
from .db_parameter_group import DbParameterGroup
from .secret import Secret
from .db_subnet_group import DbSubnetGroup
from .db_kms_key import DbKmsKey
from .monitoring_role import MonitoringRole


class RdsInstances:
    first_instance: rds.DBInstance
    second_instance: rds.DBInstance

    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        dpg: DbParameterGroup,
        s: Secret,
        dbsg: DbSubnetGroup,
        dbk: DbKmsKey,
        mr: MonitoringRole,
    ):
        engine = "postgres"

        self.first_instance = t.add_resource(
            rds.DBInstance(
                "RdsDBFirstInstance",
                Condition=c.rds_selected,
                CopyTagsToSnapshot=True,
                AllocatedStorage=If(
                    c.use_snapshot,
                    Ref("AWS::NoValue"),
                    Ref(p.storage_size),
                    # 5-1024
                ),
                StorageType="gp2",
                DeletionPolicy="Snapshot",
                UpdateReplacePolicy="Snapshot",
                Engine=engine,
                EngineVersion=Ref(p.postgres_engine_version),
                DBInstanceClass=Ref(p.instance_class),
                MultiAZ=If(c.is_prod, True, False),
                DBParameterGroupName=Ref(dpg.group),
                MasterUsername=If(
                    c.use_snapshot,
                    Ref("AWS::NoValue"),
                    Join(
                        "",
                        [
                            "{{resolve:secretsmanager:",
                            Ref(s.secret),
                            ":SecretString:username}}",
                        ],
                    ),
                ),
                MasterUserPassword=If(
                    c.use_snapshot,
                    Ref("AWS::NoValue"),
                    Join(
                        "",
                        [
                            "{{resolve:secretsmanager:",
                            Ref(s.secret),
                            ":SecretString:password}}",
                        ],
                    ),
                ),
                DBSubnetGroupName=Ref(dbsg.group),
                VPCSecurityGroups=[
                    If(
                        c.custom_local_incoming_connections_sg,
                        Ref(p.local_incoming_connections_sg),
                        ImportValue(
                            Join(
                                "",
                                [
                                    Ref(p.deployment_id),
                                    "-LocalIncomingConnectionSecurityGroupId",
                                ],
                            )
                        ),
                    )
                ],
                BackupRetentionPeriod=If(c.is_prod, 35, 2),
                KmsKeyId=If(
                    c.use_snapshot,
                    Ref("AWS::NoValue"),
                    Ref(dbk.key),
                ),
                EnableIAMDatabaseAuthentication=True,
                DBSnapshotIdentifier=If(
                    c.use_snapshot,
                    Ref(p.snapshot_id),
                    Ref("AWS::NoValue"),
                ),
                StorageEncrypted=If(c.use_snapshot, Ref("AWS::NoValue"), True),
                MonitoringInterval=If(c.is_prod, 1, 0),
                MonitoringRoleArn=If(
                    c.is_prod,
                    GetAtt(mr.role, "Arn"),
                    Ref("AWS::NoValue"),
                ),
                AutoMinorVersionUpgrade=If(c.is_prod, False, True),
                PubliclyAccessible=False,
                EnablePerformanceInsights=True,
                PerformanceInsightsKMSKeyId=Ref(dbk.key),
                PerformanceInsightsRetentionPeriod=If(c.is_prod, 731, 7),
                DeletionProtection=False,
            )
        )

        t.add_resource(
            secretsmanager.SecretTargetAttachment(
                "SecretRdsInstanceAttachment",
                Condition=c.rds_selected,
                SecretId=Ref(s.secret),
                TargetId=Ref(self.first_instance),
                TargetType="AWS::RDS::DBInstance",
            )
        )

        self.second_instance = t.add_resource(
            rds.DBInstance(
                "RdsDBReplicaForFirstInstance",
                DBInstanceClass=Ref(p.instance_class),
                Engine=engine,
                StorageType="gp2",
                SourceDBInstanceIdentifier=Ref(self.first_instance),
                Condition=c.create_replica,
            )
        )
