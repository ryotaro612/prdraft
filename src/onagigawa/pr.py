import requests
import typing


@typing.runtime_checkable
class Args(typing.Protocol):
    """This class is runtime_checkable to select a subcommand using parsing result.

    Attributes:
        organization (str): organization
        repository (str): repository
        output (str): Write the fetched pull requests to this file in JSON line format.
        size (int): # of pull requests that a response from GItHub API contains.
        offset (int): The number of page that the subcommand fetches from GitHub API. Specify this value to resume from the previous state.
    """

    organization: str
    repository: str
    output: str
    size: int
    offset: int


def run(args: Args):
    """Fetch the pull requests using GitHub API and write them to a file in JSON line format."""
    args.output


def get_pull_request(
    org: str, repo: str, github_api_token: str, offset: int, size: int
):
    requests.get(
        f"https://api.github.com/repos/{org}/{repo}/pulls",
        params={"state": "all", "direction": "asc", "page": offset, "per_page": size},
        headers={
            "accept": "application/vnd.github.full+json",
            "authorization": f"Bearer {github_api_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
