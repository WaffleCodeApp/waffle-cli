from typing import Protocol
from .deployment_states import DeploymentStates
from .deployment_settings import DeploymentSettings
from .project_settings import ProjectSettings
from .hosted_zones import HostedZones
from .certs import Certs
from .deployment_template_bucket import DeploymentTemplateBucket
from .stacks import Stacks
from .github_secrets import GitHubSecrets


class Gateways(Protocol):
    deployment_settings: DeploymentSettings
    deployment_states: DeploymentStates
    project_settings: ProjectSettings
    hosted_zones: HostedZones
    certs: Certs
    deployment_template_bucket: DeploymentTemplateBucket
    stacks: Stacks
    github_secrets: GitHubSecrets
