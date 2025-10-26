""" """

import duckdb


def upgrade(conn: duckdb.DuckDBPyConnection):
    """Upgrades the database."""
    add_migration_table(conn)


def add_migration_table(conn: duckdb.DuckDBPyConnection) -> None:
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
