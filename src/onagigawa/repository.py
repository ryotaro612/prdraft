import git
import typing


def make_diff_summary(repo: git.Repo, base: str, head: str):
    messages = _get_commit_messages(repo, base, head)
    diffs = _get_diff(repo, base, head)
    return _render_md(messages, diffs)


def _get_commit_messages(repo: git.Repo, start_sha: str, end_sha: str) -> list[str]:
    """Get commit messages between base and head SHAs."""
    messages = []
    for commit in repo.iter_commits(f"{start_sha}..{end_sha}"):
        if isinstance(commit.message, str):
            messages.append(commit.message)
        else:
            messages.append(commit.message.decode())
    return messages


class _Diff:
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


def _get_diff(repo: git.Repo, start_sha: str, end_sha: str) -> list[_Diff]:
    change_types: list[typing.Literal["A", "D", "C", "M", "R", "T", "U"] | None] = [
        diff.change_type for diff in repo.commit(start_sha).diff(repo.commit(end_sha))
    ]

    result = []
    for i, diff in enumerate(
        repo.commit(start_sha).diff(repo.commit(end_sha), create_patch=True)
    ):
        change_type = change_types[i]

        result.append(
            _Diff(
                raw=diff,
                change_type=change_type,
            )
        )

    return result


def _render_md(messages: list[str], diffs: list[_Diff]) -> str:
    md = "# Pull request\n\n"
    md += "## Deleted files\n\n"

    for deleted in [diff for diff in diffs if diff.deleted_file]:
        md += f"- `{deleted.deleted_file}`\n"

    md += "\n## Renamed files\n\n"
    for renamed in [diff for diff in diffs if diff.renamed]:
        if renamed.renamed:
            md += f"- From: `{renamed.renamed[0]}` To: `{renamed.renamed[1]}`\n"

    md += "\n## Modified files\n\n"

    for modified in [diff.modified_file() for diff in diffs]:
        if modified:
            a_path, b_path, diff = modified
            if a_path == b_path:
                md += f"filepath: `{a_path}`"
            else:
                md += f"renamed from `{a_path}` to `{b_path}`"

            md += "\n\ndiff:\n\n"
            for line in diff.splitlines():
                md += f"    {line}\n"
            md += "\n"

    md += "\n## Added files\n\n"
    for added in [diff.added_file() for diff in diffs]:
        if added:
            filepath, diff = added
            md += f"filepath: `{filepath}`\n\n"
            md += "diff:\n\n"
            for line in diff.splitlines():
                md += f"    {line}\n"
            md += "\n"

    md += "\n## Commit messages\n\n"
    for i, message in enumerate(messages):
        md += f"### Message {i + 1}\n\n"
        for line in message.splitlines():
            md += f"    {line}\n"
        md += "\n"

    return md
