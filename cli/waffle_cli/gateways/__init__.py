from ..application_logic.gateway_interfaces import Gateways
from ..application_logic.gateway_interfaces.deployment_settings import (
    DeploymentSettings,
)
from ..application_logic.gateway_interfaces.deployment_states import DeploymentStates
from ..application_logic.gateway_interfaces.hosted_zones import HostedZones
from ..application_logic.gateway_interfaces.certs import Certs
from ..application_logic.gateway_interfaces.deployment_template_bucket import (
    DeploymentTemplateBucket,
)
from ..application_logic.gateway_interfaces.stacks import Stacks
from ..application_logic.gateway_interfaces.github_secrets import GitHubSecrets
from ..application_logic.gateway_interfaces.local_files import LocalFiles
from .deployment_settings_with_json import DeploymentSettingsWithJson
from .deployment_states_with_json import DeploymentStatesWithJson
from .hosted_zones_with_r53 import HostedZonesWithRoute53
from .certs_with_cm import CertsWithCertManager
from .deployment_template_bucket_with_s3 import DeploymentTemplateBucketWithS3
from .stacks_with_cfn import StacksWithCfn
from .local_files_with_fs import LocalFilesWithFs


class _GatewayImplementations(Gateways):
    deployment_settings: DeploymentSettings
    deployment_states: DeploymentStates
    hosted_zones: HostedZones
    certs: Certs
    deployment_template_bucket: DeploymentTemplateBucket
    stacks: Stacks
    github_secrets: GitHubSecrets
    local_files: LocalFiles

    def __init__(self) -> None:
        self.deployment_settings = DeploymentSettingsWithJson()
        self.deployment_states = DeploymentStatesWithJson()
        self.hosted_zones = HostedZonesWithRoute53()
        self.certs = CertsWithCertManager()
        self.deployment_template_bucket = DeploymentTemplateBucketWithS3()
        self.stacks = StacksWithCfn()
        self.local_files = LocalFilesWithFs()


gateway_implementations = _GatewayImplementations()
