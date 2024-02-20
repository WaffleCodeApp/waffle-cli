from typing import Protocol


class Certs(Protocol):
    def request_cert_and_get_arn(
        self, deployment_id: str, full_domain_name: str, aws_region: str
    ) -> str: ...
