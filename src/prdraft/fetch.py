import duckdb
import logging
import prdraft.args as args
from prdraft.pullrequest import (
    PullRequestStorageClient,
    get_pull_requests,
    PullRequests,
)


def run(cmd_args: args.PrFetchArgs) -> int:
    """"""
    args = _Args(cmd_args)
    with duckdb.connect(args.database()) as conn:
        pr_storage = PullRequestStorageClient(conn)
        n_pull_requests: int = pr_storage.count(args.owner(), args.repository())
        per_page = 30
        page = n_pull_requests // per_page

        while True:
            response = get_pull_requests(
                args.owner(),
                args.repository(),
                args.github_api_token(),
                page,
                per_page,
            )
            if not isinstance(response, PullRequests):
                logging.error(
                    f"Failed to fetch pull requests. status code is {response.status_code}. json is {response.text}"
                )
                break
            if len(response) == 0:
                break
            response.pull_requests()
            page += 1

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

    def github_api_token(self) -> str:
        return self._args.github_api_key
