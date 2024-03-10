from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter
    invitation_sms_text: Parameter
    authentication_sms_text: Parameter
    verification_sms_text: Parameter
    create_userpool: Parameter

    def __init__(self, t: Template) -> None:
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        self.create_userpool = t.add_parameter(
            Parameter(
                "CreateUserpool",
                Description="Is manual approval required before deployment?",
                Type="String",
                AllowedValues=["True", "False"],
                Default="True",
            )
        )

        self.invitation_sms_text = t.add_parameter(
            Parameter(
                "AuthUserInvitationSMSText",
                Description="Text to be used in invitation SMS messages",
                Type="String",
                Default="Waffle: {username}, your invitation code is {####}",
            )
        )

        self.authentication_sms_text = t.add_parameter(
            Parameter(
                "AuthUserAuthenticationSMSText",
                Description="Text to be used in login SMS messages",
                Type="String",
                Default="Waffle: {username}, your verification code is {####}",
            )
        )

        self.verification_sms_text = t.add_parameter(
            Parameter(
                "AuthUserVerificationSMSText",
                Description="Text to be used in verification SMS messages",
                Type="String",
                Default="Waffle: {username}, your verification code is {####}",
            )
        )
