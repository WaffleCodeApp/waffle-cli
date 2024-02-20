from ..application_logic.gateway_interfaces import Gateways
from ..application_logic.gateway_interfaces.deployment_settings import (
    DeploymentSettings,
)
from ..application_logic.gateway_interfaces.hosted_zones import HostedZones
from .deployment_settings_with_json import DeploymentSettingsWithJson
from .hosted_zones_with_r53 import HostedZonesWithRoute53


class _GatewayImplementations(Gateways):
    deployment_settings: DeploymentSettings
    hosted_zones: HostedZones

    def __init__(self) -> None:
        self.deployment_settings = DeploymentSettingsWithJson()
        self.hosted_zones = HostedZonesWithRoute53()


gateway_implementations = _GatewayImplementations()
