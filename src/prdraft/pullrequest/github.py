import requests


class PullRequest:

    def __init__(self, raw: dict):
        self._raw = raw

    @property
    def title(self) -> str:
        return self._raw["title"]

    @property
    def id(self) -> int:
        return self._raw["id"]

    @property
    def number(self) -> int:
        return self._raw["number"]

    @property
    def merged(self) -> bool:
        """"""
        return True if self._raw.get("merged_at", False) else False

    @property
    def head_sha(self) -> str:
        """"""
        return self._raw["head"]["sha"]

    @property
    def base_sha(self) -> str:
        """"""
        return self._raw["base"]["sha"]


class PullRequests:

    def __init__(self, response: requests.models.Response):
        self._response = response

    def pull_requests(self) -> list[PullRequest]:
        return [PullRequest(item) for item in self._response.json()]

    def __len__(self) -> int:
        return len(self.pull_requests())


def get_pull_requests(
    org: str, repo: str, github_api_token: str, page: int, per_page: int
) -> requests.models.Response | PullRequests:
    resp = requests.get(
        f"https://api.github.com/repos/{org}/{repo}/pulls",
        params={
            "state": "all",
            "direction": "asc",
            "page": page,
            "per_page": per_page,
        },
        headers={
            "accept": "application/vnd.github.full+json",
            "authorization": f"Bearer {github_api_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if resp.status_code != 200:
        return resp

    return PullRequests(resp)
