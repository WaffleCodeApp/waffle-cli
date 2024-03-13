from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]
from .deployment_secret import DeploymentSecret
from .parameters import Parameters


def generate_deployment_stack_json() -> str:
    t = Template()
    parameters = Parameters(t)
    DeploymentSecret(t, parameters)

    return t.to_json()

def generate_deployment_parameter_list(
    deployment_id: str,
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
    ]
