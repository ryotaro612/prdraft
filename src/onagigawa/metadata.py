import typing
import logging
import duckdb
import git
import json


@typing.runtime_checkable
class Args(typing.Protocol):
    pullrequests: str
    repository: str
    metadata: str


class PullRequest:
    """"""

    def __init__(self, raw: dict):
        """"""
        self._raw = raw

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


def run(args: Args):
    repo = git.Repo(args.repository)
    with open(args.pullrequests, "r") as f:
        pull_requests: list[PullRequest] = [
            PullRequest(json.loads(line)) for line in f.readlines()
        ]

    pull_request_summaries = []
    for pull_request in pull_requests:
        if not pull_request.merged():
            continue
        head = pull_request.head_sha
        base = pull_request.base_sha
        if head is None or base is None:
            raise RuntimeError("head or base sha is None")

        summary = {
            "diffs": [],
            "messages": [
                commit.message for commit in repo.iter_commits(f"{base}..{head}")
            ],
        }

        change_types = [
            diff.change_type for diff in repo.commit(base).diff(repo.commit(head))
        ]

        for i, diff in enumerate(
            repo.commit(base).diff(repo.commit(head), create_patch=True)
        ):
            if isinstance(diff.diff, bytes):
                d = diff.diff.decode()
            elif isinstance(diff.diff, str):
                d = diff.diff
            else:
                d = None
            summary["diffs"].append(
                {
                    "aPath": diff.a_path,
                    "bPath": diff.b_path,
                    "diff": d,
                    "changeType": change_types[i],
                    "copiedFile": diff.copied_file,
                    "deletedFile": diff.deleted_file,
                    "renamedFile": diff.renamed_file,
                    "newFile": diff.new_file,
                }
            )
        pull_request_summaries.append(summary)

    with open(args.metadata, "w") as f:
        for pr_summary in pull_request_summaries:
            f.write(json.dumps(pr_summary) + "\n")
