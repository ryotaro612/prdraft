import argparse
import os
import typing


@typing.runtime_checkable
class InitArgs(typing.Protocol):
    """Represents command line arguments."""

    verbose: bool
    command: typing.Literal["init"]
    database: str


@typing.runtime_checkable
class PrFetchArgs(typing.Protocol):
    verbose: bool
    command: typing.Literal["pr"]
    subcommand: typing.Literal["fetch"]
    database: str
    ghrepo: str
    github_api_key: str


class Parser:

    def __init__(self) -> None:
        self._parser = _make_parser()

    def parse(self, args: list[str]) -> InitArgs | PrFetchArgs | None:
        """Parses command line arguments."""
        parsed_args = self._parser.parse_args(args)
        if parsed_args.command == "init" and isinstance(parsed_args, InitArgs):
            return parsed_args

        if parsed_args.command == "pr" and parsed_args.subcommand == "fetch":
            token = os.getenv("PRDRAFT_GITHUB_TOKEN", None)
            if not token:
                raise ValueError("PRDRAFT_GITHUB_TOKEN environment variable is not set")
            parsed_args.github_api_key = token
            if isinstance(parsed_args, PrFetchArgs):
                return parsed_args

    def print_help(self) -> None:
        self._parser.print_help()


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="prdraft is an utility that writes pull request text",
        exit_on_error=False,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    subparsers = parser.add_subparsers(help="command", dest="command")
    init_parser = subparsers.add_parser(
        "init", help="set up a database for this utility"
    )
    _define_init(init_parser)

    pr_parser = subparsers.add_parser("pr", help="process pull requests")
    _define_pr(pr_parser)
    return parser


def _define_init(parser: argparse.ArgumentParser) -> None:
    """Defines init subcommand parser."""
    parser.add_argument(
        "database",
        default="prdraft.db",
        help="A DuckDB database file",
    )


def _define_pr(parser: argparse.ArgumentParser) -> None:
    """Defines store subcommand parser."""
    subparsers = parser.add_subparsers(
        help="utilities for pull requests", dest="subcommand"
    )
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="fetch pull request data from GitHub. Use PRDRAFT_GITHUB_TOKEN to get the pull request history.",
    )
    fetch_parser.add_argument(
        "database",
        default="prdraft.db",
        help="A DuckDB database file",
    )
    fetch_parser.add_argument(
        "ghrepo",
        help="The GitHub repository to fetch data from. The format is owner/repo.",
    )
