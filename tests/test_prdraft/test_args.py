import unittest
import prdraft.args as args


class TestInterpretCommandLineArguments(unittest.TestCase):

    def test_init_is_a_subcommand(self):
        res = args.parse(["init", "prdraft.db"])
        self.assertEqual("init", res.subcommand)
        self.assertEqual("prdraft.db", res.database)
        self.assertFalse(res.verbose, "verbose is off by default")

    def test_verbose_mode_is_available(self):
        res = args.parse(["--verbose", "init", "prdraft.db"])
        self.assertTrue(res.verbose)
