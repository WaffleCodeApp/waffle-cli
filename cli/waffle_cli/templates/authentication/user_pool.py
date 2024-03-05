from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    cognito,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions
from .roles import Roles


class UserPool:
    user_pool: cognito.UserPool
    web_client: cognito.UserPoolClient

    def __init__(self, t: Template, p: Parameters, c: Conditions, r: Roles):
        self.user_pool = t.add_resource(
            cognito.UserPool(
                "AuthMFAUserPool",
                Conditions=[c.create_userpool_selected],
                AdminCreateUserConfig=cognito.AdminCreateUserConfig(
                    AllowAdminCreateUserOnly=True,
                    InviteMessageTemplate=cognito.InviteMessageTemplate(
                        SMSMessage=Ref(p.invitation_sms_text)
                    ),
                ),
                AutoVerifiedAttributes=["phone_number"],
                # NOTE: we definitely need this below on a long term,
                # I just can't get it working on the frontend.
                # https://github.com/aws-amplify/amplify-js/issues/2087
                # see also the frontend code
                # https://github.com/SYRGAPP/temp-web-frontend/blob/2e18666b8af8f6f05bda73e318d31b3195f8b8a6/src/authentication/authentication.js#L43
                # DeviceConfiguration=cognito.DeviceConfiguration(
                #    ChallengeRequiredOnNewDevice=True,
                #    DeviceOnlyRememberedOnUserPrompt=True
                # ),
                MfaConfiguration="ON",
                EnabledMfas=["SMS_MFA"],
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
                    cognito.SchemaAttribute(
                        Name="phone_number", Required=True, Mutable=True
                    ),
                    cognito.SchemaAttribute(Name="email", Required=True, Mutable=True),
                    cognito.SchemaAttribute(
                        Name="role",
                        Required=False,
                        Mutable=True,
                        AttributeDataType="String",
                        DeveloperOnlyAttribute=True,
                    ),
                    cognito.SchemaAttribute(
                        Name="organization",
                        Required=False,
                        Mutable=True,
                        AttributeDataType="String",
                        DeveloperOnlyAttribute=True,
                    ),
                    cognito.SchemaAttribute(
                        Name="projects",
                        Required=False,
                        Mutable=True,
                        AttributeDataType="String",
                        DeveloperOnlyAttribute=True,
                    ),
                ],
                SmsAuthenticationMessage=Ref(p.authentication_sms_text),
                SmsVerificationMessage=Ref(p.verification_sms_text),
                SmsConfiguration=cognito.SmsConfiguration(
                    # The docs have bugs
                    # https://forums.aws.amazon.com/thread.jspa?threadID=250495
                    SnsCallerArn=GetAtt(r.sns_role, "Arn"),
                    ExternalId=Ref("AWS::AccountId"),
                ),
                UsernameAttributes=["email"],
                UserPoolName=Join("", [Ref(p.deployment_id), "-users-MFA"]),
            )
        )

        self.web_client = t.add_resource(
            cognito.UserPoolClient(
                "AuthUserPoolClientWeb",
                DependsOn="AuthMFAUserPool",
                ClientName=Join("", [Ref(p.deployment_id), "-web-MFA"]),
                # RefreshTokenValidity=30,
                GenerateSecret=False,
                UserPoolId=Ref(self.user_pool),
            )
        )
