import typing


class Args(typing.Protocol):
    """Arguments for fetch subcommand."""

    database: str
    github_repository: str
    github_api_key: str


def run(args: Args) -> int: ...
