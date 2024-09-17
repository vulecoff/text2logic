from typing import Callable
from ..lambda_calculus.lambda_ast import LambdaExpr
from ..u_dep.dep_tree import DepTree
from ..dep2lambda_converter.default import default_converter
class Dep2Lambda: 
    def __init__(self, converter: Callable[[DepTree], LambdaExpr] = default_converter) -> None:
        self.converter = converter

    def get(self, node: DepTree):
        res = self.converter(node)
        if not isinstance(res, LambdaExpr):
            raise Exception("Unexpected errors occured in converter {}".format(self.converter.__name__))
        return res