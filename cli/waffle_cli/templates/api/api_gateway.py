from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    apigateway,
    Template,
)

from .parameters import Parameters


class ApiGateway:
    api: apigateway.RestApi
    domain_name: apigateway.DomainName
    root_method_name: str = "RootMethod"

    def __init__(self, t: Template, p: Parameters):
        self.api = t.add_resource(
            apigateway.RestApi(
                "Api",
                Description="API gateway for the backend services",
                Name=Join("", [Ref(p.deployment_id), "-API"]),
                EndpointConfiguration=apigateway.EndpointConfiguration(
                    Types=["REGIONAL"]
                ),
                BinaryMediaTypes=["multipart/form-data"],
            )
        )

        self.domain_name = t.add_resource(
            apigateway.DomainName(
                "ApiDomainName",
                DomainName=Join(
                    "",
                    [
                        Ref(p.api_subdomain),
                        ".",
                        Ref(p.full_domain_name),
                    ],
                ),
                CertificateArn=Ref(p.generic_certificate_arn),
            )
        )

        t.add_resource(
            apigateway.BasePathMapping(
                "ApiBasePathMapping",
                RestApiId=Ref(self.api),
                DomainName=Ref(self.domain_name),
            )
        )

        t.add_resource(
            apigateway.Method(
                self.root_method_name,
                AuthorizationType="NONE",
                HttpMethod="ANY",
                Integration=apigateway.Integration(Type="MOCK"),
                ResourceId=GetAtt(self.api, "RootResourceId"),
                RestApiId=Ref(self.api),
            )
        )
