import unittest
from src.u_dep.dep_tree import DepTree
from src.u_dep.transformer import Transformer

class TestDepTree(unittest.TestCase):

    def test_constructor(self):
        self.assertRaises(Exception, DepTree, "word", False, False)
        self.assertRaises(Exception, DepTree, "word", True, True)
    def test_methods(self):
        dt = DepTree("arrives", is_word=True)
        self.assertEqual(dt.label(), "arrives")
        self.assertEqual(dt.prefixed_label(), "w-arrives")

if __name__ == "__main__":
    unittest.main()