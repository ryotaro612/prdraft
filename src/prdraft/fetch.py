import typing
import prdraft.args as args
from prdraft.pullrequest.storage import pull_request_storage


def run(cmd_args: args.PrFetchArgs) -> int:
    """"""
    args = _Args(cmd_args)
    with pull_request_storage(args.database()) as pr_storage:
        n_pull_requests: int = pr_storage.count(args.owner(), args.repository())

    return 0


class _Args:

    def __init__(self, args: args.PrFetchArgs) -> None:
        self._args = args

    def owner(self) -> str:
        return self._args.ghrepo.split("/")[0]

    def repository(self) -> str:
        return self._args.ghrepo.split("/")[1]

    def database(self) -> str:
        return self._args.database
