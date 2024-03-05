from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    elasticloadbalancingv2,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions
from .cicd_security_groups import CicdSecurityGroups


class Alb:
    alb: elasticloadbalancingv2.LoadBalancer
    target_group: elasticloadbalancingv2.TargetGroup
    path: Join
    listener: elasticloadbalancingv2.Listener

    def __init__(
        self, t: Template, p: Parameters, c: Conditions, csg: CicdSecurityGroups
    ):
        self.alb = t.add_resource(
            elasticloadbalancingv2.LoadBalancer(
                "ApplicationLoadBalancer",
                Scheme="internal",
                IpAddressType="ipv4",
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
                Type="application",
                SecurityGroups=[Ref(csg.alb_security_group)],
            )
        )

        self.target_group = t.add_resource(
            elasticloadbalancingv2.TargetGroup(
                "ALBTargetGroup",
                HealthCheckIntervalSeconds="80",
                HealthCheckProtocol="HTTP",
                # NOTE: healthcheck path hardcoded:
                HealthCheckPath="/health_check",
                HealthCheckTimeoutSeconds="50",
                HealthyThresholdCount="2",
                Matcher=elasticloadbalancingv2.Matcher(HttpCode="200-299"),
                # NOTE: service port hardcoded:
                Port=80,
                Protocol="HTTP",
                TargetType="ip",
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
                TargetGroupAttributes=[
                    elasticloadbalancingv2.TargetGroupAttribute(
                        Key="deregistration_delay.timeout_seconds", Value="60"
                    )
                ],
            )
        )

        self.listener = t.add_resource(
            elasticloadbalancingv2.Listener(
                "ALBListener",
                Port=80,
                Protocol="HTTP",
                LoadBalancerArn=Ref(self.alb),
                DefaultActions=[
                    elasticloadbalancingv2.Action(
                        Type="forward", TargetGroupArn=Ref(self.target_group)
                    )
                ],
            )
        )

        # self.path = Join("", ["/", Ref(p.deployment_id), "-", Ref(p.pipeline_id), "/*"])

        # t.add_resource(
        #     elasticloadbalancingv2.ListenerRule(
        #         "ALBListenerRule",
        #         ListenerArn=Ref(listener),
        #         Conditions=[
        #             elasticloadbalancingv2.Condition(
        #                 Field="path-pattern", Values=[self.path]
        #             )
        #         ],
        #         Actions=[
        #             elasticloadbalancingv2.ListenerRuleAction(
        #                 Type="forward", TargetGroupArn=Ref(self.target_group)
        #             )
        #         ],
        #         Priority="1",
        #     )
        # )
