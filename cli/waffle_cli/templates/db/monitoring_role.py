from troposphere import iam, Template  # pyright: ignore[reportMissingTypeStubs]
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .conditions import Conditions


class MonitoringRole:
    role: iam.Role

    def __init__(self, t: Template, c: Conditions):
        self.role = t.add_resource(
            iam.Role(
                "MonitoringIAMRole",
                Condition=c.is_prod,
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
