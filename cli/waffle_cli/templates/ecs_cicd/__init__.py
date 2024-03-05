from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .secret import Secret
from .security_groups import SecurityGroups
from .roles import Roles
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .artifacts_bucket_policy import ArtifactsBucketPolicy
from .ecr_repositoty import EcrRepositoty
from .cicd_security_groups import CicdSecurityGroups
from .alb import Alb
from .alb_alarms import AlbAlarms
from .logging_group import LoggingGroup
from .codebuild_project import CodebuildProject
from .ecs_task import EcsTask
from .ecs_service import EcsService
from .codepipeline import CodePipeline
from .vpc_link import VpcLink
from .apigateway_endpoint import ApiGatewayEndpoint
from .outputs import Outputs


def generate_ecs_cicd_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    secret = Secret(t, params)
    security_groups = SecurityGroups(t, params, conditions)
    roles = Roles(t, params, conditions, secret)

    artifacts_bucket = ArtifactsBucket(t)
    cicd_roles = CicdRoles(t, params, artifacts_bucket)
    ArtifactsBucketPolicy(t, artifacts_bucket, cicd_roles)
    ecr_repositoty = EcrRepositoty(t, cicd_roles)
    cicd_security_groups = CicdSecurityGroups(t, params, conditions, security_groups)
    alb = Alb(t, params, conditions, cicd_security_groups)
    AlbAlarms(t, params, conditions, alb)
    logging_group = LoggingGroup(t, params)
    CodebuildProject(t, params, conditions, ecr_repositoty, secret, cicd_roles)
    ecs_task = EcsTask(
        t, params, conditions, roles, cicd_roles, ecr_repositoty, secret, logging_group
    )
    ecs_service = EcsService(
        t, params, conditions, ecr_repositoty, alb, cicd_security_groups, ecs_task
    )
    CodePipeline(t, params, conditions, artifacts_bucket, cicd_roles, ecs_service)
    vpc_link = VpcLink(t, params, conditions, alb, cicd_security_groups)
    ApiGatewayEndpoint(t, params, conditions, vpc_link, alb)
    Outputs(t, params, alb)

    return t.to_json()
