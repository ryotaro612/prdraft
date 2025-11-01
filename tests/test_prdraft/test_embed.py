import unittest
import os
import os.path as path
import duckdb
import uuid
import prdraft
import tempfile


class EmbedTest(unittest.TestCase):

    def test_embed_pull_requests(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            db = f"{tmpdirname}/prdraft.db"
            prdraft._main(["init", db])

            with duckdb.connect(db) as conn:
                uid = uuid.uuid4()
                conn.execute(
                    "insert into github_repository(repository_id, owner_name, repository_name) values (?, ?, ?)",
                    (uid, "org", "repo_name"),
                )
                conn.execute(
                    "insert into github_pull_request(repository_id, pull_request_id, source) values (?, ?, ?)",
                    (uid, 1, "{}"),
                )

            git_repository = path.join(
                path.dirname(path.realpath(__file__)), "..", ".."
            )
            rtn_code = prdraft._main(
                [
                    "pr",
                    "embed",
                    git_repository,
                    db,
                    "ibm-granite/granite-embedding-107m-multilingual",
                ]
            )
            self.assertEqual(0, rtn_code)
