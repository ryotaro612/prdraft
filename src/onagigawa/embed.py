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

        text = r.make_diff_summary(repo, base, head)
        print(text)
        embedding = model.embed_documents([text])[0]
        db.execute(
            "insert into pull_request_qwen3_embedding(pull_request_id, diff_text, diff_embedding) values ($id, $text, $embedding)",
            {"id": p.id, "text": text, "embedding": embedding},
        )

    return exit_code
