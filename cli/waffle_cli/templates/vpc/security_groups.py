from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    ec2,
    Tags,
    Template,
)

from .parameters import Parameters
from .vpc import Vpc


class SecurityGroups:
    local_incoming_connections_sg: ec2.SecurityGroup
    ecr_incoming_connections_sg: ec2.SecurityGroup
    local_outgoing_connections_sg: ec2.SecurityGroup
    nat_outgoing_connections_sg: ec2.SecurityGroup
    default_sg_id: GetAtt

    def __init__(self, t: Template, p: Parameters, vpc: Vpc):
        self.bastion_sg = t.add_resource(
            ec2.SecurityGroup(
                "BastionSG",
                GroupDescription="Intended for bastion hosts",
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/0",
                        FromPort=1,
                        ToPort=65535,
                        IpProtocol="tcp",
                    ),
                ],
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join(
                        "",
                        [
                            Ref(p.deployment_id),
                            "-bastion",
                        ],
                    )
                ),
            )
        )

        self.local_incoming_connections_sg = t.add_resource(
            ec2.SecurityGroup(
                "LocalIncomingConnectionSG",
                GroupDescription="Local incoming connections",
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        CidrIp=GetAtt(vpc.vpc, "CidrBlock"),
                        FromPort=1,
                        ToPort=65535,
                        IpProtocol="tcp",
                    ),
                    ec2.SecurityGroupRule(
                        SourceSecurityGroupId=GetAtt(self.bastion_sg, "GroupId"),
                        FromPort=1,
                        ToPort=65535,
                        IpProtocol="tcp",
                    ),
                ],
                SecurityGroupEgress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/32", FromPort=1, ToPort=1, IpProtocol="tcp"
                    )
                ],
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join(
                        "",
                        [
                            Ref(p.deployment_id),
                            "-localIncomingConnection",
                        ],
                    )
                ),
            )
        )

        self.ecr_incoming_connections_sg = t.add_resource(
            ec2.SecurityGroup(
                "EcrIncomingConnectionSG",
                GroupDescription="Ecr incoming connections",
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/0", FromPort=80, ToPort=80, IpProtocol="tcp"
                    ),
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/0", FromPort=443, ToPort=443, IpProtocol="tcp"
                    ),
                ],
                SecurityGroupEgress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/32", FromPort=1, ToPort=1, IpProtocol="tcp"
                    )
                ],
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join(
                        "",
                        [
                            Ref(p.deployment_id),
                            "-ecrIncomingConnection",
                        ],
                    )
                ),
            )
        )

        self.local_outgoing_connections_sg = t.add_resource(
            ec2.SecurityGroup(
                "LocalOutgoingConnectionSG",
                GroupDescription="Local outgoing connections",
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/32", FromPort=1, ToPort=1, IpProtocol="tcp"
                    )
                ],
                SecurityGroupEgress=[
                    ec2.SecurityGroupRule(
                        CidrIp=GetAtt(vpc.vpc, "CidrBlock"),
                        FromPort=1,
                        ToPort=65535,
                        IpProtocol="tcp",
                    )
                    # NOTE: add VPC gateway endpoint egress rules here
                ],
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-localOutgoingConnection"])
                ),
            )
        )

        self.nat_outgoing_connections_sg = t.add_resource(
            ec2.SecurityGroup(
                "NatOutgoingConnectionSG",
                GroupDescription="NAT outgoing connections",
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/32", FromPort=1, ToPort=1, IpProtocol="tcp"
                    )
                ],
                SecurityGroupEgress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/0", FromPort=1, ToPort=65535, IpProtocol="tcp"
                    )
                ],
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-natOutgoingConnection"])
                ),
            )
        )

        self.default_sg_id = GetAtt(vpc.vpc, "DefaultSecurityGroup")
