import duckdb
import logging
import json
import typing
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


def find_not_embeded_pull_requests(
    conn: duckdb.DuckDBPyConnection,
    repository_org: str,
    repository_name: str,
    model_id: str,
) -> typing.Generator[gh.PullRequest]:
    cur = conn.execute(
        """
    select pr.source
    from github_pull_request pr
    join github_repository r
    on r.owner_name = $repository_org and r.repository_name = $repository_name
    left join pull_request_embedding pre
    on pr.repository_id = pre.repository_id
    and pr.pull_request_id = pre.pull_request_id
    and pre.model_id = $model_id
    where pre.repository_id is null
    """,
        {
            "model_id": model_id,
            "repository_org": repository_org,
            "repository_name": repository_name,
        },
    )
    while True:
        fetched_pr = cur.fetchone()
        if fetched_pr:
            yield gh.PullRequest(json.loads(fetched_pr[0]))
        else:
            return


class EmbeddedPullRequest:

    def __init__(
        self,
        pull_request_id: int,
        embedded: typing.Sequence[float],
        text: str,
    ):
        self.pull_request_id = pull_request_id
        self.embedding = embedded
        self.text = text


def save_embedded_pull_request(
    conn: duckdb.DuckDBPyConnection,
    owner: str,
    repo_name: str,
    model_name: str,
    eprs: typing.Iterable[EmbeddedPullRequest],
) -> bool:

    record = conn.execute(
        "select repository_id from github_repository where owner_name = $owner and repository_name = $repo_name",
        {"owner": owner, "repo_name": repo_name},
    ).fetchone()
    if not record:
        return False
    repository_id = record[0]

    conn.executemany(
        """
    insert into pull_request_embedding(repository_id, pull_request_id, model_id, embedding, text)
    values (?, ?, ?, ?, ?)
    """,
        [
            (repository_id, pr.pull_request_id, model_name, pr.embedding, pr.text)
            for pr in eprs
        ],
    )
    return True


def find_similar_pull_requests(
    conn: duckdb.DuckDBPyConnection,
    owner: str,
    repo_name: str,
    model_name: str,
    pull_request_embedding: typing.Sequence[float],
    top_k: int,
) -> typing.Generator[typing.Tuple[gh.PullRequest, str]]:
    sql = """
    select pre.text, pre.source
    from pull_request_embedding pre
    join github_repository r
    on pre.repository_id = r.repository_id
    join github_pull_request pr
    on pre.pull_request_id = pr.pull_request_id
    where r.owner_name = $owner and r.repository_name = $repo_name and pre.model_id = $model_name
    order by array_cosine_distance(pre.embedding, $pull_request_embedding::FLOAT[]) limit $top_k
    """
    # "ORDER BY array_cosine_distance(diff_embedding, $embedding::FLOAT[4096]) limit 15
    cursor = conn.execute(
        sql,
        {
            "owner": owner,
            "repo_name": repo_name,
            "model_name": model_name,
            "pull_request_embedding": pull_request_embedding,
            "top_k": top_k,
        },
    )

    while True:
        record = cursor.fetchone()
        if record is None:
            break
        markdown = record[0]
        source = json.loads(record[1])
        yield gh.PullRequest(source), markdown
