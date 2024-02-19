from .command_type import Command
from .add_local_aws_profile import ConfigureAwsProfile


COMMANDS: list[Command] = [ConfigureAwsProfile]


def get_command(name: str) -> Command:
    command = next((c for c in COMMANDS if c.get_name() == name), None)
    if command is None:
        print("Command with the specified name not found:", name)
        raise Exception("Command not found")
    return command
