import typing
import logging
import os.path
import duckdb
import prdraft.upgrade as upgrade


@typing.runtime_checkable
class Args(typing.Protocol):
    """Arguments for init subcommand."""

    database: str


def run(args: Args) -> int:
    """if not exists."""
    if os.path.exists(args.database):
        logging.error('database "%s" already exists', args.database)
        return 1
    conn: duckdb.DuckDBPyConnection | None = None
    try:
        conn = duckdb.connect(database=args.database)
        upgrade.upgrade(conn)
    finally:
        if conn:
            conn.close()
    return 0
