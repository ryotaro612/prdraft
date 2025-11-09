import prdraft.args as args
import ollama
import duckdb
from mcp.server.session import ServerSession
from collections.abc import (
    Callable,
)

from collections.abc import Callable
import git
from contextlib import AbstractAsyncContextManager
from mcp.server.fastmcp import Context, FastMCP
import prdraft.pullrequest as pull
import prdraft.tokenizer as t


def run(args: args.McpArgs) -> int:
    server = make_server(args)
    server.run()
    return 0


def make_server(args: args.McpArgs) -> FastMCP:
    mcp = FastMCP("mcp server", lifespan=make_lifespan(args))
    mcp.add_tool(
        query_diff_markdown_tool,
        "query_diff_markdown",
        "make a markdown that summarizes a specified revision",
        description="This tool generates a markdown summary for a specific revision to describe a pull request",
    )
    mcp.add_tool(
        find_similar_pull_request_tool,
        "find_similar_pull_request",
        "find similar pull requests based on the diff of a specified revision",
        description="This tool finds similar pull requests based on the diff of a specified revision",
    )

    return mcp


class AppContext:
    """Application context with typed dependencies."""

    def __init__(self, database: str, repository: str) -> None:
        self.database = database
        self.repository = repository
        self.model_name = "qwen3-embedding:8b"


class LifespanContextManager(AbstractAsyncContextManager[AppContext]):
    """Lifespan context manager for MCP server."""

    def __init__(self, database: str, repository: str) -> None:
        self._database = database
        self._repository = repository

    async def __aenter__(self) -> AppContext:
        return AppContext(self._database, self._repository)

    async def __aexit__(
        self,
        _exc_type,
        _exc_value,
        _traceback,
    ) -> None:
        # https://docs.python.org/ja/3.13/reference/datamodel.html#object.__exit__
        ...


def make_lifespan(
    args: args.McpArgs,
) -> Callable[[FastMCP[AppContext]], LifespanContextManager]:
    return lambda _: LifespanContextManager(args.database, args.repository)


def query_diff_markdown_tool(
    revision: str, ctx: Context[ServerSession, AppContext]
) -> str:
    app_context = ctx.request_context.lifespan_context
    tokenizer = t.Tokenizer(model_name=app_context.model_name)

    repo = git.Repo(app_context.repository)
    markdown = pull.make_summary(repo, "main", revision, tokenizer, 3500)
    return markdown
    # Do something with tokens


def find_similar_pull_request_tool(
    owner: str,
    repo_name: str,
    revision: str,
    top_k: int,
    ctx: Context[ServerSession, AppContext],
) -> dict:
    app_context = ctx.request_context.lifespan_context
    tokenizer = t.Tokenizer(model_name=app_context.model_name)

    repo = git.Repo(app_context.repository)
    markdown = pull.make_summary(repo, "main", revision, tokenizer, 3500)

    embedding = ollama.embed(model=app_context.model_name, input=markdown).embeddings[0]
    with duckdb.connect(app_context.database) as conn:
        return {
            "pullRequests": [
                {"title": p.title, "body": p.body, "changes": d}
                for p, d in pull.find_similar_pull_requests(
                    conn, owner, repo_name, app_context.model_name, embedding, top_k
                )
            ]
        }
