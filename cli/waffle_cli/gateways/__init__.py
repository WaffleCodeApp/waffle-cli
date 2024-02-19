from ..application_logic.gateway_interfaces import Gateways
from ..application_logic.gateway_interfaces.deployment_settings import (
    DeploymentSettings,
)
from .deployment_settings_with_json import DeploymentSettingsWithJson


class GatewayImplementations(Gateways):
    deployment_settings: DeploymentSettings

    def __init__(self) -> None:
        deployment_settings = DeploymentSettingsWithJson()
        self.deployment_settings = deployment_settings
