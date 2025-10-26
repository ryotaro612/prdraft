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
        _init_db(conn)
    finally:
        if conn:
            conn.close()
    return 0


def _init_db(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
    create table if not exists migration (
        migration_id INTEGER PRIMARY KEY,
        applied_at timestamptz not null default current_timestamp
    );
    """
    )
    conn.execute(
        """
    begin transaction; insert into migration(migration_id) values(0); commit;
"""
    )
