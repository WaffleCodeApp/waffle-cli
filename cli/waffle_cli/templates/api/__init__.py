from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]


from .parameters import Parameters
from .api_gateway import ApiGateway
from .routes import Routes
from .roles import Roles
from .deployment import Deployment
from .usage_plan import UsagePlan
from .outputs import Outputs


def generate_api_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    api_gw = ApiGateway(t, params)
    Routes(t, params, api_gw)
    Roles(t)
    d = Deployment(t, api_gw)
    UsagePlan(t, api_gw, d)
    Outputs(t, api_gw, params, d)

    return t.to_json()


def generate_api_parameter_list(
    deployment_id: str,
    full_domain_name: str,
    api_subdomain: str,
    certificate_arn: str,
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
        {
            "ParameterKey": "FullDomainName",
            "ParameterValue": full_domain_name,
        },
        {
            "ParameterKey": "BackendApiHostname",
            "ParameterValue": api_subdomain,
        },
        {
            "ParameterKey": "GenericCertificateArn",
            "ParameterValue": certificate_arn,
        },
    ]
