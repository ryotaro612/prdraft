import duckdb


class PullRequestStorageClient:

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def count(self, owner_name: str, repository_name: str) -> int:
        result = self._conn.execute(
            """
            SELECT COUNT(g.repository_id) FROM github_pull_request g join github_repository r
            using(repository_id)
            WHERE owner_name = $owner_name AND repository_name = $repository_name
            """,
            {"owner_name": owner_name, "repository_name": repository_name},
        ).fetchone()
        return result[0] if result else 0
