from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    ec2,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions


class SecurityGroups:
    alb_security_group: ec2.SecurityGroup

    def __init__(self, t: Template, p: Parameters, c: Conditions):
        self.alb_security_group = t.add_resource(
            ec2.SecurityGroup(
                "AccessSecurityGroup",
                GroupDescription=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                        " for internal access",
                    ],
                ),
                VpcId=If(
                    c.custom_vpc_ref,
                    Ref(p.vpc_ref),
                    ImportValue(
                        Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-VPCRef",
                            ],
                        )
                    ),
                ),
            )
        )
