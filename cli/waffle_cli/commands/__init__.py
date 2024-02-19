from .command_type import Command
from .configure_aws_profile import ConfigureAwsProfile
from .create_new_deployment import CreateNewDeployment
from .configure_deployment_domain import ConfigureDeploymentDomain


COMMANDS: list[Command] = [
    ConfigureAwsProfile(),
    CreateNewDeployment(),
    ConfigureDeploymentDomain(),
]


def get_command(name: str) -> Command:
    command = next((c for c in COMMANDS if c.get_name() == name), None)
    if command is None:
        print("Command with the specified name not found:", name)
        raise Exception("Command not found")
    return command
