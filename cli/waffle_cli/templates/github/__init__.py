from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]
from .parameters import Parameters
from .github_secret import GithubSecret


def generate_github_stack_json() -> str:
    t = Template()
    parameters = Parameters(t)
    GithubSecret(t, parameters)

    return t.to_json()

def generate_github_parameter_list(
    deployment_id: str,
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
    ]
