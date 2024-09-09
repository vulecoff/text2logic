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

class Tree:
    def __init__(self) -> None:
        self.children: list = []
    def add_child(self, node: "Tree") -> None: 
        self.children.append(node)
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
    """

    def __init__(self, label: str, is_word: bool = False, is_dep:bool = False) -> None:
        super().__init__()
        if [is_word, is_dep].count(True) != 1: 
            raise Exception("Exactly one of {} must be true."
                            .format(["is_word", "is_dep"]))
        self._label = label
        self._is_word = is_word
        self._is_dep = is_dep
        
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
    
    def set_lambda_expr(self, expr: LambdaExpr):
        self._lambda_expr = expr
    def lambda_expr(self) -> LambdaExpr:
        if self._lambda_expr is None: 
            raise Exception("Lambda expression is not set for this TreeNode.")
        return self._lambda_expr
    
    def __repr__(self) -> str:
        s = self.prefixed_label()
        for c in self.children:
            ss: str = c.__repr__()
            # split, indent each line, and rejoin
            ss = ss.split('\n')
            ss = "\n".join([f"\t{z}" for z in ss])
            s += "\n" + ss
        return s
