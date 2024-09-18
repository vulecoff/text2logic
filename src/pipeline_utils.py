from spacy.tokens.token import Token
from .u_dep.dep_tree import DepTree
def build_deptree_from_spacy(node: Token):
    deptree = DepTree(node.dep_, is_word=False, is_dep=True)
    child = DepTree(node.text,  is_word=True, is_dep=False, pos=node.pos_, ent_type=node.ent_type_)
    deptree.add_child(child)
    for c in node.children:
        deptree.add_child(build_deptree_from_spacy(c))
    return deptree