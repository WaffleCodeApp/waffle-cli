import argparse
import sys

from commands.set_aws_profile import set_arg_parser, set_aws_profile

PROG = 'cli'
VERSION = '0.0.0'

COMMANDS = {
    'set_aws_profile': 'Configure AWS IAM credentials for a deployment'
}

def get_command_parser(with_help: bool, command: str | None = None):
    command_parser = argparse.ArgumentParser(
        prog=PROG,
        add_help=with_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='Commands:\n' + '\n'.join(['\t%s\t\t- %s' % (k,v)  for k,v in COMMANDS.items()]) if command is None else '',
        description='' if command is None else COMMANDS.get(command, ''),
    )
    command_parser.add_argument(
        "--version",
        action='version',
        version='%(prog)s ' + VERSION
    )
    command_parser.add_argument(
        "command",
        help="CLI command name",
        choices=COMMANDS.keys(),
        metavar=command or 'command'
    )
    return command_parser

if __name__ == '__main__':
    show_command_help = len(sys.argv) <= 2

    command_parser = get_command_parser(show_command_help)
    command_args, _ = command_parser.parse_known_args()
    
    parser = get_command_parser(not show_command_help, command_args.command)
    if command_args.command == 'set_aws_profile':
        set_arg_parser(parser)

    arguments = parser.parse_args()

    if command_args.command == 'set_aws_profile':
        set_aws_profile(arguments.profile)

