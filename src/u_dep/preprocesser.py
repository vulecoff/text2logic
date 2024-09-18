from .dep_tree import DepTree

# TODO: copy data node with pos? 
def merge_rtl(root: DepTree, dep:str) -> DepTree: 
    # return root
    applicable = ["compound", "quantmod"]
    assert dep in applicable
    if root.is_leaf():
        return root.copy_node_data()
    fresh_root = root.copy_node_data()
    for i, c in enumerate(root.children):
        c: DepTree
        if c.label() == dep:
            child0: DepTree = fresh_root.nth_child(0)
            x = merge_rtl(c, dep)
            fresh_root.set_child(0, DepTree( 
                label=x.nth_child(0).label() + "_" + child0.label(), 
                is_word=True, 
                pos=child0.pos(), 
                ent_type=child0.ent_type()
            ))
            for j in range(1, x.num_children()):
                fresh_root.add_child(x.nth_child(j))
        else: 
            fresh_root.add_child(merge_rtl(c, dep))
    return fresh_root

def merge_ltr(root: DepTree, dep: str) -> DepTree: 
    # return root

    """Effectively concatenate all dependents to the dep_head recursively (descendents, then siblings)
    NOTE: might have trouble with hierarchy of concatenation, but 'll see
    """
    applicable = ["xcomp", "prt"]
    assert dep in applicable
    if root.is_leaf():
        return root.copy_node_data()
    fresh_root = root.copy_node_data()
    for i, c in enumerate(root.children):
        c: DepTree
        if c.label() == dep:
            child0: DepTree = fresh_root.nth_child(0)
            x = merge_ltr(c, dep)
            fresh_root.set_child(0, DepTree(
                label=child0.label() + "_" + x.nth_child(0).label(), 
                is_word=True,
                pos=child0.pos(), 
                ent_type=child0.ent_type()
            ))
            for j in range(1, x.num_children()):
                fresh_root.add_child(x.nth_child(j))
        else: 
            fresh_root.add_child(merge_ltr(c, dep))
    return fresh_root

universals = ["every", "all"]
existentials = ["a", "some", "an"]
def enrich_determiner(root: DepTree) -> DepTree:
    if root.is_leaf():
        return root.copy_node_data()
    r = root.copy_node_data()
    if r.is_dep() and r.label() == "det":
        c: DepTree = root.nth_child(0)
        if c.label().lower() in universals:
            r._label = "det:univ"
        elif c.label().lower() in existentials:
            r._label = "det:exis"
    for c in root.children:
        r.add_child(enrich_determiner(c))
    return r

from .dep_tree import Ontology
def assign_ontology(root: DepTree): 
    if root.is_leaf():
        is_copula = next((x for x in root.parent.children if x.label() == "cop"), None)
        if root.pos() == "PROPN" or root.pos() == "PRON":
            root._ontology = Ontology.INDIVIDUAL
        elif root.pos() == "VERB" or is_copula != None:
            root._ontology = Ontology.EVENT
        else: 
            root._ontology = Ontology.NA
        return 
    root._ontology = Ontology.NA
    for c in root.children: 
        assign_ontology(c)
