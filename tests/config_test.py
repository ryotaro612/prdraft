import unittest
import os.path as path
from blanketml.config import *


class TestConfig(unittest.TestCase):

    def test_load(self):

        # arrange
        testfile = path.join(path.dirname(path.abspath(__file__)), "config.toml")
        # act
        result = load(testfile)
        # assert
        self.assertEqual(
            Config(
                insutruction="Hi",
                posts={
                    "bert": Post(ja="post.md", en=None, paper="a.pdf"),
                },
            ),
            result,
        )
