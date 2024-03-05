from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    route53,
    Template,
)
from .parameters import Parameters
from .api_gateway import ApiGateway


class Routes:
    def __init__(self, t: Template, p: Parameters, agw: ApiGateway):
        t.add_resource(
            route53.RecordSetGroup(
                "ApiDNSRecordSet",
                HostedZoneName=Join(
                    "",
                    [
                        Ref(p.full_domain_name),
                        ".",
                    ],
                ),
                Comment="DNS settings of the generic API",
                RecordSets=[
                    route53.RecordSet(
                        AliasTarget=route53.AliasTarget(  # type: ignore
                            DNSName=GetAtt(agw.domain_name, "DistributionDomainName"),
                            HostedZoneId=GetAtt(
                                agw.domain_name, "DistributionHostedZoneId"
                            ),
                            EvaluateTargetHealth=False,
                        ),
                        Name=Join(
                            "",
                            [
                                Ref(p.api_subdomain),
                                ".",
                                Ref(p.full_domain_name),
                                ".",
                            ],
                        ),
                        Type="A",
                    )
                ],
            )
        )
