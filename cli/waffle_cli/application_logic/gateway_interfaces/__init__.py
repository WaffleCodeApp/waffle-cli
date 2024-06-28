from typing import Protocol

from .deployment_states import DeploymentStates
from .deployment_settings import DeploymentSettings
from .hosted_zones import HostedZones
from .certs import Certs
from .deployment_template_bucket import DeploymentTemplateBucket
from .stacks import Stacks
from .github_secrets import GitHubSecrets
from .local_files import LocalFiles


class Gateways(Protocol):
    deployment_settings: DeploymentSettings
    deployment_states: DeploymentStates
    hosted_zones: HostedZones
    certs: Certs
    deployment_template_bucket: DeploymentTemplateBucket
    stacks: Stacks
    github_secrets: GitHubSecrets
    local_files: LocalFiles
