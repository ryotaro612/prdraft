import typing


class PullRequest:
    """"""

    def __init__(self, raw: dict):
        """"""
        self._raw = raw

    @property
    def id(self) -> int:
        """"""
        return self._raw["id"]

    @property
    def merged(self) -> bool:
        """"""
        return True if self._raw.get("merged_at", False) else False

    @property
    def head_sha(self) -> typing.Optional[str]:
        """"""
        return self._raw["head"]["sha"]

    @property
    def base_sha(self) -> typing.Optional[str]:
        """"""
        return self._raw["base"]["sha"]
