import unittest
from blanketml.parser import *


class TestParse(unittest.TestCase):

    def test_the_first_argument_is_config_file(self):
        res = parse(["co"])

        self.assertEqual(Command("co"), res)
