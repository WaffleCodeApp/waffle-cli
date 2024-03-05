from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .web_bucket import WebBucket
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .codebuild_project import CodebuildProject
from .codepipeline import CodePipeline
from .artifacts_bucket_policy import ArtifactsBucketPolicy
from .logging_bucket import LoggingBucket
from .distribution import Distribution
from .routes import Routes


def generate_cdn_cicd_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    web_bucket = WebBucket(t)
    artifacts_bucket = ArtifactsBucket(t)
    cicd_roles = CicdRoles(t, params, artifacts_bucket, web_bucket)
    CodebuildProject(t, params, conditions, cicd_roles)
    CodePipeline(t, params, cicd_roles, conditions, web_bucket, artifacts_bucket)
    ArtifactsBucketPolicy(t, artifacts_bucket, cicd_roles)
    logging_bucket = LoggingBucket(t)
    distribution = Distribution(t, conditions, params, logging_bucket, web_bucket)
    Routes(t, params, distribution)

    return t.to_json()
