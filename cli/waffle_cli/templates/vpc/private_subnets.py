from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Join,
    Ref,
    ec2,
    Tags,
    Template,
)


from .parameters import Parameters
from .vpc import Vpc
from .public_subnets import PublicSubnets


class PrivateSubnets:
    primary_private_subnet: ec2.Subnet
    secondary_private_subnet: ec2.Subnet
    primary_private_subnet_route_table: ec2.RouteTable
    secondary_private_subnet_route_table: ec2.RouteTable

    def __init__(self, t: Template, p: Parameters, vpc: Vpc, psn: PublicSubnets):
        self.primary_private_subnet = t.add_resource(
            ec2.Subnet(
                "PrimaryPrivateSubnet",
                # AssignIpv6AddressOnCreation=False,
                AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
                CidrBlock=Ref(p.primary_private_cidr),
                # Ipv6CidrBlock="",
                # 'Ipv6CidrBlock': (basestring, False),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-PrimaryPrivateSubnet"])
                ),
                VpcId=Ref(vpc.vpc),
            )
        )

        self.secondary_private_subnet = t.add_resource(
            ec2.Subnet(
                "SecondaryPrivateSubnet",
                # AssignIpv6AddressOnCreation=False,
                AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
                CidrBlock=Ref(p.secondary_private_cidr),
                # Ipv6CidrBlock="",
                # 'Ipv6CidrBlock': (basestring, False),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-SecondaryPrivateSubnet"])
                ),
                VpcId=Ref(vpc.vpc),
            )
        )

        self.primary_private_subnet_route_table = t.add_resource(
            ec2.RouteTable(
                "PrimaryPrivateSubnetRouteTable",
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join(
                        "", [Ref(p.deployment_id), "-PrimaryPrivateSubnetRouteTable"]
                    )
                ),
            )
        )

        self.secondary_private_subnet_route_table = t.add_resource(
            ec2.RouteTable(
                "SecondaryPrivateSubnetRouteTable",
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join(
                        "",
                        [
                            Ref(p.deployment_id),
                            "-SecondaryPrivateSubnetRouteTable",
                        ],
                    )
                ),
            )
        )

        t.add_resource(
            ec2.Route(
                "PrimaryPrivateSubnetRoute",
                RouteTableId=Ref(self.primary_private_subnet_route_table),
                DestinationCidrBlock="0.0.0.0/0",
                NatGatewayId=Ref(psn.primary_nat_gateway),
            )
        )

        t.add_resource(
            ec2.Route(
                "SecondaryPrivateSubnetRoute",
                RouteTableId=Ref(self.secondary_private_subnet_route_table),
                DestinationCidrBlock="0.0.0.0/0",
                NatGatewayId=Ref(psn.secondary_nat_gateway),
            )
        )

        t.add_resource(
            ec2.SubnetRouteTableAssociation(
                "PrimaryPrivateSubnetRouteTableAssociation",
                SubnetId=Ref(self.primary_private_subnet),
                RouteTableId=Ref(self.primary_private_subnet_route_table),
            )
        )

        t.add_resource(
            ec2.SubnetRouteTableAssociation(
                "SecondaryPrivateSubnetRouteTableAssociation",
                SubnetId=Ref(self.secondary_private_subnet),
                RouteTableId=Ref(self.secondary_private_subnet_route_table),
            )
        )

        primary_private_subnet_nacl = t.add_resource(
            ec2.NetworkAcl(
                "PrimaryPrivateSubnetNACL",
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-PrimaryPrivateSubnetNACL"])
                ),
            )
        )

        secondary_private_subnet_nacl = t.add_resource(
            ec2.NetworkAcl(
                "SecondaryPrivateSubnetNACL",
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-SecondaryPrivateSubnetNACL"])
                ),
            )
        )

        t.add_resource(
            ec2.NetworkAclEntry(
                "PrimaryPrivateSubnetNACLEntryInbound",
                CidrBlock="0.0.0.0/0",
                Egress=False,
                NetworkAclId=Ref(primary_private_subnet_nacl),
                Protocol=-1,
                RuleAction="allow",
                RuleNumber=100,
            )
        )

        t.add_resource(
            ec2.NetworkAclEntry(
                "PrimaryPrivateSubnetNACLEntryOutbound",
                CidrBlock="0.0.0.0/0",
                Egress=True,
                NetworkAclId=Ref(primary_private_subnet_nacl),
                Protocol=-1,
                RuleAction="allow",
                RuleNumber=100,
            )
        )

        t.add_resource(
            ec2.NetworkAclEntry(
                "SecondaryPrivateSubnetNACLEntryInbound",
                CidrBlock="0.0.0.0/0",
                Egress=False,
                NetworkAclId=Ref(secondary_private_subnet_nacl),
                Protocol=-1,
                RuleAction="allow",
                RuleNumber=100,
            )
        )

        t.add_resource(
            ec2.NetworkAclEntry(
                "SecondaryPrivateSubnetNACLEntryOutbound",
                CidrBlock="0.0.0.0/0",
                Egress=True,
                NetworkAclId=Ref(secondary_private_subnet_nacl),
                Protocol=-1,
                RuleAction="allow",
                RuleNumber=100,
            )
        )

        t.add_resource(
            ec2.SubnetNetworkAclAssociation(
                "PrimaryPrivateSubnetNACLAssociation",
                NetworkAclId=Ref(primary_private_subnet_nacl),
                SubnetId=Ref(self.primary_private_subnet),
            )
        )

        t.add_resource(
            ec2.SubnetNetworkAclAssociation(
                "SecondaryPrivateSubnetNACLAssociation",
                NetworkAclId=Ref(secondary_private_subnet_nacl),
                SubnetId=Ref(self.secondary_private_subnet),
            )
        )
