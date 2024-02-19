from datetime import datetime

from time import sleep
from typing import Any
from boto3 import Session  # type: ignore
from ..application_logic.gateway_interfaces.hosted_zones import HostedZones
from ..utils.progress_indicator import show_progress


class HostedZonesWithRoute53(HostedZones):
    def create_hosted_zone_and_get_ns_list(
        self, deployment_id: str, full_domain_name: str
    ) -> list[str]:
        session = Session(profile_name=deployment_id)

        client: Any = session.client(service_name="route53")  # type: ignore

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
