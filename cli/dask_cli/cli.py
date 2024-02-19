import argparse
import sys

from dask_cli.commands.add_aws_profile import (  # pyright: ignore[reportMissingTypeStubs]
    add_aws_profile_arg_parser,  # type: ignore
    add_aws_profile,  # type: ignore
)

COMMANDS = {"add_aws_profile": "Configure AWS IAM credentials for a deployment"}


def _get_command_parser(with_help: bool, command: str | None = None):
    command_parser = argparse.ArgumentParser(
        add_help=with_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Commands:\n"
            + "\n".join(["\t%s\t\t- %s" % (k, v) for k, v in COMMANDS.items()])
            if command is None
            else ""
        ),
        description="" if command is None else COMMANDS.get(command, ""),
    )
    command_parser.add_argument(
        "command",
        help="CLI command name",
        choices=COMMANDS.keys(),
        metavar=command or "command",
    )
    return command_parser


def main():
    show_command_help = len(sys.argv) <= 2

    command_parser = _get_command_parser(show_command_help)
    command_args, _ = command_parser.parse_known_args()

    parser = _get_command_parser(not show_command_help, command_args.command)
    if command_args.command == "add_aws_profile":
        globals()[f"{command_args.command}_arg_parser"](parser)

    arguments = vars(parser.parse_args())
    globals()[command_args.command](**arguments)


if __name__ == "__main__":
    main()
