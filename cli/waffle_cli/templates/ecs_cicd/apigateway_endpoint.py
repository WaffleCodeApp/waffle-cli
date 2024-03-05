from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
    apigateway,
)
from .parameters import Parameters
from .conditions import Conditions
from .vpc_link import VpcLink
from .alb import Alb


class ApiGatewayEndpoint:
    def __init__(self, t: Template, p: Parameters, c: Conditions, v: VpcLink, a: Alb):
        resource = t.add_resource(
            apigateway.Resource(
                "NLBApiGatewayResource",
                RestApiId=If(
                    c.custom_restapi_id,
                    Ref(p.restapi_id),
                    ImportValue(
                        Join(
                            "",
                            [Ref(p.deployment_id), "-RestApiId"],
                        )
                    ),
                ),
                ParentId=If(
                    c.custom_root_resource_id,
                    Ref(p.root_resource_id),
                    ImportValue(
                        Join(
                            "",
                            [Ref(p.deployment_id), "-RootResourceId"],
                        )
                    ),
                ),
                PathPart=Ref(p.pipeline_id),
            )
        )

        proxy_resource = t.add_resource(
            apigateway.Resource(
                "NLBApiGatewayProxyResource",
                RestApiId=If(
                    c.custom_restapi_id,
                    Ref(p.restapi_id),
                    ImportValue(
                        Join(
                            "",
                            [Ref(p.deployment_id), "-RestApiId"],
                        )
                    ),
                ),
                ParentId=Ref(resource),
                PathPart="{proxy+}",
            )
        )

        # method =
        t.add_resource(
            apigateway.Method(
                "NLBApiGatewayMethod",
                RestApiId=If(
                    c.custom_restapi_id,
                    Ref(p.restapi_id),
                    ImportValue(
                        Join(
                            "",
                            [Ref(p.deployment_id), "-RestApiId"],
                        )
                    ),
                ),
                ResourceId=Ref(proxy_resource),
                HttpMethod="ANY",
                AuthorizationType="NONE",
                ApiKeyRequired=True,
                Integration=apigateway.Integration(
                    Type="HTTP_PROXY",
                    IntegrationHttpMethod="ANY",
                    ConnectionType="VPC_LINK",
                    ConnectionId=Ref(v.vpc_link),
                    RequestParameters={
                        "integration.request.path.proxy": "method.request.path.proxy"
                    },
                    Uri=Join(
                        "",
                        ["http://", GetAtt(v.nlb, "DNSName"), "/{proxy}"],
                    ),
                ),
                RequestParameters={"method.request.path.proxy": "true"},
            )
        )
