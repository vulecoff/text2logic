import unittest
from src.u_dep.dep_tree import DepTree, DEP_PREFIX, WORD_PREFIX, Tree
from src.u_dep.transformer import Transformer

class TestDepTree(unittest.TestCase):

    def test_constructor(self):
        self.assertRaises(Exception, DepTree, "word", False, False)
        self.assertRaises(Exception, DepTree, "word", True, True)

    def test_prefixes_labels(self):
        dt = DepTree("arrives", is_word=True)
        self.assertEqual(dt.label(), "arrives")
        self.assertEqual(dt.prefixed_label(), "w-arrives")
        dt = DepTree("punct", is_dep=True)
        self.assertEqual(dt.prefixed_label(), "l-punct")
        self.assertEqual(dt.prefixed_label(), DEP_PREFIX + "punct")

    def test_nodedata_copy(self):
        dt = DepTree("advmod", is_dep=True)
        dt.add_child(DepTree("word", is_word=True))
        self.assertEqual(dt.num_children(), 1)
        dt2 = dt.copy_node_data()
        self.assertEqual(dt2.num_children() , 0)
        self.assertEqual(dt.label(), dt2.label())
        self.assertEqual(dt.is_word(), dt2.is_word())
        self.assertEqual(dt.is_dep(), dt2.is_dep())
        self.assertEqual(dt._lambda_expr, dt2._lambda_expr)

class TestTreeDS(unittest.TestCase):
    def test_methods(self): 
        root = Tree()
        c0 = Tree()
        self.assertEqual(c0.parent, None)
        root.add_child(c0)
        self.assertEqual(c0.parent, root)
        root.pop_child(0)
        self.assertEqual(c0.parent, None)
        c1 = Tree()
        c2 = Tree()
        root.add_children(c1, c2)
        self.assertTrue(c1.parent == c2.parent == root)
        c3 = Tree()
        root.set_child(1, c3)
        self.assertEqual(c3.parent, root)
        self.assertEqual(c2.parent, None)

if __name__ == "__main__":
    unittest.main()