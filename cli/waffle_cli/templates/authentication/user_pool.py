from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    If,
    Join,
    Ref,
    cognito,
    Template,
)

from .parameters import Parameters
from .roles import Roles
from .conditions import Conditions


class UserPool:
    user_pool: cognito.UserPool
    web_client: cognito.UserPoolClient

    def __init__(self, t: Template, p: Parameters, r: Roles, c: Conditions):
        self.user_pool = t.add_resource(
            cognito.UserPool(
                "MFAUserPool",
                AdminCreateUserConfig=cognito.AdminCreateUserConfig(
                    AllowAdminCreateUserOnly=If(
                        c.allow_admin_create_user_only, True, False
                    ),
                ),
                # DeviceConfiguration=cognito.DeviceConfiguration(
                #    ChallengeRequiredOnNewDevice=True,
                #    DeviceOnlyRememberedOnUserPrompt=True
                # ),
                MfaConfiguration="ON",
                EnabledMfas=["SOFTWARE_TOKEN_MFA"],
                Policies=cognito.Policies(
                    PasswordPolicy=cognito.PasswordPolicy(
                        MinimumLength=12,
                        RequireLowercase=True,
                        RequireNumbers=True,
                        RequireSymbols=True,
                        RequireUppercase=True,
                    )
                ),
                Schema=[
                    cognito.SchemaAttribute(Name="email", Required=True, Mutable=True),
                    cognito.SchemaAttribute(
                        Name="role",
                        Required=False,
                        Mutable=True,
                        AttributeDataType="String",
                    ),
                    cognito.SchemaAttribute(
                        Name="organization",
                        Required=False,
                        Mutable=True,
                        AttributeDataType="String",
                    ),
                ],
                UsernameAttributes=["email"],
                UserPoolName=Join("", [Ref(p.deployment_id), "-users"]),
            )
        )

        self.web_client = t.add_resource(
            cognito.UserPoolClient(
                "UserPoolClientWeb",
                DependsOn="MFAUserPool",
                ClientName=Join("", [Ref(p.deployment_id), "-web"]),
                GenerateSecret=False,
                # NOTE: The following would allow to have the custom attributes
                # in the identity token. But it requires a more settings, including
                # changing the authentication flow. Instead, skipping this info
                # from the identity token for now, and querying the details from
                # cognito using the AWS API at every request on the backend.
                # AllowedOAuthScopes=["profile"],
                # AllowedOAuthFlowsUserPoolClient=True,
                # AllowedOAuthFlows=["code"],
                ReadAttributes=[
                    "email",
                    "email_verified",
                    "name",
                    "picture",
                    "custom:role",
                    "custom:organization",
                ],
                WriteAttributes=["email", "name", "picture"],
                UserPoolId=Ref(self.user_pool),
            )
        )
