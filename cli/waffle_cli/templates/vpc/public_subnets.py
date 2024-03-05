from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    Tags,
    ec2,
    Template,
)

from .parameters import Parameters
from .vpc import Vpc


class PublicSubnets:
    primary_nat_gateway: ec2.NatGateway
    secondary_nat_gateway: ec2.NatGateway

    def __init__(self, t: Template, p: Parameters, vpc: Vpc):
        primary_public_subnet = t.add_resource(
            ec2.Subnet(
                "PrimaryPublicSubnet",
                AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
                CidrBlock=Ref(p.primary_public_cidr),
                MapPublicIpOnLaunch=True,
                Tags=Tags(
                    Name=Join(
                        "",
                        [Ref(p.deployment_id), "-PrimaryPublicSubnet"],
                    )
                ),
                VpcId=Ref(vpc.vpc),
            )
        )

        secondary_public_subnet = t.add_resource(
            ec2.Subnet(
                "SecondaryPublicSubnet",
                AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
                CidrBlock=Ref(p.secondary_public_cidr),
                MapPublicIpOnLaunch=True,
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-SecondaryPublicSubnet"])
                ),
                VpcId=Ref(vpc.vpc),
            )
        )

        primary_nat_eip = t.add_resource(
            ec2.EIP(
                "PrimaryNatEip",
                DependsOn="VPCGatewayAttachment",
                Domain="vpc",
                Tags=Tags({"Name": Join("", [Ref(p.deployment_id), "-PrimaryNatEip"])}),
            )
        )

        secondary_nat_eip = t.add_resource(
            ec2.EIP(
                "SecondaryNatEip",
                DependsOn="VPCGatewayAttachment",
                Domain="vpc",
                Tags=Tags(
                    {"Name": Join("", [Ref(p.deployment_id), "-SecondaryNatEip"])}
                ),
            )
        )

        self.primary_nat_gateway = t.add_resource(
            ec2.NatGateway(
                "PrimaryNatGateway",
                DependsOn="VPCGatewayAttachment",
                AllocationId=GetAtt(primary_nat_eip, "AllocationId"),
                SubnetId=Ref(primary_public_subnet),
                Tags=Tags(Name=Join("", [Ref(p.deployment_id), "-PrimaryNatGateway"])),
            )
        )

        self.secondary_nat_gateway = t.add_resource(
            ec2.NatGateway(
                "SecondaryNatGateway",
                DependsOn="VPCGatewayAttachment",
                AllocationId=GetAtt(secondary_nat_eip, "AllocationId"),
                SubnetId=Ref(secondary_public_subnet),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-SecondaryNatGateway"])
                ),
            )
        )

        public_subnet_route_table = t.add_resource(
            ec2.RouteTable(
                "PublicSubnetRouteTable",
                VpcId=Ref(vpc.vpc),
                Tags=Tags(
                    Name=Join("", [Ref(p.deployment_id), "-PublicSubnetRouteTable"])
                ),
            )
        )

        t.add_resource(
            ec2.Route(
                "PublicSubnetRoute",
                RouteTableId=Ref(public_subnet_route_table),
                DestinationCidrBlock="0.0.0.0/0",
                GatewayId=Ref(vpc.internet_gateway),
            )
        )

        t.add_resource(
            ec2.SubnetRouteTableAssociation(
                "PrimaryPublicSubnetRouteTableAssociation",
                SubnetId=Ref(primary_public_subnet),
                RouteTableId=Ref(public_subnet_route_table),
            )
        )

        t.add_resource(
            ec2.SubnetRouteTableAssociation(
                "SecondaryPublicSubnetRouteTableAssociation",
                SubnetId=Ref(secondary_public_subnet),
                RouteTableId=Ref(public_subnet_route_table),
            )
        )
