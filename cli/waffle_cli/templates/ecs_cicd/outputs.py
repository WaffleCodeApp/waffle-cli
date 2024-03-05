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
from .alb import Alb


class Outputs:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        a: Alb,
    ):
        t.add_output(
            [
                Output(
                    "AlbDnsName",
                    Description="The hostname of the deployed application load balancer",
                    Value=GetAtt(a.alb, "DNSName"),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                                "-AlbDnsName",
                            ],
                        )
                    ),
                ),
            ]
        )

        t.add_resource(
            ssm.Parameter(
                "AlbDnsNameParameter",
                Name=Join(
                    "",
                    [
                        "/",
                        Ref(p.deployment_id),
                        "/ecs/",
                        Ref(p.pipeline_id),
                        "/albDnsName",
                    ],
                ),
                Type="String",
                Value=GetAtt(a.alb, "DNSName"),
                Description="The hostname of the deployed application load balancer",
            )
        )
