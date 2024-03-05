from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    ec2,
    Join,
    Ref,
    Tags,
    Template,
)
from .parameters import Parameters


class Vpc:
    vpc: ec2.VPC
    internet_gateway: ec2.InternetGateway

    def __init__(self, t: Template, p: Parameters) -> None:
        self.vpc = t.add_resource(
            ec2.VPC(
                "VPC",
                CidrBlock=Ref(p.vpc_cidr),
                EnableDnsSupport=True,
                EnableDnsHostnames=True,
                InstanceTenancy="default",
                Tags=Tags(Name=Join("", [Ref(p.deployment_id), "-VPC"])),
            )
        )

        dhcp_options: ec2.DHCPOptions = t.add_resource(
            ec2.DHCPOptions(
                "DHCPOptions",
                DomainName=Join("", [Ref("AWS::Region"), ".compute.internal"]),
                DomainNameServers=["AmazonProvidedDNS"],
                Tags=Tags(Name=Join("", [Ref(p.deployment_id), "-DHCPOptions"])),
            )
        )

        t.add_resource(
            ec2.VPCDHCPOptionsAssociation(
                "VPCDHCPOptionsAssociation",
                VpcId=Ref(self.vpc),
                DhcpOptionsId=Ref(dhcp_options),
            )
        )

        self.internet_gateway = t.add_resource(
            ec2.InternetGateway(
                "InternetGateway",
                Tags=Tags(Name=Join("", [Ref(p.deployment_id), "-InternetGateway"])),
            )
        )

        t.add_resource(
            ec2.VPCGatewayAttachment(
                "VPCGatewayAttachment",
                VpcId=Ref(self.vpc),
                InternetGatewayId=Ref(self.internet_gateway),
            )
        )
