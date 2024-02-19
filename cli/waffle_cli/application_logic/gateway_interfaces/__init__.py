from typing import Protocol
from .deployment_settings import DeploymentSettings


class Gateways(Protocol):
    deployment_settings: DeploymentSettings
