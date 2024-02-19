from typing import Protocol
from .deployment_settings import DeploymentSettings
from .hosted_zones import HostedZones


class Gateways(Protocol):
    deployment_settings: DeploymentSettings
    hosted_zones: HostedZones
