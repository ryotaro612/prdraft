import unittest
import uuid
import duckdb
import tempfile
import prdraft
import prdraft.repository as repository


class PullRequestStorageTest(unittest.TestCase):

    def test_count_total_fetched_pull_requests(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            db = f"{tmpdirname}/prdraft.db"
            prdraft._main(["init", db])
            with duckdb.connect(database=db) as conn:
                sut = repository.RepositoryStorageClient(conn)
                repository_id = sut.save_repository_if_not_exists("a", "b")
                self.assertIsInstance(repository_id, uuid.UUID)
                next_repository_id = sut.save_repository_if_not_exists("a", "b")
                self.assertEqual(repository_id, next_repository_id)
