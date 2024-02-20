from ..application_logic.gateway_interfaces import Gateways
from ..application_logic.gateway_interfaces.deployment_settings import (
    DeploymentSettings,
)
from ..application_logic.gateway_interfaces.hosted_zones import HostedZones
from ..application_logic.gateway_interfaces.certs import Certs
from .deployment_settings_with_json import DeploymentSettingsWithJson
from .hosted_zones_with_r53 import HostedZonesWithRoute53
from .certs_with_cm import CertsWithCertManager


class _GatewayImplementations(Gateways):
    deployment_settings: DeploymentSettings
    hosted_zones: HostedZones
    certs: Certs

    def __init__(self) -> None:
        self.deployment_settings = DeploymentSettingsWithJson()
        self.hosted_zones = HostedZonesWithRoute53()
        self.certs = CertsWithCertManager()


gateway_implementations = _GatewayImplementations()
