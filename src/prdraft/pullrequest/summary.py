import git
import typing
from collections import deque


@typing.runtime_checkable
class TokenCounter(typing.Protocol):

    def count_tokens(self, text: str) -> int: ...


def make_summary(
    repo: git.Repo, base: str, head: str, tokenizer: TokenCounter, token_limit: int
):
    current_tokens = 0
    commit_messages = []
    for message in _get_commit_messages(repo, base, head):
        message_tokens = tokenizer.count_tokens(message)
        if current_tokens + message_tokens > token_limit:
            break
        commit_messages.append(message)
        current_tokens += message_tokens

    change_types: list[typing.Literal["A", "D", "C", "M", "R", "T", "U"] | None] = [
        diff.change_type for diff in repo.commit(base).diff(repo.commit(head))
    ]

    diffs = repo.commit(base).diff(repo.commit(head), create_patch=True)

    added: list[_CountDiff] = []
    modified: list[_CountDiff] = []
    deleted: list[_CountDiff] = []
    copied: list[_CountDiff] = []
    for change_type, diff in zip(change_types, diffs):
        n_a_path = 0
        if diff.a_path:
            n_a_path = tokenizer.count_tokens(diff.a_path)
        n_b_path = 0
        if diff.b_path:
            n_b_path = tokenizer.count_tokens(diff.b_path)
        n_a_mode = 0
        if diff.a_mode:
            n_a_mode = tokenizer.count_tokens(str(diff.a_mode))
        n_b_mode = 0
        if diff.b_mode:
            n_b_mode = tokenizer.count_tokens(str(diff.b_mode))

        count_diff = _CountDiff(n_a_path, n_a_mode, n_b_path, n_b_mode, diff)

        if change_type == "A":
            added.append(count_diff)
        elif change_type == "C":
            copied.append(count_diff)
        elif change_type == "D":
            deleted.append(count_diff)
        elif change_type == "M":
            modified.append(count_diff)
    meta_added: list[_CountDiff] = []
    meta_copied: list[_CountDiff] = []
    meta_deleted: list[_CountDiff] = []
    meta_modified: list[_CountDiff] = []

    for que, lst in zip(
        [meta_added, meta_modified, meta_deleted, meta_copied],
        [added, modified, deleted, copied],
    ):
        for item in lst:
            if item.total_path_mode_token() + current_tokens > token_limit:
                break
            current_tokens += item.total_path_mode_token()
            que.append(item)
    diff_added: list[_CountDiff] = []
    diff_copied: list[_CountDiff] = []
    diff_deleted: list[_CountDiff] = []
    diff_modified: list[_CountDiff] = []
    for diff_lst, meta_lst in zip(
        [diff_added, diff_modified, diff_deleted, diff_copied],
        [meta_added, meta_modified, meta_deleted, meta_copied],
    ):
        temp = list(meta_lst)
        meta_lst.clear()
        for a in temp:
            text = a.diff_text()
            if text is None:
                meta_lst.append(a)
            else:
                text_tokens = tokenizer.count_tokens(text)
                if current_tokens + text_tokens > token_limit:
                    meta_lst.append(a)
                else:
                    current_tokens += text_tokens
                    diff_lst.append(a)
    summary_md = "# Pull request summary\n\n"
    if meta_copied or diff_copied:
        summary_md += "## Copied files\n\n"
        for d in diff_copied:
            summary_md += f"from: {d.diff.a_path}(mode: {d.diff.a_mode}) to: {d.diff.b_path}(mode: {d.diff.b_mode})\n\n"
            text = d.diff_text()
            if text is None:
                raise ValueError("diff text is None")
            summary_md += "diff:\n\n"
            for line in text.splitlines():
                summary_md += f"    {line}\n"
            summary_md += "\n"
        for d in meta_copied:
            summary_md += f"from: {d.diff.a_path}(mode: {d.diff.a_mode}) to: {d.diff.b_path}(mode: {d.diff.b_mode})\n"
        summary_md += "\n"
    if meta_deleted or diff_deleted:
        summary_md += "## Deleted files\n\n"
        for d in diff_copied:
            summary_md += f"path: {d.diff.a_path} mode: {d.diff.a_mode}\n\n"
            text = d.diff_text()
            if text is None:
                raise ValueError("diff text is None")
            summary_md += "diff:\n\n"
            for line in text.splitlines():
                summary_md += f"    {line}\n"
            summary_md += "\n"
        for d in meta_copied:
            summary_md += f"path: {d.diff.a_path} mode: {d.diff.a_mode}\n"
        summary_md += "\n"

    if meta_added or diff_added:
        summary_md += "## Added files\n\n"
        for d in diff_added:
            summary_md += f"path: {d.diff.b_path} mode: {d.diff.b_mode}\n\n"
            text = d.diff_text()
            if text is None:
                raise ValueError("diff text is None")
            summary_md += "diff:\n\n"
            for line in text.splitlines():
                summary_md += f"    {line}\n"
            summary_md += "\n"
        for d in meta_added:
            summary_md += f"path: {d.diff.b_path} mode: {d.diff.b_mode}\n"
        summary_md += "\n"

    if meta_modified or diff_modified:
        summary_md += "## Modified files\n\n"
        for d in diff_modified:
            if d.diff.a_path and d.diff.b_path and d.diff.a_path != d.diff.b_path:
                headline = f"from: {d.diff.a_path}(mode: {d.diff.a_mode}) to: {d.diff.b_path}(mode: {d.diff.b_mode})\n"
            elif d.diff.a_path:
                headline = f"path: {d.diff.a_path} mode: {d.diff.a_mode}\n"
            else:
                raise ValueError("both a_path and b_path are None")
            summary_md += headline + "\n"
            text = d.diff_text()
            if text is None:
                raise ValueError("diff text is None")
            summary_md += "diff:\n\n"
            for line in text.splitlines():
                summary_md += f"    {line}\n"
            summary_md += "\n"
        for d in meta_modified:
            if d.diff.a_path and d.diff.b_path and d.diff.a_path != d.diff.b_path:
                summary_md += f"from: {d.diff.a_path}(mode: {d.diff.a_mode}) to: {d.diff.b_path}(mode: {d.diff.b_mode})\n"
            elif d.diff.a_path:
                summary_md += f"path: {d.diff.a_path} mode: {d.diff.a_mode}\n"
            else:
                raise ValueError("both a_path and b_path are None")
        summary_md += "\n"

    summary_md += "## Commit messages\n\n"
    for msg in commit_messages:
        for line in msg.splitlines():
            summary_md += f"    {line}\n"
        summary_md += "\n\n"
    return summary_md


class _CountDiff:
    def __init__(
        self, n_a_path: int, n_a_mode: int, n_b_path: int, n_b_mode: int, diff: git.Diff
    ):
        self.n_a_path = n_a_path
        self.n_a_mode = n_a_mode
        self.n_b_path = n_b_path
        self.n_b_mode = n_b_mode
        self.diff = diff

    def total_path_mode_token(self) -> int:
        return self.n_a_path + self.n_a_mode + self.n_b_path + self.n_b_mode

    def diff_text(self) -> str | None:
        return self._to_str(self.diff.diff)

    def _to_str(self, diff: str | bytes | None) -> str | None:
        res = None
        if isinstance(diff, bytes):
            res = diff.decode()
        elif isinstance(diff, str):
            res = diff
        return res


def _get_commit_messages(repo: git.Repo, start_sha: str, end_sha: str) -> list[str]:
    """Get commit messages between base and head SHAs."""
    messages = []
    for commit in repo.iter_commits(f"{start_sha}..{end_sha}"):
        if isinstance(commit.message, str):
            messages.append(commit.message)
        else:
            messages.append(commit.message.decode())
    return messages


class _Summary:

    def __init__(self, messages: list[str]):
        self.messages = messages


# https://git-scm.com/docs/git-diff/2.19.0#Documentation/git-diff.txt---diff-filterACDMRTUXB
