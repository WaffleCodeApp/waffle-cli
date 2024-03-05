from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    cognito,
    iam,
    Template,
)
from awacs.aws import (
    Allow,
    Condition,
    Statement,
    Principal,
    Policy,
    ForAnyValueStringLike,
    StringEquals,
)
from awacs.sts import AssumeRoleWithWebIdentity
from .parameters import Parameters
from .user_pool import UserPool


class IdentityPool:
    identity_pool: cognito.IdentityPool
    auth_role: iam.Role

    def __init__(self, t: Template, p: Parameters, up: UserPool):
        self.identity_pool = t.add_resource(
            cognito.IdentityPool(
                "AuthIdentityPool",
                AllowUnauthenticatedIdentities=False,
                DeveloperProviderName=Join("", [Ref(p.deployment_id), "-users"]),
                CognitoIdentityProviders=[
                    cognito.CognitoIdentityProvider(
                        ClientId=Ref(up.web_client),
                        ProviderName=GetAtt(up.user_pool, "ProviderName"),
                    ),
                ],
            )
        )

        self.auth_role = t.add_resource(
            iam.Role(
                "AuthRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRoleWithWebIdentity],
                            Principal=Principal(
                                "Federated", ["cognito-identity.amazonaws.com"]
                            ),
                            Condition=Condition(
                                [
                                    ForAnyValueStringLike(
                                        "cognito-identity.amazonaws.com:amr",
                                        "authenticated",
                                    ),
                                    StringEquals(
                                        "cognito-identity.amazonaws.com:aud",
                                        Ref(self.identity_pool),
                                    ),
                                ]
                            ),
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
                                    "Action": ["execute-api:Invoke"],
                                    "Resource": [
                                        Join(
                                            "",
                                            [
                                                "arn:aws:execute-api:",
                                                Ref("AWS::Region"),
                                                ":",
                                                Ref("AWS::AccountId"),
                                                ":",
                                                "*",
                                                "/*",
                                            ],
                                        )
                                    ],
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["cognito-sync:*", "cognito-identity:*"],
                                    "Resource": "*",
                                },
                                # NOTE: add all roles here that the auth user needs
                                # to work with
                                # {
                                #   "Effect": "Allow",
                                #   "Action": [
                                #     "dynamodb:*",
                                #     "rds:*"
                                #   ],
                                #   "Resource": "*"
                                # }
                            ],
                        },
                        PolicyName=Join(
                            "", [Ref(p.deployment_id), "-user-mfa-auth-policy"]
                        ),
                    )
                ],
            )
        )

        t.add_resource(
            cognito.IdentityPoolRoleAttachment(
                "AuthIdentityPoolRoleMap",
                DependsOn="AuthIdentityPool",
                IdentityPoolId=Ref(self.identity_pool),
                Roles={
                    # NOTE: we probably don't need unauthenticated
                    # if AllowUnauthenticatedIdentities=False is set for the
                    # authIdentityPool
                    # "unauthenticated": GetAtt(self.unauth_role, "Arn"),
                    "authenticated": GetAtt(self.auth_role, "Arn")
                },
            )
        )
