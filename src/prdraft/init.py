import logging
import os.path
import duckdb
import prdraft.args as args


def run(args: args.InitArgs) -> int:
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
    """
    vss extension does not support delete and update records.
    https://duckdb.org/docs/stable/core_extensions/vss#persistence
    """
    conn.execute(
        """
    create table if not exists migration (
        migration_id INTEGER PRIMARY KEY,
        applied_at timestamptz not null default current_timestamp
    );
    begin transaction; insert into migration(migration_id) values(0); commit;

    create table if not exists github_repository (
        repository_id uuid PRIMARY KEY,
        owner_name varchar not null,
        repository_name varchar not null,
        unique(owner_name, repository_name)
    );

    create table if not exists github_pull_request (
      repository_id uuid not null,
      pull_request_id  bigint not null,
      source json not null,
      unique(repository_id, pull_request_id),
      foreign key(repository_id) references github_repository(repository_id)
    );

    create table if not exists pull_request_embedding(
        repository_id uuid not null,
        pull_request_id bigint not null,
        model_id varchar not null,
        unique(repository_id, pull_request_id, model_id),
        embedding float[4096] not null,
        text varchar not null
    );
    """
    )
