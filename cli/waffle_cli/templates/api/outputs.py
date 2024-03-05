from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    GetAtt,
    Join,
    Output,
    Ref,
    Template,
    ssm,
)
from .parameters import Parameters
from .api_gateway import ApiGateway
from .deployment import Deployment


class Outputs:
    def __init__(self, t: Template, agw: ApiGateway, p: Parameters, d: Deployment):
        t.add_output(
            [
                Output(
                    "RestApiId",
                    Value=Ref(agw.api),
                    Export=Export(name=Join("", [Ref(p.deployment_id), "-RestApiId"])),
                ),
                Output(
                    "RootResourceId",
                    Value=GetAtt(agw.api, "RootResourceId"),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-RootResourceId"])
                    ),
                ),
                Output(
                    "ApiProtocol",
                    Value="https://",
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-ApiProtocol"])
                    ),
                ),
                Output(
                    "ApiHost",
                    Value=Ref(agw.domain_name),
                    Export=Export(name=Join("", [Ref(p.deployment_id), "-ApiHost"])),
                ),
                Output(
                    "ApiStage",
                    Value=d.stage_name,
                    Export=Export(name=Join("", [Ref(p.deployment_id), "-ApiStage"])),
                ),
            ]
        )

        t.add_resource(
            ssm.Parameter(
                "ApiGwDomainName",
                Name=Join(
                    "",
                    [
                        "/",
                        Ref(p.deployment_id),
                        "/api/",
                        "hostName",
                    ],
                ),
                Type="String",
                Value=Ref(agw.domain_name),
                Description="The hostname of the api gateway",
            )
        )
