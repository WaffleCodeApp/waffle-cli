from ..application_logic.gateway_interfaces.stacks import Stacks
from ..application_logic.gateway_interfaces import Gateways
from ..application_logic.gateway_interfaces.deployment_settings import (
    DeploymentSettings,
)
from ..application_logic.gateway_interfaces.hosted_zones import HostedZones
from ..application_logic.gateway_interfaces.certs import Certs
from ..application_logic.gateway_interfaces.deployment_template_bucket import (
    DeploymentTemplateBucket,
)
from .deployment_settings_with_json import DeploymentSettingsWithJson
from .hosted_zones_with_r53 import HostedZonesWithRoute53
from .certs_with_cm import CertsWithCertManager
from .deployment_template_bucket_with_s3 import DeploymentTemplateBucketWithS3
from .stacks_with_cfn import StacksWithCfn


class _GatewayImplementations(Gateways):
    deployment_settings: DeploymentSettings
    hosted_zones: HostedZones
    certs: Certs
    deployment_template_bucket: DeploymentTemplateBucket
    stacks: Stacks

    def __init__(self) -> None:
        self.deployment_settings = DeploymentSettingsWithJson()
        self.hosted_zones = HostedZonesWithRoute53()
        self.certs = CertsWithCertManager()
        self.deployment_template_bucket = DeploymentTemplateBucketWithS3()
        self.stacks = StacksWithCfn()


gateway_implementations = _GatewayImplementations()
