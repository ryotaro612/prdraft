import typing
from prdraft.pullrequest.storage import pull_request_storage


class Args(typing.Protocol):
    """Arguments for fetch subcommand."""

    database: str
    github_repository: str
    github_api_key: str


def run(args: Args) -> int:
    with pull_request_storage(args.database) as pr_storage:
        pr_storage
        ...

    return 0
