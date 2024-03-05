from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    ecs,
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions
from .ecr_repositoty import EcrRepositoty
from .alb import Alb
from .cicd_security_groups import CicdSecurityGroups
from .ecs_task import EcsTask


class EcsService:
    cluster: ecs.Cluster
    service: ecs.Service

    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        er: EcrRepositoty,
        alb: Alb,
        csg: CicdSecurityGroups,
        et: EcsTask,
    ):
        self.cluster = t.add_resource(ecs.Cluster("Cluster"))

        self.service = t.add_resource(
            ecs.Service(
                "Service",
                DependsOn=["TaskDefinition", "Repo", "ALBListener"],
                Cluster=GetAtt(self.cluster, "Arn"),
                DeploymentConfiguration=ecs.DeploymentConfiguration(
                    MaximumPercent="200", MinimumHealthyPercent="50"
                ),
                # NOTE: somehow eariler deployments use to work without this,
                # but new deployments fail with an issue similar to this:
                # https://github.com/aws/amazon-ecs-agent/issues/1266
                # Role=Ref(resources["ServiceRole"]),
                DesiredCount=Ref(p.instance_count),
                HealthCheckGracePeriodSeconds=60,
                LaunchType="FARGATE",
                LoadBalancers=[
                    ecs.LoadBalancer(
                        ContainerName=Ref(er.repository),
                        ContainerPort=80,
                        TargetGroupArn=Ref(alb.target_group),
                    )
                ],
                # NOTE:
                # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
                NetworkConfiguration=ecs.NetworkConfiguration(
                    AwsvpcConfiguration=ecs.AwsvpcConfiguration(
                        AssignPublicIp="DISABLED",
                        SecurityGroups=[
                            Ref(csg.instance_security_group),
                            If(
                                c.custom_ecr_incoming_connections_sg,
                                Ref(p.ecr_incoming_connection_security_group_id),
                                ImportValue(
                                    Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-EcrIncomingConnectionSecurityGroupId",
                                        ],
                                    )
                                ),
                            ),
                            If(
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
                            If(
                                c.custom_nat_outgoing_connections_sg,
                                Ref(p.nat_outgoing_connection_security_group_id),
                                ImportValue(
                                    Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-NatOutgoingConnectionSecurityGroupId",
                                        ],
                                    )
                                ),
                            ),
                        ],
                        Subnets=[
                            If(
                                c.custom_primary_private_subnet_ref,
                                Ref(p.primary_private_subnet_ref),
                                ImportValue(
                                    Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-PrimaryPrivateSubnetRef",
                                        ],
                                    )
                                ),
                            ),
                            If(
                                c.custom_secondary_private_subnet_ref,
                                Ref(p.secondary_private_subnet_ref),
                                ImportValue(
                                    Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-SecondaryPrivateSubnetRef",
                                        ],
                                    )
                                ),
                            ),
                        ],
                    )
                ),
                SchedulingStrategy="REPLICA",
                ServiceName=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                    ],
                ),
                TaskDefinition=Ref(et.task_definition),
            )
        )
