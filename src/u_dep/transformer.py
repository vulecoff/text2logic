from .dep_tree import DepTree
from  ..lambda_calculus.lambda_processor import beta_reduce, uniqueify_var_names
from .relation_priority import RelationPriority
from .dep2lambda import Dep2Lambda
from ..lambda_calculus.lambda_ast import LambdaExpr, Apply

from typing import Generator

from spacy.tokens.token import Token
def build_deptree_from_spacy(node: Token):
    deptree = DepTree(node.dep_, is_word=False, is_dep=True)
    deptree.add_child(DepTree(node.text,  is_word=True, is_dep=False))
    for c in node.children:
        deptree.add_child(build_deptree_from_spacy(c))
    return deptree

class Transformer: 
    """Transformer for Dependency tree
    """
    def __init__(self, 
                 relation_priority: RelationPriority,
                 dep2lambda: Dep2Lambda
                 ) -> None:
        self._relation_priority = relation_priority
        self._dep2lambda = dep2lambda


    def _compare(self, node: DepTree):
        """
        If word, returns MIN_NUM. If not exists, MAX_NUM
        """
        if node.is_word():
            return 0 
        elif node.is_dep():
            return self._relation_priority.get(node.label())
        raise Exception("Every node must be either a word or dependency relation.")

    def binarize(self, root: DepTree) -> DepTree:
        """
        Binarize a dep_tree. Require specific shape of deptree
        NOTE: still in development
        """
        sorted_children: list[DepTree] = sorted(root.children, key=self._compare)
        bin_tree: DepTree = None
        for c in sorted_children: 
            temp = DepTree(c.label(), is_word=c.is_word(),is_dep=c.is_dep())
            l = bin_tree # left
            r = self.binarize(c) # right
            if l != None: 
                temp.add_child(l)
            if r != None:
                temp.add_child(r)
            bin_tree = temp
        return bin_tree
    
    def _incrementer_generator(self) -> Generator[str, None, None]:
        id = 0
        while True: 
            id += 1
            nm = f"<{id}>"
            yield nm
    
    def _assign_lambda(self, root: DepTree, incrementer: Generator[str, None,None]) -> None:
        """Helper function for assign lambda"""
        if root.num_children() != 0 and root.num_children() != 2:
            raise Exception("DepTree has not been binarized.")
        
        expr = self._dep2lambda.get(root)
        root.set_lambda_expr(uniqueify_var_names(expr, incrementer))
        for c in root.children: 
            self._assign_lambda(c, incrementer)
    def assign_lambda(self, root: DepTree) -> None:
        """Reassign variable names to int so that it is unique across the dep_tree"""
        incrementer = self._incrementer_generator()
        self._assign_lambda(root, incrementer)

    def build_lambda_tree(self, root: DepTree) -> None: 
        """ Build lambda expression for the entire subtree
        """
        if root.num_children() != 0 and root.num_children() != 2:
            raise Exception("DepTree has not been binarized.")
        if root.is_leaf():
            return root.lambda_expr()
        return Apply(
            root.lambda_expr(),
            self.build_lambda_tree(root.nth_child(0)),
            self.build_lambda_tree(root.nth_child(1))
        )


    def compose_semantics(self, root: DepTree) -> LambdaExpr:
        """
        Compose semantics of dep tree using beta-reduction
        """
        if root.num_children() != 0 and root.num_children() != 2:
            raise Exception("DepTree has not been binarized.")
        e = root.lambda_expr()
        if root.is_leaf():
            return e
        return beta_reduce(Apply(
            e, 
            self.compose_semantics(root.nth_child(0)),
            self.compose_semantics(root.nth_child(1))
        ))
    
    def tree_repr_with_priority(self, root: DepTree) -> str:
        s = f"({root.prefixed_label()}, {self._compare(root)})"
        for c in root.children:
            ss = self.tree_repr_with_priority(c)
            ss = ss.split('\n')
            ss = "\n".join([f"\t{z}" for z in ss])
            s += "\n" + ss 
        return s