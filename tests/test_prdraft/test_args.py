import unittest
from unittest.mock import MagicMock
import os
import prdraft.args as args
import prdraft.init as init


class TestInterpretCommandLineArguments(unittest.TestCase):

    def test_init_is_a_command(self):
        res = args.parse(["init", "prdraft.db"])
        self.assertEqual("prdraft.db", res.database)

        self.assertEqual("init", res.command)
        self.assertFalse(res.verbose, "verbose is off by default")

    def test_verbose_mode_is_available(self):
        res = args.parse(["--verbose", "init", "prdraft.db"])
        self.assertTrue(res.verbose)

    def test_pr_fetch_is_a_sub_command(self):
        os.getenv = MagicMock(return_value="fake_token")

        res = args.parse(["pr", "fetch", "prdraft.db", "owner/repo"])
        if not isinstance(res, args.PrFetchArgs):
            self.fail("parsed args is not an instance of PrFetchArgs")

        self.assertFalse(res.verbose)
        self.assertEqual("pr", res.command)
        self.assertEqual("fetch", res.subcommand)
        self.assertEqual("owner/repo", res.ghrepo)
        self.assertEqual("fake_token", res.github_api_key)
        os.getenv.assert_called_with("PRDRAFT_GITHUB_TOKEN", None)
