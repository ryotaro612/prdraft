import argparse


def parse(args: list[str]) -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="prdraft is an utility that writes pull request text"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    subparsers = parser.add_subparsers(help="subcommand", dest="subcommand")
    init_parser = subparsers.add_parser(
        "init", help="set up a database for this utility"
    )
    _define_init(init_parser)
    return parser.parse_args(args)


def _define_init(parser: argparse.ArgumentParser) -> None:
    """Defines init subcommand parser."""
    parser.add_argument(
        "database",
        default="prdraft.db",
        help="A DuckDB database file",
    )
