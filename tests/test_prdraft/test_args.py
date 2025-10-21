import unittest
import prdraft.args as args
import prdraft.init as init


class TestInterpretCommandLineArguments(unittest.TestCase):

    def test_init_is_a_subcommand(self):
        res = args.parse(["init", "prdraft.db"])
        if isinstance(res, init.Args):
            self.assertEqual("prdraft.db", res.database)
        else:
            self.fail("parsed args is not an instance of init.Args")
        self.assertEqual("init", res.subcommand)
        self.assertFalse(res.verbose, "verbose is off by default")

    def test_verbose_mode_is_available(self):
        res = args.parse(["--verbose", "init", "prdraft.db"])
        self.assertTrue(res.verbose)
