import typing


@typing.runtime_checkable
class Args(typing.Protocol):
    """Arguments for init subcommand."""

    database: str


def run(args: Args): ...
