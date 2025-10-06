import typing
import os
import json
import git


@typing.runtime_checkable
class Args(typing.Protocol):
    pr: str
    repository: str
    dir: str


def run(args: Args) -> int:
    """Create pairs of pull requests and diffs."""
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    with open(args.pr, "r") as f:
        prs = [json.loads(line) for line in f.readlines() if len(line.strip())]

    # https://python.langchain.com/api_reference/community/vectorstores/langchain_community.vectorstores.duckdb.DuckDB.html#langchain_community.vectorstores.duckdb.DuckDB.aadd_documents
    # pr をきれいにする
    for pr in prs:
        os.path.join(args.dir, f"{pr['number']}.json")

    repo = git.Repo(args.repository)  # verify the repository is valid
    return 0
