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

    def __init__(self, repository: git.Repo, db: duckdb.DuckDBPyConnection):
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

    res = state.db.execute(
        "select pull_request_id, diff_text from pull_request_qwen3_embedding "
        "ORDER BY array_cosine_distance(diff_embedding, $embedding) limit 5",
        {"embedding": embedding},
    )

    return ", ".join([record[0] for record in res.fetchall()])


def run(args: Args) -> int:
    global state
    repo = git.Repo(args.repository)
    db = duckdb.connect(args.db)
    state = State(repo, db)
    mcp.run()
    # https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#direct-execution
    return 0
