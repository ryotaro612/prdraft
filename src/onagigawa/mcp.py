import typing
import git
import duckdb
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("onagigawa")


class Args(typing.Protocol):
    repository: str
    db: str


class State:

    def __init__(self, repository: git.Repo, db: duckdb.DuckDBPyConnection):
        self.repository = repository
        self.repository: git.Repo


state: State | None = None


@mcp.tool()
def find_similar_pull_requests(base: str, head: str) -> str:

    return ""


def run(args: Args) -> int:
    global state
    repo = git.Repo(args.repository)
    db = duckdb.connect(args.db)
    state = State(repo, db)
    mcp.run()
    # https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#direct-execution
    return 0
