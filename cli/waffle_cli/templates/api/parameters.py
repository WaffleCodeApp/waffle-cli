from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter
    full_domain_name: Parameter
    deployment_subdomain: Parameter
    api_subdomain: Parameter
    cert_arn: Parameter

    def __init__(self, t: Template):
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        self.full_domain_name = t.add_parameter(
            Parameter(
                "FullDomainName",
                Description="like dev.example.com",
                Type="String",
            )
        )

        self.api_subdomain = t.add_parameter(
            Parameter(
                "BackendApiHostname",
                Description="api from api.dev.example.com",
                Type="String",
            )
        )

        self.generic_certificate_arn = t.add_parameter(
            Parameter(
                "GenericCertificateArn",
                Description="arn of the generated certificate",
                Type="String",
            )
        )
