import unittest
import prdraft.args as args


class TestInterpretCommandLineArguments(unittest.TestCase):

    def test_init_is_a_subcommand(self):
        res = args.parse(["init", "prdraft.db"])
        self.assertEqual("init", res.subcommand)
        self.assertEqual("prdraft.db", res.database)
