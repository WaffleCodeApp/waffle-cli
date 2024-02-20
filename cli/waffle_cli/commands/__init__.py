from .command_type import Command
from .create_new_deployment import CreateNewDeployment
from .list_deployments import ListDeployments
from .configure_aws_profile import ConfigureAwsProfile
from .configure_deployment_domain import ConfigureDeploymentDomain
from .set_deployment_type import SetDeploymentType


COMMANDS: list[Command] = [
    CreateNewDeployment(),
    ListDeployments(),
    ConfigureAwsProfile(),
    ConfigureDeploymentDomain(),
    SetDeploymentType(),
]


def get_command(name: str) -> Command:
    command = next((c for c in COMMANDS if c.get_name() == name), None)
    if command is None:
        print("Command with the specified name not found:", name)
        raise Exception("Command not found")
    return command
