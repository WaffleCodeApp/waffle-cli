from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    ec2,
    logs,
    iam,
    Template,
)
from awacs.aws import Allow, Policy, Principal, Statement
from awacs.sts import AssumeRole

from .vpc import Vpc
from .parameters import Parameters


class FlowLog:
    def __init__(self, t: Template, p: Parameters, vpc: Vpc) -> None:
        log_group = t.add_resource(
            logs.LogGroup(
                "VPCFlowLogGroup",
                LogGroupName=Join("", [Ref(p.deployment_id), "-VPCFlowLogGroup"]),
                RetentionInDays=365,
            )
        )

        role = t.add_resource(
            iam.Role(
                "VPCFlowLogRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["ec2.amazonaws.com"]),
                        )
                    ]
                ),
                Path="/",
            )
        )

        t.add_resource(
            ec2.FlowLog(
                "VPCFlowLog",
                DeliverLogsPermissionArn=GetAtt(role, "Arn"),
                LogDestinationType="cloud-watch-logs",
                LogGroupName=Ref(log_group),
                ResourceId=Ref(vpc.vpc),
                ResourceType="VPC",
                TrafficType="ALL",
            )
        )
