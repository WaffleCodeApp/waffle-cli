from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    route53,
    Template,
)
from troposphere.validators import (  # pyright: ignore[reportMissingTypeStubs]
    route53 as route53_validator,
)
from .parameters import Parameters
from .distribution import Distribution


class Routes:
    def __init__(self, t: Template, p: Parameters, d: Distribution):
        t.add_resource(
            route53.RecordSetType(
                "FrontendRecordSet",
                HostedZoneName=Join(
                    "",
                    [
                        Ref(p.full_domain_name),
                        ".",
                    ],
                ),
                Comment=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                    ],
                ),
                Name=Join(
                    "", [Ref(p.web_subdomain), ".", Ref(p.full_domain_name), "."]
                ),
                Type="A",
                AliasTarget=route53_validator.AliasTarget(
                    DNSName=GetAtt(d.distribution, "DomainName"),
                    # For HostedZoneId checkout this:
                    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html
                    HostedZoneId="Z2FDTNDATAQYW2",
                ),
            )
        )
