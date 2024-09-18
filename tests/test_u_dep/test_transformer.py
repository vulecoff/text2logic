import unittest
from src.u_dep.dep_tree import DepTree, DEP_PREFIX, WORD_PREFIX
from src.u_dep.transformer import Transformer
from src.pipeline_utils import build_deptree_from_spacy
import spacy

class TestTransformer(unittest.TestCase):
    def setUp(self):
        self.nlp = spacy.load("en_core_web_sm")
    def tearDown(self) -> None:
        pass

    def test_build_from_spacy(self):
        sent = "Brutus stabbed Ceasar"
        doc= self.nlp(sent)
        root = list(doc.sents)[0].root
        dtree = build_deptree_from_spacy(root)
        self.assertEqual(DepTree.validate(dtree), True)
        

if __name__ == "__main__":
    unittest.main()