import typing
import json
import logging
import git
import duckdb
from langchain_ollama import OllamaEmbeddings
import onagigawa.pull_request as pr
import onagigawa.repository as r


@typing.runtime_checkable
class Args(typing.Protocol):
    """Arguments for the embed subcommand."""

    pr: str
    repository: str
    db: str


def run(args: Args) -> int:
    db = duckdb.connect(args.db)
    repo = git.Repo(args.repository)
    model = OllamaEmbeddings(model="qwen3-embedding:8b")
    # embeddings.embed_documents([])

    pull_requests = [json.loads(line) for line in open(args.pr, "r").readlines()]
    exit_code = 0
    for i, pull_request in enumerate(pull_requests):
        logging.debug(f"Processing pull request[{i}]")
        p = pr.PullRequest(pull_request)
        exist = db.execute(
            "select * from pull_request_qwen3_embedding where pull_request_id = $id",
            {"id": p.id},
        ).fetchone()
        if exist:
            logging.debug("Already exists in the database. Skipping.")
            continue

        if not p.merged:
            continue
        head = p.head_sha
        base = p.base_sha

        if head is None or base is None:
            logging.error(f"head or base sha is missing: pull_request={pull_request}")
            exit_code = 1
            continue

        messages = r.get_commit_messages(repo, base, head)
        diffs = r.get_diff(repo, base, head)

        text = render_md(messages, diffs)
        print(text)
        embedding = model.embed_documents([text])[0]
        db.execute(
            "insert into pull_request_qwen3_embedding(pull_request_id, diff_text, diff_embedding) values ($id, $text, $embedding)",
            {"id": p.id, "text": text, "embedding": embedding},
        )

    return exit_code


def render_md(messages: list[str], diffs: list[r.Diff]) -> str:
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
