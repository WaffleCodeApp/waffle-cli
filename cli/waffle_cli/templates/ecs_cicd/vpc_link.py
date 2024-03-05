from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
    apigateway,
    ec2,
    elasticloadbalancingv2,
)
from .parameters import Parameters
from .conditions import Conditions
from .alb import Alb
from .cicd_security_groups import CicdSecurityGroups


class VpcLink:
    nlb: elasticloadbalancingv2.LoadBalancer
    vpc_link: apigateway.VpcLink

    def __init__(
        self, t: Template, p: Parameters, c: Conditions, a: Alb, csg: CicdSecurityGroups
    ):
        nlb_security_group = t.add_resource(
            ec2.SecurityGroup(
                "NLBSecurityGroup",
                GroupName=Join(
                    "",
                    [Ref(p.deployment_id), "-", Ref(p.pipeline_id), " for NLB"],
                ),
                SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                        CidrIp="0.0.0.0/0",
                        FromPort=1,
                        ToPort=65535,
                        IpProtocol="tcp",
                    ),
                ],
                SecurityGroupEgress=[
                    ec2.SecurityGroupRule(
                        SourceSecurityGroupId=GetAtt(csg.alb_security_group, "GroupId"),
                        FromPort=1,
                        ToPort=65535,
                        IpProtocol="tcp",
                    )
                ],
                GroupDescription="From anywhere to the NLB",
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

        self.nlb = t.add_resource(
            elasticloadbalancingv2.LoadBalancer(
                "NetworkLoadBalancer",
                Scheme="internal",
                Type="network",
                Subnets=[
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
                SecurityGroups=[Ref(csg.alb_security_group), Ref(nlb_security_group)],
            )
        )

        target_group = t.add_resource(
            elasticloadbalancingv2.TargetGroup(
                "NLBTargetGroup",
                HealthCheckIntervalSeconds="80",
                HealthCheckProtocol="HTTP",
                # NOTE: healthcheck path hardcoded:
                HealthCheckPath="/health_check",
                HealthCheckTimeoutSeconds="50",
                HealthyThresholdCount="2",
                Matcher=elasticloadbalancingv2.Matcher(HttpCode="200-299"),
                # NOTE: service port hardcoded:
                Port=80,
                Protocol="TCP",
                TargetType="alb",
                UnhealthyThresholdCount="5",
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
                Targets=[
                    elasticloadbalancingv2.TargetDescription(Id=Ref(a.alb), Port=80)
                ],
            )
        )

        # listener =
        t.add_resource(
            elasticloadbalancingv2.Listener(
                "NLBListener",
                Port=80,
                Protocol="TCP",
                LoadBalancerArn=Ref(self.nlb),
                DefaultActions=[
                    elasticloadbalancingv2.Action(
                        Type="forward", TargetGroupArn=Ref(target_group)
                    )
                ],
            )
        )

        self.vpc_link = t.add_resource(
            apigateway.VpcLink(
                "NlbVpcLink",
                Name=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                        "-NlbVpcLink",
                    ],
                ),
                TargetArns=[Ref(self.nlb)],
            )
        )
