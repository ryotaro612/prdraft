import unittest
from unittest.mock import MagicMock, patch

import os
import prdraft.args as args
import prdraft.init as init


class TestInterpretCommandLineArguments(unittest.TestCase):

    def test_init_is_a_command(self):
        res = args.Parser().parse(["init", "prdraft.db"])
        if res:
            self.assertEqual("prdraft.db", res.database)
        else:
            self.fail("parsed args is None")

        self.assertEqual("init", res.command)
        self.assertFalse(res.verbose, "verbose is off by default")

    def test_verbose_mode_is_available(self):
        res = args.Parser().parse(["--verbose", "init", "prdraft.db"])
        if res:
            self.assertTrue(res.verbose)
        else:
            self.fail("parsed args is None")

    @patch("os.getenv")
    def test_pr_fetch_is_a_sub_command(self, mock_getenv):
        mock_getenv.return_value = "fake_token"

        res = args.Parser().parse(["pr", "fetch", "prdraft.db", "owner/repo"])
        if not isinstance(res, args.PrFetchArgs):
            self.fail("parsed args is not an instance of PrFetchArgs")

        self.assertFalse(res.verbose)
        self.assertEqual("pr", res.command)
        self.assertEqual("fetch", res.subcommand)
        self.assertEqual("owner/repo", res.ghrepo)
        self.assertEqual("fake_token", res.github_api_key)
        mock_getenv.assert_called_with("PRDRAFT_GITHUB_TOKEN", None)

    def test_embed_is_a_sub_command(self):
        res = args.Parser().parse(
            [
                "pr",
                "embed",
                "my-repo",
                "prdraft.db",
                "ibm-granite/granite-embedding-107m-multilingual",
            ]
        )
        if not isinstance(res, args.PrEmbedArgs):
            self.fail("parsed args is not an instance of PrEmbedArgs")

        self.assertFalse(res.verbose)
        self.assertEqual("pr", res.command)
        self.assertEqual("embed", res.subcommand)
        self.assertEqual("prdraft.db", res.database)
        self.assertEqual("ibm-granite/granite-embedding-107m-multilingual", res.model)
