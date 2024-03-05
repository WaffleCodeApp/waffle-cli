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
from .roles import Roles
from .cicd_roles import CicdRoles
from .ecr_repositoty import EcrRepositoty
from .secret import Secret
from .logging_group import LoggingGroup


class EcsTask:
    task_definition: ecs.TaskDefinition

    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        r: Roles,
        cr: CicdRoles,
        er: EcrRepositoty,
        s: Secret,
        lg: LoggingGroup,
    ):
        self.task_definition = t.add_resource(
            ecs.TaskDefinition(
                "TaskDefinition",
                DependsOn="Repo",
                Family=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                    ],
                ),
                NetworkMode="awsvpc",
                RequiresCompatibilities=["FARGATE"],
                # Cpu="256",
                # Memory="512",
                Cpu=Ref(p.ecs_task_cpu),
                Memory=Ref(p.ecs_task_ram),
                ExecutionRoleArn=GetAtt(cr.execution_role, "Arn"),
                TaskRoleArn=GetAtt(r.task_role, "Arn"),
                ContainerDefinitions=[
                    ecs.ContainerDefinition(
                        Name=Ref(er.repository),
                        Image=Join("", [er.uri, ":latest"]),
                        PortMappings=[
                            ecs.PortMapping(
                                ContainerPort=80,
                                HostPort=80,
                                Protocol="tcp",
                            )
                        ],
                        Essential=True,
                        # WorkingDirectory="/usr/src/app",
                        Environment=[
                            # passing runtime ENV vars to the container
                            ecs.Environment(
                                Name="AWS_REGION", Value=Ref("AWS::Region")
                            ),
                            ecs.Environment(
                                Name="DEPLOYMENT_SECRET_ARN",
                                Value=If(
                                    c.custom_deployment_secret_arn,
                                    Ref(p.deployment_secret_arn),
                                    ImportValue(
                                        Join(
                                            "",
                                            [
                                                Ref(p.deployment_id),
                                                "-DeploymentSecretArn",
                                            ],
                                        )
                                    ),
                                ),
                            ),
                            ecs.Environment(
                                Name="ALERTS_TOPIC_ARN",
                                Value=If(
                                    c.custom_alerts_sns_ref,
                                    Ref(p.alerts_sns_ref),
                                    ImportValue(
                                        Join(
                                            "",
                                            [
                                                Ref(p.deployment_id),
                                                "-AlertsSnsTopicRef",
                                            ],
                                        )
                                    ),
                                ),
                            ),
                            ecs.Environment(
                                Name="SERVICE_SECRET_ARN",
                                Value=Ref(s.secret),
                            ),
                            ecs.Environment(
                                Name="RUNTIME_JSON", Value=Ref(p.runtime_json)
                            ),
                            ecs.Environment(
                                Name="DEPLOYMENT_ID",
                                Value=Ref(p.deployment_id),
                            ),
                            ecs.Environment(
                                Name="DEPLOYMENT_TYPE",
                                Value=Ref(p.deployment_type),
                            ),
                            ecs.Environment(
                                Name="PIPELINE_ID",
                                Value=Ref(p.pipeline_id),
                            ),
                        ],
                        HealthCheck=ecs.HealthCheck(
                            Command=[
                                "CMD-SHELL",
                                "curl -f http://localhost:80/health_check || exit 1",
                            ],
                            StartPeriod=60,
                        ),
                        LogConfiguration=ecs.LogConfiguration(
                            LogDriver="awslogs",
                            Options={
                                "awslogs-group": Ref(lg.group),
                                "awslogs-region": Ref("AWS::Region"),
                                "awslogs-stream-prefix": Ref(p.pipeline_id),
                            },
                        ),
                    )
                ],
            )
        )
