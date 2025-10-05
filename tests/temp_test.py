import unittest
import sys
from onagigawa.args import parse


class TestTemp(unittest.TestCase):

    def test_temp(self):
        res = parse([])
        print(sys.path)
        assert False