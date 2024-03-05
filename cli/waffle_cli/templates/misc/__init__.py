from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]
from .parameters import Parameters
from .deployment_secret import DeploymentSecret
from .github_secret import GithubSecret


def generate_misc_stack_json() -> str:
    t = Template()
    parameters = Parameters(t)
    DeploymentSecret(t, parameters)
    GithubSecret(t, parameters)

    return t.to_json()
