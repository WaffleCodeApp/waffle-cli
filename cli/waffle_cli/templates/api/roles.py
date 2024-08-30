from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    Template,
    apigateway,
    iam,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from .parameters import Parameters


class Roles:
    logging_role: iam.Role

    def __init__(self, t: Template, p: Parameters):
        self.logging_role = t.add_resource(
            iam.Role(
                "LoggingRole",
                RoleName=Join("", ["Waffle-", Ref(p.deployment_id), "-api-LogRole"]),
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["apigateway.amazonaws.com"]
                            ),
                        )
                    ]
                ),
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
                ],
            )
        )

        t.add_resource(
            apigateway.Account(
                "LoggingAccount",
                DependsOn=["LoggingRole"],
                CloudWatchRoleArn=GetAtt(self.logging_role, "Arn"),
            )
        )
