import unittest
import sys
from onagigawa.args import parse


class TestInterpretCommandLineArguments(unittest.TestCase):

    def test_pr_is_subcommand(self):
        res = parse(['pr', 'orga', 'repo', 'output'])
        self.assertEqual('pr', res.subcommand, 'the passed subcommand is storead in subcommand')
        self.assertEqual('orga', res.organization)
        self.assertEqual('repo', res.repository)
        self.assertEqual('output', res.output)