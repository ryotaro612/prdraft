import argparse
import typing


@typing.runtime_checkable
class Args(typing.Protocol):
    """Represents command line arguments."""

    verbose: bool
    subcommand: typing.Literal["init"]


def parse(args: list[str]) -> Args:
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
    parsed_args = parser.parse_args(args)
    if isinstance(parsed_args, Args):
        return parsed_args
    raise RuntimeError("parsed args is not an instance of Args")


def _define_init(parser: argparse.ArgumentParser) -> None:
    """Defines init subcommand parser."""
    parser.add_argument(
        "database",
        default="prdraft.db",
        help="A DuckDB database file",
    )
