from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    Join,
    GetAtt,
    Output,
    Ref,
    Template,
)
from .vpc import Vpc
from .security_groups import SecurityGroups
from .parameters import Parameters
from .private_subnets import PrivateSubnets


class Outputs:
    def __init__(
        self,
        t: Template,
        vpc: Vpc,
        sg: SecurityGroups,
        p: Parameters,
        ps: PrivateSubnets,
    ):
        t.add_output(
            [
                Output(
                    "VPCRef",
                    Description="The VPC",
                    Value=Ref(vpc.vpc),
                    Export=Export(name=Join("", [Ref(p.deployment_id), "-VPCRef"])),
                ),
                Output(
                    "VPCCidrBlock",
                    Description="The VPC CIDR block",
                    Value=Ref(p.vpc_cidr),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-VPCCidrBlock"])
                    ),
                ),
                Output(
                    "PrimaryPrivateSubnetRef",
                    Description="The primary private subnet in the VPC",
                    Value=Ref(ps.primary_private_subnet),
                    Export=Export(
                        name=Join(
                            "", [Ref(p.deployment_id), "-PrimaryPrivateSubnetRef"]
                        )
                    ),
                ),
                Output(
                    "SecondaryPrivateSubnetRef",
                    Description="The secondary private subnet in the VPC",
                    Value=Ref(ps.secondary_private_subnet),
                    Export=Export(
                        name=Join(
                            "", [Ref(p.deployment_id), "-SecondaryPrivateSubnetRef"]
                        )
                    ),
                ),
                Output(
                    "DefaultSecurityGroupId",
                    Description="The ID of the security group that was automatically "
                    "created for the VPC",
                    Value=sg.default_sg_id,
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-DefaultSecurityGroupId"])
                    ),
                ),
                Output(
                    "LocalIncomingConnectionSecurityGroupId",
                    Description="The ID of the security group w local inbound access",
                    Value=GetAtt(sg.local_incoming_connections_sg, "GroupId"),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-LocalIncomingConnectionSecurityGroupId",
                            ],
                        )
                    ),
                ),
                Output(
                    "EcrIncomingConnectionSecurityGroupId",
                    Description="The ID of the security group w ECR inbound access",
                    Value=GetAtt(sg.ecr_incoming_connections_sg, "GroupId"),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-EcrIncomingConnectionSecurityGroupId",
                            ],
                        )
                    ),
                ),
                Output(
                    "LocalOutgoingConnectionSecurityGroupId",
                    Description="The ID of the security group w local outbound access",
                    Value=GetAtt(sg.local_outgoing_connections_sg, "GroupId"),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-LocalOutgoingConnectionSecurityGroupId",
                            ],
                        )
                    ),
                ),
                Output(
                    "NatOutgoingConnectionSecurityGroupId",
                    Description="The ID of the security group w NAT outbound access",
                    Value=GetAtt(sg.nat_outgoing_connections_sg, "GroupId"),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-NatOutgoingConnectionSecurityGroupId",
                            ],
                        )
                    ),
                ),
                Output(
                    "BastionSecurityGroupId",
                    Description="The ID of the security group for bastion hosts",
                    Value=GetAtt(sg.bastion_sg, "GroupId"),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-BastionGroupId",
                            ],
                        )
                    ),
                ),
            ]
        )
