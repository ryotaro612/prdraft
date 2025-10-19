import typing
import json
import duckdb


class Args(typing.Protocol):
    """Arguments for the embed subcommand."""

    pr: str
    diff: str
    db: str


def run(args: Args) -> int:
    db = duckdb.connect(args.db)

    pull_requests = [json.loads(line) for line in open(args.pr, "r").readlines()]
    diffs = [json.loads(line) for line in open(args.diff, "r").readlines()]

    for pull_request, diff in zip(pull_requests, diffs):
        pr_id = pull_request["id"]
        diff_text = diff["diff_text"]

    return 0
