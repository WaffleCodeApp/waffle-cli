from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    apigateway,
    iam,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole


class Roles:
    logging_role: iam.Role

    def __init__(self, t: Template):
        self.logging_role = t.add_resource(
            iam.Role(
                "LoggingRole",
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
