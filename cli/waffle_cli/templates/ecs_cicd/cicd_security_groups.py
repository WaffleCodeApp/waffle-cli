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
from .security_groups import SecurityGroups


class CicdSecurityGroups:
    alb_security_group: ec2.SecurityGroup
    instance_security_group: ec2.SecurityGroup

    def __init__(self, t: Template, p: Parameters, c: Conditions, sg: SecurityGroups):
        self.alb_security_group = t.add_resource(
            ec2.SecurityGroup(
                "ALBSecurityGroup",
                GroupName=Join(
                    "",
                    [Ref(p.deployment_id), "-", Ref(p.pipeline_id), " for ALB"],
                ),
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        SourceSecurityGroupId=If(
                            c.custom_local_outgoing_connections_sg,
                            Ref(p.local_outgoing_connection_security_group_id),
                            ImportValue(
                                Join(
                                    "",
                                    [
                                        Ref(p.deployment_id),
                                        "-LocalOutgoingConnectionSecurityGroupId",
                                    ],
                                )
                            ),
                        ),
                        IpProtocol="-1",
                    ),
                    # ec2.SecurityGroupRule(
                    #     SourceSecurityGroupId=Ref(parameters["BastionSecurityGroupID"]),
                    #     IpProtocol="-1",
                    # ),
                    ec2.SecurityGroupRule(
                        SourceSecurityGroupId=Ref(sg.alb_security_group),
                        IpProtocol="-1",
                    ),
                    ec2.SecurityGroupRule(
                        IpProtocol="-1",
                        CidrIp=If(
                            c.custom_vpc_cidr_block,
                            Ref(p.vpc_cidr_block),
                            ImportValue(
                                Join(
                                    "",
                                    [
                                        Ref(p.deployment_id),
                                        "-VPCCidrBlock",
                                    ],
                                )
                            ),
                        ),
                    ),
                ],
                GroupDescription="From backend SG, trough ALB, to instance",
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

        t.add_resource(
            ec2.SecurityGroupEgress(
                "AccessSgEgressToAlb",
                Description="Outgoing from Access to ALB SG",
                IpProtocol="tcp",
                DestinationSecurityGroupId=Ref(self.alb_security_group),
                GroupId=Ref(sg.alb_security_group),
                FromPort=80,
                ToPort=80,
            )
        )

        self.instance_security_group = t.add_resource(
            ec2.SecurityGroup(
                "InstanceSecurityGroup",
                GroupName=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                        " for the instance",
                    ],
                ),
                GroupDescription="From ALB, through instance, to outside",
                SecurityGroupIngress=[
                    # NOTE: bastion hosts are handled in the service below
                    ec2.SecurityGroupRule(
                        SourceSecurityGroupId=Ref(self.alb_security_group),
                        IpProtocol="-1",
                    ),
                    # ec2.SecurityGroupRule(
                    #     SourceSecurityGroupId=Ref(parameters["BastionSecurityGroupID"]),
                    #     IpProtocol="-1",
                    # ),
                ],
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
