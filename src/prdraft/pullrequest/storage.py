import duckdb
import prdraft.pullrequest.github as gh
import uuid


class PullRequestStorageClient:

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def count(self, owner_name: str, repository_name: str) -> int:
        """Counts the total number of fetched pull requests for the given repository."""
        result = self._conn.execute(
            """
            SELECT COUNT(g.repository_id) FROM github_pull_request g join github_repository r
            using(repository_id)
            WHERE owner_name = $owner_name AND repository_name = $repository_name
            """,
            {"owner_name": owner_name, "repository_name": repository_name},
        ).fetchone()
        return result[0] if result else 0

    def store_if_not_exists(
        self, repository_id: uuid.UUID, pull_requests: list[gh.PullRequest]
    ):
        pr_ids = [prs.id for prs in pull_requests]
        existing_ids = set(self._query_existing_pull_request_ids(repository_id, pr_ids))

        to_insert = [
            [repository_id, pull_request.id, pull_request.json()]
            for pull_request in pull_requests
            if pull_request.id not in existing_ids
        ]
        # executemanuy does not accept empty list
        if not to_insert:
            return
        self._conn.executemany(
            "insert into github_pull_request(repository_id, pull_request_id, source) values ($1, $2, $3)",
            to_insert,
        )

    def _query_existing_pull_request_ids(
        self, repository_id: uuid.UUID, pull_request_ids: list[int]
    ) -> list[int]:
        """Returns a subset of the given pull_request_ids that already exist in the database."""
        rows = self._conn.execute(
            """select pull_request_id from github_pull_request where repository_id = $1 and pull_request_id in $2""",
            (repository_id, pull_request_ids),
        ).fetchall()
        return [row[0] for row in rows]
