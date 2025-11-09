import prdraft.args as args
from collections.abc import (
    AsyncIterator,
    Awaitable,
    Callable,
    Collection,
    Iterable,
    Sequence,
)
import typing
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.lowlevel.server import Server as MCPServer


def run(args: args.McpArgs) -> int:
    server = make_server(args)
    server.run()
    return 0


def make_server(args: args.McpArgs) -> FastMCP:
    return FastMCP("mcp server", lifespan=make_lifespan(args))


class AppContext:
    """Application context with typed dependencies."""

    def __init__(self, database: str, repository: str) -> None:
        self.database = database
        self.repository = repository


class LifespanContextManager(AbstractAsyncContextManager[AppContext]):
    """Lifespan context manager for MCP server."""

    def __init__(self, database: str, repository: str) -> None:
        self._database = database
        self._repository = repository

    async def __aenter__(self) -> AppContext:
        return AppContext(self._database, self._repository)

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        # https://docs.python.org/ja/3.13/reference/datamodel.html#object.__exit__
        ...


def make_lifespan(
    args: args.McpArgs,
) -> Callable[[FastMCP[AppContext]], LifespanContextManager]:
    return lambda _: LifespanContextManager(args.database, args.repository)
