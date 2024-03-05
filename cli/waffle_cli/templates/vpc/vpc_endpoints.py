from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Join,
    Ref,
    ec2,
    Template,
)

from .security_groups import SecurityGroups
from .vpc import Vpc
from .private_subnets import PrivateSubnets


class VpcEndpoints:
    def __init__(self, t: Template, sg: SecurityGroups, vpc: Vpc, psn: PrivateSubnets):
        t.add_resource(
            ec2.VPCEndpoint(
                "EcrDkrVpcEndpoint",
                ServiceName=Join(
                    "", ["com.amazonaws.", Ref("AWS::Region"), ".ecr.dkr"]
                ),
                VpcEndpointType="Interface",
                PrivateDnsEnabled=True,
                SecurityGroupIds=[
                    Ref(sg.ecr_incoming_connections_sg),
                    Ref(sg.local_outgoing_connections_sg),
                    Ref(sg.nat_outgoing_connections_sg),
                    sg.default_sg_id,
                ],
                SubnetIds=[
                    Ref(psn.primary_private_subnet),
                    Ref(psn.secondary_private_subnet),
                ],
                VpcId=Ref(vpc.vpc),
            )
        )

        t.add_resource(
            ec2.VPCEndpoint(
                "DeploymentEcrApiVpcEndpoint",
                ServiceName=Join(
                    "", ["com.amazonaws.", Ref("AWS::Region"), ".ecr.api"]
                ),
                VpcEndpointType="Interface",
                PrivateDnsEnabled=True,
                SecurityGroupIds=[
                    Ref(sg.ecr_incoming_connections_sg),
                    Ref(sg.local_outgoing_connections_sg),
                    Ref(sg.nat_outgoing_connections_sg),
                    sg.default_sg_id,
                ],
                SubnetIds=[
                    Ref(psn.primary_private_subnet),
                    Ref(psn.secondary_private_subnet),
                ],
                VpcId=Ref(vpc.vpc),
            )
        )

        t.add_resource(
            ec2.VPCEndpoint(
                "S3VpcEndpoint",
                ServiceName=Join("", ["com.amazonaws.", Ref("AWS::Region"), ".s3"]),
                VpcEndpointType="Gateway",
                VpcId=Ref(vpc.vpc),
                RouteTableIds=[
                    Ref(psn.primary_private_subnet_route_table),
                    Ref(psn.secondary_private_subnet_route_table),
                ],
            )
        )

        t.add_resource(
            ec2.VPCEndpoint(
                "LogsVpcEndpoint",
                ServiceName=Join("", ["com.amazonaws.", Ref("AWS::Region"), ".logs"]),
                VpcEndpointType="Interface",
                PrivateDnsEnabled=True,
                SecurityGroupIds=[
                    Ref(sg.ecr_incoming_connections_sg),
                    Ref(sg.local_outgoing_connections_sg),
                    Ref(sg.nat_outgoing_connections_sg),
                    sg.default_sg_id,
                ],
                SubnetIds=[
                    Ref(psn.primary_private_subnet),
                    Ref(psn.secondary_private_subnet),
                ],
                VpcId=Ref(vpc.vpc),
            )
        )

        t.add_resource(
            ec2.VPCEndpoint(
                "DynamoDbVpcEndpoint",
                ServiceName=Join(
                    "", ["com.amazonaws.", Ref("AWS::Region"), ".dynamodb"]
                ),
                VpcEndpointType="Gateway",
                VpcId=Ref(vpc.vpc),
                RouteTableIds=[
                    Ref(psn.primary_private_subnet_route_table),
                    Ref(psn.secondary_private_subnet_route_table),
                ],
            )
        )
