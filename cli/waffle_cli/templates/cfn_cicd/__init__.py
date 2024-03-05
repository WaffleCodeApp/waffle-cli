from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .secret import Secret
from .roles import Roles
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .codebuild_project import CodebuildProject
from .codepipeline import CodePipeline
from .artifacts_bucket_policy import ArtifactsBucketPolicy


def generate_cfn_cicd_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    secret = Secret(t, params)
    roles = Roles(t, params, conditions, secret)
    artifacts_bucket = ArtifactsBucket(t)
    cicd_roles = CicdRoles(t, params, artifacts_bucket)
    CodebuildProject(t, params, conditions, artifacts_bucket, roles, secret, cicd_roles)
    CodePipeline(t, params, conditions, artifacts_bucket, cicd_roles)
    ArtifactsBucketPolicy(t, artifacts_bucket, cicd_roles)

    return t.to_json()
