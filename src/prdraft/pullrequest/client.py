import requests


def get_pull_request(
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
