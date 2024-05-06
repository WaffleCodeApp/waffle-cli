from typing import Protocol

from .deployment_settings import DeploymentSettings
from .deployment_states import DeploymentStates
from .hosted_zones import HostedZones
from .certs import Certs
from .deployment_template_bucket import DeploymentTemplateBucket
from .stacks import Stacks


class Gateways(Protocol):
    deployment_settings: DeploymentSettings
    deployment_states: DeploymentStates
    hosted_zones: HostedZones
    certs: Certs
    deployment_template_bucket: DeploymentTemplateBucket
    stacks: Stacks
