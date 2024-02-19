from typing import Protocol


class HostedZones(Protocol):
    def create_hosted_zone_and_get_ns_list(
        self, deployment_id: str, full_domain_name: str
    ) -> list[str]: ...
