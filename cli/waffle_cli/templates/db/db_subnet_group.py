from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    If,
    ImportValue,
    Join,
    Ref,
    rds,
    Template,
)

from .parameters import Parameters
from .conditions import Conditions


class DbSubnetGroup:
    group: rds.DBSubnetGroup

    def __init__(self, t: Template, p: Parameters, c: Conditions):
        self.group = t.add_resource(
            rds.DBSubnetGroup(
                "DbSubnetGroup",
                DBSubnetGroupDescription="Subnets of the DB",
                SubnetIds=[
                    If(
                        c.custom_primary_private_subnet_ref,
                        Ref(p.primary_private_subnet_ref),
                        ImportValue(
                            Join(
                                "",
                                [Ref(p.deployment_id), "-PrimaryPrivateSubnetRef"],
                            )
                        ),
                    ),
                    If(
                        c.custom_secondary_private_subnet_ref,
                        Ref(p.secondary_private_subnet_ref),
                        ImportValue(
                            Join(
                                "",
                                [Ref(p.deployment_id), "-SecondaryPrivateSubnetRef"],
                            )
                        ),
                    ),
                ],
            )
        )
