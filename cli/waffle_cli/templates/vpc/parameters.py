from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]

# from application_logic.entities.deployment_type import DeploymentType


class Parameters:
    deployment_id: Parameter
    # deployment_type: Parameter
    vpc_cidr: Parameter
    primary_private_cidr: Parameter
    secondary_private_cidr: Parameter
    primary_public_cidr: Parameter
    secondary_public_cidr: Parameter

    def __init__(self, t: Template) -> None:
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        # self.deployment_type = t.add_parameter(
        #     Parameter(
        #         "DeploymentType",
        #         Description="[ %s ]"
        #         % " | ".join(
        #             [
        #                 DeploymentType.DEV.value,
        #                 DeploymentType.PROD.value,
        #             ]
        #         ),
        #         Type="String",
        #     )
        # )

        self.vpc_cidr = t.add_parameter(
            Parameter("VPCCidr", Description="VPCCidr", Type="String")
        )

        self.primary_private_cidr = t.add_parameter(
            Parameter(
                "PrimaryPrivateCidr", Description="PrimaryPrivateCidr", Type="String"
            )
        )

        self.secondary_private_cidr = t.add_parameter(
            Parameter(
                "SecondaryPrivateCidr",
                Description="SecondaryPrivateCidr",
                Type="String",
            )
        )

        self.primary_public_cidr = t.add_parameter(
            Parameter(
                "PrimaryPublicCidr", Description="PrimaryPublicCidr", Type="String"
            )
        )

        self.secondary_public_cidr = t.add_parameter(
            Parameter(
                "SecondaryPublicCidr", Description="SecondaryPublicCidr", Type="String"
            )
        )
