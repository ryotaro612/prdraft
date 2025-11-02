import unittest
import json
import uuid
import duckdb
import tempfile
import prdraft
import prdraft.pullrequest.storage as storage
import prdraft.pullrequest as pr


class PullRequestStorageTest(unittest.TestCase):

    def test_count_total_fetched_pull_requests(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            db = f"{tmpdirname}/prdraft.db"
            prdraft._main(["init", db])
            uid = uuid.uuid4()
            with duckdb.connect(database=db) as conn:
                conn.execute(
                    """
                insert into github_repository(
                    repository_id, owner_name, repository_name) values(
                  $uid, 'owner', 'repo');
                             """,
                    {"uid": uid},
                )

                conn.execute(
                    """
                insert into github_pull_request(
                             repository_id, pull_request_id, source) values
                  ($uid, 0, '{}'),
                  ($uid, 1, '{}');
                """,
                    {"uid": uid},
                )

            with duckdb.connect(database=db) as conn:
                pr_storage = storage.PullRequestStorageClient(conn)
                num = pr_storage.count("owner", "repo")
                self.assertEqual(2, num)

    def test_store_if_not_exists(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            db = f"{tmpdirname}/prdraft.db"
            prdraft._main(["init", db])

            with duckdb.connect(db) as conn:
                repository_id = uuid.uuid4()

                conn.execute(
                    """insert into github_repository(repository_id, owner_name, repository_name) values ($1, 'owner', 'repo')""",
                    [repository_id],
                )
                conn.execute(
                    """insert into github_pull_request(repository_id, pull_request_id, source) values ($1, 9, '{}'), ($1, 8, '{}')""",
                    [repository_id],
                )

                sut = storage.PullRequestStorageClient(conn)
                sut.store_if_not_exists(
                    repository_id,
                    [
                        pr.PullRequest(
                            {
                                "id": 9,
                                "number": 9,
                                "title": "PR 9",
                                "merged_at": None,
                                "head": {},
                                "base": {},
                            }
                        ),
                        pr.PullRequest(
                            {
                                "id": 2,
                                "number": 2,
                                "title": "PR 2",
                                "merged_at": None,
                                "head": {},
                                "base": {},
                            }
                        ),
                    ],
                )
                res = conn.execute(
                    """
                    select 
                    pull_request_id from github_pull_request
                    where repository_id = $1 and pull_request_id = 2""",
                    [repository_id],
                ).fetchone()
                if res is None:
                    self.fail("Expected pull request ID 2 to be found")
                self.assertEqual(2, res[0])

    def test_find_not_embeded_pull_requests(self):
        """Generator should yield only PRs without embeddings for a given model."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            db = f"{tmpdirname}/prdraft.db"
            prdraft._main(["init", db])

            owner = "owner"
            repo = "repo"
            model_id = "test-model"

            with duckdb.connect(db) as conn:
                # Insert repository
                repository_id = uuid.uuid4()
                conn.execute(
                    """insert into github_repository(repository_id, owner_name, repository_name) values ($1, $2, $3)""",
                    [repository_id, owner, repo],
                )

                # Two pull requests in source table
                conn.executemany(
                    """insert into github_pull_request(repository_id, pull_request_id, source) values (?, ?, ?)""",
                    [
                        (repository_id, 1, json.dumps({"id": 1})),
                        (repository_id, 2, json.dumps({"id": 2})),
                        (repository_id, 3, json.dumps({"id": 3})),
                    ],
                )

                # Invoke generator
                result = storage.find_not_embeded_pull_requests(
                    conn, owner, repo, model_id
                )

                self.assertEqual({1, 2, 3}, {r.id for r in result})

                for r in result:
                    print("found pr", r)
