from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
from ..application_logic.gateway_interfaces.certs import Certs


class CertsWithCertManager(Certs):
    def _get_client(self, deployment_id: str, aws_region: str) -> Any:
        return Session(profile_name=deployment_id).client(  # type: ignore
            "acm", region_name=aws_region  # type: ignore
        )

    def request_cert_and_get_arn(
        self, deployment_id: str, full_domain_name: str, aws_region: str
    ) -> str:
        response = self._get_client(deployment_id, aws_region).request_certificate(
            DomainName=full_domain_name,
            ValidationMethod="DNS",
            SubjectAlternativeNames=[f"*.{full_domain_name}"],
            IdempotencyToken=full_domain_name.replace(".", ""),
        )
        cert_arn: str = f"{response['CertificateArn']}"
        return cert_arn
