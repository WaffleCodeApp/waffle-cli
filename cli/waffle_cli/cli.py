import argparse
import sys

from .commands import COMMANDS, get_command


def _get_command_parser(with_help: bool, command: str | None = None):
    command_parser = argparse.ArgumentParser(
        add_help=with_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Commands:\n"
            + "\n".join(
                [
                    "\t%s\t\t- %s" % (c.get_name(), c.get_descrtiption())
                    for c in COMMANDS
                ]
            )
            if command is None
            else ""
        ),
        description="" if command is None else get_command(command).get_descrtiption(),
    )
    command_parser.add_argument(
        "command",
        help="The selected command to run",
        choices=[c.get_name() for c in COMMANDS],
        metavar=command or "command",
    )
    return command_parser


def main():
    show_command_help = len(sys.argv) <= 2

    command_parser = _get_command_parser(show_command_help)
    command_args, _ = command_parser.parse_known_args()

    parser = _get_command_parser(not show_command_help, command_args.command)

    command = get_command(command_args.command)

    command.arg_parser(parser)

    arguments = vars(parser.parse_args())

    command.execute(**arguments)


if __name__ == "__main__":
    main()
