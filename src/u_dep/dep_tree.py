from ..lambda_calculus import lambda_processor
from ..lambda_calculus.lambda_ast import LambdaExpr
"""
basic tree node
binarize algorithm
from spacy

lambda-expr associated
label

procedures: --assign lambda, build_lambda, 
"""
from typing import List

class Tree:
    def __init__(self) -> None:
        self.children: List["Tree"] = []
        self.parent: "Tree" = None
    def add_child(self, node: "Tree") -> None: 
        self.children.append(node)
        node.parent = self
    def pop_child(self, idx: int):
        self.children[idx].parent = None
        self.children.pop(idx)
    def set_child(self, idx: int, node: "Tree"): 
        self.children[idx].parent = None
        self.children[idx] = node
        self.children[idx].parent = self
    def add_children(self, *nodes) -> None: 
        for n in nodes: 
            self.add_child(n)
    def nth_child(self, idx: int) -> "Tree":
        return self.children[idx]
    def is_leaf(self) -> bool: 
        return len(self.children) == 0
    def num_children(self) -> int:
        return len(self.children)
    
WORD_PREFIX = "w-"
DEP_PREFIX = "l-"
class DepTree(Tree):
    """
    For now, keep track of label, word/dependencies, and associated lambda expr
    TODO: formalize dependency tree
    """
    def __init__(self, 
                label: str, 
                is_word: bool = False,
                is_dep:bool = False, 
                pos: str = "", 
                ent_type: str = "") -> None:
        super().__init__()
        if [is_word, is_dep].count(True) != 1: 
            raise Exception("Exactly one of {} must be true."
                            .format(["is_word", "is_dep"]))
        self._label = label
        self._is_word = is_word
        self._is_dep = is_dep
        self._pos = pos 
        self._ent_type = ent_type
        
        self._lambda_expr = None
    
    def is_word(self) -> bool:
        return self._is_word
    def is_dep(self) -> bool:
        return self._is_dep
    def label(self) -> str:
        return self._label
    def prefixed_label(self) -> str:
        if self.is_word():
            return WORD_PREFIX + self.label()
        elif self.is_dep():
            return DEP_PREFIX + self.label()
        raise Exception("Code should not reach here.")
    def pos(self):
        return self._pos
    def ent_type(self):
        return self._ent_type

    def set_lambda_expr(self, expr: LambdaExpr):
        self._lambda_expr = expr
    def lambda_expr(self) -> LambdaExpr:
        if self._lambda_expr is None: 
            raise Exception("Lambda expression is not set for this TreeNode.")
        return self._lambda_expr
    
    def copy_node_data(self):
        """Return a shallow copy of this node data without any tree-related pointers"""
        dt = DepTree(
            self.label(), 
            is_word=self.is_word(),
            is_dep=self.is_dep(), 
            pos=self.pos(),
            ent_type=self.ent_type()
        )
        if self._lambda_expr != None:
            dt.set_lambda_expr(self._lambda_expr)
        return dt
    
    def __repr__(self) -> str:
        s = self.prefixed_label()
        for c in self.children:
            ss: str = c.__repr__()
            # split, indent each line, and rejoin
            ss = ss.split('\n')
            ss = "\n".join([f"\t{z}" for z in ss])
            s += "\n" + ss
        return s

    @staticmethod
    def validate(root: "DepTree"):
        """ Assert the shape of the tree
        """
        if root.is_leaf():
            assert root.is_word() and root.pos() != ""
            return True
        assert root.is_dep()
        for i, c in enumerate(root.children):
            if i == 0: 
                assert isinstance(c, DepTree) and c.is_leaf() and c.is_word()
            DepTree.validate(c)
        return True