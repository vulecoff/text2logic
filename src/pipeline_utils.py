from spacy.tokens.token import Token
from .u_dep.dep_tree import DepTree
def build_deptree_from_spacy(node: Token):
    deptree = DepTree(node.dep_, is_word=False, is_dep=True)
    child = DepTree(node.text,  is_word=True, is_dep=False, pos=node.pos_, ent_type=node.ent_type_)
    deptree.add_child(child)
    for c in node.children:
        deptree.add_child(build_deptree_from_spacy(c))
    return deptree

from typing import List
def build_from_stanza(tokens):
    # tokens = words of a sentence
    nodes: List[DepTree] = [None for i in range(len(tokens))]
    root = None
    for w in tokens:
        idx = w.id - 1
        dt = DepTree(
            label=w.deprel, 
            is_dep=True
        )
        dt2 = DepTree(
            label=w.text,
            is_word=True, 
            pos=w.upos,
            ent_type=""
        )
        dt.add_child(dt2)
        nodes[idx] = dt
    for w in tokens:
        head = w.head - 1
        idx = w.id - 1
        if head >= 0:
            nodes[head].add_child(nodes[idx])
        else: 
            assert root == None
            root = nodes[idx] 
    assert root != None
    return root
