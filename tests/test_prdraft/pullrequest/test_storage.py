import unittest
import uuid
import duckdb
import tempfile
import prdraft
import prdraft.pullrequest.storage as storage


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
