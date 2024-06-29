from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    And,
    Equals,
    Not,
    Ref,
    Template,
)
from .parameters import Parameters


class Conditions:
    use_snapshot: str = "USE_SNAPSHOT"
    create_replica: str = "CREATE_REPLICA"
    aurora_selected: str = "AURORA_SELECTED"
    rds_selected: str = "RDS_SELECTED"
    custom_vpc_ref: str = "CUSTOM_VPC_REF"
    custom_primary_private_subnet_ref: str = "CUSTOM_PRIMARY_PRIVATE_SUBNET_REF"
    custom_secondary_private_subnet_ref: str = "CUSTOM_SECONDARY_PRIVATE_SUBNET_REF"
    custom_local_incoming_connections_sg: str = "CUSTOM_LOCAL_INCOMMING_CONNECTIONS_SG"
    # custom_deployment_secret_arn: str = "CUSTOM_DEPLOYMENT_SECRET_ARN"
    custom_alerts_sns_ref: str = "CUSTOM_ALERT_SNS_REF"
    alarms_enabled: str = "ALARMS_ENABLED"
    aurora_alarms_enabled: str = "AURORA_ALARMS_ENABLED"
    multi_az: str = "MULTI_AZ"

    def __init__(self, t: Template, p: Parameters) -> None:
        t.add_condition(
            self.use_snapshot,
            Not(Equals(Ref(p.snapshot_id), "")),
        )

        t.add_condition(
            self.create_replica,
            Equals(Ref(p.create_replica), "Yes"),
        )

        t.add_condition(
            self.aurora_selected,
            Equals(Ref(p.db_type), "aurora"),
        )

        t.add_condition(
            self.rds_selected,
            Equals(Ref(p.db_type), "rds"),
        )

        t.add_condition(
            self.custom_vpc_ref,
            Not(Equals(Ref(p.vpc_ref), "")),
        )

        t.add_condition(
            self.custom_primary_private_subnet_ref,
            Not(Equals(Ref(p.primary_private_subnet_ref), "")),
        )

        t.add_condition(
            self.custom_secondary_private_subnet_ref,
            Not(Equals(Ref(p.secondary_private_subnet_ref), "")),
        )

        t.add_condition(
            self.custom_local_incoming_connections_sg,
            Not(Equals(Ref(p.local_incoming_connections_sg), "")),
        )

        # t.add_condition(
        #     self.custom_deployment_secret_arn,
        #     Not(Equals(Ref(p.deployment_secret_arn), "")),
        # )

        t.add_condition(
            self.custom_alerts_sns_ref,
            Not(Equals(Ref(p.alerts_sns_ref), "")),
        )

        t.add_condition(
            self.alarms_enabled,
            Equals(Ref(p.alarms_enabled), "True"),
        )

        t.add_condition(
            self.aurora_alarms_enabled,
            And(
                Equals(Ref(p.alarms_enabled), "True"), Equals(Ref(p.db_type), "aurora")
            ),
        )
        t.add_condition(
            self.multi_az,
            Equals(Ref(p.multi_az), "True"),
        )
