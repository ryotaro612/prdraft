import duckdb
import typing
import git
import logging
import uuid


class RepositoryStorageClient:

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def save_repository_if_not_exists(
        self, owner_name: str, repository_name: str
    ) -> uuid.UUID:
        props = {
            "owner_name": owner_name,
            "repository_name": repository_name,
        }
        self._conn.execute(
            """
            INSERT INTO github_repository (repository_id, owner_name, repository_name)
            SELECT gen_random_uuid(), $owner_name, $repository_name
            WHERE NOT EXISTS (
                SELECT 1 FROM github_repository
                WHERE owner_name = $owner_name AND repository_name = $repository_name
            );
            """,
            props,
        )
        res = self._conn.execute(
            """
            select repository_id from github_repository
            WHERE owner_name = $owner_name AND repository_name = $repository_name;
            """,
            props,
        ).fetchone()
        if res is None:
            logging.error("")
            raise RuntimeError("Failed to save or retrieve repository")
        return res[0]
