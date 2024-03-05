from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    If,
    ImportValue,
    Join,
    Ref,
    iam,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole
from .parameters import Parameters
from .conditions import Conditions
from .secret import Secret


class Roles:
    lambda_execution_role: iam.Role

    def __init__(self, t: Template, p: Parameters, c: Conditions, s: Secret):
        t.add_resource(
            iam.Role(
                "CloudWatchLoggingRole",
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

        self.lambda_execution_role = t.add_resource(
            iam.Role(
                "LambdaExecutionRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["lambda.amazonaws.com"]),
                        )
                    ]
                ),
                Policies=[
                    iam.Policy(
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "secretsmanager:Describe*",
                                        "secretsmanager:Get*",
                                        "secretsmanager:List*",
                                        "secretsmanager:UpdateSecret",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ec2:CreateNetworkInterface",
                                        "ec2:DeleteNetworkInterface",
                                        "ec2:Describe*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:*",
                                        "sqs:*",
                                        "sns:*",
                                        "ssm:*",
                                        "lambda:*",
                                        "dynamodb:*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        # TODO: only:
                                        #  cognito-idp:AdminCreateUser
                                        #  ...
                                        "cognito-idp:*",
                                    ],
                                    "Resource": If(
                                        c.custom_user_pool_arn,
                                        Ref(p.user_pool_arn),
                                        If(
                                            c.create_userpool_selected,
                                            ImportValue(
                                                Join(
                                                    "",
                                                    [
                                                        Ref(p.deployment_id),
                                                        "-AuthUserPoolArn",
                                                    ],
                                                )
                                            ),
                                            Ref("AWS::NoValue"),
                                        ),
                                    ),
                                },
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                Ref(p.pipeline_id),
                                "LambdaExecution",
                            ],
                        ),
                    )
                ],
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                ],
                Path="/",
            )
        )
