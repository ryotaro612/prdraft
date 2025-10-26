import unittest
import tempfile
import duckdb
import prdraft


class TestInitCommand(unittest.TestCase):

    def test_init_command_creates_table(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            db = f"{tmpdirname}/prdraft.db"
            prdraft._main(["init", db])
            with duckdb.connect(database=db) as conn:
                res = conn.execute("select migration_id from migration;").fetchone()
                if res is None:
                    self.fail("migration table does not exist or is empty")
                self.assertEqual(0, res[0])
