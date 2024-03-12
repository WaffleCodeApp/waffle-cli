from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter

    def __init__(self, t: Template):
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )
