from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Ref,
    apigateway,
    Template,
)

from .api_gateway import ApiGateway


class Deployment:
    deployment_name: str = "DeploymentProd"
    stage_name: str = "Prod"

    def __init__(self, t: Template, agw: ApiGateway):
        t.add_resource(
            apigateway.Deployment(
                self.deployment_name,
                DependsOn=[
                    agw.root_method_name,
                ],
                RestApiId=Ref(agw.api),
                StageName=self.stage_name,
            )
        )
