from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter
    allow_admin_create_user_only: Parameter

    def __init__(self, t: Template) -> None:
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        self.allow_admin_create_user_only = t.add_parameter(
            Parameter(
                "AllowAdminCreateUserOnly",
                Description="Only admin can create new users?",
                Type="String",
                AllowedValues=["True", "False"],
                Default="True",
            )
        )
