from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter
    database_id: Parameter
    storage_size: Parameter
    family: Parameter
    postgres_engine_version: Parameter
    instance_class: Parameter
    snapshot_id: Parameter
    create_replica: Parameter
    db_type: Parameter
    vpc_ref: Parameter
    primary_private_subnet_ref: Parameter
    secondary_private_subnet_ref: Parameter
    local_incoming_connections_sg: Parameter
    alerts_sns_ref: Parameter
    multi_az: Parameter
    log_retention_days: Parameter
    alarms_enabled: Parameter
    backup_retention: Parameter

    def __init__(self, t: Template):
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        self.database_id = t.add_parameter(
            Parameter("DatabaseId", Description="database_id", Type="String")
        )

        self.storage_size = t.add_parameter(
            Parameter(
                "AllocatedStorageSize",
                Description="Allocated storage size",
                Type="String",
                Default="6",  # making it larger than the alarm threshold
            )
        )

        self.family = t.add_parameter(
            Parameter(
                "Family",
                Description="DB family for RDS or Aurora",
                Type="String",
                Default="aurora-postgresql15",
            )
        )

        self.postgres_engine_version = t.add_parameter(
            Parameter(
                "PostgresEngineVersion",
                Description="Postgres RDS or Aurora engine version",
                Type="String",
                Default="15.3",
            )
        )

        self.instance_class = t.add_parameter(
            Parameter(
                "InstanceClass",
                Description="Postgres RDS or Aurora instance class",
                Type="String",
                Default="db.t3.micro",  # minimum encryptable for RDS
                # Default="db.t3.medium", # minimum for aurora
            )
        )

        self.snapshot_id = t.add_parameter(
            Parameter(
                "SnaphotId",
                Description="Id of a snapshot to start with",
                Type="String",
                Default="",
            )
        )

        self.create_replica = t.add_parameter(
            Parameter(
                "CreateReplica",
                Description="Boolean to setup replica creation for RDS",
                Type="String",
                Default="Yes",
            )
        )

        self.db_type = t.add_parameter(
            Parameter(
                "DBType",
                Description="DB Type - internally defined",
                Type="String",
                AllowedValues=["rds", "aurora"],
                Default="aurora",
            )
        )

        self.vpc_ref = t.add_parameter(
            Parameter(
                "VPCRef",
                Description="(optional) The VPC",
                Type="String",
                Default="",
            )
        )

        self.primary_private_subnet_ref = t.add_parameter(
            Parameter(
                "PrimaryPrivateSubnetRef",
                Description="(optional) The primary private subnet in the VPC",
                Type="String",
                Default="",
            )
        )

        self.secondary_private_subnet_ref = t.add_parameter(
            Parameter(
                "SecondaryPrivateSubnetRef",
                Description="(optional) The secondary private subnet in the VPC",
                Type="String",
                Default="",
            )
        )

        self.local_incoming_connections_sg = t.add_parameter(
            Parameter(
                "LocalIncomingConnectionSecurityGroupId",
                Description="(optional) Local inbound enabled SG",
                Type="String",
                Default="",
            )
        )

        self.alerts_sns_ref = t.add_parameter(
            Parameter(
                "AlertsSnsTopicRef",
                Description="The ref of the sns topic to deliver alarms",
                Type="String",
                Default="",
            )
        )

        self.multi_az = t.add_parameter(
            Parameter(
                "MultiAZ",
                Description="Boolean to setup replica creation for RDS",
                Type="String",
                AllowedValues=["True", "False"],
                Default="True",
            )
        )

        self.log_retention_days = t.add_parameter(
            Parameter(
                "LogRetentionDays",
                Description="(optional) Days how long logs to be retained.",
                Type="String",
                Default="365",
            )
        )

        self.alarms_enabled = t.add_parameter(
            Parameter(
                "AlarmsEnabled",
                Description="(optional) If system alarms should be set up.",
                Type="String",
                AllowedValues=["True", "False"],
                Default="True",
            )
        )

        self.backup_retention = t.add_parameter(
            Parameter(
                "BackupRetention",
                Description="(optional) Days how long automated backups should be retained",
                Type="String",
                Default="35",
            )
        )
