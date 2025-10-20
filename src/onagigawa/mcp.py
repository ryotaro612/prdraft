import typing
import logging
import git
from langchain_ollama import OllamaEmbeddings
import duckdb
from mcp.server.fastmcp import FastMCP
import onagigawa.repository as r

# Create an MCP server
mcp = FastMCP("onagigawa")


@typing.runtime_checkable
class Args(typing.Protocol):
    repository: str
    db: str


class State:

    def __init__(self, repository: git.Repo, db: str):
        self.repository = repository
        self.model = OllamaEmbeddings(model="qwen3-embedding:8b")
        self.db = db


state: State


@mcp.tool(
    name="find_similar_pull_requests",
    description="Find similar pull requests based on code changes.",
)
def find_similar_pull_requests(base: str, head: str) -> str:

    text = r.make_diff_summary(state.repository, base, head)

    embedding = state.model.embed_documents([text])[0]
    conn = duckdb.connect(state.db, read_only=True)

    res = conn.execute(
        "select pull_request_id, diff_text from pull_request_qwen3_embedding "
        "ORDER BY array_cosine_distance(diff_embedding, $embedding::FLOAT[4096]) limit 15",
        {"embedding": embedding},
    ).fetchall()

    ids = [record[0] for record in res]

    similar_texts = [
        r[1]
        for r in conn.execute(
            "select id, body from pull_request where id in $ids", {"ids": ids}
        ).fetchall()
    ]
    return "\n\n---\n\n".join(similar_texts)


@mcp.tool(
    name="make_pull_request_content",
    description="Make pull request content based on code changes and commit messages.",
)
def make_pull_request_content(base: str, head: str) -> str:

    text = r.make_diff_summary(state.repository, base, head)

    return text


def run(args: Args) -> int:
    global state
    repo = git.Repo(args.repository)
    state = State(repo, args.db)
    mcp.run()
    # https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#direct-execution
    return 0
