import git
import typing


def get_commit_messages(repo: git.Repo, start_sha: str, end_sha: str) -> list[str]:
    """Get commit messages between base and head SHAs."""
    messages = []
    for commit in repo.iter_commits(f"{start_sha}..{end_sha}"):
        if isinstance(commit.message, str):
            messages.append(commit.message)
        else:
            messages.append(commit.message.decode())
    return messages


class Diff:
    """"""

    def __init__(
        self,
        raw: git.Diff,
        change_type: typing.Literal["A", "D", "C", "M", "R", "T", "U"] | None,
    ):
        self._raw = raw
        self._change_type = change_type

    @property
    def deleted_file(self) -> str | None:
        if self._raw.deleted_file:
            assert self._change_type == "D" and self._raw.a_path
            return self._raw.a_path

    @property
    def renamed(self) -> typing.Tuple[str, str] | None:
        if self._raw.renamed_file:
            assert (
                self._change_type == "R"
                and self._raw.rename_from
                and self._raw.rename_to
            )
            return (self._raw.rename_from, self._raw.rename_to)
        return None

    def modified_file(self) -> typing.Tuple[str, str, str] | None:
        if self._change_type != "M":
            return
        diff = self._raw.diff
        if diff is None or len(diff) == 0:
            return
        if isinstance(diff, bytes):
            diff = diff.decode()

        a_path = self._raw.a_path
        b_path = self._raw.b_path
        if a_path is not None and b_path is not None:
            return (a_path, b_path, diff)

    def added_file(self) -> typing.Tuple[str, str] | None:
        if self._raw.new_file:
            b_path = self._raw.b_path
            assert self._change_type == "A" and b_path
            diff = self._raw.diff
            if diff is None or len(diff) == 0:
                return None
            if isinstance(diff, bytes):
                diff = diff.decode()

            return (b_path, diff)

    # a_path: str | None
    # b_path: str | None
    # diff: str | None
    # change_type: typing.Literal["A", "D", "C", "M", "R", "T", "U"]
    # copied_file: bool
    # deleted_file: bool
    # renamed_file: bool
    # new_file: bool


def get_diff(repo: git.Repo, start_sha: str, end_sha: str) -> list[Diff]:
    change_types: list[typing.Literal["A", "D", "C", "M", "R", "T", "U"] | None] = [
        diff.change_type for diff in repo.commit(start_sha).diff(repo.commit(end_sha))
    ]

    result = []
    for i, diff in enumerate(
        repo.commit(start_sha).diff(repo.commit(end_sha), create_patch=True)
    ):
        change_type = change_types[i]

        result.append(
            Diff(
                raw=diff,
                change_type=change_type,
            )
        )

    return result
