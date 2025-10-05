import requests
import typing
import logging
import os
import json


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


def run(args: Args) -> int:
    """Fetch the pull requests using GitHub API and write them to a file in JSON line format."""
    key = "ONAGIGAWA_GITHUB_API_KEY"
    if key not in os.environ:
        logging.error(
            "GitHub API Token is required to request pull requests. Set the token to ONAGIGAWA_GITHUB_API_KEY environment variable."
        )
        return 1

    result = []
    prev = args.offset
    rtn_code = 0
    while True:
        pull_requests = _get_pull_request(
            args.organization, args.repository, os.environ[key], prev, args.size
        )
        body = pull_requests.json()
        if pull_requests.status_code == 200:
            result.extend(body)
            if len(body) == 0:
                break
            else:
                prev += 1
        else:
            logging.error(
                f"Failed to fetch pull requests. status code is {pull_requests.status_code}. json is {body}"
            )
            rtn_code = 1
            break

    if result:
        with open(args.output, "a") as f:
            for pr in result:
                # https://jsonlines.org/ last line is strongly recommended to end with newline
                f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        logging.debug(
            f"Fetched {len(result)} pull requests. The result is written to {args.output}."
        )

    return rtn_code


def _get_pull_request(
    org: str, repo: str, github_api_token: str, offset: int, size: int
) -> requests.models.Response:
    return requests.get(
        f"https://api.github.com/repos/{org}/{repo}/pulls",
        params={"state": "all", "direction": "asc", "page": offset, "per_page": size},
        headers={
            "accept": "application/vnd.github.full+json",
            "authorization": f"Bearer {github_api_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
