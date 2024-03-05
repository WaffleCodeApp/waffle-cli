from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Ref,
    apigateway,
    Template,
)

from .api_gateway import ApiGateway
from .deployment import Deployment


class UsagePlan:
    def __init__(self, t: Template, agw: ApiGateway, d: Deployment):
        t.add_resource(
            apigateway.UsagePlan(
                "ApigatewayUsagePlan",
                DependsOn=d.deployment_name,
                ApiStages=[apigateway.ApiStage(ApiId=Ref(agw.api), Stage="Prod")],
                Description="Generic ApiKey usage plan for the backend services",
            )
        )
