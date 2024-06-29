from datetime import datetime

from time import sleep
from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
from ..application_logic.gateway_interfaces.hosted_zones import HostedZones
from ..utils.progress_indicator import show_progress


class HostedZonesWithRoute53(HostedZones):
    def _get_hosted_zone_id(
        self, deployment_id: str, full_domain_name: str
    ) -> str | None:
        session = Session(profile_name=deployment_id)
        client: Any = session.client(service_name="route53")  # type: ignore
        marker = None
        hosted_zone_id: str | None = None
        while True:
            kw = {}
            if marker is not None:
                kw["Marker"] = marker
            response = client.list_hosted_zones(**kw)
            if response.get("HostedZones", None):
                for hz in response.get("HostedZones", []):
                    if hz["Name"] == full_domain_name:
                        hosted_zone_id = hz["Id"]
                        break
            if response.get("IsTruncated", None):
                kw["Marker"] = response.get("NextMarker")
            else:
                break
        return hosted_zone_id

    def create_or_get_hosted_zone_and_get_ns_list(
        self, deployment_id: str, full_domain_name: str
    ) -> list[str]:
        existing_hosted_zone_id = self._get_hosted_zone_id(
            deployment_id, full_domain_name
        )

        session = Session(profile_name=deployment_id)
        client: Any = session.client(service_name="route53")  # type: ignore

        if existing_hosted_zone_id is None:
            response: Any = client.create_hosted_zone(
                Name=full_domain_name,
                CallerReference=datetime.now().isoformat(),
            )

            hosted_zone_id = response["HostedZone"]["Id"]
            change_id = response["ChangeInfo"]["Id"]

            if response["ChangeInfo"]["Status"] != "INSYNC":
                i = 0
                while True:
                    show_progress(i, "Creating hosted zone...")
                    i += 1
                    sleep(10)
                    response = client.get_change(Id=change_id)
                    if response["ChangeInfo"]["Status"] == "PENDING":
                        break
                show_progress(i, "Creating hosted zone done.")
                response = client.get_hosted_zone(Id=hosted_zone_id)
                # NOTE: status in theory is 'INSYNC' at this point

            name_server_list: list[str] = response["DelegationSet"]["NameServers"]
            return name_server_list
        else:
            response: Any = client.get_hosted_zone(Id=existing_hosted_zone_id)
            return response["DelegationSet"]["NameServers"]
