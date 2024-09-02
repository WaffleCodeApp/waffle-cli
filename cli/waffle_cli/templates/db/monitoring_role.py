from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    iam,
    Join,
    Ref,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .conditions import Conditions
from .parameters import Parameters


class MonitoringRole:
    role: iam.Role

    def __init__(self, t: Template, c: Conditions, p: Parameters):
        self.role = t.add_resource(
            iam.Role(
                "MonitoringIAMRole",
                Condition=c.alarms_enabled,
                RoleName=Join(
                    "",
                    [
                        "Waffle-",
                        Ref(p.deployment_id),
                        "-db-MonitoringRole",
                    ],
                ),
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["monitoring.rds.amazonaws.com"]
                            ),
                        )
                    ]
                ),
                Path="/",
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/"
                    "AmazonRDSEnhancedMonitoringRole"
                ],
            )
        )
