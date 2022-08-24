
import argparse


def get_parser():
    
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]... URL...",
        add_help=False,
    )

    general = parser.add_argument_group("General Options")
    general.add_argument(
        "-h", "--help",
        action="help",
        help="Print this help message and exit",
    )
    parser.add_argument(
        "urls",
        metavar="URL", nargs="*",
        help=argparse.SUPPRESS,
    )
    
    return parser