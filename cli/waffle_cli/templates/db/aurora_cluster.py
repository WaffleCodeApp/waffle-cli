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
from .secret import Secret
from .db_subnet_group import DbSubnetGroup
from .db_kms_key import DbKmsKey
from .db_parameter_group import DbParameterGroup
from .monitoring_role import MonitoringRole


class AuroraCluster:
    cluster: rds.DBCluster
    first_instance: rds.DBInstance
    second_instance: rds.DBInstance

    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        s: Secret,
        dbsg: DbSubnetGroup,
        dbk: DbKmsKey,
        dbpg: DbParameterGroup,
        mr: MonitoringRole,
    ):
        cpg: rds.DBClusterParameterGroup = t.add_resource(
            rds.DBClusterParameterGroup(
                "DBClusterParamGroup",
                Condition=c.aurora_selected,
                Description="DB Cluster Parameter Group",
                Family=Ref(p.family),
                Parameters={
                    "rds.force_ssl": 1,
                    # TODO: timezone
                },
            )
        )

        engine = "aurora-postgresql"

        self.cluster = t.add_resource(
            rds.DBCluster(
                "AuroraDBCluster",
                Condition=c.aurora_selected,
                DeletionPolicy="Snapshot",
                UpdateReplacePolicy="Snapshot",
                Engine=engine,
                EngineVersion=Ref(p.postgres_engine_version),
                DatabaseName=Ref("AWS::NoValue"),
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
                VpcSecurityGroupIds=[
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
                DBClusterParameterGroupName=Ref(cpg),
                KmsKeyId=If(
                    c.use_snapshot,
                    Ref("AWS::NoValue"),
                    Ref(dbk.key),
                ),
                EnableIAMDatabaseAuthentication=True,
                SnapshotIdentifier=If(
                    c.use_snapshot,
                    Ref(p.snapshot_id),
                    Ref("AWS::NoValue"),
                ),
                StorageEncrypted=If(c.use_snapshot, Ref("AWS::NoValue"), True),
            )
        )

        t.add_resource(
            secretsmanager.SecretTargetAttachment(
                "SecretAuroraClusterAttachment",
                Condition=c.aurora_selected,
                SecretId=Ref(s.secret),
                TargetId=Ref(self.cluster),
                TargetType="AWS::RDS::DBCluster",
            )
        )

        self.first_instance = t.add_resource(
            rds.DBInstance(
                "AuroraDBFirstInstance",
                Condition=c.aurora_selected,
                DBInstanceClass=Ref(p.instance_class),
                DBClusterIdentifier=Ref(self.cluster),
                Engine=engine,
                EngineVersion=Ref(p.postgres_engine_version),
                DBParameterGroupName=Ref(dbpg.group),
                MonitoringInterval=If(c.is_prod, 1, 0),
                MonitoringRoleArn=If(
                    c.is_prod,
                    GetAtt(mr.role, "Arn"),
                    Ref("AWS::NoValue"),
                ),
                AutoMinorVersionUpgrade=If(c.is_prod, False, True),
                DBSubnetGroupName=Ref(dbsg.group),
                PubliclyAccessible=False,
                EnablePerformanceInsights=True,
                PerformanceInsightsKMSKeyId=Ref(dbk.key),
                PerformanceInsightsRetentionPeriod=If(c.is_prod, 731, 7),
            )
        )

        self.second_instance = t.add_resource(
            rds.DBInstance(
                "AuroraDBSecondInstance",
                Condition=c.aurora_selected,
                DependsOn="AuroraDBFirstInstance",
                DBInstanceClass=Ref(p.instance_class),
                DBClusterIdentifier=Ref(self.cluster),
                Engine=engine,
                EngineVersion=Ref(p.postgres_engine_version),
                DBParameterGroupName=Ref(dbpg.group),
                MonitoringInterval=If(c.is_prod, 1, 0),
                MonitoringRoleArn=If(
                    c.is_prod,
                    GetAtt(mr.role, "Arn"),
                    Ref("AWS::NoValue"),
                ),
                AutoMinorVersionUpgrade=If(c.is_prod, False, True),
                DBSubnetGroupName=Ref(dbsg.group),
                PubliclyAccessible=False,
                EnablePerformanceInsights=True,
                PerformanceInsightsKMSKeyId=Ref(dbk.key),
                PerformanceInsightsRetentionPeriod=If(c.is_prod, 731, 7),
            )
        )
